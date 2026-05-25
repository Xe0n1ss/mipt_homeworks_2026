from dataclasses import dataclass


class ChunkModeError(Exception):
    pass


@dataclass(frozen=True)
class ChunkOptions:
    paragraph: int = 1
    length: int | None = None
    auto: bool = False


def parse_chunk_command(command: str) -> ChunkOptions:
    options = ChunkOptions()
    for part in command.split()[1:]:
        options = _apply_option(options, part)
    return options


def _apply_option(options: ChunkOptions, part: str) -> ChunkOptions:
    if part == '-y':
        return ChunkOptions(options.paragraph, options.length, True)
    if part.startswith('paragraph='):
        value = _positive_int(part.removeprefix('paragraph='), 'paragraph')
        return ChunkOptions(value, options.length, options.auto)
    if part.startswith('len='):
        value = _positive_int(part.removeprefix('len='), 'len')
        return ChunkOptions(options.paragraph, value, options.auto)
    raise ChunkModeError(f'Неизвестный параметр: {part}')


def split_text(text: str, options: ChunkOptions) -> list[str]:
    if options.length is not None:
        return _split_by_length(text, options.length)
    return _split_by_paragraph(text, options.paragraph)


def _split_by_length(text: str, length: int) -> list[str]:
    chunks = []
    for start in range(0, len(text), length):
        end = start + length
        chunks.append(text[start:end])
    return [chunk for chunk in chunks if chunk]


def _split_by_paragraph(text: str, paragraph_count: int) -> list[str]:
    paragraphs = [line.strip() for line in text.splitlines() if line.strip()]
    result: list[str] = []
    for start in range(0, len(paragraphs), paragraph_count):
        end = start + paragraph_count
        result.append('\n'.join(paragraphs[start:end]))
    return result


def _positive_int(raw_value: str, name: str) -> int:
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ChunkModeError(f'{name} должен быть целым числом') from exc
    if value <= 0:
        raise ChunkModeError(f'{name} должен быть больше нуля')
    return value
