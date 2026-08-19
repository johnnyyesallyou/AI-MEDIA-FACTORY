"""Hermetic tests for Error Taxonomy (Sprint 41)."""
import pytest
import requests

from core.error_taxonomy import classify_error, ErrorType


def make_http_error(status_code, headers=None):
    resp = requests.Response()
    resp.status_code = status_code
    resp.url = f"https://example.com/{status_code}"
    if headers:
        for k, v in headers.items():
            resp.headers[k] = v
    return requests.HTTPError(f"{status_code} error", response=resp)


@pytest.mark.parametrize("code,expected,action", [
    (429, ErrorType.TRANSIENT, "retry"),
    (500, ErrorType.TRANSIENT, "retry"),
    (502, ErrorType.TRANSIENT, "retry"),
    (503, ErrorType.TRANSIENT, "retry"),
    (504, ErrorType.TRANSIENT, "retry"),
    (400, ErrorType.PERMANENT, "fail"),
    (404, ErrorType.PERMANENT, "fail"),
    (410, ErrorType.PERMANENT, "fail"),
    (401, ErrorType.CONFIGURATION, "alert_disable"),
    (403, ErrorType.CONFIGURATION, "alert_disable"),
])
def test_http_classification(code, expected, action):
    c = classify_error(make_http_error(code))
    assert c.error_type == expected
    assert c.action == action


def test_severity_configuration_high():
    c = classify_error(make_http_error(401))
    assert c.severity.value == "high"


def test_retry_after_extracted():
    c = classify_error(make_http_error(429, {"Retry-After": "30"}))
    assert c.retry_after == 30


def test_timeout_is_network():
    c = classify_error(requests.Timeout("timeout"))
    assert c.error_type == ErrorType.NETWORK
    assert c.action == "retry"


def test_connection_refused_is_network():
    c = classify_error(requests.ConnectionError("Connection refused"))
    assert c.error_type == ErrorType.NETWORK


def test_dns_failure_is_network():
    c = classify_error(requests.ConnectionError("Name or service not known"))
    assert c.error_type == ErrorType.NETWORK


def test_unknown_error():
    c = classify_error(ValueError("boom"))
    assert c.error_type == ErrorType.UNKNOWN
    assert c.action == "log"


def test_to_dict():
    d = classify_error(make_http_error(404)).to_dict()
    assert d["error_type"] == "permanent"
    assert d["action"] == "fail"
    assert d["metadata"]["status_code"] == 404