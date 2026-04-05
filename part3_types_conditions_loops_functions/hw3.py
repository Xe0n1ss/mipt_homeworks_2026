#!/usr/bin/env python

from typing import Any, TypedDict

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"


EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
}


financial_transactions_storage: list[dict[str, Any]] = []

DATE_SEPARATOR = "-"
DATE_PARTS_COUNT = 3
DAY_TOKEN_LENGTH = 2
MONTH_TOKEN_LENGTH = 2
YEAR_TOKEN_LENGTH = 4
MIN_DAY = 1
MIN_MONTH = 1
MAX_MONTH = 12
MIN_YEAR = 1
INCOME_COMMAND = "income"
COST_COMMAND = "cost"
STATS_COMMAND = "stats"
CATEGORIES_COMMAND = "categories"
INCOME_PARTS_COUNT = 3
COST_PARTS_COUNT = 4
STATS_PARTS_COUNT = 2
CATEGORIES_PARTS_COUNT = 1
ZERO_AMOUNT = float(0)
FEBRUARY_MONTH = 2
LEAP_FEBRUARY_DAYS = 29
MONTH_DAYS = (
    31,
    28,
    31,
    30,
    31,
    30,
    31,
    31,
    30,
    31,
    30,
    31,
)
INCOME_INDEX_AMOUNT = 1
INCOME_INDEX_DATE = 2
COST_INDEX_CATEGORY = 1
COST_INDEX_AMOUNT = 2
COST_INDEX_DATE = 3
STATS_INDEX_DATE = 1
KEY_AMOUNT = "amount"
KEY_DATE = "date"
KEY_CATEGORY = "category"


type DateTuple = tuple[int, int, int]


class StatsSummary(TypedDict):
    total_capital: float
    month_income: float
    month_expenses: float
    category_totals: dict[str, float]


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    is_century = year % 100 == 0
    divisible_by_four_hundred = year % 400 == 0
    if is_century:
        return divisible_by_four_hundred
    return year % 4 == 0


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    raw_parts = maybe_dt.split(DATE_SEPARATOR)
    if not _has_valid_date_tokens(raw_parts):
        return None

    day, month, year = (int(raw_part) for raw_part in raw_parts)
    if not _has_valid_month_and_year(month, year):
        return None
    if not _has_valid_day(day, month, year):
        return None
    return day, month, year


def income_handler(amount: float, income_date: str) -> str:
    parsed_date = extract_date(income_date)
    if amount <= ZERO_AMOUNT:
        return _save_invalid_operation(NONPOSITIVE_VALUE_MSG)
    if parsed_date is None:
        return _save_invalid_operation(INCORRECT_DATE_MSG)

    financial_transactions_storage.append(
        {KEY_AMOUNT: amount, KEY_DATE: parsed_date},
    )
    return OP_SUCCESS_MSG


