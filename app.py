from flask import Flask, request, render_template
import sqlite3
import os
import routeros_api
from mpesa import get_mpesa_token, lipa_na_mpesa

app = Flask(__name__)

# MikroTik credentials
MIKROTIK_IP = "192.168.88.1"
MIKROTIK_USER = "Dimba"
MIKROTIK_PASS = "Radohgigos2003"

# Initialize database
def init_db():
    if not os.path.exists("database.db"):
        conn = sqlite3.connect("database.db")
        conn.execute('''CREATE TABLE IF NOT EXISTS users
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         phone TEXT NOT NULL,
                         package TEXT NOT NULL,
                         paid INTEGER DEFAULT 0)''')
        conn.commit()
        conn.close()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/pay', methods=['POST'])
def pay():
    phone = request.form.get("phone")
    package = request.form.get("package")

    # Determine payment amount
    amount = 5
    if package == "24hr":
        amount = 20
    elif package == "weekly":
        amount = 100

    # Save user in DB with paid=0
    conn = sqlite3.connect("database.db")
    conn.execute("INSERT INTO users (phone, package, paid) VALUES (?, ?, ?)", (phone, package, 0))
    conn.commit()
    conn.close()

    # Send M-Pesa STK Push
    token = get_mpesa_token()
    response = lipa_na_mpesa(phone, amount, token)
    print("STK Push Response:", response)

    return render_template("stk_sent.html")

@app.route('/mpesa/callback', methods=['POST'])
def mpesa_callback():
    data = request.json
    print("MPESA CALLBACK:", data)

    try:
        result = data['Body']['stkCallback']
        status = result['ResultCode']
        phone = result['CallbackMetadata']['Item'][4]['Value']  # Paid phone number
        package = None

        # Get package from DB
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT package FROM users WHERE phone=? AND paid=0", (phone,))
        row = cursor.fetchone()
        if row:
            package = row[0]

        # Update DB paid status
        cursor.execute("UPDATE users SET paid=1 WHERE phone=? AND paid=0", (phone,))
        conn.commit()
        conn.close()

        # Activate MikroTik user if payment successful
        if status == 0 and package:
            connection = routeros_api.RouterOsApiPool(
                MIKROTIK_IP, username=MIKROTIK_USER, password=MIKROTIK_PASS, plaintext_login=True
            )
            api = connection.get_api()
            api.get_resource('/ip/hotspot/user').add(
                name=phone,
                password=phone,
                profile=package
            )
            connection.disconnect()
            print(f"MikroTik user {phone} added for package {package}!")

    except Exception as e:
        print("Callback processing error:", e)

    return {"Result": "Received"}

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)