# 🏨 DineStay — Hotel & Restaurant Management System

A complete **console-based Hotel & Restaurant Management System** built in Python using Object-Oriented Programming principles.

> **Student Project** | Python 3.8+ | OOP | File Handling | Console App

---

## ✨ Features

| Module | Capabilities |
|---|---|
| 🏨 Room Management | Add Deluxe & Standard rooms, view availability |
| 👥 Customer Management | Register, search (recursive), update, booking history |
| 🗓 Room Booking | Book/checkout rooms with date-based pricing |
| 🍽 Restaurant | Full menu management with categories |
| 🛒 Food Ordering | Place/cancel orders, calculate totals |
| 💰 Billing | Generate invoices with 18% GST, print receipts |
| 👤 Employee Management | Add/update staff, sorted by salary |
| 📊 Reports | On-screen summary + CSV exports |
| 💾 Persistence | JSON save/load for all data |

---

## 🐍 Python Concepts Demonstrated

| Concept | Where |
|---|---|
| **Abstract Base Classes** (`abc.ABC`) | `models/room.py` — `Room` is abstract |
| **Inheritance & Polymorphism** | `DeluxeRoom`, `StandardRoom` override abstract methods |
| **Encapsulation** (name mangling `__`) | `Customer.__name`, `Employee.__salary`, `Bill.__total_amount` |
| **Decorators** | `@log_booking`, `@log_food_order`, `@log_bill` in `utils.py` |
| **Recursive Function** | `search_customer()` in `utils.py` |
| **Lambda Functions** | Sort rooms/employees/food by price/salary |
| **List Comprehension** | Available rooms, filtered orders |
| **Generator** | `generate_invoices()` yields one bill at a time |
| **Tuples** | `BASE_FACILITIES` in room classes |
| **Sets** | Unique room types, unique food categories |
| **Dictionaries** | Fast O(1) customer & room lookup |
| **`__str__` / `__repr__`** | Implemented in every class |
| **JSON File Handling** | `file_handler.py` — save/load all data |
| **CSV Reports** | Daily sales, room occupancy, employee reports |
| **Custom Exceptions** | `InvalidRoomNumber`, `RoomNotAvailable`, `InvalidCustomerID`, etc. |
| **datetime** | Timestamps on all bookings, orders, bills |

---

## 📁 Project Structure

```
DineStay/
├── main.py              # Entry point — 11-option while-loop menu
├── hotel.py             # Central Hotel class (Composition)
├── file_handler.py      # JSON save/load + CSV report generation
├── utils.py             # Decorators, recursion, lambdas, helpers
├── models/
│   ├── __init__.py
│   ├── room.py          # Abstract Room, DeluxeRoom, StandardRoom
│   ├── customer.py      # Customer with private fields
│   ├── employee.py      # Employee with private salary
│   ├── food.py          # FoodItem, Order
│   └── bill.py          # Bill, generate_invoices() generator
├── data/                # Auto-created — JSON data files
└── reports/             # Auto-created — CSV report files
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- No external packages required (uses only standard library)

### Run the Application

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/DineStay.git
cd DineStay

# Run
python main.py
```

### Startup Options
When launched, choose:
1. **Load saved data** — restores from previous session
2. **Start with demo data** — pre-loads 5 rooms, 3 customers, 4 employees, 10 menu items
3. **Start fresh** — empty system

---

## 📋 Main Menu

```
1.  Customer Management
2.  Room Management
3.  Room Booking
4.  Restaurant Management
5.  Food Ordering
6.  Billing Management
7.  Employee Management
8.  Generate Reports
9.  Save Data
10. Load Data
11. Exit
```

---

## 🏷 Sample Demo Data

| Room | Type | Price/Night |
|---|---|---|
| 101 | Deluxe | ₹4,500 |
| 102 | Deluxe | ₹5,000 |
| 201 | Standard | ₹2,000 |
| 202 | Standard | ₹2,200 |
| 203 | Standard | ₹1,800 |

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

*Built with ❤️ as a Python OOP student project.*
