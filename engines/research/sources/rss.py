import logging
import re
import requests
import feedparser

from datetime import datetime
from typing import List

from ..models import Article


logger = logging.getLogger(__name__)


class RSSSource:

    def __init__(self, source_config: dict):

        self.name = source_config["name"]
        self.url = source_config["url"]

        self.trust_score = source_config.get(
            "trust_score",
            50
        )

        self.categories = source_config.get(
            "categories",
            []
        )

        self.language = source_config.get(
            "language",
            "en"
        )


    def fetch(
        self,
        max_items: int = 50
    ) -> List[Article]:

        logger.info(
            f"Загрузка RSS: {self.name} {self.url}"
        )


        try:

            response = requests.get(
                self.url,
                headers={
                    "User-Agent":
                    "AI-Media-Factory-ResearchBot/1.0"
                },
                timeout=10
            )


            if response.status_code != 200:

                logger.warning(
                    f"{self.name}: HTTP {response.status_code}"
                )

                return []


            content_type = response.headers.get(
                "content-type",
                ""
            )


            if "xml" not in content_type and "rss" not in content_type:

                logger.warning(
                    f"{self.name}: неправильный Content-Type {content_type}"
                )


            feed = feedparser.parse(
                response.content
            )


            if feed.bozo:

                logger.warning(
                    f"{self.name}: RSS warning {feed.bozo_exception}"
                )


            if not feed.entries:

                logger.warning(
                    f"{self.name}: RSS пустой"
                )

                return []


            articles = []


            for entry in feed.entries[:max_items]:

                try:

                    article = self._parse_entry(
                        entry
                    )

                    if article:

                        articles.append(article)


                except Exception as e:

                    logger.warning(
                        f"{self.name}: ошибка статьи {e}"
                    )


            logger.info(
                f"{self.name}: получено {len(articles)} статей"
            )


            return articles



        except requests.Timeout:

            logger.error(
                f"{self.name}: RSS timeout"
            )

            return []


        except Exception as e:

            logger.exception(
                f"{self.name}: RSS ошибка {e}"
            )

            return []



    def _parse_entry(
        self,
        entry
    ) -> Article:


        title = entry.get(
            "title",
            ""
        ).strip()


        if not title:

            return None


        url = entry.get(
            "link",
            ""
        ).strip()


        if not url:

            return None



        summary = entry.get(
            "summary",
            entry.get(
                "description",
                ""
            )
        )


        content = summary


        if "content" in entry:

            try:

                content = entry.content[0].get(
                    "value",
                    content
                )

            except Exception:

                pass



        published_at = None


        if entry.get(
            "published_parsed"
        ):

            try:

                published_at = datetime(
                    *entry.published_parsed[:6]
                )

            except Exception:

                pass



        return Article(

            title=title,

            summary=self._clean_html(
                summary
            ),

            content=self._clean_html(
                content
            ),

            url=url,

            source=self.name,

            source_type="rss",

            published_at=published_at,

            language=self.language,

            categories=self.categories.copy(),

            trust_score=self.trust_score,

            status="raw"

        )



    def _clean_html(
        self,
        text: str
    ) -> str:


        if not text:

            return ""


        text = re.sub(
            r"<[^>]+>",
            "",
            text
        )


        text = re.sub(
            r"\s+",
            " ",
            text
        )


        return text.strip()
