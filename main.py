"""
DineStay - Hotel & Restaurant Management System
main.py

Demonstrates:
- While-loop menu with 11 options and sub-menus
- Exception handling (custom + built-in exceptions)
- All OOP concepts tied together
- Calling decorators, generators, recursion, lambdas indirectly
"""

# Fix Windows console encoding so emoji/Unicode characters display correctly
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding="utf-8", errors="replace"
    )

import os
from datetime import datetime

from hotel import Hotel
from models.room import InvalidRoomNumber, RoomNotAvailable
from models.customer import InvalidCustomerID
from models.food import InvalidOrderID
from models.bill import InvalidBillAmount, generate_invoices
import file_handler
from utils import (print_header, print_separator, get_int_input,
                   get_float_input, get_date_input,
                   sort_rooms_by_price, sort_food_by_price,
                   search_customer)


# ─────────────────────────────────────────────
# Banner
# ─────────────────────────────────────────────
BANNER = r"""
 ██████╗ ██╗███╗   ██╗███████╗███████╗████████╗ █████╗ ██╗   ██╗
 ██╔══██╗██║████╗  ██║██╔════╝██╔════╝╚══██╔══╝██╔══██╗╚██╗ ██╔╝
 ██║  ██║██║██╔██╗ ██║█████╗  ███████╗   ██║   ███████║ ╚████╔╝
 ██║  ██║██║██║╚██╗██║██╔══╝  ╚════██║   ██║   ██╔══██║  ╚██╔╝
 ██████╔╝██║██║ ╚████║███████╗███████║   ██║   ██║  ██║   ██║
 ╚═════╝ ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝
        Hotel & Restaurant Management System  v1.0
"""


def clear_screen() -> None:
    """Clear the console screen (cross-platform)."""
    os.system("cls" if os.name == "nt" else "clear")


def print_main_menu() -> None:
    """Print the 11-option main menu."""
    print("\n" + "═" * 55)
    print("  🏨  DineStay — MAIN MENU")
    print("═" * 55)
    options = [
        "1.  Customer Management",
        "2.  Room Management",
        "3.  Room Booking",
        "4.  Restaurant Management",
        "5.  Food Ordering",
        "6.  Billing Management",
        "7.  Employee Management",
        "8.  Generate Reports",
        "9.  Save Data",
        "10. Load Data",
        "11. Exit",
    ]
    for opt in options:
        print(f"  {opt}")
    print("═" * 55)


# ══════════════════════════════════════════════════════════
# SUB-MENU: Customer Management
# ══════════════════════════════════════════════════════════
def customer_menu(hotel: Hotel) -> None:
    while True:
        print_header("👥  CUSTOMER MANAGEMENT")
        print("  1. Register New Customer")
        print("  2. View All Customers")
        print("  3. Search Customer by ID  (Recursive Search)")
        print("  4. Update Customer Details")
        print("  5. View Booking History")
        print("  6. Back to Main Menu")
        print_separator()

        choice = get_int_input("  Enter choice: ", 1, 6)

        if choice == 1:
            # Register new customer
            print_header("Register New Customer")
            name = input("  Full Name   : ").strip()
            phone = input("  Phone       : ").strip()
            email = input("  Email       : ").strip()
            if not name or not phone or not email:
                print("  ⚠  All fields are required.")
                continue
            try:
                hotel.register_customer(name, phone, email)
            except Exception as e:
                print(f"  ❌ Error: {e}")

        elif choice == 2:
            hotel.display_all_customers()

        elif choice == 3:
            # Recursive search demonstration
            cid = get_int_input("  Enter Customer ID to search: ", 1)
            # Recursive Function: search_customer
            result = search_customer(hotel.customers, cid)
            if result:
                print(f"\n  ✅ Found: {result}")
                print(f"     Repr : {repr(result)}")
            else:
                print(f"  ❌ Customer ID {cid} not found.")

        elif choice == 4:
            cid = get_int_input("  Enter Customer ID to update: ", 1)
            try:
                customer = hotel.get_customer(cid)
                print(f"  Editing: {customer}")
                name = input("  New Name  (Enter to skip): ").strip() or None
                phone = input("  New Phone (Enter to skip): ").strip() or None
                email = input("  New Email (Enter to skip): ").strip() or None
                customer.update_details(name=name, phone=phone, email=email)
            except InvalidCustomerID as e:
                print(f"  ❌ {e}")

        elif choice == 5:
            cid = get_int_input("  Enter Customer ID: ", 1)
            try:
                customer = hotel.get_customer(cid)
                customer.view_booking_history()
            except InvalidCustomerID as e:
                print(f"  ❌ {e}")

        elif choice == 6:
            break


