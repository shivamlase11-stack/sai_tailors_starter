# Sai Tailors Management System

A modern admin-only web application for managing a tailor shop's customers, orders, measurements, payments, deliveries, sales, revenue, and expenses.

The application is designed specifically for **Sai Tailors** with a premium tailoring-inspired interface and a simple workflow for daily shop management.

---

## Features

### Admin Authentication
- Admin login only
- No public signup
- Session-based authentication
- Logout functionality

### Home Page
- Premium tailoring-inspired UI
- Sai Tailors branding
- Tailored outfit visual section
- Animated hero background
- Customer search
- Search by:
  - Customer name
  - Mobile number
  - Receipt number
- Today's delivery notification

### Customer & Order Management
- Create new customer orders
- Automatic receipt number generation
- Customer name and mobile number
- Shirt and Pant selection
- Multiple garment quantities
- Delivery date
- Order status tracking

### Shirt Management
Shirt types:
- Apple Cut
- Bhu Shirt
- Guru Shirt
- Kurta

Shirt measurements:
- Shoulder
- Chest
- Waist
- Front
- Sleeve
- Cuff
- Collar

### Pant Management

Pant measurements:
- Waist
- Hip
- Length
- Thigh
- Bottom

### Billing
- Shirt price: ₹350 each
- Pant price: ₹350 each
- Automatic subtotal calculation
- Automatic total calculation
- Paid amount
- Automatic balance calculation

### Order Status
- Pending Orders
- Completed Orders
- Mark orders as completed
- Delivery date tracking

### Sales & Reports
- Today's Sale
- Total Orders
- Weekly Sales
- Monthly Revenue
- Expenses management

### Notifications
- Notification icon available throughout the application
- Displays today's scheduled deliveries
- Shows customer name and receipt number
- Notification badge displays the number of today's pickups

---

## Technology Stack

### Frontend
- HTML5
- CSS3
- JavaScript
- Jinja2 Templates

### Backend
- Python
- Flask

### Database
- SQLite

### Fonts
- Cormorant Garamond
- Inter

---

## Project Structure

```text
sai_tailors_starter/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── home.html
│   ├── dashboard.html
│   ├── new_customer.html
│   ├── orders.html
│   ├── simple_report.html
│   └── expenses.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       └── app.js
│
└── sai_tailors.db
