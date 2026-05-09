import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import hashlib
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="7Alpha",
    page_icon="hello.png",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

.main {
    background-color: #0f172a;
    color: white;
}

.stButton>button {
    background: linear-gradient(to right,#2563eb,#7c3aed);
    color: white;
    border-radius: 12px;
    padding: 10px 20px;
    border: none;
    font-size: 16px;
    width: 100%;
}

.stTextInput>div>div>input {
    border-radius: 12px;
}

.stSelectbox>div>div {
    border-radius: 12px;
}

.popup-overlay{
    position: fixed;
    top:0;
    left:0;
    width:100%;
    height:100%;
    background: rgba(0,0,0,0.75);
    z-index:9999;
    display:flex;
    justify-content:center;
    align-items:center;
}

.popup-card{
    width:430px;
    background:#111827;
    border-radius:25px;
    padding:30px;
    box-shadow:0 0 40px rgba(0,0,0,0.6);
    animation: popup 0.25s ease;
    color:white;
}

@keyframes popup{
    from{
        transform:scale(0.9);
        opacity:0;
    }

    to{
        transform:scale(1);
        opacity:1;
    }
}

.popup-title{
    font-size:34px;
    font-weight:bold;
    text-align:center;
}

.popup-subtitle{
    text-align:center;
    color:#cbd5e1;
    margin-top:10px;
}

.plan-box{
    background:#1e293b;
    padding:20px;
    border-radius:20px;
    margin-top:20px;
    border:1px solid #334155;
}

.price{
    font-size:40px;
    font-weight:bold;
    color:#60a5fa;
    margin-top:10px;
}

.feature{
    margin-top:12px;
    color:#d1d5db;
    font-size:15px;
}

.bank-box{
    background:#0f172a;
    padding:15px;
    border-radius:15px;
    margin-top:20px;
    line-height:1.9;
}

</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("app.db", check_same_thread=False)
c = conn.cursor()

# ---------------- USERS TABLE ----------------
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# ---------------- PAYMENTS TABLE ----------------
c.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    amount TEXT,
    payment_method TEXT,
    transaction_id TEXT,
    date TEXT
)
""")

conn.commit()

# ---------------- FUNCTIONS ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):

    try:

        c.execute(
            "INSERT INTO users (username,password) VALUES (?,?)",
            (username, hash_password(password))
        )

        conn.commit()

        return True

    except:
        return False

def login_user(username, password):

    c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    )

    return c.fetchone()

def save_payment(username, amount, method, transaction_id="N/A"):

    c.execute(
        """
        INSERT INTO payments
        (username, amount, payment_method, transaction_id, date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            username,
            amount,
            method,
            transaction_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    conn.commit()

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "free_uses" not in st.session_state:
    st.session_state.free_uses = 7

if "show_payment_popup" not in st.session_state:
    st.session_state.show_payment_popup = False

# ---------------- SIDEBAR ----------------
st.sidebar.title("🌐 Web Viewer App")

menu = st.sidebar.selectbox(
    "Navigation",
    ["Login", "Signup", "Dashboard"]
)

# ---------------- SIGNUP ----------------
if menu == "Signup":

    st.title("📝 Signup")

    new_user = st.text_input("Username")

    new_password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Create Account"):

        if new_user and new_password:

            success = create_user(
                new_user,
                new_password
            )

            if success:
                st.success(
                    "Account created successfully!"
                )

            else:
                st.error(
                    "Username already exists"
                )

        else:
            st.warning(
                "Please fill all fields"
            )

# ---------------- LOGIN ----------------
elif menu == "Login":

    st.title("🔐 Login")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        result = login_user(
            username,
            password
        )

        if result:

            st.session_state.logged_in = True
            st.session_state.username = username

            st.success(
                f"Welcome {username}"
            )

        else:
            st.error(
                "Invalid username or password"
            )

# ---------------- DASHBOARD ----------------
elif menu == "Dashboard":

    if not st.session_state.logged_in:

        st.warning("Please login first")

    else:

        st.title("🚀 Dashboard")

        st.write(
            f"Logged in as: **{st.session_state.username}**"
        )

        # ---------------- WEBSITE VIEWER ----------------
        st.subheader("🌍 Website Viewer")

        st.info(
            f"Free Uses Left: {st.session_state.free_uses}"
        )

        if st.session_state.free_uses > 0:

            website_url = st.text_input(
                "Enter Website URL",
                "https://witty-muse-hub.lovable.app/"
            )

            if st.button("Open Website"):

                st.session_state.free_uses -= 1

                components.iframe(
                    website_url,
                    height=700,
                    scrolling=True
                )

        else:

            st.error(
                "Free limit reached."
            )

            amount_option = 199

            # ---------------- OPEN POPUP ----------------
            if st.button("🚀 Upgrade to Pro"):

                st.session_state.show_payment_popup = True

            # ---------------- PAYMENT POPUP ----------------
            if st.session_state.show_payment_popup:

                st.markdown(f"""
                <div class="popup-overlay">

                    <div class="popup-card">

                        <div class="popup-title">
                        ✨ Upgrade to Pro
                        </div>

                        <div class="popup-subtitle">
                        Unlock unlimited website viewing
                        with premium access.
                        </div>

                        <div class="plan-box">

                            <h2>Pro Plan</h2>

                            <div class="price">
                            ₹{amount_option}
                            </div>

                            <div class="feature">
                            ✔ Unlimited Website Views
                            </div>

                            <div class="feature">
                            ✔ Fast Loading
                            </div>

                            <div class="feature">
                            ✔ Premium Features
                            </div>

                            <div class="feature">
                            ✔ No Daily Limits
                            </div>

                        </div>

                        <div class="bank-box">

                            <b>🏦 Bank Details</b><br><br>

                            Bank Name: State Bank of India<br>

                            Account Name: Dharavath Lokesh<br>

                            Account Number: 44825241862<br>

                            IFSC Code: SBIN0021595<br>

                            UPI ID: 8688104014-y571-2@ybl<br>

                        </div>

                    </div>

                </div>
                """, unsafe_allow_html=True)

                # ---------------- TRANSACTION ID ----------------
                transaction_id = st.text_input(
                    "Enter Transaction ID / UTR Number"
                )

                col1, col2 = st.columns(2)

                # ---------------- SUBMIT PAYMENT ----------------
                with col1:

                    if st.button("✅ Submit Payment"):

                        if transaction_id:

                            save_payment(
                                st.session_state.username,
                                f"₹{amount_option}",
                                "Bank Transfer",
                                transaction_id
                            )

                            st.success(
                                "Payment submitted successfully."
                            )

                            st.session_state.show_payment_popup = False

                        else:

                            st.error(
                                "Please enter transaction ID"
                            )

                # ---------------- CLOSE POPUP ----------------
                with col2:

                    if st.button("❌ Close"):

                        st.session_state.show_payment_popup = False

        # ---------------- PAYMENT HISTORY ----------------
        st.subheader("📜 Payment History")

        c.execute(
            """
            SELECT amount,
            payment_method,
            transaction_id,
            date
            FROM payments
            WHERE username=?
            """,
            (st.session_state.username,)
        )

        payments = c.fetchall()

        if payments:

            for payment in payments:

                st.write(f"""
Amount: {payment[0]}
Method: {payment[1]}
Transaction ID: {payment[2]}
Date: {payment[3]}
""")

        else:

            st.info("No payments found")

        # ---------------- LOGOUT ----------------
        if st.button("Logout"):

            st.session_state.logged_in = False
            st.session_state.username = ""

            st.success(
                "Logged out successfully"
            )
