UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be greater than zero!"
INCORRECT_DATE_MSG = "Incorrect date!"
OP_SUCCESS_MSG = "Added"

STATS_HEADER_TEMPLATE = "Your statistics as of {date}:"
CAPITAL_TEMPLATE = "Total capital: {amount:.2f} rubles"
MONTH_PROFIT_TEMPLATE = "This month profit was {amount:.2f} rubles"
MONTH_LOSS_TEMPLATE = "This month loss was {amount:.2f} rubles"
INCOME_TEMPLATE = "Income: {amount:.2f} rubles"
COST_TEMPLATE = "Expenses: {amount:.2f} rubles"
STATS_DETAILS_TITLE = "Details (category: amount):"

INCOME_COMMAND = "income"
COST_COMMAND = "cost"
STATS_COMMAND = "stats"

EMPTY_STRING = ""
DATE_SEPARATOR = "-"
DOT_SEPARATOR = "."
COMMA_SEPARATOR = ","
PLUS_SIGN = "+"
MINUS_SIGN = "-"
ZERO_CHAR = "0"

ZERO_NUMBER = 0
FIRST_LIST_INDEX = 1
DOT_LIMIT = 1
DETAIL_DECIMALS = 10

DATE_PARTS_COUNT = 3
DAY_TOKEN_LENGTH = 2
MONTH_TOKEN_LENGTH = 2
YEAR_TOKEN_LENGTH = 4

DATE_DAY_INDEX = 0
DATE_MONTH_INDEX = 1
DATE_YEAR_INDEX = 2

INCOME_ARGS_COUNT = 3
COST_ARGS_COUNT = 4
STATS_ARGS_COUNT = 2

COMMAND_NAME_INDEX = 0
INCOME_AMOUNT_INDEX = 1
INCOME_DATE_INDEX = 2
COST_CATEGORY_INDEX = 1
COST_AMOUNT_INDEX = 2
COST_DATE_INDEX = 3
STATS_DATE_INDEX = 1

MONTH_MIN = 1
MONTH_MAX = 12
DAY_MIN = 1
YEAR_MIN = 1

FEBRUARY = 2
SHORT_MONTH_DAYS = 30
LONG_MONTH_DAYS = 31
FEBRUARY_DAYS = 28
LEAP_FEBRUARY_DAYS = 29

LEAP_DIVISOR = 4
CENTURY_DIVISOR = 100
LEAP_CENTURY_DIVISOR = 400

LONG_MONTHS = (1, 3, 5, 7, 8, 10, 12)

type DateTuple = tuple[int, int, int]
type IncomeRecord = tuple[DateTuple, float]
type CostRecord = tuple[str, DateTuple, float]


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    if year % LEAP_CENTURY_DIVISOR == ZERO_NUMBER:
        return True
    if year % CENTURY_DIVISOR == ZERO_NUMBER:
        return False
    return year % LEAP_DIVISOR == ZERO_NUMBER


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    parts = maybe_dt.split(DATE_SEPARATOR)
    if not _has_valid_date_tokens(parts):
        return None
    return _build_valid_date(parts)


def _has_valid_date_tokens(parts: list[str]) -> bool:
    expected_lengths = (DAY_TOKEN_LENGTH, MONTH_TOKEN_LENGTH, YEAR_TOKEN_LENGTH)
    if len(parts) != DATE_PARTS_COUNT:
        return False

    for token, expected_length in zip(parts, expected_lengths, strict=True):
        if len(token) != expected_length:
            return False
        if not token.isdigit():
            return False
    return True


def _build_valid_date(parts: list[str]) -> DateTuple | None:
    day = int(parts[DATE_DAY_INDEX])
    month = int(parts[DATE_MONTH_INDEX])
    year = int(parts[DATE_YEAR_INDEX])
    if not _has_valid_month_and_year(month, year):
        return None

    candidate = (day, month, year)
    if not _has_valid_day(candidate):
        return None
    return candidate


def _has_valid_month_and_year(month: int, year: int) -> bool:
    return year >= YEAR_MIN and MONTH_MIN <= month <= MONTH_MAX


def _has_valid_day(date_value: DateTuple) -> bool:
    month_days = _month_days(date_value[DATE_MONTH_INDEX], date_value[DATE_YEAR_INDEX])
    return DAY_MIN <= date_value[DATE_DAY_INDEX] <= month_days


