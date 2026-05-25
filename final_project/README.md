# GigaVibeMiptCode

Консольный чат с LLM через OpenAI-compatible API.

## Запуск

Из корня репозитория:

```bash
python final_project/main.py
```

Также можно запустить как модуль: `python -m final_project.main`.

Настройки можно передать через переменные окружения:

```bash
export API_KEY='your_key_here'
export API_HOST='http://localhost:11434/v1'
export MODEL='llama3.1'
export LIMIT_MESSAGE='20'
export LIMIT_CHARS='2000'
export TEMPERATURE='0.2'
python final_project/main.py
```

Или через `final_project/config.yaml`:

```yaml
api_key: your_key_here
api_host: http://localhost:11434/v1
model: llama3.1
limit_message: 20
limit_chars: 2000
temperature: 0.2
system_prompt: Ты помогаешь с задачами по Python.
```

Переменные окружения имеют приоритет над `config.yaml`.

## Команды

`\q` завершает программу.

`/reset` очищает историю чата и экран.

`@::path/to/file.py::` подставляет текстовый файл в сообщение. Размер одного файла ограничен 5 МБ.

`/file_chunk` запускает обработку файла по частям. Поддерживаются варианты:

```text
/file_chunk
/filechunk paragraph=3
/filechunk len=150
/filechunk paragraph=3 -y
```

Без `-y` следующий фрагмент отправляется после пустого ввода. С `-y` все фрагменты обрабатываются подряд.

## Архитектура

Проект разбит на несколько небольших частей:

`main.py` запускает приложение.

`app.py` отвечает за консольный цикл, команды пользователя и режим обработки файла по частям.

`core/history.py` хранит историю диалога и обрезает контекст по лимитам.

`core/chunks.py` разбивает текст на фрагменты для команды `/file_chunk`.

`io/config.py` читает настройки из переменных окружения и `config.yaml`.

`io/file_input.py` подставляет содержимое файлов из выражений `@::path::`.

`clients/llm_client.py` отправляет запросы в OpenAI-compatible API и читает streaming-ответ.

Тесты лежат в `tests`. Файл `coverage_report.txt` содержит последний отчёт покрытия.

## Проверки

```bash
pip install -r final_project/requirements.txt
ruff format --check final_project
flake8 final_project
ruff check --config final_project/ruff.toml final_project
mypy final_project
pytest final_project/tests
pytest --cov=final_project --cov-report=html final_project/tests
```
