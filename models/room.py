"""
DineStay - Hotel & Restaurant Management System
models/room.py

Demonstrates:
- Abstract Base Classes (abc.ABC, abstractmethod)
- Inheritance and Polymorphism
- Encapsulation
- __str__ and __repr__
- Tuples for fixed room facilities
"""

from abc import ABC, abstractmethod  # Abstract Base Class
from datetime import datetime


# ─────────────────────────────────────────────
# Custom Exceptions
# ─────────────────────────────────────────────
class InvalidRoomNumber(Exception):
    """Raised when an invalid room number is provided."""
    pass


class RoomNotAvailable(Exception):
    """Raised when a room is already booked."""
    pass


# ─────────────────────────────────────────────
# Abstract Base Class — Room
# OOP Concept: Abstraction via ABC
# ─────────────────────────────────────────────
class Room(ABC):
    """
    Abstract base class for all room types.
    Enforces that every subclass implements:
      - display_room_details()
      - calculate_room_charge()
      - book_room()
    """

    # Class-level set to track unique room types (Set usage)
    _room_types: set = set()

    def __init__(self, room_id: int, room_number: str,
                 room_type: str, room_price: float):
        # Encapsulation: public attributes (can be accessed directly)
        self.room_id = room_id
        self.room_number = room_number
        self.room_type = room_type
        self.room_price = room_price
        self.availability_status = True   # True = available
        self.booked_by = None            # customer_id when booked
        self.check_in_date = None
        self.check_out_date = None

        # Register this room type in the class-level set
        Room._room_types.add(room_type)

    # ── Abstract Methods ─────────────────────
    # OOP Concept: Abstract Methods (Polymorphism enforced at compile time)
    @abstractmethod
    def display_room_details(self) -> None:
        """Display full details of this room."""
        pass

    @abstractmethod
    def calculate_room_charge(self, nights: int) -> float:
        """Calculate total room charge for given number of nights."""
        pass

    @abstractmethod
    def book_room(self, customer_id: int,
                  check_in: datetime, check_out: datetime) -> bool:
        """Book this room for a customer."""
        pass

    # ── Concrete Methods ─────────────────────
    def release_room(self) -> None:
        """Mark the room as available again after checkout."""
        self.availability_status = True
        self.booked_by = None
        self.check_in_date = None
        self.check_out_date = None

    @classmethod
    def get_unique_room_types(cls) -> set:
        """Return the set of all unique room types registered so far."""
        # Set usage: guarantees uniqueness
        return cls._room_types

    def to_dict(self) -> dict:
        """Serialize room data to a dictionary for JSON persistence."""
        return {
            "room_id": self.room_id,
            "room_number": self.room_number,
            "room_type": self.room_type,
            "room_price": self.room_price,
            "availability_status": self.availability_status,
            "booked_by": self.booked_by,
            "check_in_date": self.check_in_date.isoformat() if self.check_in_date else None,
            "check_out_date": self.check_out_date.isoformat() if self.check_out_date else None,
        }

    def __str__(self) -> str:
        # OOP Concept: __str__ for human-readable output
        status = "Available" if self.availability_status else "Booked"
        return (f"Room {self.room_number} [{self.room_type}] "
                f"- ₹{self.room_price:.2f}/night | Status: {status}")

    def __repr__(self) -> str:
        # OOP Concept: __repr__ for unambiguous representation
        return (f"{self.__class__.__name__}(id={self.room_id}, "
                f"number='{self.room_number}', price={self.room_price})")


