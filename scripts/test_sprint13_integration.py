"""
Integration Test: Sprint 13 ComfyUI + ImageValidator на реальном посте.

Pipeline:
1. Взять approved пост из БД
2. Сгенерировать картинку (ComfyUI или Pollinations fallback)
3. Провалидировать через ImageValidator (llava:7b)
4. Опубликовать в Telegram (sendPhoto)
5. Опубликовать в VK (wall.uploadPhoto + wall.post с fallback)
"""
import sys, json, time, uuid, requests
from pathlib import Path
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM

print("=" * 70)
print("SPRINT 13 INTEGRATION TEST (FIXED)")
print("ComfyUI + ImageValidator + Real Publishing")
print("=" * 70)

db = SessionLocal()

# ============================================================
# STEP 1: Находим реальный approved пост
# ============================================================
print("\n[STEP 1] Ищем approved пост для теста...")

content = (
    db.query(ContentORM)
    .filter(ContentORM.status == "approved")
    .order_by(ContentORM.created_at.desc())
    .first()
)

if not content:
    print("❌ Нет approved постов в БД!")
    db.close()
    sys.exit(1)

print(f"✅ Найден пост:")
print(f"   ID: {content.id}")
print(f"   Headline: {content.headline[:60]}...")
print(f"   Quality score: {content.quality_score}")
print(f"   Channel ID: {content.channel_id}")

# ============================================================
# STEP 2: Генерируем картинку (ComfyUI с fallback)
# ============================================================
print("\n[STEP 2] Генерируем картинку...")

from engines.comfyui.engine import ComfyUIEngine

comfyui = ComfyUIEngine(base_url="http://comfyui:8188")
print(f"   ComfyUI доступен: {comfyui._check_health()}")
print(f"   (Если нет - будет использован Pollinations fallback)")

gen_start = time.time()
image_result = comfyui.generate(
    prompt=content.headline[:80],
    negative_prompt="low quality, blurry, text, watermark",
    width=1024,
    height=576,
    model="flux"
)
gen_time = time.time() - gen_start

if not image_result or not image_result.get("image_url"):
    print("❌ Не удалось сгенерировать картинку!")
    db.close()
    sys.exit(1)

image_url = image_result["image_url"]
source = image_result.get("source", "unknown")
print(f"✅ Картинка сгенерирована за {gen_time:.2f}s")
print(f"   Source: {source}")
print(f"   URL: {image_url[:100]}...")

# ============================================================
# STEP 3: Валидация через ImageValidator (llava:7b)
# ============================================================
print("\n[STEP 3] Валидируем картинку через llava:7b...")

from engines.image_validator.engine import ImageValidatorEngine

validator = ImageValidatorEngine(
    ollama_url="http://host.docker.internal:11434",
    model="llava:7b"
)

val_start = time.time()
validation = validator.validate(
    image_url=image_url,
    original_prompt=content.headline,
    context=f"News post illustration: {content.headline[:50]}"
)
val_time = time.time() - val_start

print(f"✅ Валидация завершена за {val_time:.2f}s")
print(f"   Quality: {validation['quality_score']}/100")
print(f"   Prompt Match: {validation['prompt_match']}/100")
print(f"   Aesthetic: {validation['aesthetic_score']}/100")
print(f"   Overall: {validation['overall_score']}/100")
print(f"   Passed: {'✅ YES' if validation['passed'] else '❌ NO'}")
print(f"   Feedback: {validation['feedback'][:150]}...")

if not validation['passed']:
    print("\n⚠️ Картинка не прошла валидацию - публикация отменена")
    db.close()
    sys.exit(0)

# Сохраняем URL в контент
content.image_url = image_url
content.image_prompt = image_result.get("prompt", "")
db.commit()
print(f"\n✅ image_url сохранён в контент {content.id}")

# ============================================================
# STEP 4: Публикация в Telegram (sendPhoto)
# ============================================================
print("\n[STEP 4] Публикуем в Telegram...")