# ══════════════════════════════════════════════════════════
# SUB-MENU: Room Management
# ══════════════════════════════════════════════════════════
def room_menu(hotel: Hotel) -> None:
    while True:
        print_header("🏨  ROOM MANAGEMENT")
        print("  1. Add New Room")
        print("  2. View All Rooms")
        print("  3. View Available Rooms (List Comprehension)")
        print("  4. View Room Details")
        print("  5. View Unique Room Types (Set)")
        print("  6. Back to Main Menu")
        print_separator()

        choice = get_int_input("  Enter choice: ", 1, 6)

        if choice == 1:
            print_header("Add New Room")
            print("  Room Types: 1. Deluxe   2. Standard")
            rtype_choice = get_int_input("  Select type: ", 1, 2)
            room_type = "Deluxe" if rtype_choice == 1 else "Standard"
            room_number = input("  Room Number (e.g. 101): ").strip()
            room_price = get_float_input("  Price per night (₹): ", 0.01)
            try:
                hotel.add_room(room_type, room_number, room_price)
            except (InvalidRoomNumber, ValueError) as e:
                print(f"  ❌ {e}")

        elif choice == 2:
            hotel.display_all_rooms()

        elif choice == 3:
            # List Comprehension demo
            available = hotel.get_available_rooms()
            if not available:
                print("  No rooms currently available.")
            else:
                print(f"\n  ✅ {len(available)} Available Room(s):")
                for r in sort_rooms_by_price(available):
                    print(f"     {r}")

        elif choice == 4:
            room_number = input("  Enter Room Number: ").strip()
            found = False
            for r in hotel.rooms:
                if r.room_number == room_number:
                    r.display_room_details()   # Polymorphic call
                    found = True
                    break
            if not found:
                print(f"  ❌ Room '{room_number}' not found.")

        elif choice == 5:
            # Set demo
            from models.room import Room
            types = Room.get_unique_room_types()
            print(f"\n  📋 Unique Room Types (Set): {types}")

        elif choice == 6:
            break


# ══════════════════════════════════════════════════════════
# SUB-MENU: Room Booking
# ══════════════════════════════════════════════════════════
def booking_menu(hotel: Hotel) -> None:
    while True:
        print_header("🗓  ROOM BOOKING")
        print("  1. Book a Room")
        print("  2. Check Out (Release Room)")
        print("  3. View All Rooms Status")
        print("  4. Back to Main Menu")
        print_separator()

        choice = get_int_input("  Enter choice: ", 1, 4)

        if choice == 1:
            print_header("Book a Room")
            # Show available rooms
            available = hotel.get_available_rooms()
            if not available:
                print("  ❌ No rooms available for booking.")
                continue
            print("  Available Rooms:")
            for r in sort_rooms_by_price(available):
                print(f"     {r}")
            print()

            cid = get_int_input("  Customer ID    : ", 1)
            room_number = input("  Room Number    : ").strip()
            check_in = get_date_input("  Check-In Date ")
            check_out = get_date_input("  Check-Out Date")

            try:
                # @log_booking decorator fires here automatically
                hotel.book_room(cid, room_number, check_in, check_out)
            except (InvalidCustomerID, InvalidRoomNumber,
                    RoomNotAvailable, ValueError) as e:
                print(f"  ❌ {e}")

        elif choice == 2:
            room_number = input("  Room Number to check out: ").strip()
            try:
                hotel.checkout_room(room_number)
            except InvalidRoomNumber as e:
                print(f"  ❌ {e}")

        elif choice == 3:
            hotel.display_all_rooms()

        elif choice == 4:
            break


