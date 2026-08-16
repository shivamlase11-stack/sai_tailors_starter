from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
import json
from datetime import date, datetime
from functools import wraps
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "sai_tailors.db"

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

SHIRT_PRICE = 350
PANT_PRICE = 350

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        mobile TEXT NOT NULL,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receipt_no TEXT UNIQUE NOT NULL,
        customer_id INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        delivery_date TEXT NOT NULL,
        shirt_type TEXT,
        shirt_qty INTEGER DEFAULT 0,
        pant_qty INTEGER DEFAULT 0,
        total_amount REAL NOT NULL,
        paid_amount REAL DEFAULT 0,
        balance REAL NOT NULL,
        status TEXT DEFAULT 'Pending',
        measurements TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    );

    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        expense_date TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

@app.route("/")
def root():
    return redirect(url_for("home") if session.get("admin") else url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        # Starter credentials. Replace with hashed credentials before production.
        if username == "admin" and password == "sai123":
            session["admin"] = True
            return redirect(url_for("home"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/home")
@login_required
def home():
    conn = get_db()
    today = date.today().isoformat()
    deliveries = conn.execute("""
        SELECT o.receipt_no, c.name, c.mobile, o.delivery_date, o.status
        FROM orders o JOIN customers c ON c.id = o.customer_id
        WHERE o.delivery_date = ? AND o.status != 'Completed'
        ORDER BY o.id DESC
    """, (today,)).fetchall()

    recent = conn.execute("""
        SELECT o.receipt_no, c.name, o.status, o.total_amount, o.delivery_date
        FROM orders o JOIN customers c ON c.id = o.customer_id
        ORDER BY o.id DESC LIMIT 6
    """).fetchall()

    conn.close()
    return render_template("home.html", deliveries=deliveries, recent=recent)

@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    today = date.today().isoformat()
    stats = {
        "today_sales": conn.execute(
            "SELECT COALESCE(SUM(paid_amount),0) FROM orders WHERE order_date=?", (today,)
        ).fetchone()[0],
        "pending": conn.execute(
            "SELECT COUNT(*) FROM orders WHERE status='Pending'"
        ).fetchone()[0],
        "completed": conn.execute(
            "SELECT COUNT(*) FROM orders WHERE status='Completed'"
        ).fetchone()[0],
        "total": conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
        "expenses": conn.execute(
            "SELECT COALESCE(SUM(amount),0) FROM expenses WHERE expense_date=?", (today,)
        ).fetchone()[0],
    }
    conn.close()
    return render_template("dashboard.html", stats=stats)

@app.route("/new-customer", methods=["GET", "POST"])
@login_required
def new_customer():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        mobile = request.form.get("mobile", "").strip()
        delivery_date = request.form.get("delivery_date", "")
        shirt_type = request.form.get("shirt_type", "")
        shirt_qty = int(request.form.get("shirt_qty", 0) or 0)
        pant_qty = int(request.form.get("pant_qty", 0) or 0)
        paid = float(request.form.get("paid", 0) or 0)
        measurements = json.dumps({
            "shirt": {
                "shoulder": request.form.get("shoulder", ""),
                "chest": request.form.get("chest", ""),
                "waist": request.form.get("shirt_waist", ""),
                "front": request.form.get("front", ""),
                "sleeve": request.form.get("sleeve", ""),
                "cuff": request.form.get("cuff", ""),
                "collar": request.form.get("collar", "")
            },
            "pant": {
                "waist": request.form.get("pant_waist", ""),
                "hip": request.form.get("hip", ""),
                "length": request.form.get("length", ""),
                "thigh": request.form.get("thigh", ""),
                "bottom": request.form.get("bottom", "")
            }
        })

        if not name or not mobile or not delivery_date or (shirt_qty == 0 and pant_qty == 0):
            flash("Name, mobile, delivery date, and at least one garment are required.", "error")
            return render_template("new_customer.html")

        total = shirt_qty * SHIRT_PRICE + pant_qty * PANT_PRICE
        balance = max(total - paid, 0)

        conn = get_db()
        existing = conn.execute(
            "SELECT id FROM customers WHERE mobile=? ORDER BY id DESC LIMIT 1", (mobile,)
        ).fetchone()

        if existing:
            customer_id = existing["id"]
        else:
            cur = conn.execute(
                "INSERT INTO customers(name,mobile,created_at) VALUES(?,?,?)",
                (name, mobile, datetime.now().isoformat())
            )
            customer_id = cur.lastrowid

        cur = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0] + 1
        receipt_no = f"ST-{cur:04d}"

        conn.execute("""
            INSERT INTO orders(
                receipt_no, customer_id, order_date, delivery_date,
                shirt_type, shirt_qty, pant_qty, total_amount,
                paid_amount, balance, status, measurements, created_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            receipt_no, customer_id, date.today().isoformat(), delivery_date,
            shirt_type, shirt_qty, pant_qty, total, paid, balance,
            "Pending", measurements, datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
        return redirect(url_for("orders", saved=receipt_no))

    return render_template("new_customer.html")

@app.route("/orders")
@login_required
def orders():
    conn = get_db()
    rows = conn.execute("""
        SELECT o.*, c.name, c.mobile
        FROM orders o JOIN customers c ON c.id=o.customer_id
        ORDER BY o.id DESC
    """).fetchall()
    conn.close()
    return render_template("orders.html", orders=rows, title="Orders")

@app.route("/pending-orders")
@login_required
def pending_orders():
    conn = get_db()
    rows = conn.execute("""
        SELECT o.*, c.name, c.mobile
        FROM orders o JOIN customers c ON c.id=o.customer_id
        WHERE o.status='Pending'
        ORDER BY o.delivery_date ASC
    """).fetchall()
    conn.close()
    return render_template("orders.html", orders=rows, title="Pending Orders")

@app.route("/completed-orders")
@login_required
def completed_orders():
    conn = get_db()
    rows = conn.execute("""
        SELECT o.*, c.name, c.mobile
        FROM orders o JOIN customers c ON c.id=o.customer_id
        WHERE o.status='Completed'
        ORDER BY o.id DESC
    """).fetchall()
    conn.close()
    return render_template("orders.html", orders=rows, title="Completed Orders")

@app.route("/orders/<int:order_id>/complete", methods=["POST"])
@login_required
def complete_order(order_id):
    conn = get_db()
    conn.execute("UPDATE orders SET status='Completed' WHERE id=?", (order_id,))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for("orders"))

@app.route("/search")
@login_required
def search():
    q = request.args.get("q", "").strip()
    conn = get_db()
    rows = conn.execute("""
        SELECT o.receipt_no, c.name, c.mobile, o.status, o.delivery_date, o.balance
        FROM orders o JOIN customers c ON c.id=o.customer_id
        WHERE c.name LIKE ? OR c.mobile LIKE ? OR o.receipt_no LIKE ?
        ORDER BY o.id DESC LIMIT 10
    """, (f"%{q}%", f"%{q}%", f"%{q}%")).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route("/sales")
@login_required
def sales():
    conn = get_db()
    today = date.today().isoformat()
    rows = conn.execute("""
        SELECT o.receipt_no, c.name, o.paid_amount, o.total_amount
        FROM orders o JOIN customers c ON c.id=o.customer_id
        WHERE o.order_date=?
        ORDER BY o.id DESC
    """, (today,)).fetchall()
    total = sum(r["paid_amount"] for r in rows)
    conn.close()
    return render_template("simple_report.html", title="Today's Sale", value=total, rows=rows,
                           columns=["receipt_no","name","paid_amount","total_amount"])

@app.route("/weekly-sales")
@login_required
def weekly_sales():
    conn = get_db()
    rows = conn.execute("""
        SELECT order_date, COALESCE(SUM(paid_amount),0) AS amount
        FROM orders
        GROUP BY order_date
        ORDER BY order_date DESC LIMIT 7
    """).fetchall()
    conn.close()
    return render_template("simple_report.html", title="Weekly Sales", value=sum(r["amount"] for r in rows),
                           rows=rows, columns=["order_date","amount"])

@app.route("/monthly-revenue")
@login_required
def monthly_revenue():
    conn = get_db()
    month = date.today().strftime("%Y-%m")
    rows = conn.execute("""
        SELECT order_date, COALESCE(SUM(paid_amount),0) AS amount
        FROM orders
        WHERE substr(order_date,1,7)=?
        GROUP BY order_date
        ORDER BY order_date
    """, (month,)).fetchall()
    conn.close()
    return render_template("simple_report.html", title="Monthly Revenue",
                           value=sum(r["amount"] for r in rows), rows=rows,
                           columns=["order_date","amount"])

@app.route("/expenses", methods=["GET", "POST"])
@login_required
def expenses():
    conn = get_db()
    if request.method == "POST":
        description = request.form.get("description", "").strip()
        amount = float(request.form.get("amount", 0) or 0)
        expense_date = request.form.get("expense_date") or date.today().isoformat()
        if description and amount > 0:
            conn.execute(
                "INSERT INTO expenses(description,amount,expense_date) VALUES(?,?,?)",
                (description, amount, expense_date)
            )
            conn.commit()
    rows = conn.execute("SELECT * FROM expenses ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("expenses.html", expenses=rows)

@app.context_processor
def inject_globals():
    conn = get_db()
    today = date.today().isoformat()
    count = conn.execute(
        "SELECT COUNT(*) FROM orders WHERE delivery_date=? AND status!='Completed'", (today,)
    ).fetchone()[0]
    conn.close()
    return {"notification_count": count, "today": today}

init_db()

if __name__ == "__main__":
    app.run(debug=True)
