import pathlib

p = pathlib.Path("/app/backend/automation/jobs/news_publish_job.py")
c = p.read_text(encoding="utf-8")

# 1. Импорт
if "ABTestFramework" not in c:
    c = c.replace(
        "from engines.channel_profiles import resolve_channel_profile",
        "from engines.channel_profiles import resolve_channel_profile\nfrom engines.ab_test_framework import ABTestFramework",
        1,
    )

# 2. Init в __init__
if "self.ab_framework" not in c:
    c = c.replace(
        "        self.logger = logging.getLogger(self.__class__.__name__)",
        "        self.logger = logging.getLogger(self.__class__.__name__)\n        self.ab_framework = ABTestFramework()",
        1,
    )

# 3. Поиск активного теста в run() после profile
old = '''            publisher = get_publisher_for_channel(news_channel)'''
new = '''            # A/B test (если есть running тест для этого канала)
            active_test = self.ab_framework.get_active_test(
                channel_id=news_channel.id,
                content_type=profile.get("content_type", "news"),
            )
            if active_test:
                self.logger.info(f"Active A/B test: {active_test.name}")

            publisher = get_publisher_for_channel(news_channel)'''
if old in c:
    c = c.replace(old, new, 1)

# 4. Назначение варианта перед _publish_one
old2 = '''                try:
                    result = self._publish_one('''
new2 = '''                # A/B: назначение варианта
                variant = None
                if active_test:
                    variant = self.ab_framework.assign_variant(active_test, item.id)
                    self.ab_framework.record_exposure(str(active_test.id), str(item.id), variant["id"])
                    self.logger.info(f"Post assigned to variant: {variant.get('name')}")

                try:
                    result = self._publish_one('''
if old2 in c:
    c = c.replace(old2, new2, 1)

# 5. Передача variant в вызов
old3 = '''                        channel=news_channel,
                        profile=profile,
                    )'''
new3 = '''                        channel=news_channel,
                        profile=profile,
                        variant=variant,
                    )'''
if old3 in c:
    c = c.replace(old3, new3, 1)

# 6. Сигнатура _publish_one
old4 = '''        channel: ChannelORM,
        profile: dict,
    ) -> Dict[str, Any]:'''
new4 = '''        channel: ChannelORM,
        profile: dict,
        variant: dict = None,
    ) -> Dict[str, Any]:'''
if old4 in c:
    c = c.replace(old4, new4, 1)

# 7. Применение variant config к formatting
old5 = '''        publishing_policy = profile.get("publishing_policy", {})
        formatting = profile.get("formatting_profile", {})
        title_name = news_article.title'''
new5 = '''        publishing_policy = profile.get("publishing_policy", {})
        formatting = dict(profile.get("formatting_profile", {}))
        
        # A/B: применяем overrides из варианта
        if variant and variant.get("config"):
            cfg = variant["config"]
            for key in ("emoji_header", "include_description", "max_hashtags", "unescape_html"):
                if key in cfg:
                    formatting[key] = cfg[key]
        
        title_name = news_article.title'''
if old5 in c:
    c = c.replace(old5, new5, 1)

# 8. Variant может отключать картинку
old6 = '''        # Для news можно публиковать без картинки (как text post)
        if not image_url:
            self.logger.info(f"Publishing as text post (no valid image)")'''
new6 = '''        # A/B: вариант может отключать картинку
        if variant and variant.get("config", {}).get("include_image") is False:
            image_url = None
            image_bytes = None

        # Для news можно публиковать без картинки (как text post)
        if not image_url:
            self.logger.info(f"Publishing as text post (no valid image)")'''
if old6 in c:
    c = c.replace(old6, new6, 1)

p.write_text(c, encoding="utf-8")
print("✅ NewsPublishJob: A/B integration added")