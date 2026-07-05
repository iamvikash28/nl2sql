"""
create_database.py
-------------------
Generates a sample SQLite database (shop.db) with three related tables:
    customers  - who bought things
    products   - what was sold
    orders     - the transactions linking customers to products

Run this once before starting the app:
    python create_database.py
"""

import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "shop.db"

# ---- Sample data pools -----------------------------------------------------

FIRST_NAMES = ["Aarav", "Vivaan", "Diya", "Ananya", "Ishaan", "Priya", "Rohan",
               "Kavya", "Arjun", "Meera", "Karan", "Neha", "Sanya", "Aditya",
               "Riya", "Vikram", "Pooja", "Rahul", "Tanvi", "Yash"]
LAST_NAMES = ["Sharma", "Verma", "Gupta", "Patel", "Kumar", "Singh", "Reddy",
              "Nair", "Iyer", "Das", "Mehta", "Joshi", "Rao", "Malhotra"]

CITIES = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Hyderabad", "Pune",
          "Kolkata", "Ahmedabad", "Jaipur", "Lucknow"]

CATEGORIES = ["Electronics", "Clothing", "Home & Kitchen", "Books",
              "Sports", "Beauty", "Toys", "Groceries"]

PRODUCT_NAMES = {
    "Electronics": ["Wireless Earbuds", "Smart Watch", "Bluetooth Speaker",
                    "Power Bank", "Laptop Stand", "USB-C Hub"],
    "Clothing": ["Cotton T-Shirt", "Denim Jacket", "Running Shoes",
                 "Formal Shirt", "Hoodie", "Sneakers"],
    "Home & Kitchen": ["Non-stick Pan", "Air Fryer", "Coffee Maker",
                       "Blender", "Table Lamp", "Storage Boxes"],
    "Books": ["Novel - Fiction", "Self Help Guide", "Cookbook",
              "Biography", "Sci-Fi Novel", "Business Book"],
    "Sports": ["Yoga Mat", "Dumbbell Set", "Cricket Bat", "Football",
               "Resistance Bands", "Water Bottle"],
    "Beauty": ["Face Cream", "Shampoo", "Perfume", "Lipstick",
               "Sunscreen", "Hair Serum"],
    "Toys": ["Building Blocks", "Remote Car", "Puzzle Set",
             "Action Figure", "Board Game", "Soft Toy"],
    "Groceries": ["Basmati Rice 5kg", "Olive Oil 1L", "Almonds 500g",
                  "Green Tea Box", "Honey 500g", "Whole Wheat Atta 5kg"],
}


def build_database():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Start fresh every time this script runs
    cur.executescript("""
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS customers;

        CREATE TABLE customers (
            customer_id   INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            city          TEXT,
            signup_date   TEXT
        );

        CREATE TABLE products (
            product_id   INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category     TEXT,
            price        REAL
        );

        CREATE TABLE orders (
            order_id     INTEGER PRIMARY KEY,
            customer_id  INTEGER,
            product_id   INTEGER,
            quantity     INTEGER,
            order_date   TEXT,
            sales        REAL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (product_id)  REFERENCES products(product_id)
        );
    """)

    random.seed(42)  # reproducible sample data

    # ---- customers ----
    customers = []
    for i in range(1, 61):  # 60 customers
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        city = random.choice(CITIES)
        signup = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 500))
        customers.append((i, name, city, signup.strftime("%Y-%m-%d")))
    cur.executemany("INSERT INTO customers VALUES (?,?,?,?)", customers)

    # ---- products ----
    products = []
    pid = 1
    for category, names in PRODUCT_NAMES.items():
        for name in names:
            price = round(random.uniform(150, 5000), 2)
            products.append((pid, name, category, price))
            pid += 1
    cur.executemany("INSERT INTO products VALUES (?,?,?,?)", products)

    # ---- orders (the transactional table) ----
    orders = []
    order_id = 1
    for _ in range(800):  # 800 orders
        customer_id = random.randint(1, 60)
        product = random.choice(products)
        product_id, _, _, price = product
        quantity = random.randint(1, 5)
        order_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 550))
        sales = round(price * quantity, 2)
        orders.append((order_id, customer_id, product_id, quantity,
                        order_date.strftime("%Y-%m-%d"), sales))
        order_id += 1
    cur.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?)", orders)

    conn.commit()
    conn.close()
    print(f"✅ Database created: {DB_PATH}")
    print(f"   customers: {len(customers)} rows")
    print(f"   products:  {len(products)} rows")
    print(f"   orders:    {len(orders)} rows")


if __name__ == "__main__":
    build_database()