def _month_days(month: int, year: int) -> int:
    if month == FEBRUARY:
        if is_leap_year(year):
            return LEAP_FEBRUARY_DAYS
        return FEBRUARY_DAYS

    if month in LONG_MONTHS:
        return LONG_MONTH_DAYS
    return SHORT_MONTH_DAYS


def _parse_positive_amount(raw_amount: str) -> float | None:
    normalized = raw_amount.replace(COMMA_SEPARATOR, DOT_SEPARATOR)
    normalized = normalized.removeprefix(PLUS_SIGN)
    if not _is_valid_signed_decimal(normalized):
        return None

    amount = float(normalized)
    if amount <= ZERO_NUMBER:
        return None
    return amount


def _is_valid_signed_decimal(value: str) -> bool:
    if value == EMPTY_STRING:
        return False

    unsigned_value = value.removeprefix(MINUS_SIGN)
    if unsigned_value == EMPTY_STRING:
        return False
    if unsigned_value.count(DOT_SEPARATOR) > DOT_LIMIT:
        return False
    return _is_valid_unsigned_decimal(unsigned_value)


def _is_valid_unsigned_decimal(value: str) -> bool:
    if DOT_SEPARATOR not in value:
        return value.isdigit()

    left_part, right_part = value.split(DOT_SEPARATOR, maxsplit=DOT_LIMIT)
    if left_part == EMPTY_STRING and right_part == EMPTY_STRING:
        return False
    return _is_digit_part_or_empty(left_part) and _is_digit_part_or_empty(right_part)


def _is_digit_part_or_empty(value: str) -> bool:
    return value == EMPTY_STRING or value.isdigit()


def _is_valid_category(category_name: str) -> bool:
    return category_name != EMPTY_STRING and DOT_SEPARATOR not in category_name and COMMA_SEPARATOR not in category_name


def _date_sort_key(date_value: DateTuple) -> tuple[int, int, int]:
    return (
        date_value[DATE_YEAR_INDEX],
        date_value[DATE_MONTH_INDEX],
        date_value[DATE_DAY_INDEX],
    )


def _is_not_later(event_date: DateTuple, target_date: DateTuple) -> bool:
    return _date_sort_key(event_date) <= _date_sort_key(target_date)


def _is_same_month(event_date: DateTuple, target_date: DateTuple) -> bool:
    return (
        event_date[DATE_MONTH_INDEX] == target_date[DATE_MONTH_INDEX]
        and event_date[DATE_YEAR_INDEX] == target_date[DATE_YEAR_INDEX]
    )


def _format_detail_amount(amount: float) -> str:
    return f"{amount:.{DETAIL_DECIMALS}f}".rstrip(ZERO_CHAR).rstrip(DOT_SEPARATOR)


def _read_commands() -> list[str]:
    commands: list[str] = []
    with open(ZERO_NUMBER) as stdin_stream:
        for raw_line in stdin_stream:
            command_line = raw_line.strip()
            if command_line != EMPTY_STRING:
                commands.append(command_line)
    return commands


def _process_command(
    command_line: str,
    incomes: list[IncomeRecord],
    costs: list[CostRecord],
) -> None:
    parts = command_line.split()
    command_name = parts[COMMAND_NAME_INDEX]

    if command_name == INCOME_COMMAND:
        _handle_income(parts, incomes)
        return
    if command_name == COST_COMMAND:
        _handle_cost(parts, costs)
        return
    if command_name == STATS_COMMAND:
        _handle_stats(parts, incomes, costs)
        return
    print(UNKNOWN_COMMAND_MSG)


def _handle_income(parts: list[str], incomes: list[IncomeRecord]) -> None:
    if len(parts) != INCOME_ARGS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = _parse_positive_amount(parts[INCOME_AMOUNT_INDEX])
    if amount is None:
        print(NONPOSITIVE_VALUE_MSG)
        return

    parsed_date = extract_date(parts[INCOME_DATE_INDEX])
    if parsed_date is None:
        print(INCORRECT_DATE_MSG)
        return

    incomes.append((parsed_date, amount))
    print(OP_SUCCESS_MSG)