# ══════════════════════════════════════════════════════════
# SUB-MENU: Restaurant Management
# ══════════════════════════════════════════════════════════
def restaurant_menu(hotel: Hotel) -> None:
    while True:
        print_header("🍽  RESTAURANT MANAGEMENT")
        print("  1. Add Food Item to Menu")
        print("  2. View Full Menu (sorted by price — Lambda)")
        print("  3. Update Food Item Price")
        print("  4. View Unique Food Categories (Set)")
        print("  5. Back to Main Menu")
        print_separator()

        choice = get_int_input("  Enter choice: ", 1, 5)

        if choice == 1:
            print_header("Add Menu Item")
            food_name = input("  Food Name  : ").strip()
            category = input("  Category   : ").strip()
            price = get_float_input("  Price (₹)  : ", 0.01)
            if food_name and category:
                hotel.add_food_item(food_name, category, price)
            else:
                print("  ⚠  Food name and category are required.")

        elif choice == 2:
            hotel.display_menu()

        elif choice == 3:
            if not hotel.menu:
                print("  Menu is empty.")
                continue
            hotel.display_menu()
            fid = get_int_input("  Enter Food ID to update: ", 1)
            food_item = next((f for f in hotel.menu if f.food_id == fid), None)
            if food_item is None:
                print(f"  ❌ Food ID {fid} not found.")
            else:
                new_price = get_float_input("  New Price (₹): ", 0.01)
                try:
                    food_item.update_price(new_price)
                except ValueError as e:
                    print(f"  ❌ {e}")

        elif choice == 4:
            from models.food import FoodItem
            cats = FoodItem.get_all_categories()
            print(f"\n  📋 Food Categories (Set): {cats}")

        elif choice == 5:
            break


# ══════════════════════════════════════════════════════════
# SUB-MENU: Food Ordering
# ══════════════════════════════════════════════════════════
def food_ordering_menu(hotel: Hotel) -> None:
    while True:
        print_header("🛒  FOOD ORDERING")
        print("  1. Place New Food Order")
        print("  2. Cancel an Order")
        print("  3. View Order Details")
        print("  4. View All Orders")
        print("  5. Back to Main Menu")
        print_separator()

        choice = get_int_input("  Enter choice: ", 1, 5)

        if choice == 1:
            if not hotel.menu:
                print("  ❌ Menu is empty. Add food items first.")
                continue
            hotel.display_menu()
            cid = get_int_input("  Customer ID: ", 1)

            items_to_order = []
            print("  Add items (enter 0 as Food ID to finish):")
            while True:
                fid = get_int_input("    Food ID  : ", 0)
                if fid == 0:
                    break
                qty = get_int_input("    Quantity : ", 1)
                items_to_order.append((fid, qty))

            if not items_to_order:
                print("  ⚠  No items selected.")
                continue

            try:
                # @log_food_order decorator fires here
                order = hotel.place_food_order(cid, items_to_order)
                order.display_order()
            except (InvalidCustomerID, InvalidOrderID) as e:
                print(f"  ❌ {e}")

        elif choice == 2:
            oid = get_int_input("  Order ID to cancel: ", 1)
            order = next((o for o in hotel.orders if o.order_id == oid), None)
            if order is None:
                print(f"  ❌ Order ID {oid} not found.")
            else:
                order.cancel_order()

        elif choice == 3:
            oid = get_int_input("  Order ID to view: ", 1)
            order = next((o for o in hotel.orders if o.order_id == oid), None)
            if order is None:
                print(f"  ❌ Order ID {oid} not found.")
            else:
                order.display_order()

        elif choice == 4:
            if not hotel.orders:
                print("  No orders placed yet.")
            else:
                print_header("ALL ORDERS")
                for o in hotel.orders:
                    print(f"  {o}")   # Uses __str__

        elif choice == 5:
            break


# ══════════════════════════════════════════════════════════
# SUB-MENU: Billing Management
# ══════════════════════════════════════════════════════════
def billing_menu(hotel: Hotel) -> None:
    while True:
        print_header("💰  BILLING MANAGEMENT")
        print("  1. Generate Bill for Customer")
        print("  2. View All Bills")
        print("  3. Print Invoice (single bill)")
        print("  4. Print All Invoices (Generator)")
        print("  5. Mark Bill as Paid")
        print("  6. Back to Main Menu")
        print_separator()

        choice = get_int_input("  Enter choice: ", 1, 6)

        if choice == 1:
            cid = get_int_input("  Customer ID: ", 1)
            room_number = input("  Room Number (Enter to skip): ").strip() or None
            try:
                # @log_bill decorator fires here
                bill = hotel.generate_bill(cid, room_number)
                bill.print_invoice()
            except (InvalidCustomerID, InvalidBillAmount) as e:
                print(f"  ❌ {e}")

        elif choice == 2:
            hotel.display_all_bills()

        elif choice == 3:
            bid = get_int_input("  Bill ID to print: ", 1)
            bill = next((b for b in hotel.bills if b.bill_id == bid), None)
            if bill is None:
                print(f"  ❌ Bill ID {bid} not found.")
            else:
                bill.print_invoice()

        elif choice == 4:
            if not hotel.bills:
                print("  No bills to print.")
            else:
                # Generator: generate_invoices yields one at a time
                print(f"\n  🖨  Printing {len(hotel.bills)} invoice(s) "
                      f"via generator...")
                hotel.print_all_invoices()

        elif choice == 5:
            bid = get_int_input("  Bill ID to mark as paid: ", 1)
            bill = next((b for b in hotel.bills if b.bill_id == bid), None)
            if bill is None:
                print(f"  ❌ Bill ID {bid} not found.")
            else:
                bill.mark_paid()

        elif choice == 6:
            break


