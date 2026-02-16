import mysql.connector
import matplotlib.pyplot as plt


db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Waverly@12",
    database="finance_tracker"
)

cursor = db.cursor()

print("Connected to MySQL successfully!")

def add_expense():
    print("\nAvailable Categories:")

    cursor.execute("SELECT Category_ID, Category_Name FROM Category WHERE Type='Expense'")
    categories = cursor.fetchall()

    for cat in categories:
        print(cat[0], "-", cat[1])

    category_id = int(input("Choose Category ID: "))
    amount = float(input("Enter amount: "))
    date = input("Enter date (YYYY-MM-DD): ")
    mode = input("Payment mode: ")
    desc = input("Description: ")

    sql = """
    INSERT INTO Expense(User_ID, Category_ID, Amount, Date, Payment_Mode, Description)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (current_user, category_id, amount, date, mode, desc)

    cursor.execute(sql, values)
    db.commit()

    print("Expense added successfully!")


def add_income():
    source = input("Enter income source: ")
    amount = float(input("Enter amount: "))
    date = input("Enter date (YYYY-MM-DD): ")

    sql = """
    INSERT INTO Income(User_ID, Source, Amount, Date)
    VALUES (%s, %s, %s, %s)
    """

    values = (current_user, source, amount, date)


    cursor.execute(sql, values)
    db.commit()

    print("Income added successfully!")

def total_expense():
    cursor.execute("SELECT SUM(Amount) FROM Expense")
    result = cursor.fetchone()[0]

    print("Total Expense:", result)

def show_savings():
    cursor.execute("SELECT SUM(Amount) FROM Income")
    income = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(Amount) FROM Expense")
    expense = cursor.fetchone()[0] or 0

    print("Total Income:", income)
    print("Total Expense:", expense)
    print("Savings:", income - expense)

def show_expense_chart():
    cursor.execute("""
    SELECT Category.Category_Name, SUM(Expense.Amount)
    FROM Expense
    JOIN Category ON Expense.Category_ID = Category.Category_ID
    GROUP BY Category.Category_Name
    """)

    data = cursor.fetchall()

    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    plt.pie(amounts, labels=categories, autopct='%1.1f%%')
    plt.title("Expense Distribution")
    plt.show()

def register():
    print("\n---- Register New User ----")
    name = input("Enter Name: ")
    email = input("Enter Email: ")
    password = input("Create Password: ")
    occupation = input("Enter Occupation: ")

    sql = """
    INSERT INTO User(Name, Email, Password, Monthly_Income, Occupation)
    VALUES (%s, %s, %s, %s, %s)
    """

    values = (name, email, password, 0, occupation)

    try:
        cursor.execute(sql, values)
        db.commit()
        print("Registration successful! You can now login.")
    except:
        print("Email already exists or error occurred.")


def login():
    print("\n---- Login ----")
    email = input("Enter Email: ")
    password = input("Enter Password: ")

    sql = "SELECT * FROM User WHERE Email=%s AND Password=%s"
    values = (email, password)

    cursor.execute(sql, values)
    user = cursor.fetchone()

    if user:
        print("Login successful! Welcome", user[1])
        return user[0]   # returns User_ID
    else:
        print("Invalid email or password")
        return None


print("\n1. Login")
print("2. Register")

first_choice = input("Enter choice: ")

if first_choice == "2":
    register()

current_user = login()
if not current_user:
    exit()



while True:
    print("\n---- Personal Finance Tracker ----")
    print("1. Add Expense")
    print("2. Add Income")
    print("3. View Total Expense")
    print("4. View Savings")
    print("5. Show Expense Chart")
    print("6. Exit")


    choice = input("Enter choice: ")

    if choice == "1":
        add_expense()

    elif choice == "2":
        add_income()

    elif choice == "3":
        total_expense()

    elif choice == "4":
        show_savings()

    elif choice == "5":
        show_expense_chart()


    elif choice == "6":
        print("Goodbye!")
        break

    else:
        print("Invalid choice")

