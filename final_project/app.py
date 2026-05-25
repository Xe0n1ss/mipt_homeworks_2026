import os
from pathlib import Path

from final_project.clients.llm_client import LlmClient, LlmError
from final_project.core.chunks import ChunkModeError, ChunkOptions, parse_chunk_command, split_text
from final_project.core.history import ChatHistory, Message
from final_project.io.config import ConfigError, load_config
from final_project.io.file_input import FileInputError, expand_file_markers, read_text_file


QUIT_COMMAND = r'\q'


def run() -> None:
    try:
        config = load_config()
    except ConfigError as exc:
        print(exc)
        return
    app = ConsoleApp(LlmClient(config), ChatHistory(config.limit_message, config.limit_chars))
    app.loop()


class ConsoleApp:
    def __init__(self, client: LlmClient, history: ChatHistory) -> None:
        self.client = client
        self.history = history

    def loop(self) -> None:
        while True:
            raw_text = _read_input('>>> ')
            if raw_text is None:
                return
            if raw_text == QUIT_COMMAND:
                return
            if _handle_command(self, raw_text):
                continue
            _handle_chat_message(self, raw_text)


def _read_input(prompt: str) -> str | None:
    try:
        return input(prompt)
    except EOFError:
        print()
        return None


def _handle_command(app: ConsoleApp, raw_text: str) -> bool:
    if raw_text == '/reset':
        app.history.clear()
        _clear_screen()
        return True
    if _is_file_chunk_command(raw_text):
        _run_file_chunk(app, raw_text)
        return True
    return False


def _is_file_chunk_command(raw_text: str) -> bool:
    return raw_text.startswith('/file_chunk') or raw_text.startswith('/filechunk')


def _handle_chat_message(app: ConsoleApp, raw_text: str) -> None:
    try:
        user_text = expand_file_markers(raw_text)
    except FileInputError as exc:
        print(exc)
        return
    app.history.add('user', user_text)
    try:
        answer = _print_stream(app.client, app.history.messages)
    except KeyboardInterrupt:
        print('\nЗапрос прерван')
        return
    except LlmError as exc:
        print(exc)
        return
    app.history.add('assistant', answer)


def _run_file_chunk(app: ConsoleApp, command: str) -> None:
    try:
        options = parse_chunk_command(command)
    except ChunkModeError as exc:
        print(exc)
        return
    file_task = _read_file_task()
    if file_task is None:
        return
    try:
        chunks = _read_chunks(file_task[0], options)
    except (FileInputError, ChunkModeError) as exc:
        print(exc)
        return
    print('Принято. Начинаю обработку:')
    _process_chunks(app.client, file_task[1], chunks, options.auto)
    print('Обработка файла завершена.')


def _read_file_task() -> tuple[str, str] | None:
    path_text = _read_input('Введите путь до файла\n>>> ')
    if path_text is None or path_text == QUIT_COMMAND:
        return None
    prompt = _read_input('Принято. Что нужно сделать для каждого фрагмента?\n>>> ')
    if prompt is None or prompt == QUIT_COMMAND:
        return None
    return path_text, prompt


def _read_chunks(path_text: str, options: ChunkOptions) -> list[str]:
    text = read_text_file(Path(path_text).expanduser())
    return split_text(text, options)


def _process_chunks(client: LlmClient, prompt: str, chunks: list[str], auto: bool) -> None:
    for index, chunk in enumerate(chunks):
        if index > 0 and not auto:
            next_action = _read_input('>>> ')
            if next_action is None or next_action == QUIT_COMMAND:
                return
        _process_chunk(client, prompt, chunk)


def _process_chunk(client: LlmClient, prompt: str, chunk: str) -> None:
    message = Message(role='user', content=f'{prompt}\n\n{chunk}')
    try:
        _print_stream(client, [message])
    except KeyboardInterrupt:
        print('\nЗапрос прерван')
    except LlmError as exc:
        print(exc)


def _print_stream(client: LlmClient, messages: list[Message]) -> str:
    tokens: list[str] = []
    for token in client.stream_complete(messages):
        print(token, end='', flush=True)
        tokens.append(token)
    print()
    return ''.join(tokens)


def _clear_screen() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')
