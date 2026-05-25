from final_project.core.chunks import ChunkOptions, parse_chunk_command, split_text


def test_parse_command_with_paragraph_and_auto() -> None:
    options = parse_chunk_command('/filechunk paragraph=3 -y')

    assert options == ChunkOptions(paragraph=3, auto=True)


def test_split_by_length() -> None:
    assert split_text('abcdef', ChunkOptions(length=2)) == ['ab', 'cd', 'ef']


def test_split_by_paragraph_group() -> None:
    text = 'one\n\ntwo\nthree\n'

    assert split_text(text, ChunkOptions(paragraph=2)) == ['one\ntwo', 'three']
