"""
DineStay - Hotel & Restaurant Management System
file_handler.py

Demonstrates:
- JSON file handling: save/load all data
- CSV file handling: generate reports
- datetime module for timestamps
- Exception handling: FileNotFoundError
"""

import json
import csv
import os
from datetime import datetime

from models.customer import Customer
from models.employee import Employee
from models.food import FoodItem, Order
from models.bill import Bill
from models.room import DeluxeRoom, StandardRoom


# ─────────────────────────────────────────────
# Directory Setup
# ─────────────────────────────────────────────
DATA_DIR = "data"
REPORTS_DIR = "reports"

def _ensure_dirs() -> None:
    """Create data and reports directories if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)


# ══════════════════════════════════════════════════════════
# JSON SAVE FUNCTIONS
# File Handling: json module for persistence
# ══════════════════════════════════════════════════════════

def save_customers(customers: list) -> None:
    """Serialize and save all customers to customers.json."""
    _ensure_dirs()
    path = os.path.join(DATA_DIR, "customers.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in customers], f, indent=2)
    print(f"  💾 Customers saved to '{path}'")


def save_rooms(rooms: list) -> None:
    """Serialize and save all rooms to rooms.json."""
    _ensure_dirs()
    path = os.path.join(DATA_DIR, "rooms.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump([r.to_dict() for r in rooms], f, indent=2)
    print(f"  💾 Rooms saved to '{path}'")


def save_employees(employees: list) -> None:
    """Serialize and save all employees to employees.json."""
    _ensure_dirs()
    path = os.path.join(DATA_DIR, "employees.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump([e.to_dict() for e in employees], f, indent=2)
    print(f"  💾 Employees saved to '{path}'")


def save_menu(menu: list) -> None:
    """Save the restaurant menu to menu.json."""
    _ensure_dirs()
    path = os.path.join(DATA_DIR, "menu.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump([item.to_dict() for item in menu], f, indent=2)
    print(f"  💾 Menu saved to '{path}'")


def save_orders(orders: list) -> None:
    """Save all orders to orders.json."""
    _ensure_dirs()
    path = os.path.join(DATA_DIR, "orders.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump([o.to_dict() for o in orders], f, indent=2)
    print(f"  💾 Orders saved to '{path}'")


def save_bills(bills: list) -> None:
    """Save all bills to bills.json."""
    _ensure_dirs()
    path = os.path.join(DATA_DIR, "bills.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump([b.to_dict() for b in bills], f, indent=2)
    print(f"  💾 Bills saved to '{path}'")


def save_all(hotel) -> None:
    """
    Save all hotel data at once.
    Calls all individual save functions.
    """
    save_customers(hotel.customers)
    save_rooms(hotel.rooms)
    save_employees(hotel.employees)
    save_menu(hotel.menu)
    save_orders(hotel.orders)
    save_bills(hotel.bills)
    print("\n  ✅ All data saved successfully.")


# ══════════════════════════════════════════════════════════
# JSON LOAD FUNCTIONS
# Exception Handling: FileNotFoundError when data files missing
# ══════════════════════════════════════════════════════════

def load_customers() -> list:
    """Load customers from customers.json. Returns empty list if missing."""
    path = os.path.join(DATA_DIR, "customers.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        customers = [Customer.from_dict(c) for c in data]
        print(f"  📂 Loaded {len(customers)} customer(s) from '{path}'")
        return customers
    except FileNotFoundError:
        print(f"  ⚠  '{path}' not found. Starting with no customers.")
        return []
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  ⚠  Error reading '{path}': {e}")
        return []


def load_rooms() -> list:
    """Load rooms from rooms.json. Reconstructs DeluxeRoom or StandardRoom."""
    path = os.path.join(DATA_DIR, "rooms.json")
    rooms = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for d in data:
            subtype = d.get("subtype", "StandardRoom")
            if subtype == "DeluxeRoom":
                r = DeluxeRoom(
                    room_id=d["room_id"],
                    room_number=d["room_number"],
                    room_price=d["room_price"],
                    wifi=d.get("wifi", True),
                    minibar=d.get("minibar", True),
                    complimentary_breakfast=d.get("complimentary_breakfast", True),
                )
            else:
                r = StandardRoom(
                    room_id=d["room_id"],
                    room_number=d["room_number"],
                    room_price=d["room_price"],
                    television=d.get("television", True),
                    air_conditioning=d.get("air_conditioning", True),
                )
            r.availability_status = d.get("availability_status", True)
            r.booked_by = d.get("booked_by")
            ci = d.get("check_in_date")
            co = d.get("check_out_date")
            r.check_in_date = datetime.fromisoformat(ci) if ci else None
            r.check_out_date = datetime.fromisoformat(co) if co else None
            rooms.append(r)
        print(f"  📂 Loaded {len(rooms)} room(s) from '{path}'")
    except FileNotFoundError:
        print(f"  ⚠  '{path}' not found. Starting with no rooms.")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  ⚠  Error reading '{path}': {e}")
    return rooms


def load_employees() -> list:
    """Load employees from employees.json."""
    path = os.path.join(DATA_DIR, "employees.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        employees = [Employee.from_dict(e) for e in data]
        print(f"  📂 Loaded {len(employees)} employee(s) from '{path}'")
        return employees
    except FileNotFoundError:
        print(f"  ⚠  '{path}' not found. Starting with no employees.")
        return []
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  ⚠  Error reading '{path}': {e}")
        return []


def load_menu() -> list:
    """Load food menu from menu.json."""
    path = os.path.join(DATA_DIR, "menu.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        menu = [FoodItem.from_dict(item) for item in data]
        print(f"  📂 Loaded {len(menu)} menu item(s) from '{path}'")
        return menu
    except FileNotFoundError:
        print(f"  ⚠  '{path}' not found. Starting with empty menu.")
        return []
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  ⚠  Error reading '{path}': {e}")
        return []


def load_orders(menu: list) -> list:
    """Load orders from orders.json. Needs menu to rebuild FoodItem refs."""
    path = os.path.join(DATA_DIR, "orders.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        orders = [Order.from_dict(o, menu) for o in data]
        print(f"  📂 Loaded {len(orders)} order(s) from '{path}'")
        return orders
    except FileNotFoundError:
        print(f"  ⚠  '{path}' not found. Starting with no orders.")
        return []
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  ⚠  Error reading '{path}': {e}")
        return []


def load_bills() -> list:
    """Load bills from bills.json."""
    path = os.path.join(DATA_DIR, "bills.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        bills = [Bill.from_dict(b) for b in data]
        print(f"  📂 Loaded {len(bills)} bill(s) from '{path}'")
        return bills
    except FileNotFoundError:
        print(f"  ⚠  '{path}' not found. Starting with no bills.")
        return []
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  ⚠  Error reading '{path}': {e}")
        return []


def load_all(hotel) -> None:
    """
    Load all hotel data from JSON files into the hotel object.
    """
    hotel.customers = load_customers()
    hotel.rooms = load_rooms()
    hotel.employees = load_employees()
    hotel.menu = load_menu()
    hotel.orders = load_orders(hotel.menu)
    hotel.bills = load_bills()

    # Rebuild fast-lookup dictionaries after loading
    hotel._customer_dict = {c.customer_id: c for c in hotel.customers}
    hotel._room_dict = {r.room_number: r for r in hotel.rooms}

    print("\n  ✅ All data loaded successfully.")


# ══════════════════════════════════════════════════════════
# CSV REPORT FUNCTIONS
# File Handling: csv module for human-readable reports
# ══════════════════════════════════════════════════════════

def generate_daily_sales_report(bills: list) -> str:
    """
    Generate a CSV report of all bills (daily sales).
    Returns the path to the created file.
    """
    _ensure_dirs()
    # datetime: timestamp in filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(REPORTS_DIR, f"daily_sales_{timestamp}.csv")

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Header row
        writer.writerow([
            "Bill ID", "Customer ID", "Customer Name",
            "Room Charges (₹)", "Food Charges (₹)",
            "GST (₹)", "Total Amount (₹)", "Status", "Generated On"
        ])
        # Data rows
        for b in bills:
            writer.writerow([
                b.bill_id,
                b.customer_id,
                b.customer_name,
                f"{b.room_charges:.2f}",
                f"{b.food_charges:.2f}",
                f"{b.tax:.2f}",
                f"{b.total_amount:.2f}",
                "Paid" if b.is_paid else "Pending",
                b.generated_on.strftime("%d-%m-%Y %H:%M:%S"),
            ])

    print(f"  📊 Daily Sales Report saved to '{path}'")
    return path


def generate_room_occupancy_report(rooms: list) -> str:
    """
    Generate a CSV report of room occupancy status.
    """
    _ensure_dirs()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(REPORTS_DIR, f"room_occupancy_{timestamp}.csv")

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Room ID", "Room Number", "Type", "Price (₹/night)",
            "Status", "Booked By (Customer ID)",
            "Check-In", "Check-Out"
        ])
        for r in rooms:
            writer.writerow([
                r.room_id,
                r.room_number,
                r.room_type,
                f"{r.room_price:.2f}",
                "Available" if r.availability_status else "Booked",
                r.booked_by or "—",
                r.check_in_date.strftime("%d-%m-%Y") if r.check_in_date else "—",
                r.check_out_date.strftime("%d-%m-%Y") if r.check_out_date else "—",
            ])

    print(f"  📊 Room Occupancy Report saved to '{path}'")
    return path


def generate_employee_report(employees: list) -> str:
    """
    Generate a CSV report of all employees.
    """
    _ensure_dirs()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(REPORTS_DIR, f"employee_report_{timestamp}.csv")

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Employee ID", "Name", "Designation",
            "Department", "Salary (₹)", "Joined On"
        ])
        for e in employees:
            writer.writerow([
                e.employee_id,
                e.name,
                e.designation,
                e.department,
                f"{e.salary:.2f}",
                e.joined_on.strftime("%d-%m-%Y"),
            ])

    print(f"  📊 Employee Report saved to '{path}'")
    return path


EXPLORE_FILE = os.path.join(DATA_DIR, "explore.json")


def load_explore_data() -> list:
    """Load explore locations data from explore.json. Seeds default data if missing."""
    _ensure_dirs()
    if os.path.exists(EXPLORE_FILE):
        try:
            with open(EXPLORE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # Default Seed data including affordable options
    default_data = [
        {
            "location_id": 1,
            "name": "DineStay Heritage Palace",
            "city": "Jaipur, Rajasthan",
            "image": "explore_jaipur.png",
            "restaurant_image": "rest_jaipur.png",
            "tier": "Luxury",
            "price_range": "₹4,500 - ₹8,000 / night",
            "description": "A magnificent royal heritage palace offering guests a taste of Rajputana majesty. Dine stay like royalty in our hand-painted fresco suites and enjoy royal hospitality.",
            "restaurant_name": "The Maharaja Dining Hall",
            "restaurant_description": "Famous for its authentic Rajasthani 'Thali' and Mughlai recipes, cooked with traditional clay-pot techniques and served in gold-trimmed chinaware under heritage chandeliers.",
            "room_ambience": "Regal furnishings, traditional Jharokha window seats, carved wooden beds, and authentic ethnic tapestries blending royal heritage with modern bathrooms.",
            "facilities": ["24/7 Royal Room Service", "Private Heritage Balcony", "Swimming Pool", "High-speed WiFi", "Guided Palace Tour"],
            "rating": 4.8,
            "cuisine": "Mughlai, North Indian, Royal Rajasthani",
            "avg_price": "₹1,500 for two",
            "branches": ["Jaipur Heritage Palace", "Delhi CP", "Mumbai Bandra"],
            "popular_dishes": [
                {"name": "Paneer Tikka", "image": "food_paneer.png", "price": "₹280"},
                {"name": "Laal Maas Kebab", "image": "food_chicken.png", "price": "₹350"},
                {"name": "Grilled Pomfret", "image": "food_fish.png", "price": "₹450"},
                {"name": "Brownie Sundae", "image": "food_dessert.png", "price": "₹180"}
            ],
            "events": [
                {
                    "event_id": 1,
                    "title": "Traditional Kathputli Puppet Show & Folk Dance",
                    "date": "2026-06-25",
                    "time": "18:30",
                    "venue": "Palace Courtyard",
                    "description": "An enchanting evening featuring traditional Rajasthani puppet shows, Ghoomar dancers, and live sarangi musicians with complimentary snacks."
                }
            ]
        },
        {
            "location_id": 2,
            "name": "DineStay Coconut Grove",
            "city": "Kochi, Kerala",
            "image": "explore_kochi.png",
            "restaurant_image": "rest_kochi.png",
            "tier": "Premium",
            "price_range": "₹3,500 - ₹6,000 / night",
            "description": "Nestled along the pristine backwaters, Coconut Grove offers a serene retreat with swaying palm trees and refreshing coastal breezes.",
            "restaurant_name": "The Backwater Grill",
            "restaurant_description": "Specializing in fresh local seafood, Karimeen Pollichathu, and coastal coconut curries, dining right beside the serene river estuary.",
            "room_ambience": "Tropical teakwood interiors, open-to-sky shower areas, bamboo shutters, and relaxing patio views of the Kochi backwaters.",
            "facilities": ["Ayurvedic Spa Treatments", "Backwater Houseboat Cruises", "Complimentary Breakfast", "Free High-speed WiFi"],
            "rating": 4.6,
            "cuisine": "Coastal Kerala, Seafood, South Indian",
            "avg_price": "₹1,200 for two",
            "branches": ["Fort Kochi Beach", "Alleppey Backwaters"],
            "popular_dishes": [
                {"name": "Paneer Malai Tikka", "image": "food_paneer.png", "price": "₹260"},
                {"name": "Chicken Fritters", "image": "food_chicken.png", "price": "₹320"},
                {"name": "Karimeen Pollichathu", "image": "food_fish.png", "price": "₹480"},
                {"name": "Coconut Souffle", "image": "food_dessert.png", "price": "₹160"}
            ],
            "events": [
                {
                    "event_id": 1,
                    "title": "Ayurveda Wellness & Yoga Retreat",
                    "date": "2026-06-28",
                    "time": "07:00",
                    "venue": "Meditation Pavilion",
                    "description": "Start your morning with guided yoga postures and breathing techniques, followed by wellness consultation talks with Ayurvedic doctors."
                }
            ]
        },
        {
            "location_id": 3,
            "name": "DineStay Vista",
            "city": "Mumbai, Maharashtra",
            "image": "explore_mumbai.png",
            "restaurant_image": "rest_mumbai.png",
            "tier": "Luxury",
            "price_range": "₹5,000 - ₹9,500 / night",
            "description": "A striking modern high-rise overlooking the Arabian Sea, combining sleek urban architecture with luxury high-end comfort.",
            "restaurant_name": "The Skyline Bistro",
            "restaurant_description": "An award-winning rooftop gourmet bistro serving progressive global cuisines, signature craft mixology, and a breathtaking 360-degree skyline view.",
            "room_ambience": "Sleek glass walls, premium floor-to-ceiling city views, smart home touch controls, and automated plush modern furnishing.",
            "facilities": ["Rooftop Infinity Pool", "24-Hour Executive Lounge", "Fitness Center", "Meeting & Business Suites"],
            "rating": 4.9,
            "cuisine": "Modern European, Progressive Indian, Italian",
            "avg_price": "₹2,000 for two",
            "branches": ["Colaba Vista", "Bandra High Street", "Bengaluru Indiranagar"],
            "popular_dishes": [
                {"name": "Truffle Pizza Sliders", "image": "food_paneer.png", "price": "₹320"},
                {"name": "Butter Chicken Tacos", "image": "food_chicken.png", "price": "₹380"},
                {"name": "Pan-Seared Salmon", "image": "food_fish.png", "price": "₹550"},
                {"name": "Classic Tiramisu", "image": "food_dessert.png", "price": "₹220"}
            ],
            "events": [
                {
                    "event_id": 1,
                    "title": "Sunsets & Saxophone Live Sessions",
                    "date": "2026-06-30",
                    "time": "18:00",
                    "venue": "Skyline Rooftop Bar",
                    "description": "Sip cocktails and watch the sun dip below the ocean horizon while listening to soothing live jazz saxophone sessions."
                }
            ]
        },
        {
            "location_id": 4,
            "name": "DineStay Himalayan Retreat",
            "city": "Shimla, Himachal Pradesh",
            "image": "explore_shimla.png",
            "restaurant_image": "rest_shimla.png",
            "tier": "Premium",
            "price_range": "₹4,000 - ₹7,000 / night",
            "description": "Escape to our tranquil mountain lodge surrounded by pine forests and snow-capped peaks, perfect for adventure or ultimate relaxation.",
            "restaurant_name": "The Pine Wood Hearth",
            "restaurant_description": "Enjoy cozy fireside dining featuring wood-fired pizzas, local Himachali stews, and hot spiced mountain tea (Kahwa).",
            "room_ambience": "Cozy pine-wood paneling, stone fireplaces, thermal heating, and large bay windows looking out over misty mountain valleys.",
            "facilities": ["Cozy Stone Fireplace", "Heated Indoor Lounge", "Guided Trekking & Hikes", "Complimentary High-speed WiFi"],
            "rating": 4.5,
            "cuisine": "Himachali, Wood-fired Italian, Continental",
            "avg_price": "₹1,000 for two",
            "branches": ["Mall Road Shimla", "Manali Valley Lodge"],
            "popular_dishes": [
                {"name": "Paneer Woodfired Flatbread", "image": "food_paneer.png", "price": "₹240"},
                {"name": "Cozy Roasted Chicken", "image": "food_chicken.png", "price": "₹320"},
                {"name": "Fireside Trout Grill", "image": "food_fish.png", "price": "₹420"},
                {"name": "Warm Apple Crumble", "image": "food_dessert.png", "price": "₹150"}
            ],
            "events": [
                {
                    "event_id": 1,
                    "title": "Bonfire Night & Mountain Stargazing",
                    "date": "2026-07-05",
                    "time": "20:00",
                    "venue": "Terrace Fire Pit",
                    "description": "Gather around the crackling bonfire for live acoustic guitars, roasted marshmallows, and a guided tour of the constellations."
                }
            ]
        },
        {
            "location_id": 5,
            "name": "DineStay Silicon Valley",
            "city": "Bengaluru, Karnataka",
            "image": "explore_bengaluru.png",
            "restaurant_image": "rest_bengaluru.png",
            "tier": "Executive",
            "price_range": "₹3,500 - ₹6,500 / night",
            "description": "A high-tech garden hotel in the heart of Bengaluru's IT hub, catering to both digital nomads and corporate leaders.",
            "restaurant_name": "The Cyber Cafe & Taproom",
            "restaurant_description": "Bengaluru's premier microbrewery and workspace restaurant, serving hand-crafted beers, woodfired pizzas, and global fusion cuisine.",
            "room_ambience": "Ergonomic work desks, smart voice assistants, high-speed fiber internet, and sleek corporate layouts with garden terrace access.",
            "facilities": ["Co-working Hubs", "In-house Microbrewery", "Voice-Controlled Rooms", "High-speed Fiber WiFi"],
            "rating": 4.7,
            "cuisine": "American Craft, Fusion, Finger Food",
            "avg_price": "₹1,200 for two",
            "branches": ["Indiranagar Taproom", "Whitefield Garden", "Koramangala Hub"],
            "popular_dishes": [
                {"name": "Craft Cheese Nachos", "image": "food_paneer.png", "price": "₹220"},
                {"name": "Peri Peri Wings", "image": "food_chicken.png", "price": "₹280"},
                {"name": "Crispy Fish Fingers", "image": "food_fish.png", "price": "₹320"},
                {"name": "Molten Lava Cake", "image": "food_dessert.png", "price": "₹160"}
            ],
            "events": [
                {
                    "event_id": 1,
                    "title": "Tech & Startup Networking Mixer",
                    "date": "2026-07-08",
                    "time": "18:30",
                    "venue": "Taproom Garden",
                    "description": "An informal networking mixer for local tech enthusiasts, startups, and founders with free craft beer tastings and bites."
                }
            ]
        },
        {
            "location_id": 6,
            "name": "DineStay Goa Beach Inn",
            "city": "Goa (North Goa)",
            "image": "explore_goa.png",
            "restaurant_image": "rest_goa.png",
            "tier": "Budget Friendly",
            "price_range": "₹1,200 - ₹2,500 / night",
            "description": "An affordable, vibrant beachside inn designed for backpackers and families looking for clean, comfortable seaside lodging without the high price tag.",
            "restaurant_name": "The Sun & Sand Shack",
            "restaurant_description": "A lively open-air shack serving fresh catch-of-the-day fish fry, traditional Goan vindaloo, and pocket-friendly tropical mocktails.",
            "room_ambience": "Bright coastal-themed decor, tiled floors, clean air conditioning, and a breezy porch just steps from the sand.",
            "facilities": ["Steps from the Beach", "Bicycle & Scooter Rentals", "Self-Service Laundry", "Free High-speed WiFi"],
            "rating": 4.4,
            "cuisine": "Goan, Seafood, Portuguese",
            "avg_price": "₹800 for two",
            "branches": ["Calangute Beachfront Inn", "Anjuna Coast Shack"],
            "popular_dishes": [
                {"name": "Goan Chilli Paneer", "image": "food_paneer.png", "price": "₹200"},
                {"name": "Vindaloo Croquettes", "image": "food_chicken.png", "price": "₹260"},
                {"name": "Butter Garlic Calamari", "image": "food_fish.png", "price": "₹350"},
                {"name": "Bebinca with Ice Cream", "image": "food_dessert.png", "price": "₹140"}
            ],
            "events": [
                {
                    "event_id": 1,
                    "title": "Beach BBQ & Acoustic Night",
                    "date": "2026-07-12",
                    "time": "19:30",
                    "venue": "Beachfront Cafe",
                    "description": "Enjoy a budget-friendly beachfront barbecue under fairy lights with live acoustic hits and refreshing drinks."
                }
            ]
        },
        {
            "location_id": 7,
            "name": "DineStay Transit Lodge",
            "city": "Delhi (NCR)",
            "image": "explore_delhi.png",
            "restaurant_image": "rest_delhi.png",
            "tier": "Budget Friendly",
            "price_range": "₹1,000 - ₹2,200 / night",
            "description": "A clean, modern, and extremely affordable transit hotel located near major transport links, perfect for budget travelers and short city layovers.",
            "restaurant_name": "The Chutney Express",
            "restaurant_description": "A pocket-friendly cafe serving iconic Delhi street food favorites, parathas, samosa chaat, and cutting masala chai.",
            "room_ambience": "Simple, functional, and spotlessly clean layout with comfortable pocket-spring mattresses and bright, well-lit spaces.",
            "facilities": ["24/7 Front Desk & Check-in", "Near Airport/Metro Station", "Free High-speed WiFi", "Luggage Storage"],
            "rating": 4.3,
            "cuisine": "Delhi Street Food, Fast Food, North Indian",
            "avg_price": "₹500 for two",
            "branches": ["Connaught Place Transit", "Chandni Chowk Cafe", "Noida Sector 62"],
            "popular_dishes": [
                {"name": "Tangy Samosa Chaat", "image": "food_paneer.png", "price": "₹120"},
                {"name": "Chole Bhature Platter", "image": "food_chicken.png", "price": "₹150"},
                {"name": "Butter Chicken Roll", "image": "food_fish.png", "price": "₹180"},
                {"name": "Kulfi Falooda Sundae", "image": "food_dessert.png", "price": "₹100"}
            ],
            "events": [
                {
                    "event_id": 1,
                    "title": "Delhi Heritage Street Food Walk",
                    "date": "2026-07-15",
                    "time": "17:00",
                    "venue": "Lobby Meeting Point",
                    "description": "Join our local guide for an affordable street food walk to sample the best chaat and parathas in Old Delhi (metro fare included!)."
                }
            ]
        }
    ]
    save_explore_data(default_data)
    return default_data


def save_explore_data(data: list) -> None:
    """Save explore locations data to explore.json."""
    _ensure_dirs()
    with open(EXPLORE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

