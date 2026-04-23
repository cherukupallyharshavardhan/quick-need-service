from datetime import datetime
from functools import wraps
from pathlib import Path
import re

import sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for


app = Flask(__name__)
app.secret_key = "quickneed_secret_key"

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database.db"

DEFAULT_SERVICES = {
    "electrician": {
        "name": "Electrician",
        "tagline": "Wiring, fan, switchboard and power fixes",
        "icon": "EL",
        "price_from": 249,
        "accent": "amber",
        "image": "https://images.unsplash.com/photo-1621905252507-b35492cc74b4?auto=format&fit=crop&w=900&q=80",
    },
    "plumber": {
        "name": "Plumber",
        "tagline": "Leak repair, fittings and drainage support",
        "icon": "PL",
        "price_from": 299,
        "accent": "teal",
        "image": "https://images.unsplash.com/photo-1585704032915-c3400ca199e7?auto=format&fit=crop&w=900&q=80",
    },
    "carpenter": {
        "name": "Carpenter",
        "tagline": "Furniture repair and woodwork jobs",
        "icon": "CA",
        "price_from": 349,
        "accent": "coral",
        "image": "https://images.unsplash.com/photo-1513467655676-561b7d489a88?auto=format&fit=crop&w=900&q=80",
    },
    "ac-repair": {
        "name": "AC Repair",
        "tagline": "Service, cooling fixes and gas refill support",
        "icon": "AC",
        "price_from": 449,
        "accent": "blue",
        "image": "https://images.unsplash.com/photo-1621905251918-48416bd8575a?auto=format&fit=crop&w=900&q=80",
    },
    "home-cleaning": {
        "name": "Cleaning",
        "tagline": "Home and sofa deep clean",
        "icon": "CL",
        "price_from": 699,
        "accent": "mint",
        "image": "https://images.unsplash.com/photo-1581578731548-c64695cc6952?auto=format&fit=crop&w=900&q=80",
    },
    "painting": {
        "name": "Painting",
        "tagline": "Wall and door painting",
        "icon": "PA",
        "price_from": 799,
        "accent": "rose",
        "image": "https://images.unsplash.com/photo-1562259949-e8e7689d7828?auto=format&fit=crop&w=900&q=80",
    },
}

DEFAULT_PROVIDERS = {
    "electrician": [
        {
            "slug": "suresh-electricals",
            "name": "Suresh Electricals",
            "rating": 4.9,
            "experience": "8 years",
            "eta": "35 min",
            "price": 249,
            "phone": "9000001101",
            "badge": "Fast response",
        },
        {
            "slug": "ramesh-power-care",
            "name": "Ramesh Power Care",
            "rating": 4.7,
            "experience": "6 years",
            "eta": "50 min",
            "price": 299,
            "phone": "9000001102",
            "badge": "Trusted local pro",
        },
    ],
    "plumber": [
        {
            "slug": "aqua-fix-team",
            "name": "Aqua Fix Team",
            "rating": 4.8,
            "experience": "7 years",
            "eta": "40 min",
            "price": 299,
            "phone": "9000001201",
            "badge": "Leak specialists",
        },
        {
            "slug": "pipe-doctor",
            "name": "Pipe Doctor",
            "rating": 4.6,
            "experience": "5 years",
            "eta": "55 min",
            "price": 349,
            "phone": "9000001202",
            "badge": "Same-day visits",
        },
    ],
    "carpenter": [
        {
            "slug": "woodcraft-hub",
            "name": "Woodcraft Hub",
            "rating": 4.8,
            "experience": "9 years",
            "eta": "1 hr",
            "price": 349,
            "phone": "9000001301",
            "badge": "Furniture experts",
        },
        {
            "slug": "urban-carpentry",
            "name": "Urban Carpentry",
            "rating": 4.5,
            "experience": "4 years",
            "eta": "1 hr 10 min",
            "price": 399,
            "phone": "9000001302",
            "badge": "Custom fixes",
        },
    ],
    "ac-repair": [
        {
            "slug": "cooling-point",
            "name": "Cooling Point",
            "rating": 4.9,
            "experience": "10 years",
            "eta": "45 min",
            "price": 449,
            "phone": "9000001401",
            "badge": "Cooling experts",
        },
        {
            "slug": "chill-tech",
            "name": "Chill Tech",
            "rating": 4.7,
            "experience": "6 years",
            "eta": "1 hr",
            "price": 499,
            "phone": "9000001402",
            "badge": "Weekend support",
        },
    ],
    "home-cleaning": [
        {
            "slug": "sparkle-home-care",
            "name": "Sparkle Home Care",
            "rating": 4.8,
            "experience": "5 years",
            "eta": "Tomorrow",
            "price": 699,
            "phone": "9000001501",
            "badge": "Deep clean crew",
        },
        {
            "slug": "neatnest-services",
            "name": "NeatNest Services",
            "rating": 4.6,
            "experience": "4 years",
            "eta": "Tomorrow",
            "price": 749,
            "phone": "9000001502",
            "badge": "Eco-friendly products",
        },
    ],
    "painting": [
        {
            "slug": "wallcraft-painting",
            "name": "WallCraft Painting",
            "rating": 4.8,
            "experience": "8 years",
            "eta": "Consult in 1 day",
            "price": 799,
            "phone": "9000001601",
            "badge": "Interior wall specialists",
        },
        {
            "slug": "fresh-coat-pros",
            "name": "Fresh Coat Pros",
            "rating": 4.7,
            "experience": "6 years",
            "eta": "Consult in 2 days",
            "price": 899,
            "phone": "9000001602",
            "badge": "Quick repaint team",
        },
    ],
}