# ─────────────────────────────────────────────
# Concrete Class — DeluxeRoom
# OOP Concept: Inheritance + Polymorphism (method overriding)
# ─────────────────────────────────────────────
class DeluxeRoom(Room):
    """
    Luxury room with premium amenities.
    Inherits from Room and overrides all abstract methods.
    """

    # Tuple: immutable fixed facility list for a DeluxeRoom
    BASE_FACILITIES: tuple = ("King Bed", "LCD TV", "Private Balcony",
                              "Jacuzzi", "Room Service 24x7")

    def __init__(self, room_id: int, room_number: str, room_price: float,
                 wifi: bool = True,
                 minibar: bool = True,
                 complimentary_breakfast: bool = True):
        # Call parent constructor (Inheritance)
        super().__init__(room_id, room_number, "Deluxe", room_price)
        self.wifi = wifi
        self.minibar = minibar
        self.complimentary_breakfast = complimentary_breakfast

    # OOP Concept: Polymorphism — overriding abstract method
    def display_room_details(self) -> None:
        print("\n" + "=" * 55)
        print(f"  🏨  DELUXE ROOM — {self.room_number}")
        print("=" * 55)
        print(f"  Room ID   : {self.room_id}")
        print(f"  Price     : ₹{self.room_price:.2f} / night")
        print(f"  Status    : {'✅ Available' if self.availability_status else '❌ Booked'}")
        print(f"  Wi-Fi     : {'Yes' if self.wifi else 'No'}")
        print(f"  Minibar   : {'Yes' if self.minibar else 'No'}")
        print(f"  Breakfast : {'Complimentary' if self.complimentary_breakfast else 'Chargeable'}")
        print(f"  Facilities: {', '.join(self.BASE_FACILITIES)}")
        if self.booked_by:
            print(f"  Booked By : Customer #{self.booked_by}")
            print(f"  Check-In  : {self.check_in_date.strftime('%d-%m-%Y')}")
            print(f"  Check-Out : {self.check_out_date.strftime('%d-%m-%Y')}")
        print("=" * 55)

    # OOP Concept: Polymorphism — overriding abstract method
    def calculate_room_charge(self, nights: int) -> float:
        """
        Deluxe room charge includes a 10% premium surcharge.
        """
        base_charge = self.room_price * nights
        surcharge = base_charge * 0.10   # 10% premium surcharge
        return base_charge + surcharge

    # OOP Concept: Polymorphism — overriding abstract method
    def book_room(self, customer_id: int,
                  check_in: datetime, check_out: datetime) -> bool:
        if not self.availability_status:
            # Exception Handling: RoomNotAvailable
            raise RoomNotAvailable(
                f"Room {self.room_number} is already booked.")
        self.availability_status = False
        self.booked_by = customer_id
        self.check_in_date = check_in
        self.check_out_date = check_out
        return True

    def to_dict(self) -> dict:
        """Extend parent to_dict with subclass-specific fields."""
        data = super().to_dict()
        data.update({
            "subtype": "DeluxeRoom",
            "wifi": self.wifi,
            "minibar": self.minibar,
            "complimentary_breakfast": self.complimentary_breakfast,
        })
        return data

    def __str__(self) -> str:
        return (f"[DELUXE] Room {self.room_number} "
                f"- ₹{self.room_price:.2f}/night "
                f"| {'Available' if self.availability_status else 'Booked'}")

    def __repr__(self) -> str:
        return (f"DeluxeRoom(id={self.room_id}, "
                f"number='{self.room_number}', price={self.room_price}, "
                f"wifi={self.wifi}, minibar={self.minibar})")


# ─────────────────────────────────────────────
# Concrete Class — StandardRoom
# OOP Concept: Inheritance + Polymorphism
# ─────────────────────────────────────────────
class StandardRoom(Room):
    """
    Budget-friendly room with essential amenities.
    Inherits from Room and overrides all abstract methods.
    """

    # Tuple: immutable fixed facility list for a StandardRoom
    BASE_FACILITIES: tuple = ("Double Bed", "Television", "Air Conditioning",
                              "Hot Water", "Room Service")

    def __init__(self, room_id: int, room_number: str, room_price: float,
                 television: bool = True,
                 air_conditioning: bool = True):
        super().__init__(room_id, room_number, "Standard", room_price)
        self.television = television
        self.air_conditioning = air_conditioning

    # OOP Concept: Polymorphism — overriding abstract method
    def display_room_details(self) -> None:
        print("\n" + "=" * 55)
        print(f"  🛏  STANDARD ROOM — {self.room_number}")
        print("=" * 55)
        print(f"  Room ID   : {self.room_id}")
        print(f"  Price     : ₹{self.room_price:.2f} / night")
        print(f"  Status    : {'✅ Available' if self.availability_status else '❌ Booked'}")
        print(f"  TV        : {'Yes' if self.television else 'No'}")
        print(f"  A/C       : {'Yes' if self.air_conditioning else 'No'}")
        print(f"  Facilities: {', '.join(self.BASE_FACILITIES)}")
        if self.booked_by:
            print(f"  Booked By : Customer #{self.booked_by}")
            print(f"  Check-In  : {self.check_in_date.strftime('%d-%m-%Y')}")
            print(f"  Check-Out : {self.check_out_date.strftime('%d-%m-%Y')}")
        print("=" * 55)

    # OOP Concept: Polymorphism — overriding abstract method
    def calculate_room_charge(self, nights: int) -> float:
        """Standard room has no extra surcharge."""
        return self.room_price * nights

    # OOP Concept: Polymorphism — overriding abstract method
    def book_room(self, customer_id: int,
                  check_in: datetime, check_out: datetime) -> bool:
        if not self.availability_status:
            raise RoomNotAvailable(
                f"Room {self.room_number} is already booked.")
        self.availability_status = False
        self.booked_by = customer_id
        self.check_in_date = check_in
        self.check_out_date = check_out
        return True

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "subtype": "StandardRoom",
            "television": self.television,
            "air_conditioning": self.air_conditioning,
        })
        return data

    def __str__(self) -> str:
        return (f"[STANDARD] Room {self.room_number} "
                f"- ₹{self.room_price:.2f}/night "
                f"| {'Available' if self.availability_status else 'Booked'}")

    def __repr__(self) -> str:
        return (f"StandardRoom(id={self.room_id}, "
                f"number='{self.room_number}', price={self.room_price}, "
                f"tv={self.television}, ac={self.air_conditioning})")
