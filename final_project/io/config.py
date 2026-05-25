import os
from dataclasses import dataclass
from pathlib import Path


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class AppConfig:
    api_key: str
    api_host: str
    model: str
    limit_message: int | None
    limit_chars: int | None
    temperature: float
    system_prompt: str | None


API_KEY = 'api_key'
API_HOST = 'api_host'
MODEL = 'model'
LIMIT_MESSAGE = 'limit_message'
LIMIT_CHARS = 'limit_chars'
TEMPERATURE = 'temperature'
SYSTEM_PROMPT = 'system_prompt'
DEFAULT_MODEL = 'gpt-4o-mini'
DEFAULT_TEMPERATURE = '0.2'
SINGLE_QUOTE = chr(39)


def load_config(path: Path | None = None) -> AppConfig:
    values = _read_yaml(_config_path(path))
    merged = {
        API_KEY: _env_or_file('API_KEY', values, API_KEY),
        API_HOST: _env_or_file('API_HOST', values, API_HOST),
        MODEL: _env_or_file('MODEL', values, MODEL) or DEFAULT_MODEL,
        LIMIT_MESSAGE: _env_or_file('LIMIT_MESSAGE', values, LIMIT_MESSAGE),
        LIMIT_CHARS: _env_or_file('LIMIT_CHARS', values, LIMIT_CHARS),
        TEMPERATURE: _env_or_file('TEMPERATURE', values, TEMPERATURE) or DEFAULT_TEMPERATURE,
        SYSTEM_PROMPT: _env_or_file('SYSTEM_PROMPT', values, SYSTEM_PROMPT),
    }
    api_key = merged[API_KEY]
    api_host = merged[API_HOST]
    if api_key is None or api_host is None:
        raise ConfigError('Нужны API_KEY и API_HOST или файл config.yaml с api_key и api_host')
    return AppConfig(
        api_key=api_key,
        api_host=api_host,
        model=merged[MODEL] or DEFAULT_MODEL,
        limit_message=_parse_optional_int(merged[LIMIT_MESSAGE], LIMIT_MESSAGE),
        limit_chars=_parse_optional_int(merged[LIMIT_CHARS], LIMIT_CHARS),
        temperature=_parse_temperature(merged[TEMPERATURE]),
        system_prompt=merged[SYSTEM_PROMPT] or None,
    )


def _env_or_file(env_name: str, values: dict[str, str], key: str) -> str | None:
    env_value = os.environ.get(env_name)
    if env_value is not None and env_value.strip():
        return env_value.strip()
    value = values.get(key)
    if value is not None and value.strip():
        return value.strip()
    return None


def _config_path(path: Path | None) -> Path:
    if path is not None:
        return path
    local_path = Path('config.yaml')
    if local_path.exists():
        return local_path
    return Path(__file__).with_name('config.yaml')


def _read_yaml(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for line in _read_lines(path):
        item = _parse_yaml_line(line, path)
        if item is not None:
            values[item[0]] = _clean_yaml_value(item[1])
    return values


def _read_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding='utf-8-sig').splitlines()
    except OSError as exc:
        raise ConfigError(f'Не удалось прочитать {path}: {exc}') from exc


def _parse_yaml_line(line: str, path: Path) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith('#'):
        return None
    if ':' not in stripped:
        raise ConfigError(f'Некорректная строка в {path}: {line}')
    key, value = stripped.split(':', 1)
    key = key.strip()
    if not key:
        raise ConfigError(f'Пустой ключ в {path}: {line}')
    return key, value.strip()


def _clean_yaml_value(value: str) -> str:
    if _is_single_quoted(value):
        return value[1:-1]
    return value


def _is_single_quoted(value: str) -> bool:
    if len(value) < 2:
        return False
    return value[0] == value[-1] == SINGLE_QUOTE


def _parse_optional_int(value: str | None, name: str) -> int | None:
    if value is None:
        return None
    try:
        number = int(value)
    except ValueError as exc:
        raise ConfigError(f'{name} должен быть целым числом') from exc
    if number <= 0:
        raise ConfigError(f'{name} должен быть больше нуля')
    return number


def _parse_temperature(value: str | None) -> float:
    if value is None:
        return 0.2
    try:
        temperature = float(value)
    except ValueError as exc:
        raise ConfigError('temperature должен быть числом от 0 до 1') from exc
    if temperature < 0 or temperature > 1:
        raise ConfigError('temperature должен быть числом от 0 до 1')
    return temperature
