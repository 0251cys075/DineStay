"""
DineStay - Hotel & Restaurant Management System
models/bill.py

Demonstrates:
- Encapsulation: name mangling for __total_amount, __tax
- Static method: calculate_tax()
- Generator: generate_invoices()
- __str__ and __repr__
- datetime for bill timestamps
"""

from datetime import datetime


# ─────────────────────────────────────────────
# Custom Exception
# ─────────────────────────────────────────────
class InvalidBillAmount(Exception):
    """Raised when bill amount is negative or invalid."""
    pass


# ─────────────────────────────────────────────
# Bill Class
# OOP Concept: Encapsulation (private billing info)
# ─────────────────────────────────────────────
class Bill:
    """
    Represents a final invoice for a customer's stay and food orders.
    Billing information is protected via name mangling.
    """

    GST_RATE = 0.18   # 18% GST (constant)

    def __init__(self, bill_id: int, customer_id: int,
                 room_charges: float, food_charges: float,
                 customer_name: str = "Guest"):
        self.bill_id = bill_id
        self.customer_id = customer_id
        self.customer_name = customer_name

        # Encapsulation: name-mangled private billing attributes
        self.__room_charges = room_charges
        self.__food_charges = food_charges
        self.__tax = 0.0
        self.__total_amount = 0.0

        # datetime: record when the bill was generated
        self.generated_on = datetime.now()
        self.is_paid = False

    # ── Property Accessors ─────────────────
    @property
    def room_charges(self) -> float:
        return self.__room_charges

    @property
    def food_charges(self) -> float:
        return self.__food_charges

    @property
    def tax(self) -> float:
        return self.__tax

    @property
    def total_amount(self) -> float:
        return self.__total_amount

    # ── Static Method ──────────────────────
    @staticmethod
    def calculate_tax(subtotal: float) -> float:
        """
        Calculate GST at 18% on the given subtotal.
        Static Method: does not need access to instance or class state.
        """
        return round(subtotal * Bill.GST_RATE, 2)

    # ── Instance Methods ───────────────────
    def generate_bill(self) -> None:
        """
        Compute tax and total, then confirm bill generation.
        """
        subtotal = self.__room_charges + self.__food_charges
        if subtotal < 0:
            raise InvalidBillAmount("Bill subtotal cannot be negative.")

        # Static method call
        self.__tax = Bill.calculate_tax(subtotal)
        self.__total_amount = round(subtotal + self.__tax, 2)
        print(f"\n  ✅ Bill #{self.bill_id} generated for Customer #{self.customer_id}")

    def mark_paid(self) -> None:
        """Mark this bill as paid."""
        self.is_paid = True
        print(f"  💳 Bill #{self.bill_id} marked as PAID.")

    def print_invoice(self) -> None:
        """Print a detailed formatted invoice to the console."""
        print("\n" + "╔" + "═" * 53 + "╗")
        print("║{:^53}║".format("★  DineStay Hotels & Restaurants  ★"))
        print("║{:^53}║".format("INVOICE"))
        print("╠" + "═" * 53 + "╣")
        print(f"║  Bill ID       : {self.bill_id:<34}║")
        print(f"║  Customer      : {self.customer_name:<34}║")
        print(f"║  Customer ID   : {self.customer_id:<34}║")
        print(f"║  Generated On  : "
              f"{self.generated_on.strftime('%d-%m-%Y %H:%M:%S'):<34}║")
        print("╠" + "═" * 53 + "╣")
        print(f"║  Room Charges  : ₹{self.__room_charges:<33,.2f}║")
        print(f"║  Food Charges  : ₹{self.__food_charges:<33,.2f}║")
        print("║" + "─" * 53 + "║")
        subtotal = self.__room_charges + self.__food_charges
        print(f"║  Subtotal      : ₹{subtotal:<33,.2f}║")
        print(f"║  GST (18%)     : ₹{self.__tax:<33,.2f}║")
        print("╠" + "═" * 53 + "╣")
        print(f"║  TOTAL AMOUNT  : ₹{self.__total_amount:<33,.2f}║")
        print(f"║  Payment Status: {'PAID ✅' if self.is_paid else 'PENDING ⏳':<34}║")
        print("╚" + "═" * 53 + "╝")

    def to_dict(self) -> dict:
        """Serialize Bill to dict for JSON storage."""
        return {
            "bill_id": self.bill_id,
            "customer_id": self.customer_id,
            "customer_name": self.customer_name,
            "room_charges": self.__room_charges,
            "food_charges": self.__food_charges,
            "tax": self.__tax,
            "total_amount": self.__total_amount,
            "generated_on": self.generated_on.isoformat(),
            "is_paid": self.is_paid,
        }

    @staticmethod
    def from_dict(data: dict) -> "Bill":
        """Reconstruct a Bill from a dict."""
        b = Bill(
            bill_id=data["bill_id"],
            customer_id=data["customer_id"],
            room_charges=data["room_charges"],
            food_charges=data["food_charges"],
            customer_name=data.get("customer_name", "Guest"),
        )
        # Restore computed fields via name-mangled access (within class)
        b._Bill__tax = data.get("tax", 0.0)
        b._Bill__total_amount = data.get("total_amount", 0.0)
        b.generated_on = datetime.fromisoformat(data["generated_on"])
        b.is_paid = data.get("is_paid", False)
        return b

    def __str__(self) -> str:
        return (f"Bill #{self.bill_id} | Customer #{self.customer_id} "
                f"| Total: ₹{self.__total_amount:.2f} "
                f"| {'Paid' if self.is_paid else 'Pending'}")

    def __repr__(self) -> str:
        return (f"Bill(id={self.bill_id}, customer_id={self.customer_id}, "
                f"total={self.__total_amount}, paid={self.is_paid})")


# ─────────────────────────────────────────────
# Generator Function
# Python Concept: Generator — yields one bill at a time
# ─────────────────────────────────────────────
def generate_invoices(bills: list):
    """
    Generator that yields one Bill at a time for batch printing.
    Useful for processing large sets of bills without loading all into memory.

    Usage:
        for bill in generate_invoices(hotel.bills):
            bill.print_invoice()
    """
    for bill in bills:
        yield bill   # Generator: yields control back to caller each iteration
