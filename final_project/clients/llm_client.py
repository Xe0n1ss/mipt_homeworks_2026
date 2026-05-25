import json
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Any
from urllib.request import Request, urlopen

from final_project.core.history import Message
from final_project.io.config import AppConfig


CHOICES = 'choices'
CONTENT = 'content'
DONE_MARK = '[DONE]'
MESSAGE = 'message'
ROLE = 'role'


class LlmError(Exception):
    pass


@dataclass(frozen=True)
class LlmClient:
    config: AppConfig

    def complete(self, messages: Iterable[Message]) -> str:
        payload = self._payload(messages, stream=False)
        data = self._request(payload)
        try:
            return str(data[CHOICES][0][MESSAGE][CONTENT])
        except (KeyError, IndexError, TypeError) as exc:
            raise LlmError('Сервер вернул неожиданный ответ') from exc

    def stream_complete(self, messages: Iterable[Message]) -> Iterator[str]:
        payload = self._payload(messages, stream=True)
        request = self._build_request(payload)
        for token in _stream_tokens(request):
            yield token

    def _payload(self, messages: Iterable[Message], stream: bool) -> dict[str, Any]:
        api_messages = []
        if self.config.system_prompt:
            api_messages.append({ROLE: 'system', CONTENT: self.config.system_prompt})
        api_messages.extend({ROLE: message.role, CONTENT: message.content} for message in messages)
        return {
            'model': self.config.model,
            'messages': api_messages,
            'temperature': self.config.temperature,
            'stream': stream,
        }

    def _request(self, payload: dict[str, Any]) -> dict[str, Any]:
        request = self._build_request(payload)
        try:
            with urlopen(request, timeout=120) as response:
                raw = response.read().decode('utf-8')
        except OSError as exc:
            raise LlmError(f'Ошибка запроса к модели: {exc}') from exc
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LlmError('Сервер вернул не JSON') from exc
        if not isinstance(parsed, dict):
            raise LlmError('Сервер вернул неожиданный ответ')
        return parsed

    def _build_request(self, payload: dict[str, Any]) -> Request:
        url = '{0}/chat/completions'.format(self.config.api_host.rstrip('/'))
        auth_header = 'Bearer {0}'.format(self.config.api_key)
        body = json.dumps(payload).encode('utf-8')
        return Request(
            url=url,
            data=body,
            headers={
                'Authorization': auth_header,
                'Content-Type': 'application/json',
            },
            method='POST',
        )


def _stream_tokens(request: Request) -> Iterator[str]:
    try:
        with urlopen(request, timeout=120) as response:
            yield from _read_stream_response(response)
    except OSError as exc:
        raise LlmError(f'Ошибка запроса к модели: {exc}') from exc


def _read_stream_response(response: Iterable[bytes]) -> Iterator[str]:
    for raw_line in response:
        token = _extract_stream_token(raw_line)
        if token is None:
            continue
        if token == DONE_MARK:
            break
        yield token


def _extract_stream_token(raw_line: bytes) -> str | None:
    line = raw_line.decode('utf-8', errors='replace').strip()
    if not line.startswith('data:'):
        return None
    data = line.removeprefix('data:').strip()
    if data == DONE_MARK:
        return DONE_MARK
    return _load_stream_token(data)


def _load_stream_token(data: str) -> str:
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError:
        return ''
    try:
        token = parsed[CHOICES][0]['delta'].get(CONTENT, '')
    except (KeyError, IndexError, TypeError):
        return ''
    return str(token)