telegram_channel = (
    db.query(ChannelORM)
    .filter(
        ChannelORM.id == content.channel_id,
        ChannelORM.platform == "telegram",
        ChannelORM.is_active == True,
        ChannelORM.is_connected == True
    )
    .first()
)

telegram_result = None
if telegram_channel and telegram_channel.bot_token and telegram_channel.chat_id:
    from engines.telegram.publisher import TelegramPublisher
    
    publisher = TelegramPublisher(
        bot_token=telegram_channel.bot_token,
        chat_id=telegram_channel.chat_id
    )
    
    try:
        telegram_result = publisher.publish_photo(
            text=content.draft_text or content.headline,
            image_url=image_url
        )
        if telegram_result.get("status") == "success":
            msg_id = telegram_result.get("message_id")
            content.telegram_message_id = str(msg_id)
            db.commit()
            print(f"✅ Telegram: опубликовано! message_id={msg_id}")
        else:
            print(f"⚠️ Telegram: {telegram_result}")
    except Exception as e:
        print(f"❌ Telegram error: {e}")
else:
    print("⚠️ Нет активного Telegram канала с credentials - пропускаем")
    print(f"   Channel: {telegram_channel.name if telegram_channel else 'not found'}")
    print(f"   Platform: {telegram_channel.platform if telegram_channel else 'N/A'}")

# ============================================================
# STEP 5: Публикация в VK (с fallback на text-only)
# ============================================================
print("\n[STEP 5] Публикуем в VK...")

vk_channel = (
    db.query(ChannelORM)
    .filter(ChannelORM.platform == "vk", ChannelORM.is_active == True)
    .first()
)

vk_result = None
vk_published_with_image = False

