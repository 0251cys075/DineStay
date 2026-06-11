"""
DineStay - Hotel & Restaurant Management System
utils.py

Demonstrates:
- Decorators: @log_booking, @log_food_order, @log_bill
- Recursive function: search_customer()
- Lambda functions for sorting
- datetime for timestamps
- functools.wraps for preserving metadata
"""

import functools
from datetime import datetime


# ══════════════════════════════════════════════════════════
# DECORATORS
# Python Concept: Decorators — add logging behaviour
#   without modifying the original function.
# ══════════════════════════════════════════════════════════

def log_booking(func):
    """
    Decorator: logs a timestamped line whenever a room booking occurs.
    Wraps any function that performs a booking action.
    """
    @functools.wraps(func)   # Preserve original function metadata
    def wrapper(*args, **kwargs):
        # Decorator: print log BEFORE executing the wrapped function
        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        print(f"\n  📌 [LOG | {timestamp}] BOOKING action triggered: "
              f"'{func.__name__}' called.")
        result = func(*args, **kwargs)
        print(f"  📌 [LOG | {timestamp}] BOOKING action '{func.__name__}' "
              f"completed.")
        return result
    return wrapper


def log_food_order(func):
    """
    Decorator: logs a timestamped line whenever a food order is placed.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        print(f"\n  🍴 [LOG | {timestamp}] FOOD ORDER action triggered: "
              f"'{func.__name__}' called.")
        result = func(*args, **kwargs)
        print(f"  🍴 [LOG | {timestamp}] FOOD ORDER '{func.__name__}' "
              f"completed.")
        return result
    return wrapper


def log_bill(func):
    """
    Decorator: logs a timestamped line whenever a bill is generated.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        print(f"\n  💰 [LOG | {timestamp}] BILLING action triggered: "
              f"'{func.__name__}' called.")
        result = func(*args, **kwargs)
        print(f"  💰 [LOG | {timestamp}] BILLING '{func.__name__}' "
              f"completed.")
        return result
    return wrapper


# ══════════════════════════════════════════════════════════
# RECURSIVE FUNCTION
# Python Concept: Recursion — searches without a loop
# ══════════════════════════════════════════════════════════

def search_customer(customer_list: list, customer_id: int,
                    index: int = 0):
    """
    Recursively searches through customer_list for a customer
    matching customer_id.

    Base cases:
      1. index >= len(customer_list) → not found, return None
      2. customer_list[index].customer_id == customer_id → found, return it

    Recursive case:
      Call search_customer with index + 1
    """
    # Base case 1: exhausted the list
    if index >= len(customer_list):
        return None

    # Base case 2: found the customer
    if customer_list[index].customer_id == customer_id:
        return customer_list[index]

    # Recursive case: move to next index
    return search_customer(customer_list, customer_id, index + 1)


def search_room_by_number(room_list: list, room_number: str,
                          index: int = 0):
    """
    Recursively searches room_list for a room with the given room_number.
    Same recursive pattern as search_customer.
    """
    if index >= len(room_list):
        return None
    if room_list[index].room_number == room_number:
        return room_list[index]
    return search_room_by_number(room_list, room_number, index + 1)


# ══════════════════════════════════════════════════════════
# LAMBDA FUNCTIONS
# Python Concept: Lambda — anonymous one-liner functions
# ══════════════════════════════════════════════════════════

# Sort rooms by price (ascending)
sort_rooms_by_price = lambda rooms: sorted(rooms, key=lambda r: r.room_price)

# Sort employees by salary (ascending)
sort_employees_by_salary = lambda emps: sorted(emps, key=lambda e: e.salary)

# Sort food items by price (ascending)
sort_food_by_price = lambda items: sorted(items, key=lambda f: f.price)

# Sort bills by total amount (descending — highest bills first)
sort_bills_by_amount = lambda bills: sorted(
    bills, key=lambda b: b.total_amount, reverse=True
)


# ══════════════════════════════════════════════════════════
# UTILITY HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════

def get_int_input(prompt: str, min_val: int = None,
                  max_val: int = None) -> int:
    """
    Prompt the user for an integer with optional range validation.
    Raises ValueError for non-integer inputs.
    """
    while True:
        try:
            value = int(input(prompt))
            if min_val is not None and value < min_val:
                print(f"  ⚠  Please enter a value ≥ {min_val}.")
                continue
            if max_val is not None and value > max_val:
                print(f"  ⚠  Please enter a value ≤ {max_val}.")
                continue
            return value
        except ValueError:
            print("  ⚠  Invalid input. Please enter a whole number.")


def get_float_input(prompt: str, min_val: float = 0.0) -> float:
    """Prompt the user for a float with minimum-value validation."""
    while True:
        try:
            value = float(input(prompt))
            if value < min_val:
                print(f"  ⚠  Value must be ≥ {min_val}.")
                continue
            return value
        except ValueError:
            print("  ⚠  Invalid input. Please enter a number.")


def get_date_input(prompt: str) -> datetime:
    """Prompt the user for a date in DD-MM-YYYY format."""
    while True:
        date_str = input(prompt + " (DD-MM-YYYY): ").strip()
        try:
            return datetime.strptime(date_str, "%d-%m-%Y")
        except ValueError:
            print("  ⚠  Invalid date format. Use DD-MM-YYYY.")


def print_separator(char: str = "─", width: int = 55) -> None:
    """Print a separator line."""
    print("  " + char * width)


def print_header(title: str, width: int = 55) -> None:
    """Print a centred section header."""
    print("\n" + "═" * width)
    print(f"  {title.center(width - 2)}")
    print("═" * width)
