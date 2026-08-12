import pytest

import tv_claude_bridge as bridge
from tests.test_qml import BULLISH_LEGS, build

SECRET = "s3cret"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(bridge, "WEBHOOK_SECRET", SECRET)
    monkeypatch.setattr(bridge, "ENABLE_LLM_COMMENTARY", False)
    monkeypatch.setattr(bridge, "send_telegram", lambda message: True)
    bridge.app.config["TESTING"] = True
    return bridge.app.test_client()


def bar_payload():
    return {
        "symbol": "XAUUSD",
        "tf": "15",
        "secret": SECRET,
        "bars": [
            {"t": b.time, "o": b.open, "h": b.high, "l": b.low, "c": b.close}
            for b in build(110, BULLISH_LEGS)
        ],
    }


def test_health_needs_no_secret(client):
    assert client.get("/health").get_json() == {"status": "ok"}


def test_bar_series_is_analysed(client):
    resp = client.post("/webhook", json=bar_payload())

    assert resp.status_code == 200
    setup = resp.get_json()["setup"]
    assert setup["direction"] == "BULLISH"
    assert setup["status"] == "TRIGGERED"
    assert setup["entry"] == pytest.approx(99.9)


def test_secret_may_travel_in_a_header(client):
    payload = bar_payload()
    del payload["secret"]

    resp = client.post("/webhook", json=payload, headers={"X-Webhook-Secret": SECRET})
    assert resp.status_code == 200


def test_pre_detected_setup_is_accepted(client):
    resp = client.post(
        "/webhook",
        json={
            "symbol": "EURUSD",
            "secret": SECRET,
            "direction": "bearish",
            "qml": 1.09500,
            "entry": 1.09500,
            "sl": 1.09650,
            "tp": 1.08900,
            "choch": 1.09200,
            "head": 1.09800,
        },
    )

    assert resp.status_code == 200
    setup = resp.get_json()["setup"]
    assert setup["direction"] == "BEARISH"
    assert setup["rr"] == pytest.approx(4.0)


def test_wrong_secret_is_rejected(client):
    payload = bar_payload()
    payload["secret"] = "wrong"

    assert client.post("/webhook", json=payload).status_code == 401


def test_missing_secret_is_rejected(client):
    payload = bar_payload()
    del payload["secret"]

    assert client.post("/webhook", json=payload).status_code == 401


def test_server_without_a_configured_secret_refuses_to_work(client, monkeypatch):
    monkeypatch.setattr(bridge, "WEBHOOK_SECRET", None)

    assert client.post("/webhook", json=bar_payload()).status_code == 503


@pytest.mark.parametrize(
    "payload",
    [
        {"secret": SECRET, "bars": [{"t": 1}]},
        {"secret": SECRET, "direction": "sideways", "qml": 1, "entry": 1, "sl": 1, "tp": 1},
        {"secret": SECRET, "direction": "BULLISH", "qml": 1},
    ],
)
def test_malformed_payloads_give_400_not_500(client, payload):
    resp = client.post("/webhook", json=payload)

    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_non_json_body_gives_400(client):
    resp = client.post("/webhook", data="not json", content_type="text/plain")
    assert resp.status_code == 400


def test_series_with_no_pattern_reports_no_setup(client):
    payload = bar_payload()
    payload["bars"] = [
        {"t": b.time, "o": b.open, "h": b.high, "l": b.low, "c": b.close}
        for b in build(100, [(100, 40)])
    ]

    resp = client.post("/webhook", json=payload)
    assert resp.status_code == 200
    assert resp.get_json()["setup"] is None