def _handle_cost(parts: list[str], costs: list[CostRecord]) -> None:
    if len(parts) != COST_ARGS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return

    category_name = parts[COST_CATEGORY_INDEX]
    if not _is_valid_category(category_name):
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = _parse_positive_amount(parts[COST_AMOUNT_INDEX])
    if amount is None:
        print(NONPOSITIVE_VALUE_MSG)
        return

    parsed_date = extract_date(parts[COST_DATE_INDEX])
    if parsed_date is None:
        print(INCORRECT_DATE_MSG)
        return

    costs.append((category_name, parsed_date, amount))
    print(OP_SUCCESS_MSG)


def _handle_stats(
    parts: list[str],
    incomes: list[IncomeRecord],
    costs: list[CostRecord],
) -> None:
    if len(parts) != STATS_ARGS_COUNT:
        print(UNKNOWN_COMMAND_MSG)
        return

    stats_date = parts[STATS_DATE_INDEX]
    parsed_date = extract_date(stats_date)
    if parsed_date is None:
        print(INCORRECT_DATE_MSG)
        return
    _show_stats(stats_date, parsed_date, incomes, costs)


def _show_stats(
    stats_date: str,
    target_date: DateTuple,
    incomes: list[IncomeRecord],
    costs: list[CostRecord],
) -> None:
    capital = _calculate_capital(target_date, incomes, costs)
    month_income = _calculate_month_income(target_date, incomes)
    month_cost, category_totals = _calculate_month_cost_and_categories(target_date, costs)
    _print_stats_overview(stats_date, capital, month_income, month_cost)
    _print_category_details(category_totals)


def _calculate_capital(
    target_date: DateTuple,
    incomes: list[IncomeRecord],
    costs: list[CostRecord],
) -> float:
    capital: float = ZERO_NUMBER
    for income_date, amount in incomes:
        if _is_not_later(income_date, target_date):
            capital += amount

    for _, cost_date, amount in costs:
        if _is_not_later(cost_date, target_date):
            capital -= amount
    return capital


def _calculate_month_income(target_date: DateTuple, incomes: list[IncomeRecord]) -> float:
    month_income: float = ZERO_NUMBER
    for income_date, amount in incomes:
        if _is_not_later(income_date, target_date) and _is_same_month(income_date, target_date):
            month_income += amount
    return month_income


def _calculate_month_cost_and_categories(
    target_date: DateTuple,
    costs: list[CostRecord],
) -> tuple[float, dict[str, float]]:
    month_cost: float = ZERO_NUMBER
    category_totals: dict[str, float] = {}
    for category_name, cost_date, amount in costs:
        if _is_not_later(cost_date, target_date) and _is_same_month(cost_date, target_date):
            month_cost += amount
            category_totals[category_name] = category_totals.get(category_name, ZERO_NUMBER) + amount
    return month_cost, category_totals


def _print_stats_overview(
    stats_date: str,
    capital: float,
    month_income: float,
    month_cost: float,
) -> None:
    print(STATS_HEADER_TEMPLATE.format(date=stats_date))
    print(CAPITAL_TEMPLATE.format(amount=capital))
    _print_month_result(month_income, month_cost)
    print(INCOME_TEMPLATE.format(amount=month_income))
    print(COST_TEMPLATE.format(amount=month_cost))
    print()
    print(STATS_DETAILS_TITLE)


def _print_month_result(month_income: float, month_cost: float) -> None:
    delta = month_income - month_cost
    if delta >= ZERO_NUMBER:
        print(MONTH_PROFIT_TEMPLATE.format(amount=delta))
        return
    print(MONTH_LOSS_TEMPLATE.format(amount=-delta))


def _print_category_details(category_totals: dict[str, float]) -> None:
    for index, category_name in enumerate(sorted(category_totals), start=FIRST_LIST_INDEX):
        formatted_amount = _format_detail_amount(category_totals[category_name])
        print(f"{index}. {category_name}: {formatted_amount}")


def income_handler(amount: float, income_date: str) -> str:
    parsed_date = extract_date(income_date)
    if amount <= ZERO_NUMBER:
        return NONPOSITIVE_VALUE_MSG
    if parsed_date is None:
        return INCORRECT_DATE_MSG
    return OP_SUCCESS_MSG


def main() -> None:
    incomes: list[IncomeRecord] = []
    costs: list[CostRecord] = []
    for command_line in _read_commands():
        _process_command(command_line, incomes, costs)


if __name__ == "__main__":
    main()
