"""Structural tests for the no-build static softphone page.

These assert the page contract (CDN SDK, status indicator, Call/Hangup, the
WebRTC call lifecycle) without a browser: the page is read as text.
"""

from __future__ import annotations

from pathlib import Path

import mint_token as mt

HTML_PATH = Path(__file__).with_name(mt.HTML_FILENAME)


def _html() -> str:
    return HTML_PATH.read_text(encoding="utf-8")


def _handler_body(html: str, marker: str) -> str:
    """Return the brace-balanced body of the `function () { ... }` after marker.

    The Voice SDK emits `disconnect` from the Call, not the Device, so the
    tests below assert *which object* owns each handler and *what the handler
    actually does*. A plain `in html` search is not enough for that.
    """
    start = html.index(marker)
    brace = html.index("{", start)
    depth = 0
    for index in range(brace, len(html)):
        char = html[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return html[brace + 1 : index]
    raise AssertionError(f"unbalanced braces after {marker!r}")


def test_page_loads_voice_sdk_from_cdn_without_a_build_step():
    html = _html()
    # The SDK MUST come from a CDN that actually serves it. sdk.twilio.com
    # returned HTTP 403 on this environment for every version tested, so it
    # must NOT be referenced.
    assert "cdn.jsdelivr.net/npm/@twilio/voice-sdk" in html
    assert "sdk.twilio.com" not in html
    # Version is pinned for reproducibility (no floating "latest").
    assert "@twilio/voice-sdk@2.12.0/dist/twilio.min.js" in html
    # No bundler/module graph: no relative JS imports and no npm artifacts.
    assert "type=\"module\"" not in html
    assert "import " not in html


def test_page_has_status_indicator_and_call_hangup_controls():
    html = _html()
    assert 'id="status"' in html
    assert 'id="call"' in html
    assert 'id="hangup"' in html
    assert "Call" in html
    assert "Hangup" in html


def test_page_obtains_token_from_same_origin():
    html = _html()
    assert 'fetch("/token"' in html


def test_page_wires_webrtc_call_lifecycle():
    html = _html()
    assert "Twilio.Device" in html
    assert "device.connect()" in html
    assert "device.disconnectAll()" in html


def test_page_attaches_lifecycle_handlers_to_the_returned_call():
    html = _html()
    # `device.connect()` RETURNS the Call; the lifecycle events live on it.
    assert "call.on(\"accept\"" in html
    assert "call.on(\"disconnect\"" in html


def test_page_does_not_listen_for_disconnect_on_the_device():
    # The Device never emits "disconnect" (it emits registered/unregistered/
    # incoming/error/tokenWillExpire). A handler there never fires, which left
    # the status stuck on "llamando..." after the call ended.
    assert "device.on(\"disconnect\"" not in _html()


def test_page_awaits_the_call_promise_from_connect():
    # In @twilio/voice-sdk v2, device.connect() returns a Promise<Call>, NOT a
    # Call. A synchronous `call = device.connect()` leaves `call` as a Promise
    # and `call.on` is not a function, throwing before Hangup is enabled.
    html = _html()
    assert "device.connect().then(" in html
    assert ".catch(" in html


def test_page_enables_hangup_immediately_in_the_click_handler():
    # setConnected(true) must run before/independently of the resolved Call, so
    # Hangup is enabled even while the connect promise is still pending.
    body = _handler_body(_html(), 'callButton.addEventListener("click"')
    assert "setConnected(true)" in body
    assert body.index("setConnected(true)") < body.index("device.connect().then(")


def test_page_attaches_call_lifecycle_handlers_inside_the_then_callback():
    # Triangulation: the handlers must be registered on the Call resolved by the
    # promise, i.e. inside the click handler, after `device.connect().then(`.
    body = _handler_body(_html(), 'callButton.addEventListener("click"')
    assert body.index("device.connect().then(") < body.index('call.on("accept"')
    assert 'call.on("accept"' in body
    assert 'call.on("disconnect"' in body


def test_call_disconnect_handler_resets_status_and_controls():
    body = _handler_body(_html(), 'call.on("disconnect"')
    assert "setStatus(" in body
    assert "setConnected(false)" in body


def test_call_accept_handler_enables_hangup_via_connected_state():
    body = _handler_body(_html(), 'call.on("accept"')
    assert "setStatus(" in body
    assert "setConnected(true)" in body


def test_hangup_still_ends_the_call_through_disconnect_all():
    assert "device.disconnectAll()" in _html()


def test_identity_is_not_editable_from_the_page():
    html = _html()
    # The identity is shown for feedback but there is no input control that
    # could supply an arbitrary value (design.md D7).
    assert "<input" not in html