# ══════════════════════════════════════════════════════════
# SUB-MENU: Employee Management
# ══════════════════════════════════════════════════════════
def employee_menu(hotel: Hotel) -> None:
    while True:
        print_header("👤  EMPLOYEE MANAGEMENT")
        print("  1. Add New Employee")
        print("  2. View All Employees (sorted by salary — Lambda)")
        print("  3. View Employee Details")
        print("  4. Update Employee Details")
        print("  5. Back to Main Menu")
        print_separator()

        choice = get_int_input("  Enter choice: ", 1, 5)

        if choice == 1:
            print_header("Add New Employee")
            name = input("  Full Name    : ").strip()
            designation = input("  Designation  : ").strip()
            department = input("  Department   : ").strip()
            salary = get_float_input("  Salary (₹)   : ", 0.0)
            if name and designation and department:
                try:
                    hotel.add_employee(name, designation, salary, department)
                except ValueError as e:
                    print(f"  ❌ {e}")
            else:
                print("  ⚠  All fields are required.")

        elif choice == 2:
            hotel.display_all_employees()

        elif choice == 3:
            eid = get_int_input("  Employee ID: ", 1)
            emp = next((e for e in hotel.employees
                        if e.employee_id == eid), None)
            if emp is None:
                print(f"  ❌ Employee ID {eid} not found.")
            else:
                emp.display_employee()
                print(f"  __repr__: {repr(emp)}")

        elif choice == 4:
            eid = get_int_input("  Employee ID to update: ", 1)
            emp = next((e for e in hotel.employees
                        if e.employee_id == eid), None)
            if emp is None:
                print(f"  ❌ Employee ID {eid} not found.")
            else:
                print(f"  Editing: {emp}")
                name = input("  New Name        (Enter to skip): ").strip() or None
                designation = input("  New Designation (Enter to skip): ").strip() or None
                dept = input("  New Department  (Enter to skip): ").strip() or None
                sal_str = input("  New Salary ₹    (Enter to skip): ").strip()
                salary = float(sal_str) if sal_str else None
                try:
                    emp.update_employee(name=name, designation=designation,
                                        salary=salary, department=dept)
                except ValueError as e:
                    print(f"  ❌ {e}")

        elif choice == 5:
            break


# ══════════════════════════════════════════════════════════
# SUB-MENU: Generate Reports
# ══════════════════════════════════════════════════════════
def reports_menu(hotel: Hotel) -> None:
    while True:
        print_header("📊  GENERATE REPORTS")
        print("  1. Hotel Summary (on-screen)")
        print("  2. Daily Sales Report (CSV)")
        print("  3. Room Occupancy Report (CSV)")
        print("  4. Employee Report (CSV)")
        print("  5. Back to Main Menu")
        print_separator()

        choice = get_int_input("  Enter choice: ", 1, 5)

        if choice == 1:
            hotel.generate_report()

        elif choice == 2:
            path = file_handler.generate_daily_sales_report(hotel.bills)
            print(f"  ✅ Report saved: {path}")

        elif choice == 3:
            path = file_handler.generate_room_occupancy_report(hotel.rooms)
            print(f"  ✅ Report saved: {path}")

        elif choice == 4:
            path = file_handler.generate_employee_report(hotel.employees)
            print(f"  ✅ Report saved: {path}")

        elif choice == 5:
            break


