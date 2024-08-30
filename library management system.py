import mysql.connector
import re
from tabulate import tabulate
from datetime import datetime, timedelta

# Connect to MySQL Database
databaseobj = mysql.connector.connect(
    host='localhost',
    user='root',
    password='faith',
    database='library_management_system'
)
cursor = databaseobj.cursor()

# Create tables with improved error handling
def create_tables():
    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            role VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS authors (
            author_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            bio TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            book_id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            author_id INT,
            genre VARCHAR(100),
            description TEXT,
            status VARCHAR(50) DEFAULT 'Available',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES authors(author_id) ON DELETE SET NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            amount DECIMAL(10, 2) NOT NULL,
            method VARCHAR(50),
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(50),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memberships (
            membership_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            plan_name VARCHAR(255),
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            price DECIMAL(10, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            feedback_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            content TEXT,
            date_submitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            book_id INT,
            book_title VARCHAR(50),
            checkout_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date TIMESTAMP,
            return_date TIMESTAMP,
            fine_amount DECIMAL(10, 2) DEFAULT 0.00,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
        )
        ''')
        cursor.execute("CREATE TABLE IF NOT EXISTS Plans ("
                      "membership_id INT AUTO_INCREMENT PRIMARY KEY,"
                      "membership_plan VARCHAR(50),"
                      "price varchar(50))")

        databaseobj.commit()
        print("Tables created successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

create_tables()

# Function to validate password
def validate_password(password):
    if len(password) < 6 or len(password) > 24:
        print("Password must be between 6 and 24 characters long.")
        return False
    if not re.search(r'[A-Z]', password):
        print("Password must contain at least one capital letter.")
        return False
    if not re.search(r'[0-9]', password):
        print("Password must contain at least one number.")
        return False
    if not re.search(r'[\W_]', password):  # Special character validation
        print("Password must contain at least one special character.")
        return False
    return True

# Register new user or admin
def register():
    while True:
        try:
            print("Register your details here.")

            # Validate username
            while True:
                username = input("Create a username (alphanumeric): ")
                if not username.isalnum():
                    print("Username must be alphanumeric (letters and numbers only).")
                else:
                    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
                    if cursor.fetchone():
                        print("Username already exists, please choose another.")
                    else:
                        break

            # Validate password
            while True:
                password = input("Enter the password: ")
                if validate_password(password):
                    break

            while True:
                email = input("Enter the e-mail id: ")
                if re.fullmatch(r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$', email):
                    break
                else:
                    print("Wrong Attempt! Use a valid email format.")

            # Assign role based on username (for simplicity)
            if username.lower().startswith('admin'):
                role = 'admin'
            else:
                role = 'member'

            # Insert validated data into the database
            insert_query = "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (username, password, email, role))
            databaseobj.commit()
            print(f"You have successfully registered as a {role}!")
            break
        except mysql.connector.Error as e:
            print("Error:", e)

# Add a new author (Admin only)
def add_author():
    while True:
        try:
            name = input("Enter author's name: ")
            bio = input("Enter author's bio: ")

            insert_query = "INSERT INTO authors (name, bio) VALUES (%s, %s)"
            cursor.execute(insert_query, (name, bio))
            databaseobj.commit()
            print("Author added successfully!")
            break
        except mysql.connector.Error as err:
            print(f"Error: {err}")

# View all authors
def view_authors():
    try:
        cursor.execute("SELECT * FROM authors ORDER BY name ASC")
        result = cursor.fetchall()
        if result:
            print(tabulate(result, headers=["Author ID", "Name", "Bio", "Created At"]))
        else:
            print("No authors found.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Add a new book (Admin only)
def add_book():
    while True:
        try:
            title = input("Enter book title: ")
            author_id = int(input("Enter author ID: "))

            # Check if the author exists
            cursor.execute("SELECT * FROM authors WHERE author_id=%s", (author_id,))
            author = cursor.fetchone()

            if not author:
                print("Author does not exist. Please add the author first.")
                add_author()  # Option to add the author if they don't exist
                continue

            genre = input("Enter book genre: ")
            description = input("Enter book description: ")
            insert_query = "INSERT INTO books (title, author_id, genre, description, status) VALUES (%s, %s, %s, %s, 'Available')"
            cursor.execute(insert_query, (title, author_id, genre, description))
            databaseobj.commit()
            print("Book added successfully!")
            break
        except mysql.connector.Error as err:
            print(f"Error: {err}")

# List all books
def list_books():
    try:
        cursor.execute("SELECT * FROM books ORDER BY title ASC")
        result = cursor.fetchall()
        if result:
            print(tabulate(result, headers=["Book ID", "Title", "Author ID", "Genre", "Description", "Status", "Created At"]))
        else:
            print("No books found.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# View genres
def view_genres():
    try:
        cursor.execute("SELECT DISTINCT genre FROM books ORDER BY genre ASC")
        result = cursor.fetchall()
        if result:
            print(tabulate(result, headers=["Genre"]))
        else:
            print("No genres found.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# View author information
def view_author_info():
    try:
        query = "SELECT * FROM authors"
        cursor.execute(query)
        author = cursor.fetchall()
        if author:
            print(tabulate(author, headers=["Author ID", "Name", "Bio", "Created At"]))
        else:
            print("Author not found.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Borrow a book
def borrow_book():
    try:
        book_title = input("Enter book title to borrow: ")
        cursor.execute("SELECT book_id, status FROM books WHERE title=%s", (book_title,))
        book = cursor.fetchone()
        if not book:
            print("Book not found.")
            return

        book_id, status = book
        if status.lower() != 'available':
            print("Sorry, this book is currently unavailable.")
            return

        # Assuming user_id is retrieved from the session or passed as a parameter
        user_id = int(input("Enter your user ID: "))  # Or retrieve it from the session
        cursor.execute("SELECT * FROM transactions WHERE user_id=%s AND book_id=%s AND return_date IS NULL", (user_id, book_id))
        ongoing_transaction = cursor.fetchone()
        if ongoing_transaction:
            print("You already have this book borrowed.")
            return

        due_date = datetime.now() + timedelta(days=14)  # Assuming 14 days borrow period
        borrow_query = "INSERT INTO transactions (user_id, book_id, book_title, checkout_date, due_date) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(borrow_query, (user_id, book_id, book_title, datetime.now(), due_date))

        # Update book status to 'Borrowed'
        cursor.execute("UPDATE books SET status='Borrowed' WHERE book_id=%s", (book_id,))
        databaseobj.commit()
        print(f"Book '{book_title}' has been borrowed successfully. Due date is {due_date.strftime('%Y-%m-%d')}.")

        # Process Payment
        process_payment(user_id, book_title)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
def process_payment(user_id, book_title):
    try:
        amount = 5.00  # Assuming a fixed charge for borrowing a book; adjust as needed
        method = input("Enter payment method (e.g., Credit Card, PayPal): ")
        status = 'Completed'

        # Insert payment details into the payments table
        payment_query = "INSERT INTO payments (user_id, amount, method, status) VALUES (%s, %s, %s, %s)"
        cursor.execute(payment_query, (user_id, amount, method, status))
        databaseobj.commit()
        print(f"Payment of ${amount:.2f} for the book '{book_title}' has been processed successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


# Return a borrowed book
def return_book():
    try:
        book_title = input("Enter book title to return: ")
        user_id = int(input("Enter your user ID: "))  # Or retrieve it from the session

        cursor.execute("SELECT transaction_id, due_date FROM transactions WHERE user_id=%s AND book_title=%s AND return_date IS NULL", (user_id, book_title))
        transaction = cursor.fetchone()
        if not transaction:
            print("No such borrowed book found.")
            return

        transaction_id, due_date = transaction
        return_date = datetime.now()

        fine_amount = 0
        if return_date > due_date:
            days_late = (return_date - due_date).days
            fine_amount = days_late * 2.00  # Assuming $2 per day late fee

        return_query = "UPDATE transactions SET return_date=%s, fine_amount=%s WHERE transaction_id=%s"
        cursor.execute(return_query, (return_date, fine_amount, transaction_id))
        cursor.execute("UPDATE books SET status='Available' WHERE title=%s", (book_title,))
        databaseobj.commit()
        print(f"Book '{book_title}' returned successfully. Fine amount: ${fine_amount:.2f}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# View borrowing history
def view_borrowing_history():
    user_id = int(input("Enter your user ID: "))  # Or retrieve it from the session
    try:
        cursor.execute("SELECT * FROM transactions WHERE user_id=%s ORDER BY checkout_date DESC", (user_id,))
        result = cursor.fetchall()
        if result:
            print(tabulate(result, headers=["Transaction ID", "User ID", "Book ID", "Book Title", "Checkout Date", "Due Date", "Return Date", "Fine Amount"]))
        else:
            print("No borrowing history found.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Provide feedback
def provide_feedback():
    user_id = int(input("Enter your user ID: "))  # Or retrieve it from the session
    feedback_content = input("Enter your feedback: ")

    try:
        insert_query = "INSERT INTO feedback (user_id, content) VALUES (%s, %s)"
        cursor.execute(insert_query, (user_id, feedback_content))
        databaseobj.commit()
        print("Feedback submitted successfully!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# View feedback
def view_feedback():
    try:
        cursor.execute("SELECT f.feedback_id, u.username, f.content, f.date_submitted FROM feedback f JOIN users u ON f.user_id = u.user_id ORDER BY f.date_submitted DESC")
        feedbacks = cursor.fetchall()
        if feedbacks:
            print(tabulate(feedbacks, headers=["Feedback ID", "Username", "Content", "Date Submitted"]))
        else:
            print("No feedback available.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")



# Admin panel
def admin_panel():
    while True:
        print("\nAdmin Panel")
        print("1. Add Author")
        print("2. View Authors")
        print("3. Add Book")
        print("4. List Books")
        print("5. View Genres")
        print("6. View Author Information")
        print("7. View Feedback")  # New option to view feedback
        print("8. Logout")

        choice = input("Enter your choice: ")

        if choice == '1':
            add_author()
        elif choice == '2':
            view_authors()
        elif choice == '3':
            add_book()
        elif choice == '4':
            list_books()
        elif choice == '5':
            view_genres()
        elif choice == '6':
            view_author_info()
        elif choice == '7':
            view_feedback()  # Call the view feedback function
        elif choice == '8':
            break
        else:
            print("Invalid choice. Please try again.")


# Member panel
# Member panel
def member_panel():
    while True:
        print("\n--- Member Panel ---")
        print("1. View Membership Plans")
        print("2. View Books")
        print("3. View Genres")
        print("4. View Author Information")
        print("5. Borrow Book")
        print("6. Return Book")
        print("7. Provide Feedback")  # New option
        print("8. Logout")

        choice = input("Choose an option: ")

        if choice == "1":
            view_membership_plan()
        elif choice == "2":
            list_books()
        elif choice == "3":
            view_genres()
        elif choice == "4":
            view_author_info()
        elif choice == "5":
            borrow_book()
        elif choice == "6":
            return_book()
        elif choice == "7":
            provide_feedback()  # Call the feedback function
        elif choice == "8":
            break
        else:
            print("Invalid choice, please try again.")


# Function to add a membership plan
def add_membership_plan(user_id):
    try:
        # Check if the user already has an active membership plan
        cursor.execute("SELECT * FROM memberships WHERE user_id=%s AND end_date > %s", (user_id, datetime.now()))
        active_plan = cursor.fetchone()

        if active_plan:
            print("You already have an active membership plan.")
            return

        print("\nChoose a membership plan:")
        print("1. Basic Plan - $10/month")
        print("2. Premium Plan - $25/month")
        print("3. VIP Plan - $50/month")

        plan_choice = input("Enter your choice: ")

        if plan_choice == '1':
            plan_name = 'Basic Plan'
            price = 10.00
        elif plan_choice == '2':
            plan_name = 'Premium Plan'
            price = 25.00
        elif plan_choice == '3':
            plan_name = 'VIP Plan'
            price = 50.00
        else:
            print("Invalid choice.")
            return

        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)

        insert_query = "INSERT INTO memberships (user_id, plan_name, start_date, end_date, price) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (user_id, plan_name, start_date, end_date, price))
        databaseobj.commit()
        print(f"{plan_name} added successfully for user ID {user_id}!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def view_membership_plan():
    query = 'SELECT membership_id, membership_plan, price FROM plans'
    cursor.execute(query)
    query_result = cursor.fetchall()
    print(tabulate(query_result, headers=["membership_id", "membership_plan","price"]))
# Login function
# Login function
def login():
    username = input("Enter username: ")
    password = input("Enter password: ")

    cursor.execute("SELECT user_id, username, password, email, role FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()

    if user:
        user_id, username, password, email, role = user
        print(f"Welcome {username}!")

        if role == 'admin':
            admin_panel()
        else:
            # Check if the user has an active membership plan
            cursor.execute("SELECT * FROM memberships WHERE user_id=%s AND end_date > %s", (user_id, datetime.now()))
            active_plan = cursor.fetchone()

            if not active_plan:
                add_membership_plan(user_id)  # Prompt for membership plan if none exists

            member_panel()
    else:
        print("Invalid username or password.")


# Main function
def main():
    while True:
        print("\nLibrary Management System")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            register()
        elif choice == '2':
            login()
        elif choice == '3':
            print("Goodbye! Thankyou For Using Library Management System")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
