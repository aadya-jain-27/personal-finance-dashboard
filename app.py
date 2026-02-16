import streamlit as st
import mysql.connector
import matplotlib.pyplot as plt

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Waverly@12",
    database="finance_tracker"
)

cursor = db.cursor()

st.sidebar.title("🔐 Account")

mode = st.sidebar.radio("Select Option", ["Login", "Register"])

# ---------------- REGISTER ----------------
if mode == "Register":
    name = st.sidebar.text_input("Name")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    occupation = st.sidebar.text_input("Occupation")

    if st.sidebar.button("Create Account"):
        try:
            cursor.execute("""
                INSERT INTO User(Name, Email, Password, Monthly_Income, Occupation)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, email, password, 0, occupation))

            db.commit()
            st.sidebar.success("Account created! Now login.")
        except:
            st.sidebar.error("Email already exists")

# ---------------- LOGIN ----------------
if mode == "Login":
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        cursor.execute(
            "SELECT User_ID, Name FROM User WHERE Email=%s AND Password=%s",
            (email, password)
        )
        user = cursor.fetchone()

        if user:
            st.session_state.user_id = user[0]
            st.session_state.user_name = user[1]
            st.session_state.email = email
            st.sidebar.success("Logged in!")
        else:
            st.sidebar.error("Invalid credentials")


# If not logged in, stop the app
if "user_id" not in st.session_state:
    
    st.markdown(
        """
        <div style='text-align: center; padding-top: 80px;'>
            <h1>Personal Finance Dashboard</h1>
            <h3>Track • Save • Grow</h3>
            <p style='font-size:18px; color:gray;'>
                Manage your income, expenses, and savings in one place.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info("👈 Please Login or Register from the sidebar to continue")

    st.stop()


# Use stored session values
user_id = st.session_state.user_id
user_name = st.session_state.user_name
email = st.session_state.email




st.success(f"Logged in as: {user_name} ({email})")
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()


st.title("💰 Personal Finance Dashboard")

cursor.execute("SELECT SUM(Amount) FROM Expense WHERE User_ID=%s", (user_id,))

total_expense = cursor.fetchone()[0] or 0

cursor.execute("SELECT SUM(Amount) FROM Income WHERE User_ID=%s", (user_id,))

total_income = cursor.fetchone()[0] or 0

savings = total_income - total_expense

st.subheader("📊 Summary")
st.write("Total Income:", total_income)
st.write("Total Expense:", total_expense)
st.write("Savings:", savings)

st.subheader("➕ Add Expense")

cursor.execute("SELECT Category_ID, Category_Name FROM Category WHERE Type='Expense'")
categories = cursor.fetchall()

category_dict = {name: cid for cid, name in categories}

selected_category = st.selectbox("Category", list(category_dict.keys()))


amount = st.number_input("Amount", min_value=0.0)
date = st.date_input("Date")
mode = st.text_input("Payment Mode")
desc = st.text_input("Description")

if st.button("Add Expense"):
    sql = """
    INSERT INTO Expense(User_ID, Category_ID, Amount, Date, Payment_Mode, Description)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (user_id, category_dict[selected_category], amount, date, mode, desc)

    cursor.execute(sql, values)
    db.commit()
    st.success("Expense Added!")
    st.rerun()

st.subheader("➕ Add Income")

source = st.text_input("Income Source (Salary, Freelance, Gift, etc)")
income_amount = st.number_input("Income Amount", min_value=0.0, key="income_amt")
income_date = st.date_input("Income Date", key="income_date")

if st.button("Add Income"):
    sql = """
    INSERT INTO Income(User_ID, Source, Amount, Date)
    VALUES (%s, %s, %s, %s)
    """
    values = (user_id, source, income_amount, income_date)

    cursor.execute(sql, values)
    db.commit()

    st.success("Income Added!")
    st.rerun()


st.subheader("📊 Expense Distribution")

cursor.execute("""
SELECT Category.Category_Name, SUM(Expense.Amount)
FROM Expense
JOIN Category ON Expense.Category_ID = Category.Category_ID
WHERE Expense.User_ID = %s
GROUP BY Category.Category_Name
""", (user_id,))


data = cursor.fetchall()

if data:
    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    fig, ax = plt.subplots()
    ax.pie(amounts, labels=categories, autopct='%1.1f%%')
    st.pyplot(fig)