# ══════════════════════════════════════════════════════════
# SEED DATA — pre-populate for demo/testing
# ══════════════════════════════════════════════════════════
def seed_demo_data(hotel: Hotel) -> None:
    """Pre-populate hotel with sample data for demonstration."""
    print("\n  🔧 Loading demo data...")

    # Rooms
    hotel.add_room("Deluxe", "101", 4500.00)
    hotel.add_room("Deluxe", "102", 5000.00)
    hotel.add_room("Standard", "201", 2000.00)
    hotel.add_room("Standard", "202", 2200.00)
    hotel.add_room("Standard", "203", 1800.00)

    # Customers
    hotel.register_customer("Arjun Sharma",  "+91-9876543210", "arjun@email.com")
    hotel.register_customer("Priya Menon",   "+91-9123456780", "priya@email.com")
    hotel.register_customer("Rohan Verma",   "+91-9988776655", "rohan@email.com")

    # Employees
    hotel.add_employee("Suresh Kumar",   "Front Desk Manager",  45000, "Reception")
    hotel.add_employee("Anita Nair",     "Executive Chef",      60000, "Restaurant")
    hotel.add_employee("Deepak Singh",   "Housekeeping Lead",   30000, "Housekeeping")
    hotel.add_employee("Kavya Reddy",    "Billing Manager",     40000, "Finance")

    # Menu items — Tuples concept reflected in BASE_FACILITIES
    hotel.add_food_item("Masala Dosa",        "Breakfast",    120.00)
    hotel.add_food_item("Paneer Butter Masala","Main Course", 280.00)
    hotel.add_food_item("Chicken Biryani",     "Main Course", 350.00)
    hotel.add_food_item("Veg Fried Rice",      "Main Course", 200.00)
    hotel.add_food_item("Mango Lassi",         "Beverages",   80.00)
    hotel.add_food_item("Masala Chai",         "Beverages",   40.00)
    hotel.add_food_item("Gulab Jamun",         "Desserts",    100.00)
    hotel.add_food_item("Ice Cream Sundae",    "Desserts",    150.00)
    hotel.add_food_item("Caesar Salad",        "Starters",    180.00)
    hotel.add_food_item("Garlic Bread",        "Starters",    120.00)

    print("  ✅ Demo data loaded successfully!\n")


# ══════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# Python Concept: While-loop menu with 11 options
# ══════════════════════════════════════════════════════════
def main() -> None:
    """
    Main application loop.
    Presents an 11-option menu; each leads to a sub-menu.
    """
    print(BANNER)
    print("  Welcome to DineStay Hotel & Restaurant Management System")
    print("  " + "─" * 53)

    # Create the central Hotel instance (Composition)
    hotel = Hotel("DineStay")

    # Ask user whether to load saved data or start fresh / use demo
    print("\n  Startup Options:")
    print("  1. Load saved data")
    print("  2. Start with demo data")
    print("  3. Start fresh (empty)")
    startup = get_int_input("  Choose: ", 1, 3)

    if startup == 1:
        file_handler.load_all(hotel)
        hotel.sync_id_counters()
    elif startup == 2:
        seed_demo_data(hotel)
    # else: start fresh — hotel is already empty

    # ── Main Menu While Loop ─────────────────
    # Python Concept: While-loop menu
    while True:
        print_main_menu()
        choice = get_int_input("  Enter your choice (1-11): ", 1, 11)

        if choice == 1:
            customer_menu(hotel)

        elif choice == 2:
            room_menu(hotel)

        elif choice == 3:
            booking_menu(hotel)

        elif choice == 4:
            restaurant_menu(hotel)

        elif choice == 5:
            food_ordering_menu(hotel)

        elif choice == 6:
            billing_menu(hotel)

        elif choice == 7:
            employee_menu(hotel)

        elif choice == 8:
            reports_menu(hotel)

        elif choice == 9:
            # Save Data
            print_header("💾  SAVE DATA")
            try:
                file_handler.save_all(hotel)
            except Exception as e:
                print(f"  ❌ Error saving data: {e}")

        elif choice == 10:
            # Load Data
            print_header("📂  LOAD DATA")
            confirm = input(
                "  This will overwrite current session data. Proceed? (y/n): "
            ).strip().lower()
            if confirm == "y":
                try:
                    file_handler.load_all(hotel)
                    hotel.sync_id_counters()
                except Exception as e:
                    print(f"  ❌ Error loading data: {e}")

        elif choice == 11:
            # Exit
            save_prompt = input(
                "\n  💾 Save data before exiting? (y/n): "
            ).strip().lower()
            if save_prompt == "y":
                try:
                    file_handler.save_all(hotel)
                except Exception as e:
                    print(f"  ⚠  Could not save: {e}")
            print("\n  Thank you for using DineStay! 🏨")
            print("  Goodbye!\n")
            sys.exit(0)


# ─────────────────────────────────────────────
# Entry point guard
# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()
