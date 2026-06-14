"""
DineStay - Flask Web Application
app.py — Two-role authentication system

Roles:
  admin  → Full CRUD access (hardcoded credentials)
  user   → Read-only access (self-registered via /signup)

Decorators:
  @login_required  → any logged-in session (user OR admin)
  @admin_required  → admin session only
"""

import os
import sys
import io
import functools
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fix Windows console encoding for emoji/Unicode
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from datetime import datetime, timedelta
from typing import Optional
from flask import (Flask, render_template, request, redirect,
                   url_for, flash, session, jsonify, make_response)

sys.path.insert(0, os.path.dirname(__file__))

from hotel import Hotel
from models.room import InvalidRoomNumber, RoomNotAvailable
from models.customer import InvalidCustomerID
from models.food import FoodItem, InvalidOrderID
from models.bill import Bill, generate_invoices
import file_handler
import auth_handler

# ── Vercel /tmp storage ──
if os.environ.get("VERCEL"):
    file_handler.DATA_DIR    = "/tmp/dinestay_data"
    file_handler.REPORTS_DIR = "/tmp/dinestay_reports"
    auth_handler.USERS_FILE  = "/tmp/dinestay_data/users.json"
    auth_handler.ADMIN_FILE  = "/tmp/dinestay_data/admin.json"
    file_handler.EXPLORE_FILE = "/tmp/dinestay_data/explore.json"

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dinestay-ultra-secret-2024-xK9#mP")

# ── Session configuration ──────────────────────────────────────────────────
# Sessions are permanent by default — browser-close will NOT clear the session.
# Individual login routes set session.permanent = True/False based on Remember Me.
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)  # Remember Me: 30 days
app.config["SESSION_COOKIE_HTTPONLY"]    = True   # JS cannot read session cookie
app.config["SESSION_COOKIE_SAMESITE"]   = "Lax"  # CSRF protection
# Admin credentials are now managed dynamically via auth_handler



# ══════════════════════════════════════════════════════════
# AUTH HELPERS
# ══════════════════════════════════════════════════════════

def get_role() -> Optional[str]:
    """Return 'admin', 'user', or None (not logged in)."""
    return session.get("role")


def is_logged_in() -> bool:
    return session.get("role") in ("admin", "user")


def is_admin_session() -> bool:
    return session.get("role") == "admin"


