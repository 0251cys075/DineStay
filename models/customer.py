"""
DineStay - Hotel & Restaurant Management System
models/customer.py

Demonstrates:
- Encapsulation with name mangling (__ prefix for private attributes)
- __str__ and __repr__
- Instance methods
- Dictionaries for fast lookup
- datetime for timestamps
"""

from datetime import datetime


# ─────────────────────────────────────────────
# Custom Exception
# ─────────────────────────────────────────────
class InvalidCustomerID(Exception):
    """Raised when an invalid customer ID is provided."""
    pass


# ─────────────────────────────────────────────
# Customer Class
# OOP Concept: Encapsulation via name mangling (__)
# ─────────────────────────────────────────────
class Customer:
    """
    Represents a hotel/restaurant customer.
    Uses name mangling to protect sensitive personal details.
    """

    def __init__(self, customer_id: int, name: str,
                 phone: str, email: str):
        self.customer_id = customer_id

        # Encapsulation: name-mangled private attributes
        self.__name = name          # __ makes it Customer__name internally
        self.__phone = phone
        self.__email = email

        # Booking history: list of dicts {room_number, check_in, check_out}
        self.booking_history: list = []

        # Timestamp of registration using datetime module
        self.registered_on = datetime.now()

    # ── Property Accessors (Encapsulation via getters) ──
    @property
    def name(self) -> str:
        return self.__name

    @property
    def phone(self) -> str:
        return self.__phone

    @property
    def email(self) -> str:
        return self.__email

    # ── Methods ─────────────────────────────
    def register_customer(self) -> None:
        """Display registration confirmation."""
        print(f"\n  ✅ Customer '{self.__name}' registered successfully!")
        print(f"     Customer ID : {self.customer_id}")
        print(f"     Phone       : {self.__phone}")
        print(f"     Email       : {self.__email}")
        print(f"     Registered  : {self.registered_on.strftime('%d-%m-%Y %H:%M:%S')}")

    def update_details(self, name: str = None,
                       phone: str = None,
                       email: str = None) -> None:
        """Update customer personal details (encapsulated via setters)."""
        if name:
            self.__name = name
        if phone:
            self.__phone = phone
        if email:
            self.__email = email
        print(f"  ✅ Details updated for Customer #{self.customer_id}")

    def view_booking_history(self) -> None:
        """Display all past bookings for this customer."""
        print(f"\n  📋 Booking History for {self.__name} (ID: {self.customer_id})")
        print("  " + "-" * 50)
        if not self.booking_history:
            print("  No bookings found.")
        else:
            for i, booking in enumerate(self.booking_history, 1):
                print(f"  {i}. Room {booking.get('room_number')} | "
                      f"Check-In: {booking.get('check_in')} | "
                      f"Check-Out: {booking.get('check_out')} | "
                      f"Charge: ₹{booking.get('charge', 0):.2f}")

    def add_booking(self, room_number: str,
                    check_in: str, check_out: str,
                    charge: float) -> None:
        """Append a booking record to history."""
        self.booking_history.append({
            "room_number": room_number,
            "check_in": check_in,
            "check_out": check_out,
            "charge": charge,
            "booked_on": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        })

    def to_dict(self) -> dict:
        """Serialize customer to dict for JSON storage.
        Dictionary usage: fast key-based lookup."""
        return {
            "customer_id": self.customer_id,
            "name": self.__name,              # Access via mangled name
            "phone": self.__phone,
            "email": self.__email,
            "booking_history": self.booking_history,
            "registered_on": self.registered_on.isoformat(),
        }

    @staticmethod
    def from_dict(data: dict) -> "Customer":
        """Reconstruct a Customer from a dict (loaded from JSON)."""
        c = Customer(
            customer_id=data["customer_id"],
            name=data["name"],
            phone=data["phone"],
            email=data["email"],
        )
        c.booking_history = data.get("booking_history", [])
        c.registered_on = datetime.fromisoformat(data["registered_on"])
        return c

    def __str__(self) -> str:
        # OOP Concept: __str__
        return (f"Customer #{self.customer_id}: {self.__name} "
                f"| 📞 {self.__phone} | ✉  {self.__email}")

    def __repr__(self) -> str:
        # OOP Concept: __repr__
        return (f"Customer(id={self.customer_id}, "
                f"name='{self.__name}', phone='{self.__phone}')")
