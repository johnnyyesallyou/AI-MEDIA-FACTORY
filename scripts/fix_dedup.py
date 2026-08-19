import pathlib, py_compile

f = pathlib.Path('backend/automation/jobs/monitoring_job.py')
s = f.read_text(encoding='utf-8')

# Старый метод с багом
old_method = '''    def _should_alert(self, redis_client, key: str, payload: str) -> bool:
        """Returns True if alert should be sent (not deduped)."""
        if redis_client is None:
            return True
        full_key = f"{self.ALERT_DEDUP_PREFIX}{key}"
        try:
            existing = redis_client.get(full_key)
            if existing and existing.decode("utf-8") == payload:
                return False
            redis_client.setex(full_key, self.ALERT_DEDUP_TTL_SECONDS, payload)
            return True
        except Exception as e:
            logger.warning("Redis dedup failed: %s", e)
            return True'''

# Новый метод: dedup_key отдельно от message
new_method = '''    def _should_alert(self, redis_client, key: str, dedup_value: str) -> bool:
        """Returns True if alert should be sent (not deduped).
        
        dedup_value: stable identifier (service name + status), without timestamp.
        """
        if redis_client is None:
            return True
        full_key = f"{self.ALERT_DEDUP_PREFIX}{key}"
        try:
            existing = redis_client.get(full_key)
            if existing and existing.decode("utf-8") == dedup_value:
                return False
            redis_client.setex(full_key, self.ALERT_DEDUP_TTL_SECONDS, dedup_value)
            return True
        except Exception as e:
            logger.warning("Redis dedup failed: %s", e)
            return True'''

if old_method in s:
    s = s.replace(old_method, new_method, 1)
    print("✅ Метод _should_alert обновлён")
else:
    print("⚠️ Старый метод не найден")

# Обновляем вызовы _should_alert в run()
old_call = '''                if self._send_alert(redis_client, key, msg):
                    alerts_sent += 1
                else:
                    alerts_suppressed += 1'''

new_call = '''                dedup_value = f"{check['name']}:{check['status']}:{check['detail']}"
                if self._send_alert(redis_client, key, dedup_value, msg):
                    alerts_sent += 1
                else:
                    alerts_suppressed += 1'''

count = s.count(old_call)
if count > 0:
    s = s.replace(old_call, new_call)
    print(f"✅ Обновлены {count} вызова _send_alert")
else:
    print("⚠️ Вызовы _send_alert не найдены")

# Обновляем _send_alert signature
old_send = '''    def _send_alert(self, redis_client, key: str, text_msg: str) -> bool:
        """Sends alert if not deduped. Returns True if sent."""
        if not self.alert_bot_token or not self.alert_chat_id:
            logger.info("ALERT_BOT_TOKEN/ALERT_CHAT_ID not set - skipping alert")
            return False
        if not self._should_alert(redis_client, key, text_msg):
            logger.info("Alert suppressed (dedup): %s", key)
            return False'''

new_send = '''    def _send_alert(self, redis_client, key: str, dedup_value: str, text_msg: str) -> bool:
        """Sends alert if not deduped. Returns True if sent.
        
        dedup_value: stable identifier for dedup (without timestamp).
        text_msg: full message with timestamp for user.
        """
        if not self.alert_bot_token or not self.alert_chat_id:
            logger.info("ALERT_BOT_TOKEN/ALERT_CHAT_ID not set - skipping alert")
            return False
        if not self._should_alert(redis_client, key, dedup_value):
            logger.info("Alert suppressed (dedup): %s", key)
            return False'''

if old_send in s:
    s = s.replace(old_send, new_send, 1)
    print("✅ Метод _send_alert обновлён")
else:
    print("⚠️ Метод _send_alert не найден")

f.write_text(s, encoding='utf-8')

try:
    py_compile.compile(str(f), doraise=True)
    print("✅✅✅ monitoring_job.py валиден")
except py_compile.PyCompileError as e:
    print(f"❌ Ошибка: {e}")