HELP_ITEMS = [
    {
        "question": "How do I book a service?",
        "answer": "Pick a category, choose a provider, select address and time, then confirm your booking.",
    },
    {
        "question": "Payment options?",
        "answer": "Cash on service is accepted. You can pay your professional after the job is complete.",
    },
    {
        "question": "Can I reschedule a booking?",
        "answer": "Cancel an upcoming booking from the Bookings tab and place a new booking for your preferred slot.",
    },
    {
        "question": "Are professionals verified?",
        "answer": "All listed pros are screened and rated based on service quality, punctuality, and customer feedback.",
    },
]

ALLOWED_BOOKING_STATUSES = {
    "Pending",
    "Accepted",
    "In Progress",
    "Completed",
    "Cancel Requested",
    "Cancelled",
}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def column_exists(conn, table_name, column_name):
    columns = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return any(column["name"] == column_name for column in columns)


def add_column_if_missing(conn, table_name, column_name, definition):
    if not column_exists(conn, table_name, column_name):
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            phone TEXT,
            password TEXT,
            role TEXT DEFAULT 'user'
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            service TEXT,
            provider TEXT,
            name TEXT,
            address TEXT,
            date TEXT,
            time TEXT,
            issue TEXT,
            status TEXT DEFAULT 'Pending'
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE,
            name TEXT NOT NULL,
            tagline TEXT NOT NULL,
            icon TEXT,
            price_from INTEGER DEFAULT 0,
            accent TEXT,
            image TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS providers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_slug TEXT NOT NULL,
            slug TEXT UNIQUE,
            name TEXT NOT NULL,
            rating REAL DEFAULT 4.5,
            experience TEXT,
            eta TEXT,
            price INTEGER DEFAULT 0,
            phone TEXT,
            badge TEXT
        )
        """
    )

    add_column_if_missing(conn, "users", "full_name", "TEXT")
    add_column_if_missing(conn, "users", "city", "TEXT")
    add_column_if_missing(conn, "bookings", "customer_phone", "TEXT")
    add_column_if_missing(conn, "bookings", "provider_phone", "TEXT")
    add_column_if_missing(conn, "bookings", "amount", "INTEGER DEFAULT 0")
    add_column_if_missing(conn, "bookings", "created_at", "TEXT")

    conn.execute(
        """
        UPDATE bookings
        SET created_at = COALESCE(created_at, date || ' ' || time)
        WHERE created_at IS NULL
        """
    )
    conn.execute(
        """
        UPDATE users
        SET full_name = COALESCE(NULLIF(full_name, ''), substr(email, 1, instr(email, '@') - 1))
        WHERE email LIKE '%@%'
        """
    )

    services_count = conn.execute("SELECT COUNT(*) FROM services").fetchone()[0]
    if services_count == 0:
        for slug, service in DEFAULT_SERVICES.items():
            conn.execute(
                """
                INSERT INTO services (slug, name, tagline, icon, price_from, accent, image)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    slug,
                    service["name"],
                    service["tagline"],
                    service["icon"],
                    service["price_from"],
                    service["accent"],
                    service["image"],
                ),
            )

    providers_count = conn.execute("SELECT COUNT(*) FROM providers").fetchone()[0]
    if providers_count == 0:
        for service_slug, provider_list in DEFAULT_PROVIDERS.items():
            for provider in provider_list:
                conn.execute(
                    """
                    INSERT INTO providers (
                        service_slug, slug, name, rating, experience, eta, price, phone, badge
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        service_slug,
                        provider["slug"],
                        provider["name"],
                        provider["rating"],
                        provider["experience"],
                        provider["eta"],
                        provider["price"],
                        provider["phone"],
                        provider["badge"],
                    ),
                )
    conn.commit()
    conn.close()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_email" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Admin access is required for that page.", "warning")
            return redirect(url_for("home"))
        return view(*args, **kwargs)

    return wrapped_view


def customer_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get("role") == "admin":
            flash("Please use the admin dashboard for admin access.", "warning")
            return redirect(url_for("admin_dashboard"))
        return view(*args, **kwargs)

    return wrapped_view


def get_current_user():
    if "user_email" not in session:
        return None
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (session["user_email"],),
    ).fetchone()
    conn.close()
    return user


def slugify(value):
    normalized = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return normalized.strip("-") or "item"


def get_services(search_query=""):
    conn = get_db()
    services = conn.execute(
        """
        SELECT
            s.*,
            COUNT(p.id) AS providers_count
        FROM services s
        LEFT JOIN providers p ON p.service_slug = s.slug
        GROUP BY s.id
        ORDER BY s.name
        """
    ).fetchall()
    conn.close()

    results = [dict(service) for service in services]
    if search_query:
        query = search_query.strip().lower()
        results = [
            service
            for service in results
            if query in service["name"].lower() or query in service["tagline"].lower()
        ]
    return results


def get_service(service_slug):
    conn = get_db()
    service = conn.execute(
        "SELECT * FROM services WHERE slug = ?",
        (service_slug,),
    ).fetchone()
    conn.close()
    return service


def get_providers(service_slug=None):
    conn = get_db()
    if service_slug:
        providers = conn.execute(
            "SELECT * FROM providers WHERE service_slug = ? ORDER BY name",
            (service_slug,),
        ).fetchall()
    else:
        providers = conn.execute(
            "SELECT * FROM providers ORDER BY name"
        ).fetchall()
    conn.close()
    return providers


def get_provider(service_slug, provider_slug):
    conn = get_db()
    provider = conn.execute(
        "SELECT * FROM providers WHERE service_slug = ? AND slug = ?",
        (service_slug, provider_slug),
    ).fetchone()
    conn.close()
    return provider


def booking_status_breakdown(bookings):
    counts = {
        "total": len(bookings),
        "pending": 0,
        "accepted": 0,
        "in_progress": 0,
        "completed": 0,
        "cancel_requested": 0,
        "cancelled": 0,
    }
    for booking in bookings:
        status = (booking["status"] or "").strip().lower()
        if status == "pending":
            counts["pending"] += 1
        elif status == "accepted":
            counts["accepted"] += 1
        elif status == "in progress":
            counts["in_progress"] += 1
        elif status == "completed":
            counts["completed"] += 1
        elif status == "cancel requested":
            counts["cancel_requested"] += 1
        elif status == "cancelled":
            counts["cancelled"] += 1
    return counts


def filter_bookings(bookings, tab):
    tab = (tab or "upcoming").strip().lower()
    if tab == "completed":
        return [booking for booking in bookings if (booking["status"] or "").strip().lower() == "completed"]
    if tab == "cancelled":
        return [booking for booking in bookings if (booking["status"] or "").strip().lower() in {"cancelled", "cancel requested"}]
    return [
        booking
        for booking in bookings
        if (booking["status"] or "").strip().lower() not in {"completed", "cancelled", "cancel requested"}
    ]


@app.context_processor
def inject_layout_data():
    return {
        "nav_services": get_services(),
        "current_role": session.get("role"),
        "current_endpoint": request.endpoint,
    }


@app.route("/")
def intro():
    if session.get("user_email"):
        return redirect(url_for("admin_dashboard" if session.get("role") == "admin" else "home"))
    return render_template("intro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_email"):
        return redirect(url_for("admin_dashboard" if session.get("role") == "admin" else "home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (email, password),
        ).fetchone()
        conn.close()

        if not user:
            flash("Invalid email or password.", "danger")
            return render_template("login.html")

        session["user_email"] = user["email"]
        session["role"] = user["role"] or "user"
        session["display_name"] = user["full_name"] or user["email"].split("@")[0]
        if session["role"] == "admin":
            flash("Welcome admin.", "success")
            return redirect(url_for("admin_dashboard"))

        flash("Welcome back.", "success")
        return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        city = request.form.get("city", "").strip()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm", "").strip()

        if not all([full_name, email, phone, city, password, confirm]):
            flash("Please fill in every field.", "warning")
            return render_template("signup.html")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("signup.html")

        conn = get_db()
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,),
        ).fetchone()
        if existing:
            conn.close()
            flash("That email is already registered.", "warning")
            return render_template("signup.html")

        conn.execute(
            """
            INSERT INTO users (full_name, email, phone, city, password, role)
            VALUES (?, ?, ?, ?, ?, 'user')
            """,
            (full_name, email, phone, city, password),
        )
        conn.commit()
        conn.close()
        flash("Account created. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/home")
@login_required
@customer_required
def home():
    search_query = request.args.get("q", "").strip().lower()
    current_user = get_current_user()
    services = get_services(search_query)
    conn = get_db()
    recent_bookings = conn.execute(
        """
        SELECT * FROM bookings
        WHERE user_email = ?
        ORDER BY id DESC
        LIMIT 3
        """,
        (session["user_email"],),
    ).fetchall()
    user_booking_rows = conn.execute(
        "SELECT * FROM bookings WHERE user_email = ?",
        (session["user_email"],),
    ).fetchall()
    conn.close()

    stats = booking_status_breakdown(user_booking_rows)
    return render_template(
        "home.html",
        user_name=session.get("display_name", session["user_email"].split("@")[0]),
        services=services,
        recent_bookings=recent_bookings,
        stats=stats,
        current_user=current_user,
        search_query=search_query,
    )


@app.route("/services/<service_slug>")
@login_required
@customer_required
def service_detail(service_slug):
    service = get_service(service_slug)
    if not service:
        flash("That service category was not found.", "warning")
        return redirect(url_for("home"))

    return render_template(
        "service.html",
        service_slug=service_slug,
        service=service,
        providers=get_providers(service_slug),
    )


@app.route("/book/<service_slug>/<provider_slug>", methods=["GET", "POST"])
@login_required
@customer_required
def book_service(service_slug, provider_slug):
    service = get_service(service_slug)
    provider = get_provider(service_slug, provider_slug)

    if not service or not provider:
        flash("The selected provider is unavailable.", "warning")
        return redirect(url_for("home"))

    if request.method == "POST":
        customer_name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        date = request.form.get("date", "").strip()
        time = request.form.get("time", "").strip()
        issue = request.form.get("issue", "").strip()

        if not all([customer_name, phone, address, date, time, issue]):
            flash("Please complete the booking form.", "warning")
            return render_template(
                "book.html",
                service=service,
                service_slug=service_slug,
                provider=provider,
                today=datetime.now().strftime("%Y-%m-%d"),
            )

        conn = get_db()
        conn.execute(
            """
            INSERT INTO bookings (
                user_email, service, provider, customer_phone, provider_phone, name, address,
                date, time, issue, status, amount, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', ?, ?)
            """,
            (
                session["user_email"],
                service["name"],
                provider["name"],
                phone,
                provider["phone"],
                customer_name,
                address,
                date,
                time,
                issue,
                provider["price"],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        booking_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.commit()
        conn.close()
        flash(f"{service['name']} booking created with {provider['name']}.", "success")
        return redirect(url_for("booking_success", booking_id=booking_id))

    current_user = get_current_user()
    return render_template(
        "book.html",
        service=service,
        service_slug=service_slug,
        provider=provider,
        current_user=current_user,
        today=datetime.now().strftime("%Y-%m-%d"),
    )


@app.route("/my-bookings")
@login_required
@customer_required
def my_bookings():
    active_tab = request.args.get("tab", "upcoming").strip().lower()
    conn = get_db()
    bookings = conn.execute(
        """
        SELECT * FROM bookings
        WHERE user_email = ?
        ORDER BY id DESC
        """,
        (session["user_email"],),
    ).fetchall()
    conn.close()

    return render_template(
        "my_bookings.html",
        bookings=bookings,
        filtered_bookings=filter_bookings(bookings, active_tab),
        active_tab=active_tab,
        stats=booking_status_breakdown(bookings),
    )


@app.route("/booking-success/<int:booking_id>")
@login_required
@customer_required
def booking_success(booking_id):
    conn = get_db()
    booking = conn.execute(
        "SELECT * FROM bookings WHERE id = ? AND user_email = ?",
        (booking_id, session["user_email"]),
    ).fetchone()
    conn.close()
    if not booking:
        flash("Booking not found.", "warning")
        return redirect(url_for("my_bookings"))
    return render_template("booking_success.html", booking=booking)


@app.route("/help")
@login_required
@customer_required
def help_page():
    return render_template("help.html", help_items=HELP_ITEMS)


@app.route("/profile", methods=["GET", "POST"])
@login_required
@customer_required
def profile():
    conn = get_db()
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        city = request.form.get("city", "").strip()
        if not all([full_name, phone, city]):
            flash("Please fill in all profile fields.", "warning")
        else:
            conn.execute(
                """
                UPDATE users
                SET full_name = ?, phone = ?, city = ?
                WHERE email = ?
                """,
                (full_name, phone, city, session["user_email"]),
            )
            conn.commit()
            session["display_name"] = full_name
            flash("Profile updated.", "success")

    user = get_current_user()
    bookings = conn.execute(
        "SELECT * FROM bookings WHERE user_email = ? ORDER BY id DESC",
        (session["user_email"],),
    ).fetchall()
    conn.close()

    return render_template(
        "profile.html",
        user=user,
        stats=booking_status_breakdown(bookings),
        latest_booking=bookings[0] if bookings else None,
    )


@app.route("/request-cancel/<int:booking_id>")
@login_required
@customer_required
def request_cancel(booking_id):
    conn = get_db()
    booking = conn.execute(
        "SELECT * FROM bookings WHERE id = ? AND user_email = ?",
        (booking_id, session["user_email"]),
    ).fetchone()

    if not booking:
        conn.close()
        flash("Booking not found.", "warning")
        return redirect(url_for("my_bookings"))

    current_status = (booking["status"] or "").strip().lower()
    if current_status in {"completed", "cancelled"}:
        conn.close()
        flash("That booking can no longer be cancelled.", "warning")
        return redirect(url_for("my_bookings"))

    conn.execute(
        "UPDATE bookings SET status = 'Cancel Requested' WHERE id = ?",
        (booking_id,),
    )
    conn.commit()
    conn.close()
    flash("Cancellation request sent to admin.", "success")
    return redirect(url_for("my_bookings"))


@app.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    conn = get_db()
    bookings = conn.execute(
        "SELECT * FROM bookings ORDER BY id DESC"
    ).fetchall()
    users = conn.execute(
        "SELECT * FROM users ORDER BY id DESC"
    ).fetchall()
    conn.close()
    services = get_services()
    providers = get_providers()

    return render_template(
        "admin.html",
        bookings=bookings,
        services=services,
        providers=providers,
        stats=booking_status_breakdown(bookings),
        user_count=len(users),
        service_count=len(services),
        provider_count=len(providers),
    )


@app.route("/update-status/<int:booking_id>/<status>")
@login_required
@admin_required
def update_status(booking_id, status):
    normalized = status.replace("-", " ").title()
    if normalized not in ALLOWED_BOOKING_STATUSES:
        flash("Unsupported booking status.", "warning")
        return redirect(url_for("admin_dashboard"))

    conn = get_db()
    booking = conn.execute(
        "SELECT id FROM bookings WHERE id = ?",
        (booking_id,),
    ).fetchone()
    if not booking:
        conn.close()
        flash("Booking not found.", "warning")
        return redirect(url_for("admin_dashboard"))

    conn.execute(
        "UPDATE bookings SET status = ? WHERE id = ?",
        (normalized, booking_id),
    )
    conn.commit()
    conn.close()
    flash(f"Booking #{booking_id} marked as {normalized}.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/services/save", methods=["POST"])
@login_required
@admin_required
def save_service():
    current_slug = request.form.get("current_slug", "").strip()
    slug = slugify(request.form.get("slug", "") or request.form.get("name", ""))
    name = request.form.get("name", "").strip()
    tagline = request.form.get("tagline", "").strip()
    icon = request.form.get("icon", "").strip() or "SV"
    price_from = request.form.get("price_from", "").strip() or "0"
    accent = request.form.get("accent", "").strip() or "blue"
    image = request.form.get("image", "").strip()

    if not all([slug, name, tagline]):
        flash("Service name, slug, and tagline are required.", "warning")
        return redirect(url_for("admin_dashboard"))

    conn = get_db()
    duplicate = conn.execute(
        "SELECT id FROM services WHERE slug = ? AND slug != ?",
        (slug, current_slug or "__new__"),
    ).fetchone()
    if duplicate:
        conn.close()
        flash("That service slug is already in use.", "warning")
        return redirect(url_for("admin_dashboard"))

    if current_slug:
        conn.execute(
            """
            UPDATE services
            SET slug = ?, name = ?, tagline = ?, icon = ?, price_from = ?, accent = ?, image = ?
            WHERE slug = ?
            """,
            (slug, name, tagline, icon, int(price_from), accent, image, current_slug),
        )
        conn.execute(
            "UPDATE providers SET service_slug = ? WHERE service_slug = ?",
            (slug, current_slug),
        )
        flash("Service updated.", "success")
    else:
        conn.execute(
            """
            INSERT INTO services (slug, name, tagline, icon, price_from, accent, image)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (slug, name, tagline, icon, int(price_from), accent, image),
        )
        flash("Service added.", "success")

    conn.commit()
    conn.close()
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/services/delete/<service_slug>")
@login_required
@admin_required
def delete_service(service_slug):
    conn = get_db()
    conn.execute("DELETE FROM providers WHERE service_slug = ?", (service_slug,))
    conn.execute("DELETE FROM services WHERE slug = ?", (service_slug,))
    conn.commit()
    conn.close()
    flash("Service and related providers deleted.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/providers/save", methods=["POST"])
@login_required
@admin_required
def save_provider():
    provider_id = request.form.get("provider_id", "").strip()
    service_slug = request.form.get("service_slug", "").strip()
    slug = slugify(request.form.get("slug", "") or request.form.get("name", ""))
    name = request.form.get("name", "").strip()
    rating = request.form.get("rating", "").strip() or "4.5"
    experience = request.form.get("experience", "").strip()
    eta = request.form.get("eta", "").strip()
    price = request.form.get("price", "").strip() or "0"
    phone = request.form.get("phone", "").strip()
    badge = request.form.get("badge", "").strip()

    if not all([service_slug, slug, name]):
        flash("Provider service, name, and slug are required.", "warning")
        return redirect(url_for("admin_dashboard"))

    conn = get_db()
    duplicate = conn.execute(
        "SELECT id FROM providers WHERE slug = ? AND id != ?",
        (slug, int(provider_id) if provider_id else -1),
    ).fetchone()
    if duplicate:
        conn.close()
        flash("That provider slug is already in use.", "warning")
        return redirect(url_for("admin_dashboard"))

    if provider_id:
        conn.execute(
            """
            UPDATE providers
            SET service_slug = ?, slug = ?, name = ?, rating = ?, experience = ?, eta = ?, price = ?, phone = ?, badge = ?
            WHERE id = ?
            """,
            (service_slug, slug, name, float(rating), experience, eta, int(price), phone, badge, int(provider_id)),
        )
        flash("Provider updated.", "success")
    else:
        conn.execute(
            """
            INSERT INTO providers (service_slug, slug, name, rating, experience, eta, price, phone, badge)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (service_slug, slug, name, float(rating), experience, eta, int(price), phone, badge),
        )
        flash("Provider added.", "success")

    conn.commit()
    conn.close()
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/providers/delete/<int:provider_id>")
@login_required
@admin_required
def delete_provider(provider_id):
    conn = get_db()
    conn.execute("DELETE FROM providers WHERE id = ?", (provider_id,))
    conn.commit()
    conn.close()
    flash("Provider deleted.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/manifest.webmanifest")
def manifest():
    return jsonify(
        {
            "name": "Quick Need Service",
            "short_name": "QuickNeed",
            "start_url": url_for("login"),
            "scope": "/",
            "display": "standalone",
            "background_color": "#f7f2e8",
            "theme_color": "#0f766e",
            "description": "Book trusted home services with a mobile-friendly installable app.",
            "icons": [
                {
                    "src": url_for("static", filename="icons/icon-192.svg"),
                    "sizes": "192x192",
                    "type": "image/svg+xml",
                    "purpose": "any maskable",
                },
                {
                    "src": url_for("static", filename="icons/icon-512.svg"),
                    "sizes": "512x512",
                    "type": "image/svg+xml",
                    "purpose": "any maskable",
                },
            ],
        }
    )


@app.route("/offline")
def offline():
    return render_template("offline.html")


init_db()


if __name__ == "__main__":
    app.run(debug=True)
