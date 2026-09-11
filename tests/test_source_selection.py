"""Sprint 76.2: Smart Source Selection — quality, rotation, diversity, matching.

Проверяет:
1. QualityRegistry: record/quality_adjustment (только после >=3 попыток).
2. SmartSourceSelector: базовый порядок, diversity (языковая), rotation,
   quality-коррекция (падение ненадёжного источника).
3. API: GET /sources/select, POST /sources/metrics, POST /sources/select/record-pick.
"""
from engines.source_selection import (
    DEFAULT_REGISTRY, QualityRegistry, SmartSourceSelector,
)


def _news_top1(selector):
    return selector.select("news", top_k=1, diversity=False, rotation=False)[0]


def test_quality_adjustment_needs_min_attempts():
    reg = QualityRegistry()
    reg.record("habr", "success")
    reg.record("habr", "success")
    assert reg.quality_adjustment("habr") == 0.0  # < 3 попыток -> нет данных


def test_quality_adjustment_failing_source_negative():
    reg = QualityRegistry()
    for _ in range(3):
        reg.record("habr", "failure")
    assert reg.quality_adjustment("habr") < 0
    assert reg.get("habr").success_rate == 0.0


def test_quality_adjustment_reliable_source_positive():
    reg = QualityRegistry()
    for _ in range(3):
        reg.record("habr", "success", items=10)
    assert reg.get("habr").total_items == 30
    assert reg.quality_adjustment("habr") > 0


def test_select_base_top1_is_habr_for_news_fresh():
    sel = SmartSourceSelector(QualityRegistry())
    top = _news_top1(sel)
    assert top.source_id == "habr"


def test_diversity_selects_different_language_in_top2():
    sel = SmartSourceSelector(QualityRegistry())
    sel_top2 = sel.select("news", top_k=2, diversity=True, rotation=False)
    ids = [s.source_id for s in sel_top2]
    assert "habr" in ids
    assert "techcrunch" in ids, "diversity должен дать ru+en источник"
    langs = {lang for s in sel_top2 for lang in s.languages}
    assert {"ru", "en"}.issubset(langs)


def test_no_diversity_returns_first_two():
    sel = SmartSourceSelector(QualityRegistry())
    top2 = sel.select("news", top_k=2, diversity=False, rotation=False)
    assert [s.source_id for s in top2] == ["habr", "vc"]


def test_rotation_alternates_pick():
    reg = QualityRegistry()
    sel = SmartSourceSelector(reg)
    first = sel.select("news", top_k=1, diversity=False, rotation=True)[0].source_id
    reg.bump_selection(first)  # после первого использования
    second = sel.select("news", top_k=1, diversity=False, rotation=True)[0].source_id
    assert second != first, "ротация должна менять источник"


def test_quality_failure_removes_top_source():
    reg = QualityRegistry()
    # habr изначально топ; сделаем его ненадёжным
    for _ in range(3):
        reg.record("habr", "failure")
    sel = SmartSourceSelector(reg)
    top = _news_top1(sel)
    assert top.source_id != "habr"
    habr = next(s for s in sel.select("news", diversity=False, rotation=False)
                if s.source_id == "habr")
    assert habr.final_score < top.final_score


def test_rotation_penalty_scales_with_usage():
    reg = QualityRegistry()
    sel = SmartSourceSelector(reg)
    before = {s.source_id: s.final_score for s in sel.select("news", diversity=False)}
    reg.bump_selection("habr")
    after = {s.source_id: s.final_score for s in sel.select("news", diversity=False)}
    assert after["habr"] < before["habr"]
    assert after["habr"] == before["habr"] - 3.0


def test_default_registry_is_singleton():
    assert DEFAULT_REGISTRY is not None
    DEFAULT_REGISTRY.reset()


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

def _client():
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)


def test_api_select_sorted_by_final():
    DEFAULT_REGISTRY.reset()
    client = _client()
    resp = client.get("/api/v1/sources/discover/select", params={"content_type": "news"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["results"]
    finals = [r["final_score"] for r in data["results"]]
    assert finals == sorted(finals, reverse=True)


def test_api_metrics_affects_selection():
    DEFAULT_REGISTRY.reset()
    client = _client()
    for _ in range(3):
        r = client.post("/api/v1/sources/metrics",
                        json={"source_id": "habr", "outcome": "failure"})
        assert r.status_code == 200
    assert client.post(
        "/api/v1/sources/metrics",
        json={"source_id": "habr", "outcome": "failure"},
    ).json()["quality_adjustment"] < 0

    resp = client.get("/api/v1/sources/discover/select",
                      params={"content_type": "news", "diversity": "false",
                              "rotation": "false"})
    assert resp.json()["results"][0]["source_id"] != "habr"
    DEFAULT_REGISTRY.reset()


def test_api_record_pick_tracks_selection():
    DEFAULT_REGISTRY.reset()
    client = _client()
    for _ in range(2):
        r = client.post("/api/v1/sources/select/record-pick",
                        json={"source_id": "habr"})
        assert r.status_code == 200
    last = client.post("/api/v1/sources/select/record-pick",
                       json={"source_id": "habr"}).json()
    assert last["selection_count"] == 3
    DEFAULT_REGISTRY.reset()