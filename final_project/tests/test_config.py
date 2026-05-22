from pathlib import Path

import pytest

from final_project.io.config import ConfigError, load_config


def test_load_config_prefers_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / 'config.yaml'
    config_path.write_text(
        'api_key: file-key\napi_host: http://file/v1\nlimit_message: 3\n',
        encoding='utf-8',
    )
    monkeypatch.setenv('API_KEY', 'env-key')

    config = load_config(config_path)

    assert config.api_key == 'env-key'
    assert config.api_host == 'http://file/v1'
    assert config.limit_message == 3


def test_load_config_requires_connection(tmp_path: Path) -> None:
    with pytest.raises(ConfigError):
        load_config(tmp_path / 'missing.yaml')
