from typing import List
from ..models.channel import ChannelConfig
from ..models.policy import ChannelPolicy
from ..models.prompt_tracking import GenerationRecord

class PolicyEngine:
    """
    Движок проверки политик. Вызывается на разных этапах воркфлоу.
    """
    
    def __init__(self):
        pass

    def check_pre_generation(self, channel: ChannelConfig, policy: ChannelPolicy, daily_post_count: int) -> dict:
        """
        Проверка ПЕРЕД началом генерации (например, не превышен ли лимит постов).
        """
        if daily_post_count >= policy.max_posts_per_day:
            return {
                "allowed": False,
                "reason": f"Достигнут дневной лимит постов ({policy.max_posts_per_day})"
            }
        return {"allowed": True, "reason": "OK"}

    def check_post_quality(self, policy: ChannelPolicy, fact_score: int, quality_score: int) -> dict:
        """
        Проверка качества ПЕРЕД публикацией (интеграция со Sprint 7).
        """
        if fact_score < policy.min_fact_check_score:
            return {
                "allowed": False,
                "reason": f"Fact Score ({fact_score}) ниже минимального порога ({policy.min_fact_check_score})"
            }
        if quality_score < policy.min_quality_score:
            return {
                "allowed": False,
                "reason": f"Quality Score ({quality_score}) ниже минимального порога ({policy.min_quality_score})"
            }
        return {"allowed": True, "reason": "Quality checks passed"}

    def check_news_freshness(self, news_age_hours: int, policy: ChannelPolicy) -> dict:
        """
        Проверка актуальности новости.
        """
        if news_age_hours > policy.max_news_age_hours:
            return {
                "allowed": False,
                "reason": f"Новость слишком старая ({news_age_hours}ч > {policy.max_news_age_hours}ч)"
            }
        return {"allowed": True, "reason": "OK"}