def login_required(f):
    """Decorator: any logged-in user (admin OR regular user)."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not is_logged_in():
            flash("Please log in to continue.", "error")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Decorator: admin only. Regular users get an Access Denied page."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not is_logged_in():
            flash("Please log in to continue.", "error")
            return redirect(url_for("login", next=request.path))
        if not is_admin_session():
            flash("🚫 Access Denied — Admin privileges required.", "error")
            return redirect(url_for("access_denied"))
        return f(*args, **kwargs)
    return decorated


# ── Context processor: inject auth info into every template ──
@app.context_processor
def inject_auth():
    return dict(
        is_admin=is_admin_session(),
        is_logged=is_logged_in(),
        current_user=session.get("username", ""),
        current_role=session.get("role", ""),
    )


# ── In-memory Hotel instance ──
hotel = Hotel("DineStay")

# Try loading all data from files
file_handler.load_all(hotel)


def _seed_if_empty():
    if not hotel.rooms:
        hotel.add_room("Deluxe",   "101", 4500.00)
        hotel.add_room("Deluxe",   "102", 5000.00)
        hotel.add_room("Standard", "201", 2000.00)
        hotel.add_room("Standard", "202", 2200.00)
        hotel.add_room("Standard", "203", 1800.00)
    if not hotel.customers:
        hotel.register_customer("Arjun Sharma", "+91-9876543210", "arjun@email.com")
        hotel.register_customer("Priya Menon",  "+91-9123456780", "priya@email.com")
        hotel.register_customer("Rohan Verma",  "+91-9988776655", "rohan@email.com")
    if not hotel.employees:
        hotel.add_employee("Suresh Kumar", "Front Desk Manager", 45000, "Reception")
        hotel.add_employee("Anita Nair",   "Executive Chef",     60000, "Restaurant")
        hotel.add_employee("Deepak Singh", "Housekeeping Lead",  30000, "Housekeeping")
        hotel.add_employee("Kavya Reddy",  "Billing Manager",    40000, "Finance")
    if not hotel.menu:
        hotel.add_food_item("Masala Dosa",         "Breakfast",    120.00)
        hotel.add_food_item("Paneer Butter Masala", "Main Course", 280.00)
        hotel.add_food_item("Chicken Biryani",      "Main Course", 350.00)
        hotel.add_food_item("Veg Fried Rice",       "Main Course", 200.00)
        hotel.add_food_item("Mango Lassi",          "Beverages",    80.00)
        hotel.add_food_item("Masala Chai",          "Beverages",    40.00)
        hotel.add_food_item("Gulab Jamun",          "Desserts",    100.00)
        hotel.add_food_item("Ice Cream Sundae",     "Desserts",    150.00)
        hotel.add_food_item("Caesar Salad",         "Starters",    180.00)
        hotel.add_food_item("Garlic Bread",         "Starters",    120.00)

    # Seed initial transactions (bookings, orders, bills) to make it premium!
    if not hotel.bills and len(hotel.customers) >= 2 and len(hotel.rooms) >= 3:
        from datetime import timedelta
        today = datetime.now()
        
        # Book room 101 for Arjun (Customer 1)
        check_in_1 = today - timedelta(days=5)
        check_out_1 = today - timedelta(days=2)
        hotel.book_room(1, "101", check_in_1, check_out_1)
        hotel.checkout_room("101")  # Make it available again
        
        # Book room 201 for Priya (Customer 2)
        check_in_2 = today - timedelta(days=2)
        check_out_2 = today + timedelta(days=2)
        hotel.book_room(2, "201", check_in_2, check_out_2)
        
        # Place food orders
        # Arjun ordered Masala Dosa (ID 1, qty 2) and Mango Lassi (ID 5, qty 2)
        hotel.place_food_order(1, [(1, 2), (5, 2)])
        
        # Priya ordered Chicken Biryani (ID 3, qty 1) and Gulab Jamun (ID 7, qty 2)
        hotel.place_food_order(2, [(3, 1), (7, 2)])
        
        # Generate bills
        # Bill for Arjun (paid)
        bill1 = hotel.generate_bill(1, "101")
        bill1.mark_paid()
        
        # Bill for Priya (pending)
        hotel.generate_bill(2, "201")


if not hotel.rooms:
    _seed_if_empty()
    file_handler.save_all(hotel)
else:
    hotel.sync_id_counters()



# ══════════════════════════════════════════════════════════
# AUTH ROUTES  (Public — no decorator)
# ══════════════════════════════════════════════════════════

@app.route("/login", methods=["GET", "POST"])
def login():
    if is_logged_in():
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username   = request.form.get("username", "").strip()
        password   = request.form.get("password", "").strip()
        login_type = request.form.get("login_type", "user")  # "user" or "admin"
        remember   = request.form.get("remember_me") == "on"  # Remember Me checkbox

        if login_type == "admin":
            if auth_handler.verify_admin(username, password):
                session.permanent   = remember  # 30-day cookie if checked, session-only if not
                session["role"]     = "admin"
                session["username"] = auth_handler.get_admin_username()  # Always use stored name
                flash(f"✅ Welcome, Admin {session['username']}! Full access granted.", "success")
                return redirect(request.args.get("next") or url_for("dashboard"))
            else:
                flash("Incorrect admin credentials. Please try again.", "error")
        else:
            user = auth_handler.verify_user(username, password)
            if user:
                session.permanent       = remember
                session["role"]         = "user"
                session["username"]     = user["username"]
                session["display_name"] = user.get("display_name", username)
                flash(f"✅ Welcome back, {user.get('display_name', username)}!", "success")
                return redirect(request.args.get("next") or url_for("dashboard"))
            else:
                flash("Incorrect username or password. Please try again.", "error")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if is_logged_in():
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        display  = request.form.get("display_name", "").strip() or username.capitalize()
        password = request.form.get("password", "").strip()
        confirm  = request.form.get("confirm_password", "").strip()

        if password != confirm:
            flash("Passwords do not match.", "error")
        else:
            try:
                user = auth_handler.register_user(username, password)
                # Override display name if provided
                users = auth_handler.load_users()
                for u in users:
                    if u["username"] == username.strip().lower():
                        u["display_name"] = display
                auth_handler.save_users(users)

                flash(f"Account created! Welcome, {display}. Please log in.", "success")
                return redirect(url_for("login"))
            except ValueError as e:
                flash(str(e), "error")

    return render_template("signup.html")


@app.route("/logout")
def logout():
    name = session.get("display_name") or session.get("username", "")
    session.clear()
    flash(f"Goodbye, {name}! You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/access-denied")
@login_required
def access_denied():
    return render_template("access_denied.html")


# ══════════════════════════════════════════════════════════
# DASHBOARD  — any logged-in user
# ══════════════════════════════════════════════════════════

@app.route("/")
@login_required
def dashboard():
    available  = [r for r in hotel.rooms if r.availability_status]
    booked     = [r for r in hotel.rooms if not r.availability_status]
    paid_bills = [b for b in hotel.bills if b.is_paid]
    revenue    = sum(b.total_amount for b in paid_bills)
    from models.room import Room
    from models.food import FoodItem as FI
    return render_template("dashboard.html",
        total_rooms=len(hotel.rooms),
        available_rooms=len(available),
        booked_rooms=len(booked),
        total_customers=len(hotel.customers),
        total_employees=len(hotel.employees),
        total_orders=len(hotel.orders),
        total_bills=len(hotel.bills),
        revenue=revenue,
        recent_customers=hotel.customers[-5:][::-1],
        recent_orders=hotel.orders[-5:][::-1],
        room_types=list(Room.get_unique_room_types()),
        food_categories=list(FI.get_all_categories()),
        rooms=hotel.rooms
    )


# ══════════════════════════════════════════════════════════
# CUSTOMERS
# View → any user | Add/Edit → admin only
# ══════════════════════════════════════════════════════════

@app.route("/customers")
@admin_required
def customers():
    return render_template("customers.html", customers=hotel.customers)


@app.route("/customers/add", methods=["GET", "POST"])
@admin_required
def add_customer():
    if request.method == "POST":
        name  = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        if not name or not phone or not email:
            flash("All fields are required.", "error")
        else:
            try:
                hotel.register_customer(name, phone, email)
                file_handler.save_all(hotel)
                flash(f"Customer '{name}' registered!", "success")
                return redirect(url_for("customers"))
            except Exception as e:
                flash(str(e), "error")
    return render_template("customer_form.html", action="Add", customer=None)


@app.route("/customers/<int:cid>/edit", methods=["GET", "POST"])
@admin_required
def edit_customer(cid):
    try:
        customer = hotel.get_customer(cid)
    except InvalidCustomerID as e:
        flash(str(e), "error")
        return redirect(url_for("customers"))
    if request.method == "POST":
        name  = request.form.get("name", "").strip() or None
        phone = request.form.get("phone", "").strip() or None
        email = request.form.get("email", "").strip() or None
        customer.update_details(name=name, phone=phone, email=email)
        file_handler.save_all(hotel)
        flash("Customer updated!", "success")
        return redirect(url_for("customers"))
    return render_template("customer_form.html", action="Edit", customer=customer)


@app.route("/customers/<int:cid>/history")
@admin_required
def customer_history(cid):
    try:
        customer = hotel.get_customer(cid)
    except InvalidCustomerID as e:
        flash(str(e), "error")
        return redirect(url_for("customers"))
    return render_template("customer_history.html", customer=customer)


# ══════════════════════════════════════════════════════════
# ROOMS
# View → any user | Add/Checkout → admin only
# ══════════════════════════════════════════════════════════

@app.route("/rooms")
@login_required
def rooms():
    sorted_rooms = sorted(hotel.rooms, key=lambda r: r.room_price)
    from models.room import Room
    return render_template("rooms.html", rooms=sorted_rooms,
                           room_types=Room.get_unique_room_types())


@app.route("/rooms/add", methods=["GET", "POST"])
@admin_required
def add_room():
    if request.method == "POST":
        room_type   = request.form.get("room_type", "Standard")
        room_number = request.form.get("room_number", "").strip()
        try:
            room_price = float(request.form.get("room_price", 0))
        except ValueError:
            flash("Invalid price.", "error")
            return render_template("room_form.html")
        try:
            hotel.add_room(room_type, room_number, room_price)
            file_handler.save_all(hotel)
            flash(f"{room_type} Room '{room_number}' added!", "success")
            return redirect(url_for("rooms"))
        except (InvalidRoomNumber, ValueError) as e:
            flash(str(e), "error")
    return render_template("room_form.html")


@app.route("/rooms/<room_number>/details")
@login_required
def room_details(room_number):
    room = hotel._room_dict.get(room_number)
    if not room:
        flash(f"Room '{room_number}' not found.", "error")
        return redirect(url_for("rooms"))
    return render_template("room_details.html", room=room)


@app.route("/rooms/<room_number>/checkout", methods=["POST"])
@admin_required
def checkout_room(room_number):
    try:
        hotel.checkout_room(room_number)
        file_handler.save_all(hotel)
        flash(f"Room '{room_number}' checked out!", "success")
    except (InvalidRoomNumber, Exception) as e:
        flash(str(e), "error")
    return redirect(url_for("rooms"))


# ══════════════════════════════════════════════════════════
# BOOKING  — admin only
# ══════════════════════════════════════════════════════════

@app.route("/booking", methods=["GET", "POST"])
@admin_required
def booking():
    available_rooms = hotel.get_available_rooms()
    sorted_rooms = sorted(available_rooms, key=lambda r: r.room_price)
    if request.method == "POST":
        try:
            cid         = int(request.form.get("customer_id", 0))
            room_number = request.form.get("room_number", "").strip()
            check_in    = datetime.strptime(request.form.get("check_in"), "%Y-%m-%d")
            check_out   = datetime.strptime(request.form.get("check_out"), "%Y-%m-%d")
            hotel.book_room(cid, room_number, check_in, check_out)
            file_handler.save_all(hotel)
            nights = (check_out - check_in).days
            flash(f"Room '{room_number}' booked for {nights} night(s)!", "success")
            return redirect(url_for("rooms"))
        except (InvalidCustomerID, InvalidRoomNumber,
                RoomNotAvailable, ValueError) as e:
            flash(str(e), "error")
    return render_template("booking.html",
                           rooms=sorted_rooms,
                           customers=hotel.customers)


# ══════════════════════════════════════════════════════════
# MENU
# View → any user | Add/Edit price → admin only
# ══════════════════════════════════════════════════════════

@app.route("/menu")
@login_required
def menu():
    sorted_menu = sorted(hotel.menu, key=lambda f: f.price)
    from models.food import FoodItem as FI
    return render_template("menu.html", menu=sorted_menu,
                           categories=FI.get_all_categories())


@app.route("/menu/add", methods=["GET", "POST"])
@admin_required
def add_food():
    if request.method == "POST":
        food_name = request.form.get("food_name", "").strip()
        category  = request.form.get("category", "").strip()
        try:
            price = float(request.form.get("price", 0))
        except ValueError:
            flash("Invalid price.", "error")
            return render_template("food_form.html", item=None)
        if not food_name or not category:
            flash("All fields required.", "error")
        else:
            hotel.add_food_item(food_name, category, price)
            file_handler.save_all(hotel)
            flash(f"'{food_name}' added to menu!", "success")
            return redirect(url_for("menu"))
    return render_template("food_form.html", item=None)


@app.route("/menu/<int:fid>/edit", methods=["GET", "POST"])
@admin_required
def edit_food(fid):
    item = next((f for f in hotel.menu if f.food_id == fid), None)
    if not item:
        flash("Food item not found.", "error")
        return redirect(url_for("menu"))
    if request.method == "POST":
        try:
            new_price = float(request.form.get("price", 0))
            item.update_price(new_price)
            file_handler.save_all(hotel)
            flash("Price updated!", "success")
            return redirect(url_for("menu"))
        except ValueError as e:
            flash(str(e), "error")
    return render_template("food_form.html", item=item)


# ══════════════════════════════════════════════════════════
# ORDERS
# View → any user | Place/Cancel → admin only
# ══════════════════════════════════════════════════════════

@app.route("/orders")
@admin_required
def orders():
    sorted_orders = sorted(hotel.orders,
                           key=lambda o: o.order_time, reverse=True)
    return render_template("orders.html", orders=sorted_orders)


@app.route("/orders/place", methods=["GET", "POST"])
@admin_required
def place_order():
    if request.method == "POST":
        try:
            cid = int(request.form.get("customer_id", 0))
            items = []
            for item in hotel.menu:
                qty_str = request.form.get(f"qty_{item.food_id}", "0")
                try:
                    qty = int(qty_str)
                except ValueError:
                    qty = 0
                if qty > 0:
                    items.append((item.food_id, qty))
            if not items:
                flash("Please select at least one item.", "error")
            else:
                order = hotel.place_food_order(cid, items)
                file_handler.save_all(hotel)
                flash(f"Order #{order.order_id} placed! Total: ₹{order.total_amount:.2f}", "success")
                return redirect(url_for("orders"))
        except (InvalidCustomerID, InvalidOrderID, ValueError) as e:
            flash(str(e), "error")
    sorted_menu = sorted(hotel.menu, key=lambda f: f.price)
    from models.food import FoodItem as FI
    return render_template("place_order.html",
                           customers=hotel.customers,
                           menu=sorted_menu,
                           categories=FI.get_all_categories())


@app.route("/orders/<int:oid>/cancel", methods=["POST"])
@admin_required
def cancel_order(oid):
    order = next((o for o in hotel.orders if o.order_id == oid), None)
    if order:
        order.cancel_order()
        file_handler.save_all(hotel)
        flash(f"Order #{oid} cancelled.", "success")
    else:
        flash(f"Order #{oid} not found.", "error")
    return redirect(url_for("orders"))


# ══════════════════════════════════════════════════════════
# BILLING
# View → any user | Generate/Mark Paid → admin only
# ══════════════════════════════════════════════════════════

@app.route("/billing")
@admin_required
def billing():
    sorted_bills = sorted(hotel.bills,
                          key=lambda b: b.generated_on, reverse=True)
    return render_template("billing.html", bills=sorted_bills)


@app.route("/billing/generate", methods=["GET", "POST"])
@admin_required
def generate_bill():
    if request.method == "POST":
        try:
            cid         = int(request.form.get("customer_id", 0))
            room_number = request.form.get("room_number", "").strip() or None
            bill = hotel.generate_bill(cid, room_number)
            file_handler.save_all(hotel)
            flash(f"Bill #{bill.bill_id} generated! Total: ₹{bill.total_amount:.2f}", "success")
            return redirect(url_for("view_bill", bid=bill.bill_id))
        except (InvalidCustomerID, Exception) as e:
            flash(str(e), "error")
    return render_template("generate_bill.html",
                           customers=hotel.customers,
                           rooms=hotel.rooms)


@app.route("/billing/<int:bid>")
@admin_required
def view_bill(bid):
    bill = next((b for b in hotel.bills if b.bill_id == bid), None)
    if not bill:
        flash(f"Bill #{bid} not found.", "error")
        return redirect(url_for("billing"))
    customer = hotel._customer_dict.get(bill.customer_id)
    return render_template("invoice.html", bill=bill, customer=customer)


@app.route("/billing/<int:bid>/pay", methods=["POST"])
@admin_required
def mark_paid(bid):
    bill = next((b for b in hotel.bills if b.bill_id == bid), None)
    if bill:
        bill.mark_paid()
        file_handler.save_all(hotel)
        flash(f"Bill #{bid} marked as paid!", "success")
    else:
        flash("Bill not found.", "error")
    return redirect(url_for("billing"))


# ══════════════════════════════════════════════════════════
# EMPLOYEES
# View → any user | Add/Edit → admin only
# ══════════════════════════════════════════════════════════

@app.route("/employees")
@admin_required
def employees():
    sorted_emps = sorted(hotel.employees, key=lambda e: e.salary, reverse=True)
    return render_template("employees.html", employees=sorted_emps)


@app.route("/employees/add", methods=["GET", "POST"])
@admin_required
def add_employee():
    if request.method == "POST":
        name        = request.form.get("name", "").strip()
        designation = request.form.get("designation", "").strip()
        department  = request.form.get("department", "").strip()
        try:
            salary = float(request.form.get("salary", 0))
        except ValueError:
            flash("Invalid salary.", "error")
            return render_template("employee_form.html", emp=None)
        if not name or not designation or not department:
            flash("All fields required.", "error")
        else:
            hotel.add_employee(name, designation, salary, department)
            file_handler.save_all(hotel)
            flash(f"Employee '{name}' added!", "success")
            return redirect(url_for("employees"))
    return render_template("employee_form.html", emp=None)


@app.route("/employees/<int:eid>/edit", methods=["GET", "POST"])
@admin_required
def edit_employee(eid):
    emp = next((e for e in hotel.employees if e.employee_id == eid), None)
    if not emp:
        flash("Employee not found.", "error")
        return redirect(url_for("employees"))
    if request.method == "POST":
        name        = request.form.get("name", "").strip() or None
        designation = request.form.get("designation", "").strip() or None
        department  = request.form.get("department", "").strip() or None
        sal_str     = request.form.get("salary", "").strip()
        salary = float(sal_str) if sal_str else None
        try:
            emp.update_employee(name=name, designation=designation,
                                salary=salary, department=department)
            file_handler.save_all(hotel)
            flash("Employee updated!", "success")
            return redirect(url_for("employees"))
        except ValueError as e:
            flash(str(e), "error")
    return render_template("employee_form.html", emp=emp)


# ── Image URL helpers ──────────────────────────────────────────────────
# Each key maps a food/room/person name to a reliable, correctly-matched Unsplash URL.
# Using fixed Unsplash photo IDs (not random) so images are always consistent.

_FOOD_IMAGE_URLS = {
    # ─ Beverages ─
    "Masala Chai": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=600&q=80",
    "Mango Lassi": "https://images.unsplash.com/photo-1625944525533-473f1a3d54e7?w=600&q=80",
    # ─ Breakfast ─
    "Masala Dosa": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=600&q=80",
    # ─ Main Course ─
    "Paneer Butter Masala": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=600&q=80",
    "Chicken Biryani": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600&q=80",
    "Veg Fried Rice": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=600&q=80",
    # ─ Starters ─
    "Caesar Salad": "https://images.unsplash.com/photo-1546793665-c74683f339c1?w=600&q=80",
    "Garlic Bread": "https://images.unsplash.com/photo-1619531040576-f9416740661b?w=600&q=80",
    # ─ Desserts ─
    "Gulab Jamun": "https://images.unsplash.com/photo-1666113836546-7b5e2f0d1aff?w=600&q=80",
    "Ice Cream Sundae": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=600&q=80",
}

_ROOM_IMAGE_URLS = {
    "Deluxe":   "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800&q=80",
    "Standard": "https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=800&q=80",
    "Suite":    "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800&q=80",
    "Presidential": "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800&q=80",
}

_DEFAULT_ROOM_IMG    = "https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=800&q=80"
_DEFAULT_FOOD_IMG    = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600&q=80"

_EMP_IMAGE_URLS = {
    "Suresh Kumar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&q=80",
    "Anita Nair":   "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=300&q=80",
    "Deepak Singh": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=300&q=80",
    "Kavya Reddy":  "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=300&q=80",
}
_DEFAULT_EMP_IMG = "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=300&q=80"


# ── Context processor: inject visual asset mapping into every template ──
@app.context_processor
def inject_food_metadata():
    food_details = {
        "Masala Dosa": {
            "description": "Crispy rice-lentil crepe stuffed with spiced potato mash, served with fresh coconut chutney and hot sambar.",
            "is_veg": True,
            "rating": 4.7,
            "popularity": "Must Try",
            "best_seller": True,
            "image": _FOOD_IMAGE_URLS["Masala Dosa"],
        },
        "Paneer Butter Masala": {
            "description": "Creamy, rich and mildly sweet gravy made of butter, tomatoes, cashews, and soft melt-in-mouth paneer cubes.",
            "is_veg": True,
            "rating": 4.8,
            "popularity": "Best Seller",
            "best_seller": True,
            "image": _FOOD_IMAGE_URLS["Paneer Butter Masala"],
        },
        "Chicken Biryani": {
            "description": "Fragrant long-grain basmati rice layered with tender marinated chicken, exotic ground spices, and pure saffron.",
            "is_veg": False,
            "rating": 4.9,
            "popularity": "Top Rated",
            "best_seller": True,
            "image": _FOOD_IMAGE_URLS["Chicken Biryani"],
        },
        "Veg Fried Rice": {
            "description": "Flavorful stir-fried rice tossed with chopped garden vegetables, light soy sauce, green onions, and garlic pepper.",
            "is_veg": True,
            "rating": 4.4,
            "popularity": "Classic",
            "best_seller": False,
            "image": _FOOD_IMAGE_URLS["Veg Fried Rice"],
        },
        "Mango Lassi": {
            "description": "Thick, creamy yogurt drink blended with sweet Alphonso mango pulp, sugar, and a dash of ground cardamom.",
            "is_veg": True,
            "rating": 4.6,
            "popularity": "Must Try",
            "best_seller": True,
            "image": _FOOD_IMAGE_URLS["Mango Lassi"],
        },
        "Masala Chai": {
            "description": "Brewed black tea leaves simmered with whole milk, crushed ginger, cardamom pods, cinnamon, and spices.",
            "is_veg": True,
            "rating": 4.7,
            "popularity": "Popular Choice",
            "best_seller": False,
            "image": _FOOD_IMAGE_URLS["Masala Chai"],
        },
        "Gulab Jamun": {
            "description": "Soft milk-solid round balls deep-fried to golden brown, soaked in hot sugar syrup infused with rose water.",
            "is_veg": True,
            "rating": 4.8,
            "popularity": "Sweet Delight",
            "best_seller": True,
            "image": _FOOD_IMAGE_URLS["Gulab Jamun"],
        },
        "Ice Cream Sundae": {
            "description": "Scoops of premium double chocolate and vanilla ice cream loaded with hot chocolate fudge, nuts, and a cherry.",
            "is_veg": True,
            "rating": 4.5,
            "popularity": "Popular",
            "best_seller": False,
            "image": _FOOD_IMAGE_URLS["Ice Cream Sundae"],
        },
        "Caesar Salad": {
            "description": "Crisp green romaine lettuce tossed with creamy Caesar sauce dressing, toasted garlic croutons, and parmesan cheese shavings.",
            "is_veg": True,
            "rating": 4.3,
            "popularity": "Fresh & Healthy",
            "best_seller": False,
            "image": _FOOD_IMAGE_URLS["Caesar Salad"],
        },
        "Garlic Bread": {
            "description": "Toasted baguette slices smothered with aromatic fresh garlic butter, parsley herb flakes, and gooey melted mozzarella.",
            "is_veg": True,
            "rating": 4.5,
            "popularity": "Crispy Starter",
            "best_seller": False,
            "image": _FOOD_IMAGE_URLS["Garlic Bread"],
        },
    }

    emp_details = {
        "Suresh Kumar": {"image": _EMP_IMAGE_URLS["Suresh Kumar"], "phone": "+91 98765 43210", "email": "suresh@dinestay.com"},
        "Anita Nair":   {"image": _EMP_IMAGE_URLS["Anita Nair"],   "phone": "+91 91234 56780", "email": "anita@dinestay.com"},
        "Deepak Singh": {"image": _EMP_IMAGE_URLS["Deepak Singh"], "phone": "+91 99887 76655", "email": "deepak@dinestay.com"},
        "Kavya Reddy":  {"image": _EMP_IMAGE_URLS["Kavya Reddy"],  "phone": "+91 97766 55443", "email": "kavya@dinestay.com"},
    }

    room_details = {
        "Deluxe": {
            "image": _ROOM_IMAGE_URLS["Deluxe"],
            "description": "Premium luxury suite featuring smart controls, ocean/city views, and premium mini-bars.",
        },
        "Standard": {
            "image": _ROOM_IMAGE_URLS["Standard"],
            "description": "Cozy room with dedicated workspace, high-definition entertainment, and clean layout.",
        },
        "Suite": {
            "image": _ROOM_IMAGE_URLS["Suite"],
            "description": "Expansive suite with separate living area, panoramic views, and butler service.",
        },
        "Presidential": {
            "image": _ROOM_IMAGE_URLS["Presidential"],
            "description": "The pinnacle of luxury — private terrace, jacuzzi, personal chef, and 24/7 concierge.",
        },
    }

    return dict(
        food_details=food_details,
        emp_details=emp_details,
        room_details=room_details,
        food_image_urls=_FOOD_IMAGE_URLS,
        room_image_urls=_ROOM_IMAGE_URLS,
        default_food_img=_DEFAULT_FOOD_IMG,
        default_room_img=_DEFAULT_ROOM_IMG,
        default_emp_img=_DEFAULT_EMP_IMG,
        emp_image_urls=_EMP_IMAGE_URLS,
    )


# ── Report Export Endpoints (CSV & Print PDF) ──
@app.route("/reports/export/<report_type>")
@admin_required
def export_report(report_type):
    import csv
    import io
    from flask import Response
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    filename = f"dinestay_{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    if report_type == "revenue":
        writer.writerow(["Bill ID", "Customer ID", "Customer Name", "Room Charges (INR)", "Food Charges (INR)", "GST (INR)", "Total Amount (INR)", "Status", "Date"])
        paid_bills = [b for b in hotel.bills if b.is_paid]
        for b in paid_bills:
            writer.writerow([b.bill_id, b.customer_id, b.customer_name, b.room_charges, b.food_charges, b.tax, b.total_amount, "Paid", b.generated_on.strftime("%d-%m-%Y")])
    elif report_type == "bookings":
        writer.writerow(["Room Number", "Room Type", "Price (INR/night)", "Status", "Booked By (Cust ID)", "Check-In", "Check-Out"])
        for r in hotel.rooms:
            status = "Available" if r.availability_status else "Booked"
            booked_by = r.booked_by or "—"
            check_in = r.check_in_date.strftime("%d-%m-%Y") if r.check_in_date else "—"
            check_out = r.check_out_date.strftime("%d-%m-%Y") if r.check_out_date else "—"
            writer.writerow([r.room_number, r.room_type, r.room_price, status, booked_by, check_in, check_out])
    elif report_type == "customers":
        writer.writerow(["Customer ID", "Name", "Phone", "Email", "Registered On", "Total Bookings"])
        for c in hotel.customers:
            writer.writerow([c.customer_id, c.name, c.phone, c.email, c.registered_on.strftime("%d-%m-%Y"), len(c.booking_history)])
    elif report_type == "occupancy":
        writer.writerow(["Room Number", "Room Type", "Price (INR/night)", "Occupancy Status"])
        for r in hotel.rooms:
            status = "Vacant" if r.availability_status else "Occupied"
            writer.writerow([r.room_number, r.room_type, r.room_price, status])
    elif report_type == "orders":
        writer.writerow(["Order ID", "Customer ID", "Items Ordered", "Total Amount (INR)", "Status", "Time"])
        for o in hotel.orders:
            items_str = ", ".join([f"{fi.food_name} x{qty}" for fi, qty in o.ordered_items])
            writer.writerow([o.order_id, o.customer_id, items_str, o.total_amount, o.order_status, o.order_time.strftime("%d-%m-%Y %H:%M")])
    else:
        flash("Invalid report type.", "error")
        return redirect(url_for("reports"))
        
    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


@app.route("/reports/print/<report_type>")
@admin_required
def print_report(report_type):
    available = [r for r in hotel.rooms if r.availability_status]
    booked    = [r for r in hotel.rooms if not r.availability_status]
    paid_bills   = [b for b in hotel.bills if b.is_paid]
    unpaid_bills = [b for b in hotel.bills if not b.is_paid]
    revenue      = sum(b.total_amount for b in paid_bills)
    food_revenue = sum(b.food_charges for b in paid_bills)
    room_revenue = sum(b.room_charges for b in paid_bills)
    confirmed_orders = [o for o in hotel.orders if o.order_status == "Confirmed"]
    
    return render_template("report_print.html",
        report_type=report_type,
        hotel=hotel,
        available_rooms=available,
        booked_rooms=booked,
        paid_bills=paid_bills,
        unpaid_bills=unpaid_bills,
        revenue=revenue,
        food_revenue=food_revenue,
        room_revenue=room_revenue,
        confirmed_orders=confirmed_orders,
        datetime=datetime
    )


# ══════════════════════════════════════════════════════════
# REPORTS  — any logged-in user
# ══════════════════════════════════════════════════════════

@app.route("/reports")
@admin_required
def reports():
    available = [r for r in hotel.rooms if r.availability_status]
    booked    = [r for r in hotel.rooms if not r.availability_status]
    paid_bills   = [b for b in hotel.bills if b.is_paid]
    unpaid_bills = [b for b in hotel.bills if not b.is_paid]
    revenue      = sum(b.total_amount for b in paid_bills)
    food_revenue = sum(b.food_charges for b in paid_bills)
    room_revenue = sum(b.room_charges for b in paid_bills)
    confirmed_orders = [o for o in hotel.orders if o.order_status == "Confirmed"]
    return render_template("reports.html",
        hotel=hotel,
        available_rooms=available,
        booked_rooms=booked,
        paid_bills=paid_bills,
        unpaid_bills=unpaid_bills,
        revenue=revenue,
        food_revenue=food_revenue,
        room_revenue=room_revenue,
        confirmed_orders=confirmed_orders,
    )


# ── Admin: view all registered users ──
@app.route("/admin/users")
@admin_required
def admin_users():
    users = auth_handler.get_all_users()
    return render_template("admin_users.html", users=users)


# ── Admin: delete a registered user ──
@app.route("/admin/users/<username>/delete", methods=["POST"])
@admin_required
def delete_user(username):
    deleted = auth_handler.delete_user(username)
    if deleted:
        flash(f"✅ User '{username}' has been removed.", "success")
    else:
        flash(f"❌ User '{username}' not found.", "error")
    return redirect(url_for("admin_users"))


# ── Regular user: change own password ──
@app.route("/profile", methods=["GET", "POST"])
@login_required
def user_profile():
    if is_admin_session():
        return redirect(url_for("admin_profile"))

    if request.method == "POST":
        old_password = request.form.get("old_password", "").strip()
        new_password = request.form.get("new_password", "").strip()
        confirm      = request.form.get("confirm_password", "").strip()

        if not old_password:
            flash("⚠️ Please enter your current password.", "error")
        elif new_password != confirm:
            flash("❌ New passwords do not match.", "error")
        else:
            try:
                auth_handler.change_user_password(
                    session["username"], old_password, new_password
                )
                flash("✅ Password changed successfully! Please log in again.", "success")
                session.clear()
                return redirect(url_for("login"))
            except ValueError as e:
                flash(f"❌ {e}", "error")

    return render_template("user_profile.html")


# ── Admin Settings: Profile Update ──
@app.route("/admin/profile", methods=["GET", "POST"])
@admin_required
def admin_profile():
    creds = auth_handler.load_admin_credentials()
    if request.method == "POST":
        action           = request.form.get("action", "update")  # "update" or "change_password"
        old_password     = request.form.get("old_password", "").strip()
        new_username     = request.form.get("username", "").strip()
        new_password     = request.form.get("new_password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        # ── Validate: old password is ALWAYS required ────────────────────────
        if not old_password:
            flash("⚠️ Please enter your current password to make any changes.", "error")
        elif not auth_handler.verify_admin_password(old_password):
            flash("❌ Current password is incorrect. No changes were saved.", "error")
        elif action == "change_password":
            # ── Password change only ─────────────────────────────────────────
            if not new_password:
                flash("⚠️ Please enter a new password.", "error")
            elif new_password != confirm_password:
                flash("❌ New passwords do not match.", "error")
            else:
                try:
                    auth_handler.change_admin_password(old_password, new_password)
                    flash("✅ Password changed successfully! Please log in again.", "success")
                    session.clear()  # Force re-login with new password
                    return redirect(url_for("login"))
                except ValueError as e:
                    flash(f"❌ {e}", "error")
        else:
            # ── Username (and optionally password) change ─────────────────────
            if not new_username:
                flash("⚠️ Username cannot be empty.", "error")
            elif new_password and new_password != confirm_password:
                flash("❌ New passwords do not match.", "error")
            else:
                try:
                    auth_handler.update_admin_credentials(
                        new_username,
                        new_password if new_password else None,
                        old_password=old_password,
                        require_old_password=True,
                    )
                    # Keep session in sync with new username
                    session["username"] = new_username
                    session.modified = True
                    flash("✅ Admin profile updated successfully! Changes are saved permanently.", "success")
                    return redirect(url_for("admin_profile"))
                except ValueError as e:
                    flash(f"❌ {e}", "error")

    return render_template("admin_profile.html", admin_username=creds["username"])


# ══════════════════════════════════════════════════════════
# EXPLORE INDIA MODULE
# ══════════════════════════════════════════════════════════

@app.route("/explore")
@login_required
def explore():
    locations = file_handler.load_explore_data()
    return render_template("explore.html", locations=locations)


@app.route("/explore/<int:loc_id>")
@login_required
def explore_detail(loc_id):
    locations = file_handler.load_explore_data()
    location = next((l for l in locations if l["location_id"] == loc_id), None)
    if not location:
        flash("Location not found.", "error")
        return redirect(url_for("explore"))
    return render_template("explore_detail.html", location=location)


@app.route("/admin/explore/add", methods=["GET", "POST"])
@admin_required
def explore_add():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        city = request.form.get("city", "").strip()
        tier = request.form.get("tier", "Premium").strip()
        price_range = request.form.get("price_range", "").strip()
        description = request.form.get("description", "").strip()
        restaurant_name = request.form.get("restaurant_name", "").strip()
        restaurant_description = request.form.get("restaurant_description", "").strip()
        room_ambience = request.form.get("room_ambience", "").strip()
        facilities_raw = request.form.get("facilities", "").strip()
        facilities = [f.strip() for f in facilities_raw.split(",") if f.strip()]

        rating_val = request.form.get("rating", "4.5").strip()
        try:
            rating = float(rating_val)
        except ValueError:
            rating = 4.5
        cuisine = request.form.get("cuisine", "").strip()
        avg_price = request.form.get("avg_price", "").strip()
        branches_raw = request.form.get("branches", "").strip()
        branches = [b.strip() for b in branches_raw.split(",") if b.strip()]

        if not name or not city or not description:
            flash("Name, City, and Description are required.", "error")
        else:
            locations = file_handler.load_explore_data()
            new_id = max((l["location_id"] for l in locations), default=0) + 1
            new_loc = {
                "location_id": new_id,
                "name": name,
                "city": city,
                "image": "explore_jaipur.png", # Fallback default image
                "restaurant_image": "rest_jaipur.png", # Fallback default restaurant image
                "tier": tier,
                "price_range": price_range,
                "description": description,
                "restaurant_name": restaurant_name,
                "restaurant_description": restaurant_description,
                "room_ambience": room_ambience,
                "facilities": facilities,
                "rating": rating,
                "cuisine": cuisine,
                "avg_price": avg_price,
                "branches": branches,
                "popular_dishes": [
                    {"name": "Paneer Tikka Platter", "image": "food_paneer.png", "price": "₹250"},
                    {"name": "Classic Chicken Kebab", "image": "food_chicken.png", "price": "₹320"},
                    {"name": "Garlic Butter Fish", "image": "food_fish.png", "price": "₹420"},
                    {"name": "Chocolate Brownie Sundae", "image": "food_dessert.png", "price": "₹180"}
                ],
                "events": []
            }
            locations.append(new_loc)
            file_handler.save_explore_data(locations)
            flash(f"Destination '{name}' added successfully!", "success")
            return redirect(url_for("explore"))

    return render_template("explore_form.html", action="Add", location=None, facilities_str="", branches_str="")


@app.route("/admin/explore/<int:loc_id>/edit", methods=["GET", "POST"])
@admin_required
def explore_edit(loc_id):
    locations = file_handler.load_explore_data()
    location = next((l for l in locations if l["location_id"] == loc_id), None)
    if not location:
        flash("Location not found.", "error")
        return redirect(url_for("explore"))

    if request.method == "POST":
        location["name"] = request.form.get("name", "").strip()
        location["city"] = request.form.get("city", "").strip()
        location["tier"] = request.form.get("tier", "Premium").strip()
        location["price_range"] = request.form.get("price_range", "").strip()
        location["description"] = request.form.get("description", "").strip()
        location["restaurant_name"] = request.form.get("restaurant_name", "").strip()
        location["restaurant_description"] = request.form.get("restaurant_description", "").strip()
        location["room_ambience"] = request.form.get("room_ambience", "").strip()
        facilities_raw = request.form.get("facilities", "").strip()
        location["facilities"] = [f.strip() for f in facilities_raw.split(",") if f.strip()]

        rating_val = request.form.get("rating", "4.5").strip()
        try:
            location["rating"] = float(rating_val)
        except ValueError:
            location["rating"] = 4.5
        location["cuisine"] = request.form.get("cuisine", "").strip()
        location["avg_price"] = request.form.get("avg_price", "").strip()
        branches_raw = request.form.get("branches", "").strip()
        location["branches"] = [b.strip() for b in branches_raw.split(",") if b.strip()]

        # Ensure fallback images and dishes exist if not present in the loaded JSON object
        if "restaurant_image" not in location:
            location["restaurant_image"] = "rest_jaipur.png"
        if "popular_dishes" not in location:
            location["popular_dishes"] = [
                {"name": "Paneer Tikka Platter", "image": "food_paneer.png", "price": "₹250"},
                {"name": "Classic Chicken Kebab", "image": "food_chicken.png", "price": "₹320"},
                {"name": "Garlic Butter Fish", "image": "food_fish.png", "price": "₹420"},
                {"name": "Chocolate Brownie Sundae", "image": "food_dessert.png", "price": "₹180"}
            ]

        if not location["name"] or not location["city"] or not location["description"]:
            flash("Name, City, and Description are required.", "error")
        else:
            file_handler.save_explore_data(locations)
            flash(f"Destination '{location['name']}' updated successfully!", "success")
            return redirect(url_for("explore_detail", loc_id=loc_id))

    # Convert lists back to comma separated strings for form
    facilities_str = ", ".join(location.get("facilities", []))
    branches_str = ", ".join(location.get("branches", []))
    return render_template("explore_form.html", action="Edit", location=location, facilities_str=facilities_str, branches_str=branches_str)


@app.route("/admin/explore/<int:loc_id>/delete", methods=["POST"])
@admin_required
def explore_delete(loc_id):
    locations = file_handler.load_explore_data()
    location = next((l for l in locations if l["location_id"] == loc_id), None)
    if not location:
        flash("Location not found.", "error")
    else:
        locations.remove(location)
        file_handler.save_explore_data(locations)
        flash("Destination deleted successfully.", "success")
    return redirect(url_for("explore"))


@app.route("/admin/explore/<int:loc_id>/events/add", methods=["GET", "POST"])
@admin_required
def explore_event_add(loc_id):
    locations = file_handler.load_explore_data()
    location = next((l for l in locations if l["location_id"] == loc_id), None)
    if not location:
        flash("Location not found.", "error")
        return redirect(url_for("explore"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        date_str = request.form.get("date", "").strip()
        time_str = request.form.get("time", "").strip()
        venue = request.form.get("venue", "").strip()
        description = request.form.get("description", "").strip()

        if not title or not date_str or not venue:
            flash("Title, Date, and Venue are required.", "error")
        else:
            events = location.setdefault("events", [])
            new_ev_id = max((e["event_id"] for e in events), default=0) + 1
            new_event = {
                "event_id": new_ev_id,
                "title": title,
                "date": date_str,
                "time": time_str,
                "venue": venue,
                "description": description
            }
            events.append(new_event)
            file_handler.save_explore_data(locations)
            flash("Event added successfully!", "success")
            return redirect(url_for("explore_detail", loc_id=loc_id))

    return render_template("explore_event_form.html", action="Add", location=location, event=None)


@app.route("/admin/explore/<int:loc_id>/events/<int:ev_id>/edit", methods=["GET", "POST"])
@admin_required
def explore_event_edit(loc_id, ev_id):
    locations = file_handler.load_explore_data()
    location = next((l for l in locations if l["location_id"] == loc_id), None)
    if not location:
        flash("Location not found.", "error")
        return redirect(url_for("explore"))

    event = next((e for e in location.get("events", []) if e["event_id"] == ev_id), None)
    if not event:
        flash("Event not found.", "error")
        return redirect(url_for("explore_detail", loc_id=loc_id))

    if request.method == "POST":
        event["title"] = request.form.get("title", "").strip()
        event["date"] = request.form.get("date", "").strip()
        event["time"] = request.form.get("time", "").strip()
        event["venue"] = request.form.get("venue", "").strip()
        event["description"] = request.form.get("description", "").strip()

        if not event["title"] or not event["date"] or not event["venue"]:
            flash("Title, Date, and Venue are required.", "error")
        else:
            file_handler.save_explore_data(locations)
            flash("Event updated successfully!", "success")
            return redirect(url_for("explore_detail", loc_id=loc_id))

    return render_template("explore_event_form.html", action="Edit", location=location, event=event)


@app.route("/admin/explore/<int:loc_id>/events/<int:ev_id>/delete", methods=["POST"])
@admin_required
def explore_event_delete(loc_id, ev_id):
    locations = file_handler.load_explore_data()
    location = next((l for l in locations if l["location_id"] == loc_id), None)
    if not location:
        flash("Location not found.", "error")
        return redirect(url_for("explore"))

    event = next((e for e in location.get("events", []) if e["event_id"] == ev_id), None)
    if not event:
        flash("Event not found.", "error")
    else:
        location["events"].remove(event)
        file_handler.save_explore_data(locations)
        flash("Event deleted successfully.", "success")
    return redirect(url_for("explore_detail", loc_id=loc_id))


@app.route("/api/chat", methods=["POST", "OPTIONS"])
def api_chat():
    import requests
    if request.method == "OPTIONS":
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        return response

    # Get data from request
    req_data = request.get_json(silent=True) or {}
    user_message = req_data.get("message", "").strip()

    if not user_message:
        response = make_response(jsonify({"error": "Message is required"}), 400)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        response = make_response(jsonify({"error": "API key is not configured"}), 500)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    # Groq API completions call
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    system_instruction = "You are a helpful assistant for Dine-Stay, a restaurant and hotel booking website. Help users with menu, rooms, pricing, availability, and bookings. Be friendly and brief."
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": system_instruction
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        "max_tokens": 1000
    }

    try:
        api_response = requests.post(url, headers=headers, json=payload, timeout=30)
        api_response.raise_for_status()
        res_json = api_response.json()
        
        # Parse the reply from Groq
        try:
            bot_reply = res_json["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            bot_reply = "I apologize, but I received an invalid response structure from the assistant engine."
            
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        try:
            if 'api_response' in locals() and api_response.text:
                err_json = api_response.json()
                if "error" in err_json and "message" in err_json["error"]:
                    error_msg = err_json["error"]["message"]
        except Exception:
            pass
        bot_reply = f"Error communicating with Groq: {error_msg}"

    response = make_response(jsonify({"reply": bot_reply}))
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return response


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

