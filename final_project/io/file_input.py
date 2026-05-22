import re
from pathlib import Path


MAX_FILE_SIZE = 5 * 1024 * 1024
FILE_MARKER = re.compile(r'@::(.*?)::')


class FileInputError(Exception):
    pass


def expand_file_markers(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        path = Path(match.group(1)).expanduser()
        return '\n{0}'.format(read_text_file(path))

    return FILE_MARKER.sub(replace, text)


def read_text_file(path: Path) -> str:
    _check_text_path(path)
    return _read_text(path)


def _check_text_path(path: Path) -> None:
    if not path.exists():
        raise FileInputError(f'Файл не найден: {path}')
    if not path.is_file():
        raise FileInputError(f'Это не файл: {path}')
    _check_file_size(path)


def _check_file_size(path: Path) -> None:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise FileInputError(f'Не удалось проверить файл {path}: {exc}') from exc
    if size > MAX_FILE_SIZE:
        raise FileInputError(f'Файл больше 5 МБ: {path}')


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8-sig')
    except UnicodeDecodeError as exc:
        raise FileInputError(f'Файл не похож на UTF-8 текст: {path}') from exc
    except OSError as exc:
        raise FileInputError(f'Не удалось прочитать файл {path}: {exc}') from exc