if vk_channel and vk_channel.vk_group_id and vk_channel.vk_access_token:
    group_id = vk_channel.vk_group_id.lstrip("-")
    access_token = vk_channel.vk_access_token
    
    try:
        # 5.1 Скачиваем картинку локально
        print(f"   Скачиваем картинку для VK...")
        img_response = requests.get(image_url, timeout=60)
        img_response.raise_for_status()
        
        temp_path = Path(f"/tmp/vk_photo_{uuid.uuid4().hex[:8]}.png")
        temp_path.write_bytes(img_response.content)
        print(f"   Скачано: {len(img_response.content)} bytes")
        
        # 5.2 Получаем upload URL от VK
        upload_url_resp = requests.get(
            "https://api.vk.com/method/photos.getWallUploadServer",
            params={
                "group_id": group_id,
                "access_token": access_token,
                "v": "5.199"
            },
            timeout=30
        ).json()
        
        upload_url = upload_url_resp.get("response", {}).get("upload_url")
        
        # Проверяем ошибку 27 (group auth not allowed)
        if not upload_url or "error" in upload_url_resp:
            error = upload_url_resp.get("error", {})
            error_code = error.get("error_code")
            
            if error_code == 27:
                print(f"⚠️ VK ошибка 27: group token не может загружать фото")
                print(f"   Используем fallback: публикация без фото")
                
                # Fallback: публикуем только текст
                post_resp = requests.post(
                    "https://api.vk.com/method/wall.post",
                    data={
                        "owner_id": f"-{group_id}",
                        "from_group": 1,
                        "message": content.draft_text or content.headline,
                        "access_token": access_token,
                        "v": "5.199"
                    },
                    timeout=30
                ).json()
                
                if "response" in post_resp and "post_id" in post_resp["response"]:
                    post_id = post_resp["response"]["post_id"]
                    print(f"✅ VK: опубликовано (text-only)! post_id={post_id}")
                    print(f"   URL: https://vk.com/wall-{group_id}_{post_id}")
                    vk_result = post_id
                    vk_published_with_image = False
                else:
                    print(f"❌ VK wall.post failed: {post_resp}")
            else:
                print(f"❌ VK: не получен upload_url: {upload_url_resp}")
        else:
            # 5.3 Загружаем фото на сервер VK
            with open(temp_path, "rb") as f:
                upload_resp = requests.post(
                    upload_url,
                    files={"photo": f},
                    timeout=60
                ).json()
            
            if "photo" not in upload_resp:
                print(f"❌ VK upload failed: {upload_resp}")
                # Fallback на text-only
                print(f"   Используем fallback: публикация без фото")
                post_resp = requests.post(
                    "https://api.vk.com/method/wall.post",
                    data={
                        "owner_id": f"-{group_id}",
                        "from_group": 1,
                        "message": content.draft_text or content.headline,
                        "access_token": access_token,
                        "v": "5.199"
                    },
                    timeout=30
                ).json()
                
                if "response" in post_resp and "post_id" in post_resp["response"]:
                    post_id = post_resp["response"]["post_id"]
                    print(f"✅ VK: опубликовано (text-only fallback)! post_id={post_id}")
                    vk_result = post_id
            else:
                # 5.4 Сохраняем фото в VK
                save_resp = requests.get(
                    "https://api.vk.com/method/photos.saveWallPhoto",
                    params={
                        "group_id": group_id,
                        "photo": upload_resp["photo"],
                        "server": upload_resp.get("server"),
                        "hash": upload_resp.get("hash"),
                        "access_token": access_token,
                        "v": "5.199"
                    },
                    timeout=30
                ).json()
                
                photos = save_resp.get("response", [])
                if not photos:
                    print(f"❌ VK save failed: {save_resp}")
                    # Fallback на text-only
                    print(f"   Используем fallback: публикация без фото")
                    post_resp = requests.post(
                        "https://api.vk.com/method/wall.post",
                        data={
                            "owner_id": f"-{group_id}",
                            "from_group": 1,
                            "message": content.draft_text or content.headline,
                            "access_token": access_token,
                            "v": "5.199"
                        },
                        timeout=30
                    ).json()
                    
                    if "response" in post_resp and "post_id" in post_resp["response"]:
                        post_id = post_resp["response"]["post_id"]
                        print(f"✅ VK: опубликовано (text-only fallback)! post_id={post_id}")
                        vk_result = post_id
                else:
                    photo_attachment = f"photo{photos[0]['owner_id']}_{photos[0]['id']}"
                    
                    # 5.5 Публикуем пост с фото
                    post_resp = requests.post(
                        "https://api.vk.com/method/wall.post",
                        data={
                            "owner_id": f"-{group_id}",
                            "from_group": 1,
                            "message": content.draft_text or content.headline,
                            "attachments": photo_attachment,
                            "access_token": access_token,
                            "v": "5.199"
                        },
                        timeout=30
                    ).json()
                    
                    if "response" in post_resp and "post_id" in post_resp["response"]:
                        post_id = post_resp["response"]["post_id"]
                        print(f"✅ VK: опубликовано с фото! post_id={post_id}")
                        print(f"   URL: https://vk.com/wall-{group_id}_{post_id}")
                        vk_result = post_id
                        vk_published_with_image = True
                    else:
                        print(f"❌ VK wall.post failed: {post_resp}")
        
        # Чистим временный файл
        temp_path.unlink(missing_ok=True)
    except Exception as e:
        print(f"❌ VK error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("⚠️ Нет активного VK канала с credentials - пропускаем")

# ============================================================
# ИТОГОВЫЙ ОТЧЁТ
# ============================================================
print("\n" + "=" * 70)
print("ИТОГОВЫЙ ОТЧЁТ")
print("=" * 70)
print(f"Пост: {content.headline[:50]}...")
print(f"Генерация: {gen_time:.2f}s ({source})")
print(f"Валидация: {val_time:.2f}s (score={validation['overall_score']}/100)")
print(f"Telegram: {'✅ опубликовано с фото' if telegram_result and telegram_result.get('status')=='success' else '❌'}")
print(f"VK: {'✅ опубликовано с фото' if vk_result and vk_published_with_image else '✅ опубликовано (text-only)' if vk_result else '❌'}")
print("=" * 70)

db.close()
