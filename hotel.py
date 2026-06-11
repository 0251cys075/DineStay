"""
DineStay - Hotel & Restaurant Management System
hotel.py

Demonstrates:
- Composition: Hotel contains Rooms, Customers, Employees, Orders, Bills
- Decorator usage: @log_booking, @log_food_order, @log_bill
- List comprehension: available rooms
- Dictionary: fast customer/room lookups
- Lambda: sorting
- Generator usage
- __str__ and __repr__
"""

from datetime import datetime

from models.room import Room, DeluxeRoom, StandardRoom, RoomNotAvailable
from models.room import InvalidRoomNumber
from models.customer import Customer, InvalidCustomerID
from models.employee import Employee
from models.food import FoodItem, Order, InvalidOrderID
from models.bill import Bill, generate_invoices
from utils import (log_booking, log_food_order, log_bill,
                   search_customer, search_room_by_number,
                   sort_rooms_by_price, sort_employees_by_salary,
                   sort_food_by_price)


# ─────────────────────────────────────────────
# Hotel Class
# OOP Concept: Composition — Hotel aggregates all entities
# ─────────────────────────────────────────────
class Hotel:
    """
    Central class that orchestrates the entire hotel & restaurant system.
    Uses composition to manage rooms, customers, employees, orders, bills.
    """

    def __init__(self, name: str = "DineStay"):
        self.name = name

        # Lists for each entity (Composition)
        self.rooms: list = []
        self.customers: list = []
        self.employees: list = []
        self.menu: list = []
        self.orders: list = []
        self.bills: list = []

        # Dictionaries: fast O(1) lookup by ID/number
        # Dictionary usage
        self._customer_dict: dict = {}   # customer_id → Customer
        self._room_dict: dict = {}        # room_number  → Room

        # Auto-incrementing ID counters
        self._next_room_id = 1
        self._next_customer_id = 1
        self._next_employee_id = 1
        self._next_food_id = 1
        self._next_order_id = 1
        self._next_bill_id = 1

        # Set: track unique room types & food categories
        # (delegated to class-level sets in Room and FoodItem)

    # ════════════════════════════════════════
    # ROOM MANAGEMENT
    # ════════════════════════════════════════

    def add_room(self, room_type: str, room_number: str,
                 room_price: float, **kwargs) -> Room:
        """
        Add a new room to the hotel.
        room_type: 'Deluxe' or 'Standard'
        """
        # Validate room number uniqueness
        if room_number in self._room_dict:
            raise InvalidRoomNumber(
                f"Room number '{room_number}' already exists.")

        if room_type.lower() == "deluxe":
            room = DeluxeRoom(
                room_id=self._next_room_id,
                room_number=room_number,
                room_price=room_price,
                wifi=kwargs.get("wifi", True),
                minibar=kwargs.get("minibar", True),
                complimentary_breakfast=kwargs.get("complimentary_breakfast", True),
            )
        elif room_type.lower() == "standard":
            room = StandardRoom(
                room_id=self._next_room_id,
                room_number=room_number,
                room_price=room_price,
                television=kwargs.get("television", True),
                air_conditioning=kwargs.get("air_conditioning", True),
            )
        else:
            raise InvalidRoomNumber(
                f"Unknown room type '{room_type}'. Use 'Deluxe' or 'Standard'.")

        self.rooms.append(room)
        self._room_dict[room_number] = room   # Dictionary: add to fast lookup
        self._next_room_id += 1
        print(f"\n  ✅ {room_type} Room '{room_number}' "
              f"added at ₹{room_price:.2f}/night.")
        return room

    def get_available_rooms(self) -> list:
        """
        Return all available rooms using list comprehension.
        Python Concept: List Comprehension
        """
        # List comprehension: filter rooms where availability_status is True
        return [room for room in self.rooms if room.availability_status]

    def display_all_rooms(self) -> None:
        """Display a summary list of all rooms sorted by price."""
        if not self.rooms:
            print("  No rooms registered.")
            return
        print("\n" + "═" * 65)
        print("  🏨  ALL ROOMS — DineStay")
        print("═" * 65)
        print(f"  {'#':<4} {'Room No.':<10} {'Type':<12} "
              f"{'Price/Night':>12}  {'Status'}")
        print("  " + "─" * 61)

        # Lambda: sort rooms by price before display
        for i, room in enumerate(sort_rooms_by_price(self.rooms), 1):
            status = "✅ Available" if room.availability_status else "❌ Booked"
            print(f"  {i:<4} {room.room_number:<10} {room.room_type:<12} "
                  f"₹{room.room_price:>10,.2f}  {status}")
        print("═" * 65)
        print(f"  Unique Room Types: {Room.get_unique_room_types()}")

    # ════════════════════════════════════════
    # CUSTOMER MANAGEMENT
    # ════════════════════════════════════════

    def register_customer(self, name: str, phone: str,
                          email: str) -> Customer:
        """Register a new customer and add to dictionary lookup."""
        # Check duplicate phone
        for c in self.customers:
            if c.phone == phone:
                print(f"  ⚠  A customer with phone {phone} already exists "
                      f"(ID: {c.customer_id}).")
                return c

        customer = Customer(
            customer_id=self._next_customer_id,
            name=name, phone=phone, email=email
        )
        self.customers.append(customer)
        # Dictionary: add to fast lookup map
        self._customer_dict[customer.customer_id] = customer
        self._next_customer_id += 1
        customer.register_customer()
        return customer

    def get_customer(self, customer_id: int) -> Customer:
        """
        Fetch a customer by ID using:
        1. Fast dictionary lookup first.
        2. Recursive search as fallback.
        """
        # Dictionary lookup (O(1))
        if customer_id in self._customer_dict:
            return self._customer_dict[customer_id]

        # Recursive search (fallback)
        result = search_customer(self.customers, customer_id)
        if result is None:
            raise InvalidCustomerID(
                f"Customer with ID {customer_id} not found.")
        return result

    def display_all_customers(self) -> None:
        """Display a table of all registered customers."""
        if not self.customers:
            print("  No customers registered.")
            return
        print("\n" + "═" * 65)
        print("  👥  ALL CUSTOMERS — DineStay")
        print("═" * 65)
        print(f"  {'ID':<6} {'Name':<25} {'Phone':<15} {'Email'}")
        print("  " + "─" * 61)
        for c in self.customers:
            print(f"  {c.customer_id:<6} {c.name:<25} "
                  f"{c.phone:<15} {c.email}")
        print("═" * 65)

    # ════════════════════════════════════════
    # ROOM BOOKING
    # Decorator: @log_booking
    # ════════════════════════════════════════

    @log_booking   # Decorator: logs this action with timestamp
    def book_room(self, customer_id: int, room_number: str,
                  check_in: datetime, check_out: datetime) -> Bill:
        """
        Book a room for a customer.
        Decorated with @log_booking for automatic timestamp logging.
        """
        # Get customer (uses dictionary + recursive search)
        customer = self.get_customer(customer_id)

        # Get room (dictionary lookup, then recursive search)
        if room_number in self._room_dict:
            room = self._room_dict[room_number]
        else:
            room = search_room_by_number(self.rooms, room_number)
            if room is None:
                raise InvalidRoomNumber(
                    f"Room '{room_number}' not found.")

        # Book the room (polymorphic call — works for any Room subclass)
        # OOP Concept: Polymorphism
        room.book_room(customer_id, check_in, check_out)

        # Calculate nights and charge
        nights = (check_out - check_in).days
        if nights <= 0:
            raise ValueError("Check-out must be after check-in.")

        # Polymorphic: calculate_room_charge is overridden in each subclass
        charge = room.calculate_room_charge(nights)

        # Update customer booking history
        customer.add_booking(
            room_number=room_number,
            check_in=check_in.strftime("%d-%m-%Y"),
            check_out=check_out.strftime("%d-%m-%Y"),
            charge=charge,
        )

        print(f"\n  🏨 Room '{room_number}' booked for '{customer.name}' "
              f"({nights} night(s)) | Charge: ₹{charge:.2f}")
        return charge

    def checkout_room(self, room_number: str) -> None:
        """Release a room back to available status."""
        if room_number in self._room_dict:
            room = self._room_dict[room_number]
        else:
            room = search_room_by_number(self.rooms, room_number)
            if room is None:
                raise InvalidRoomNumber(f"Room '{room_number}' not found.")

        if room.availability_status:
            print(f"  ⚠  Room '{room_number}' is already available.")
            return

        room.release_room()
        print(f"  ✅ Room '{room_number}' checked out and now available.")

    # ════════════════════════════════════════
    # RESTAURANT / FOOD MANAGEMENT
    # ════════════════════════════════════════

    def add_food_item(self, food_name: str, category: str,
                      price: float) -> FoodItem:
        """Add a new item to the restaurant menu."""
        item = FoodItem(
            food_id=self._next_food_id,
            food_name=food_name,
            category=category,
            price=price,
        )
        self.menu.append(item)
        self._next_food_id += 1
        print(f"  ✅ '{food_name}' added to menu at ₹{price:.2f}.")
        return item

    def display_menu(self) -> None:
        """Display the full restaurant menu sorted by price."""
        if not self.menu:
            print("  Menu is empty.")
            return
        print("\n" + "═" * 60)
        print("  🍽  DineStay RESTAURANT MENU")
        print("═" * 60)
        print(f"  {'ID':<5} {'Item':<28} {'Category':<15} {'Price':>8}")
        print("  " + "─" * 56)
        # Lambda: sort food by price for display
        for item in sort_food_by_price(self.menu):
            print(f"  {item.food_id:<5} {item.food_name:<28} "
                  f"{item.category:<15} ₹{item.price:>7.2f}")
        print("═" * 60)
        # Set: display unique categories
        print(f"  Categories: {FoodItem.get_all_categories()}")

    # ════════════════════════════════════════
    # FOOD ORDERING
    # Decorator: @log_food_order
    # ════════════════════════════════════════

    @log_food_order   # Decorator: logs this action with timestamp
    def place_food_order(self, customer_id: int,
                         food_ids_quantities: list) -> Order:
        """
        Place a food order for a customer.
        food_ids_quantities: list of (food_id, quantity) tuples

        Decorated with @log_food_order for automatic logging.
        """
        # Validate customer exists
        customer = self.get_customer(customer_id)

        # Create new order
        order = Order(
            order_id=self._next_order_id,
            customer_id=customer_id,
        )
        self._next_order_id += 1

        # Dictionary: build food ID → FoodItem map for fast lookup
        menu_dict = {item.food_id: item for item in self.menu}

        for food_id, quantity in food_ids_quantities:
            if food_id not in menu_dict:
                print(f"  ⚠  Food ID {food_id} not found in menu. Skipping.")
                continue
            order.place_order(menu_dict[food_id], quantity)

        self.orders.append(order)
        print(f"\n  ✅ Order #{order.order_id} placed for "
              f"'{customer.name}' | Total: ₹{order.total_amount:.2f}")
        return order

    # ════════════════════════════════════════
    # EMPLOYEE MANAGEMENT
    # ════════════════════════════════════════

    def add_employee(self, name: str, designation: str,
                     salary: float, department: str) -> Employee:
        """Add a new employee to the hotel."""
        emp = Employee(
            employee_id=self._next_employee_id,
            name=name,
            designation=designation,
            salary=salary,
            department=department,
        )
        self.employees.append(emp)
        self._next_employee_id += 1
        emp.add_employee()
        return emp

    def display_all_employees(self) -> None:
        """Display a table of all employees sorted by salary."""
        if not self.employees:
            print("  No employees registered.")
            return
        print("\n" + "═" * 70)
        print("  👤  ALL EMPLOYEES — DineStay")
        print("═" * 70)
        print(f"  {'ID':<6} {'Name':<22} {'Designation':<20} "
              f"{'Department':<15} {'Salary':>10}")
        print("  " + "─" * 66)
        # Lambda: sort by salary
        for emp in sort_employees_by_salary(self.employees):
            print(f"  {emp.employee_id:<6} {emp.name:<22} "
                  f"{emp.designation:<20} {emp.department:<15} "
                  f"₹{emp.salary:>9,.2f}")
        print("═" * 70)

    # ════════════════════════════════════════
    # BILLING
    # Decorator: @log_bill
    # ════════════════════════════════════════

    @log_bill   # Decorator: logs this action with timestamp
    def generate_bill(self, customer_id: int,
                      room_number: str = None) -> Bill:
        """
        Generate a bill for a customer combining room and food charges.
        Decorated with @log_bill for automatic logging.
        """
        customer = self.get_customer(customer_id)

        # Calculate room charges from booking history
        room_charges = 0.0
        if room_number:
            # Find the latest booking for this room in customer history
            for booking in customer.booking_history:
                if booking.get("room_number") == room_number:
                    room_charges = booking.get("charge", 0.0)
                    break

        # Calculate food charges: sum all confirmed orders for this customer
        # List comprehension: filter orders belonging to this customer
        customer_orders = [
            o for o in self.orders
            if o.customer_id == customer_id and o.order_status == "Confirmed"
        ]
        food_charges = sum(o.total_amount for o in customer_orders)

        # Create and generate the bill
        bill = Bill(
            bill_id=self._next_bill_id,
            customer_id=customer_id,
            room_charges=room_charges,
            food_charges=food_charges,
            customer_name=customer.name,
        )
        self._next_bill_id += 1
        bill.generate_bill()
        self.bills.append(bill)
        return bill

    def display_all_bills(self) -> None:
        """Display a summary of all bills."""
        if not self.bills:
            print("  No bills generated yet.")
            return
        print("\n" + "═" * 65)
        print("  💰  ALL BILLS — DineStay")
        print("═" * 65)
        print(f"  {'Bill#':<7} {'Customer ID':<14} {'Room ₹':>10} "
              f"{'Food ₹':>10} {'GST ₹':>8} {'Total ₹':>10}  {'Status'}")
        print("  " + "─" * 61)
        for b in self.bills:
            print(f"  {b.bill_id:<7} {b.customer_id:<14} "
                  f"₹{b.room_charges:>8,.2f} ₹{b.food_charges:>8,.2f} "
                  f"₹{b.tax:>6,.2f} ₹{b.total_amount:>8,.2f}  "
                  f"{'Paid' if b.is_paid else 'Pending'}")
        print("═" * 65)

    def print_all_invoices(self) -> None:
        """
        Print all invoices one at a time using the generator.
        Python Concept: Generator
        """
        # Generator usage: generate_invoices yields one bill at a time
        for bill in generate_invoices(self.bills):
            bill.print_invoice()
            input("  Press Enter for next invoice...")

    # ════════════════════════════════════════
    # REPORTS
    # ════════════════════════════════════════

    def generate_report(self) -> None:
        """
        Print an on-screen summary report for the hotel.
        """
        # List comprehension: count booked rooms
        booked_rooms = [r for r in self.rooms if not r.availability_status]
        available_rooms = [r for r in self.rooms if r.availability_status]

        # List comprehension: count paid bills
        paid_bills = [b for b in self.bills if b.is_paid]
        total_revenue = sum(b.total_amount for b in paid_bills)

        print("\n" + "═" * 60)
        print("  📊  HOTEL SUMMARY REPORT — DineStay")
        print("  " + datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        print("═" * 60)
        print(f"  Total Rooms        : {len(self.rooms)}")
        print(f"  Available Rooms    : {len(available_rooms)}")
        print(f"  Booked Rooms       : {len(booked_rooms)}")
        print(f"  Total Customers    : {len(self.customers)}")
        print(f"  Total Employees    : {len(self.employees)}")
        print(f"  Total Food Orders  : {len(self.orders)}")
        print(f"  Total Bills        : {len(self.bills)}")
        print(f"  Paid Bills         : {len(paid_bills)}")
        print(f"  Revenue (Paid)     : ₹{total_revenue:,.2f}")
        print(f"  Unique Room Types  : {Room.get_unique_room_types()}")
        print(f"  Food Categories    : {FoodItem.get_all_categories()}")
        print("═" * 60)

    # ════════════════════════════════════════
    # ID COUNTER SYNC (called after loading data)
    # ════════════════════════════════════════

    def sync_id_counters(self) -> None:
        """After loading data, sync auto-increment counters."""
        if self.rooms:
            self._next_room_id = max(r.room_id for r in self.rooms) + 1
        if self.customers:
            self._next_customer_id = max(c.customer_id for c in self.customers) + 1
        if self.employees:
            self._next_employee_id = max(e.employee_id for e in self.employees) + 1
        if self.menu:
            self._next_food_id = max(f.food_id for f in self.menu) + 1
        if self.orders:
            self._next_order_id = max(o.order_id for o in self.orders) + 1
        if self.bills:
            self._next_bill_id = max(b.bill_id for b in self.bills) + 1

    def __str__(self) -> str:
        return (f"Hotel '{self.name}' | Rooms: {len(self.rooms)} | "
                f"Customers: {len(self.customers)} | "
                f"Employees: {len(self.employees)}")

    def __repr__(self) -> str:
        return (f"Hotel(name='{self.name}', rooms={len(self.rooms)}, "
                f"customers={len(self.customers)}, "
                f"employees={len(self.employees)})")
