from dataclasses import dataclass


@dataclass(frozen=True)
class Message:
    role: str
    content: str


class ChatHistory:
    def __init__(self, limit_message: int | None, limit_chars: int | None) -> None:
        self._messages: list[Message] = []
        self._limit_message = limit_message
        self._limit_chars = limit_chars

    @property
    def messages(self) -> list[Message]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()

    def add(self, role: str, content: str) -> None:
        message = Message(role=role, content=self._fit_single_message(content))
        self._messages.append(message)
        self._trim()

    def _fit_single_message(self, content: str) -> str:
        if self._limit_chars is not None and len(content) > self._limit_chars:
            start = len(content) - self._limit_chars
            return content[start:]
        return content

    def _trim(self) -> None:
        _trim_message_count(self._messages, self._limit_message)
        _trim_chars(self._messages, self._limit_chars)


def _trim_message_count(messages: list[Message], limit_message: int | None) -> None:
    if limit_message is not None:
        while len(messages) > limit_message:
            messages.pop(0)


def _trim_chars(messages: list[Message], limit_chars: int | None) -> None:
    if limit_chars is not None:
        while messages and _chars_count(messages) > limit_chars:
            if len(messages) == 1:
                _cut_first_message(messages, limit_chars)
                break
            messages.pop(0)


def _cut_first_message(messages: list[Message], limit_chars: int) -> None:
    message = messages[0]
    content = message.content[-limit_chars:]
    messages[0] = Message(message.role, content)


def _chars_count(messages: list[Message]) -> int:
    return sum(len(message.content) for message in messages)
