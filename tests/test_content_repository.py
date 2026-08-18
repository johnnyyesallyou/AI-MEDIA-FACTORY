from core.repositories.content_repository import ContentRepository


def test_content_repository_has_exists_method():
    assert hasattr(ContentRepository, "exists")
