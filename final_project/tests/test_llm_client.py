import json
from collections.abc import Iterable

import pytest

from final_project.clients.llm_client import (
    CONTENT,
    LlmClient,
    _extract_stream_token,
    _load_stream_token,
)
from final_project.core.history import Message
from final_project.io.config import AppConfig


HELLO = 'hello'


def test_payload_adds_system_prompt() -> None:
    client = LlmClient(_config(system_prompt='rules'))

    payload = client._payload([Message(role='user', content=HELLO)], stream=True)

    assert payload['messages'] == [
        {'role': 'system', CONTENT: 'rules'},
        {'role': 'user', CONTENT: HELLO},
    ]
    assert payload['stream'] is True


def test_extract_stream_token() -> None:
    data = json.dumps({'choices': [{'delta': {CONTENT: HELLO}}]})
    raw_line = 'data: {0}'.format(data).encode('utf-8')

    assert _extract_stream_token(raw_line) == HELLO
    assert _load_stream_token('bad json') == ''


def test_complete_reads_response(monkeypatch: pytest.MonkeyPatch) -> None:
    client = LlmClient(_config())

    def fake_urlopen(request: object, timeout: int) -> FakeResponse:
        assert timeout == 120
        assert request is not None
        return FakeResponse()

    monkeypatch.setattr('final_project.clients.llm_client.urlopen', fake_urlopen)

    assert client.complete([Message(role='user', content=HELLO)]) == 'answer'


class FakeResponse:
    def __enter__(self) -> 'FakeResponse':
        return self

    def __exit__(self, *args: object) -> None:
        pass

    def read(self) -> bytes:
        message = {'message': {CONTENT: 'answer'}}
        return json.dumps({'choices': [message]}).encode('utf-8')

    def __iter__(self) -> Iterable[bytes]:
        return iter(())


def _config(system_prompt: str | None = None) -> AppConfig:
    return AppConfig(
        api_key='key',
        api_host='http://server/v1',
        model='model',
        limit_message=None,
        limit_chars=None,
        temperature=0.2,
        system_prompt=system_prompt,
    )