def cost_handler(
    category_name: str,
    amount: float,
    income_date: str,
) -> str:
    parsed_date = extract_date(income_date)
    if amount <= ZERO_AMOUNT:
        return _save_invalid_operation(NONPOSITIVE_VALUE_MSG)
    if not _is_valid_category(category_name):
        return _save_invalid_operation(NOT_EXISTS_CATEGORY)
    if parsed_date is None:
        return _save_invalid_operation(INCORRECT_DATE_MSG)

    financial_transactions_storage.append(
        {
            KEY_CATEGORY: category_name,
            KEY_AMOUNT: amount,
            KEY_DATE: parsed_date,
        }
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    categories = _iter_categories()
    return "\n".join(categories)


def stats_handler(report_date: str) -> str:
    parsed_date = extract_date(report_date)
    if parsed_date is None:
        return INCORRECT_DATE_MSG

    summary = _build_stats_summary(parsed_date)
    return _render_stats(report_date, summary)


def main() -> None:
    while True:
        try:
            command_line = input().strip()
        except EOFError:
            return

        if not command_line:
            continue
        print(_run_command(command_line))


def _run_command(command_line: str) -> str:
    parts = command_line.split()
    action = parts[0]

    if action == INCOME_COMMAND:
        return _handle_income_command(parts)
    if action == COST_COMMAND:
        return _handle_cost_command(parts)
    if action == STATS_COMMAND:
        return _handle_stats_command(parts)
    if action == CATEGORIES_COMMAND:
        return _handle_categories_command(parts)
    return UNKNOWN_COMMAND_MSG


def _handle_income_command(parts: list[str]) -> str:
    if len(parts) != INCOME_PARTS_COUNT:
        return UNKNOWN_COMMAND_MSG

    amount = _to_float(parts[INCOME_INDEX_AMOUNT])
    if amount is None:
        return NONPOSITIVE_VALUE_MSG
    return income_handler(amount, parts[INCOME_INDEX_DATE])


def _handle_cost_command(parts: list[str]) -> str:
    if len(parts) != COST_PARTS_COUNT:
        return UNKNOWN_COMMAND_MSG

    amount = _to_float(parts[COST_INDEX_AMOUNT])
    if amount is None:
        return NONPOSITIVE_VALUE_MSG
    return cost_handler(
        parts[COST_INDEX_CATEGORY],
        amount,
        parts[COST_INDEX_DATE],
    )


def _handle_stats_command(parts: list[str]) -> str:
    if len(parts) != STATS_PARTS_COUNT:
        return UNKNOWN_COMMAND_MSG
    return stats_handler(parts[STATS_INDEX_DATE])


def _handle_categories_command(parts: list[str]) -> str:
    if len(parts) != CATEGORIES_PARTS_COUNT:
        return UNKNOWN_COMMAND_MSG
    return cost_categories_handler()


def _to_float(raw_amount: str) -> float | None:
    try:
        return float(raw_amount)
    except ValueError:
        return None


def _save_invalid_operation(error_msg: str) -> str:
    financial_transactions_storage.append({})
    return error_msg


def _has_valid_date_tokens(raw_parts: list[str]) -> bool:
    expected_token_lengths = (
        DAY_TOKEN_LENGTH,
        MONTH_TOKEN_LENGTH,
        YEAR_TOKEN_LENGTH,
    )
    if len(raw_parts) != DATE_PARTS_COUNT:
        return False

    for raw_part, expected_length in zip(
        raw_parts,
        expected_token_lengths,
        strict=True,
    ):
        if len(raw_part) != expected_length:
            return False
        if not raw_part.isdigit():
            return False
    return True


def _has_valid_month_and_year(month: int, year: int) -> bool:
    return year >= MIN_YEAR and MIN_MONTH <= month <= MAX_MONTH


def _has_valid_day(day: int, month: int, year: int) -> bool:
    days_in_month = _month_days(month, year)
    return MIN_DAY <= day <= days_in_month


def _month_days(month: int, year: int) -> int:
    if month == FEBRUARY_MONTH and is_leap_year(year):
        return LEAP_FEBRUARY_DAYS
    return MONTH_DAYS[month - 1]


def _is_valid_category(category_name: str) -> bool:
    if "::" not in category_name:
        return False

    common_category, direct_category = category_name.split("::", maxsplit=1)
    if common_category not in EXPENSE_CATEGORIES:
        return False
    return direct_category in EXPENSE_CATEGORIES[common_category]


def _iter_categories() -> list[str]:
    categories: list[str] = []
    for common_category, direct_categories in EXPENSE_CATEGORIES.items():
        categories.extend(
            f"{common_category}::{direct_category}"
            for direct_category in direct_categories
        )
    return categories


def _build_stats_summary(
    report_date: DateTuple,
) -> StatsSummary:
    total_capital = ZERO_AMOUNT
    month_income = ZERO_AMOUNT
    month_expenses = ZERO_AMOUNT
    category_totals: dict[str, float] = {}

    for operation in financial_transactions_storage:
        if not operation:
            continue
        summary_values = (total_capital, month_income, month_expenses)
        (
            total_capital,
            month_income,
            month_expenses,
        ) = _update_summary_from_operation(
            operation,
            report_date,
            summary_values,
            category_totals,
        )

    return {
        "total_capital": total_capital,
        "month_income": month_income,
        "month_expenses": month_expenses,
        "category_totals": category_totals,
    }


def _apply_income(
    operation: dict[str, Any],
    report_date: DateTuple,
    total_capital: float,
    month_income: float,
) -> tuple[float, float]:
    amount = float(operation[KEY_AMOUNT])
    total_capital += amount
    if _is_same_month(operation[KEY_DATE], report_date):
        month_income += amount
    return total_capital, month_income


def _apply_cost(
    operation: dict[str, Any],
    report_date: DateTuple,
    total_capital: float,
    month_expenses: float,
    category_totals: dict[str, float],
) -> tuple[float, float]:
    amount = float(operation[KEY_AMOUNT])
    total_capital -= amount
    if _is_same_month(operation[KEY_DATE], report_date):
        month_expenses += amount
        _add_category_total(
            category_totals,
            str(operation[KEY_CATEGORY]),
            amount,
        )
    return total_capital, month_expenses


def _add_category_total(
    category_totals: dict[str, float],
    category_name: str,
    amount: float,
) -> None:
    try:
        category_totals[category_name] += amount
    except KeyError:
        category_totals[category_name] = amount


def _update_summary_from_operation(
    operation: dict[str, Any],
    report_date: DateTuple,
    summary_values: tuple[float, float, float],
    category_totals: dict[str, float],
) -> tuple[float, float, float]:
    total_capital, month_income, month_expenses = summary_values
    operation_date = operation[KEY_DATE]
    if not _is_not_later(operation_date, report_date):
        return summary_values
    if KEY_CATEGORY in operation:
        total_capital, month_expenses = _apply_cost(
            operation,
            report_date,
            total_capital,
            month_expenses,
            category_totals,
        )
        return total_capital, month_income, month_expenses
    total_capital, month_income = _apply_income(
        operation,
        report_date,
        total_capital,
        month_income,
    )
    return total_capital, month_income, month_expenses


def _render_stats(report_date: str, summary: StatsSummary) -> str:
    total_capital = summary["total_capital"]
    month_income = summary["month_income"]
    month_expenses = summary["month_expenses"]
    category_totals = summary["category_totals"]

    amount_word = _amount_word(total_capital)
    category_details = _render_category_details(category_totals)
    return (
        f"Your statistics as of {report_date}:\n"
        f"Total capital: {total_capital} rubles\n"
        "This month, "
        f"the {amount_word} "
        f"amounted to {total_capital} rubles.\n"
        f"Income: {month_income} rubles\n"
        f"Expenses: {month_expenses} rubles\n"
        "\n"
        "Details (category: amount):\n"
        f"{category_details}\n"
    )


def _amount_word(total_capital: float) -> str:
    if total_capital < ZERO_AMOUNT:
        return "loss"
    return "profit"


def _render_category_details(category_totals: dict[str, float]) -> str:
    lines: list[str] = []
    for index, category_with_amount in enumerate(category_totals.items()):
        category, amount = category_with_amount
        lines.append(f"{index}. {category}: {amount}")
    return "\n".join(lines)


def _is_not_later(left_date: DateTuple, right_date: DateTuple) -> bool:
    left_day, left_month, left_year = left_date
    right_day, right_month, right_year = right_date
    return (
        left_year,
        left_month,
        left_day,
    ) <= (
        right_year,
        right_month,
        right_day,
    )


def _is_same_month(left_date: DateTuple, right_date: DateTuple) -> bool:
    _, left_month, left_year = left_date
    _, right_month, right_year = right_date
    return left_month == right_month and left_year == right_year


if __name__ == "__main__":
    main()
