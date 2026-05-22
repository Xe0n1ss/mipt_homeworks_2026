from pathlib import Path

import pytest

from final_project.io.file_input import FileInputError, expand_file_markers


def test_expand_file_marker(tmp_path: Path) -> None:
    path = tmp_path / 'sample.txt'
    path.write_text('print(1)', encoding='utf-8')

    assert expand_file_markers(f'check @::{path}::') == 'check \nprint(1)'


def test_expand_file_marker_missing_file(tmp_path: Path) -> None:
    path = tmp_path / 'missing.txt'

    with pytest.raises(FileInputError):
        expand_file_markers(f'check @::{path}::')
