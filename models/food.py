"""
DineStay - Hotel & Restaurant Management System
models/food.py

Demonstrates:
- FoodItem class with sets for unique food categories
- Order class with list of ordered items
- Lambda for sorting food items by price
- __str__ and __repr__
- datetime for order timestamps
"""

from datetime import datetime


# ─────────────────────────────────────────────
# Custom Exception
# ─────────────────────────────────────────────
class InvalidOrderID(Exception):
    """Raised when an invalid order ID is provided."""
    pass


# ─────────────────────────────────────────────
# FoodItem Class
# OOP Concept: Encapsulation, Sets for unique categories
# ─────────────────────────────────────────────
class FoodItem:
    """
    Represents a single item on the restaurant menu.
    Tracks all unique food categories via a class-level set.
    """

    # Set usage: guarantees unique food categories across all items
    _all_categories: set = set()

    def __init__(self, food_id: int, food_name: str,
                 category: str, price: float):
        self.food_id = food_id
        self.food_name = food_name
        self.category = category
        self.price = price

        # Register category in the class-level set (uniqueness guaranteed)
        FoodItem._all_categories.add(category)

    @classmethod
    def get_all_categories(cls) -> set:
        """Return the set of all unique food categories."""
        # Set usage
        return cls._all_categories

    def display_food(self) -> None:
        """Display this food item's details."""
        print(f"  [{self.food_id:>3}] {self.food_name:<30} "
              f"| {self.category:<15} | ₹{self.price:.2f}")

    def update_price(self, new_price: float) -> None:
        """Update the price of this food item."""
        if new_price <= 0:
            raise ValueError("Price must be positive.")
        old_price = self.price
        self.price = new_price
        print(f"  ✅ Price of '{self.food_name}' updated: "
              f"₹{old_price:.2f} → ₹{new_price:.2f}")

    def to_dict(self) -> dict:
        """Serialize FoodItem to dict."""
        return {
            "food_id": self.food_id,
            "food_name": self.food_name,
            "category": self.category,
            "price": self.price,
        }

    @staticmethod
    def from_dict(data: dict) -> "FoodItem":
        """Reconstruct a FoodItem from a dict."""
        return FoodItem(
            food_id=data["food_id"],
            food_name=data["food_name"],
            category=data["category"],
            price=data["price"],
        )

    def __str__(self) -> str:
        return f"[{self.food_id}] {self.food_name} ({self.category}) - ₹{self.price:.2f}"

    def __repr__(self) -> str:
        return (f"FoodItem(id={self.food_id}, name='{self.food_name}', "
                f"category='{self.category}', price={self.price})")


# ─────────────────────────────────────────────
# Order Class
# OOP Concept: Composition (Order contains FoodItems)
# ─────────────────────────────────────────────
class Order:
    """
    Represents a food order placed by a customer.
    Maintains a list of (FoodItem, quantity) tuples.
    """

    # Lambda: sort ordered items by price descending
    sort_by_price = staticmethod(
        lambda items: sorted(items, key=lambda x: x[0].price, reverse=True)
    )

    def __init__(self, order_id: int, customer_id: int):
        self.order_id = order_id
        self.customer_id = customer_id
        # List of tuples: (FoodItem, quantity)
        # Tuple usage: each ordered item stored as (item, qty)
        self.ordered_items: list = []
        self.total_amount: float = 0.0
        self.order_status: str = "Pending"   # Pending / Confirmed / Cancelled
        # datetime: record exact order placement time
        self.order_time = datetime.now()

    def place_order(self, food_item: FoodItem, quantity: int = 1) -> None:
        """Add a food item to this order."""
        if self.order_status == "Cancelled":
            raise InvalidOrderID(f"Order #{self.order_id} is cancelled.")
        # Tuple: store (item_object, quantity)
        self.ordered_items.append((food_item, quantity))
        self.order_status = "Confirmed"
        self.total_amount = self.calculate_total()
        print(f"  ✅ Added '{food_item.food_name}' x{quantity} to Order #{self.order_id}")

    def cancel_order(self) -> None:
        """Cancel this order."""
        if self.order_status == "Cancelled":
            print(f"  ⚠  Order #{self.order_id} is already cancelled.")
            return
        self.order_status = "Cancelled"
        self.ordered_items.clear()
        self.total_amount = 0.0
        print(f"  ❌ Order #{self.order_id} has been cancelled.")

    def calculate_total(self) -> float:
        """Calculate total order amount from all items and quantities."""
        # List comprehension: sum price * qty for each (item, qty) tuple
        return sum(item.price * qty for item, qty in self.ordered_items)

    def display_order(self) -> None:
        """Print a formatted order summary."""
        print("\n" + "=" * 55)
        print(f"  🍽  ORDER #{self.order_id}  |  Status: {self.order_status}")
        print("=" * 55)
        print(f"  Customer ID : {self.customer_id}")
        print(f"  Order Time  : {self.order_time.strftime('%d-%m-%Y %H:%M:%S')}")
        print("  " + "-" * 53)
        if self.ordered_items:
            for food_item, qty in self.ordered_items:
                print(f"  {food_item.food_name:<30} x{qty}  "
                      f"₹{food_item.price * qty:.2f}")
        else:
            print("  No items in this order.")
        print("  " + "-" * 53)
        print(f"  TOTAL       : ₹{self.total_amount:.2f}")
        print("=" * 55)

    def to_dict(self) -> dict:
        """Serialize Order to dict."""
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "ordered_items": [
                {"food_id": fi.food_id, "food_name": fi.food_name,
                 "price": fi.price, "category": fi.category, "quantity": qty}
                for fi, qty in self.ordered_items
            ],
            "total_amount": self.total_amount,
            "order_status": self.order_status,
            "order_time": self.order_time.isoformat(),
        }

    @staticmethod
    def from_dict(data: dict, menu: list) -> "Order":
        """Reconstruct an Order from dict (menu needed to rebuild FoodItem refs)."""
        # Dictionary lookup: find FoodItem by food_id in the menu list
        menu_dict = {fi.food_id: fi for fi in menu}
        o = Order(order_id=data["order_id"], customer_id=data["customer_id"])
        for item_data in data.get("ordered_items", []):
            fid = item_data["food_id"]
            qty = item_data["quantity"]
            fi = menu_dict.get(fid)
            if fi is None:
                # Rebuild FoodItem from serialised data if not in current menu
                fi = FoodItem(fid, item_data["food_name"],
                              item_data["category"], item_data["price"])
            o.ordered_items.append((fi, qty))
        o.total_amount = data.get("total_amount", 0.0)
        o.order_status = data.get("order_status", "Pending")
        o.order_time = datetime.fromisoformat(data["order_time"])
        return o

    def __str__(self) -> str:
        return (f"Order #{self.order_id} | Customer #{self.customer_id} "
                f"| Items: {len(self.ordered_items)} "
                f"| Total: ₹{self.total_amount:.2f} | {self.order_status}")

    def __repr__(self) -> str:
        return (f"Order(id={self.order_id}, customer_id={self.customer_id}, "
                f"status='{self.order_status}', total={self.total_amount})")
