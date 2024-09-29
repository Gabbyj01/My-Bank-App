import sqlite3
import getpass
from hashlib import sha256

def hash_password(password):
    return sha256(password.encode()).hexdigest()



conn = sqlite3.connect("bank.db")
cursor = conn.cursor()

cursor.execute ("""
        CREATE TABLE IF NOT EXISTS users(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               full_name TEXT NOT NULL,
               username TEXT NOT NULL,
               password TEXT NOT NULL,
               balance REAL NOT NULL
        );       
""")

cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               user_id INTEGER NOT NULL,
               type_of_transaction TEXT NOT NULL,
               amount REAL NOT NULL,
               timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
               FOREIGN KEY (user_id) REFERENCES users(id) 
        );
""")

conn.commit()
conn.close()

def collect_and_validate_input(prompt, data_type, input_name, value_error_msg=""):
    data_type_map = {"int": int, "float": float}
    while True:
        field = input(prompt).strip()
        if not field:
            print(f"{input_name.title()} cannot be blank")
            continue
        if data_type == "str":
            return field
        try:
            field = data_type_map[data_type](field)
        except ValueError:
            print(value_error_msg)
            continue
        return field

# Function to add a new user
def users_registration():
        
     try:
             
          conn = sqlite3.connect("bank.db")
          cursor = conn.cursor()

          full_name = collect_and_validate_input("Enter your full name: ", "str", "Full Name")
          username = collect_and_validate_input("Enter your username: ", "str", "Username")

          while True:
               initial_deposit = collect_and_validate_input("Enter your initial deposit: ", "float", "Initial Deposit", "Initial deposit must be a number")
               if initial_deposit < 0:
                    print("Initial deposit must be a positive number.")
                    continue
               break

          while True:
               password = getpass.getpass("Password: ").strip()
               if not password:
                    print("Password cannot be blank")
                    continue

               repeat_password = getpass.getpass("Confirm Password: ").strip()
               if not repeat_password:
                    print("Password cannot be blank")
                    continue

               if password != repeat_password:
                    print("Paswords must match")
                    continue

               hashed_password = hash_password(password)
               break    
                 
          try:
               cursor.execute("""
               SELECT COUNT(*) FROM users
               WHERE username = ?
               """, (username,))
               if cursor.fetchone()[0] > 0:
                    print("User already exist, kindly choose another username.")
                    return
               
               cursor.execute("""
               INSERT INTO users(full_name, username, password, balance) 
               VALUES(?, ?, ?, ?)                
               """, (full_name, username, hashed_password, initial_deposit))
               conn.commit()
               print("Account created successfully")
          except sqlite3.IntegrityError as e:
               print(f"User already exist: {e}")
          finally:
               conn.close()
     except sqlite3.Error as e:
          print(f"Error occurred in connecting to DB: {e}")
     print("Registration successful")
          
     
          

# User Login function
def log_in():
     conn = sqlite3.connect("bank.db")
     cursor = conn.cursor()

     username = collect_and_validate_input("Enter username: ", "str", "Username") 
     while True:  
          password = getpass.getpass("password: ").strip()
          if not password:
               print("password cannot be blank")
               continue                  
          else:
               break

     try:
          hashed_password = hash_password(password)

          cursor.execute("""
                    SELECT id FROM users
                    WHERE username = ? AND password = ?
          """, (username, hashed_password,))

          user = cursor.fetchone()
          conn.close()
          if user:
               print("Login successful")
               return user[0]
          else:
               print("Invalid username or password")

     except sqlite3.Error as e:
          print(f"Error occurred in connecting to DB: {e}")
     return None
     
     
        
    

# Bank transactions functions

# Deposit function
def deposit(user_id, amount):
      try:
        conn = sqlite3.connect("bank.db")
        cursor = conn.cursor()

        cursor.execute("""
                UPDATE users
                SET balance = balance + ?
                WHERE id = ?
        """, (amount, user_id,))
        
        cursor.execute("""
                INSERT INTO transactions (user_id, type_of_transaction, amount) 
                VALUES(?, "deposit", ?)
        """, (user_id, amount,))
        conn.commit()
      except sqlite3.Error as e:
        print(f"An error has occurred: {e}")
      finally:  
        conn.close()

#Withdrawal function
def withdrawal(user_id, amount):
     try:
          conn = sqlite3.connect("bank.db")
          cursor = conn.cursor()

          cursor.execute("""
               SELECT balance FROM users
               WHERE id = ?
          """, (user_id,))
          
          current_balance = cursor.fetchone()
          
          if current_balance[0] < amount:
               print("You have insufficient fund")
               return
          
          if current_balance[0] >= amount:
               
               cursor.execute("""
                    UPDATE users
                    SET balance = balance - ?
                    WHERE id = ?
               """, (amount, user_id,))

          cursor.execute("""
                    INSERT INTO transactions (user_id, type_of_transaction, amount)
                    VALUES (?, 'withdrawal', ?)
          """, (user_id, amount,))
          conn.commit()
          print(f"Your withdrawal of {amount} is successful.")
     except sqlite3.Error as e:
          print(f"An error has occurred: {e}")
     finally:
          conn.close()

# Function to get balance
def get_balance(user_id):
     try:
        conn = sqlite3.connect("bank.db")
        cursor = conn.cursor()

        cursor.execute("""
                SELECT balance FROM users
                WHERE id = ?
        """, (user_id,))
        balance = cursor.fetchone()

        if balance is None:
             print("User not found.")
             return
        balance = balance[0]
        print(f"Dear customer your current balance is: ₦{balance:.2f}")
     except sqlite3.Error as e:
          print(f"Sorry an error has occurred: {e}")
     finally:
          conn.close()

# Transaction history function
def transaction_history(user_id):
     try:
          conn = sqlite3.connect("bank.db")
          cursor = conn.cursor()

          cursor.execute("""
                SELECT user_id, type_of_transaction, amount, timestamp FROM transactions
                WHERE user_id = ?
          """, (user_id,))
          transactions = cursor.fetchall()
          if transactions:
               for transaction in transactions:
                    print(f"User ID: {transaction[0]}, Type: {transaction[1]}, Amount: {transaction[2]}, Timestamp: {transaction[3]}")
          else:
               print("You have no transactions yet")
     except sqlite3.Error as e:
          print(f"Sorry an error as occurred: {e}")
     finally:
          conn.close()

banking_menu = """
1. Deposit
2. Withdraw
3. Check balance
4. Transaction history
5. Logout
"""

main_menu = """
1. Register as a new customer
2. Log in 
3. Exit
"""

def main():
     while True:
          print(main_menu)
          choice = input("Select an option from 1 - 3: ")

          if choice == "1":
               users_registration()
               continue
          elif choice == "2":
               
               user_id = log_in()

               if user_id is None:
                    continue
                    
               print(banking_menu)
               while True:
                    transaction_option = input("Selection your transaction option from 1 - 5: ").strip()
                    if transaction_option == "1":
                         while True:
                              amount = collect_and_validate_input("Enter amount you want to deposit: ", "float", "Amount", "Deposit Amount must be a number")
                              if amount <= 0:
                                   print("Deposit Amount must be greater than 0")
                                   continue
                              break
                         deposit(user_id, amount)
                         print(f"Your deposit of {amount} was successful")
                    elif transaction_option == "2":
                         while True:
                              amount = collect_and_validate_input("Enter amount you want to withdraw: ", "float", "Amount", "Withdrawal Amount must be a number")
                              if amount <= 0:
                                   print("Withdrawal Amount must be greater than 0")
                                   continue
                              break 
                         withdrawal(user_id, amount)                         
                    elif transaction_option == "3":
                         get_balance(user_id)
                         
                    elif transaction_option == "4":
                         transaction_history(user_id)
                         
                    elif transaction_option == "5":
                         print("Bye! Thank you for banking with us!")
                         break
                    else:
                         print("Invalid transaction option")
     
          elif choice == "3":
               print("Exiting the bank App")
               break
          else:
               print("You entered invalid choice")

main()


                              