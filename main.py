import pymysql
from tabulate import tabulate

cnxn = pymysql.connect(host="localhost", user="root", password="tiger", db="atm")
atm = cnxn.cursor()

def subMenu():
    try:
        global acc_no
        print('''
    ===============================================================================
    +++++++++++++++++++++++ Automated Teller Machine ++++++++++++++++++++++++++++++
    ===============================================================================
            ''')
        print('''
    1. Check Balance
    2. Deposit 
    3. Withdraw
    4. Transfer
    5. View Transaction
    6. Log Out
            ''')
        x = int(input("Enter your choice: "))
        if x == 1:
            chkbal()
        elif x == 2:
            depo()
        elif x == 3:
            withd()
        elif x == 4:
            trnfr()
        elif x == 5:
            tnxn()
        else: 
            mainMenu()
    except Exception as e:
        print("Error occurred: ", e)

def mainMenu():
    try:
        global acc_no
        print('''
    ===============================================================================
    +++++++++++++++++++++++ Automated Teller Machine ++++++++++++++++++++++++++++++
    ===============================================================================
            ''')
        found = False
        while True:
            x = int(input("Enter your account number: "))
            y = int(input("Enter your pin: "))
            atm.execute("select acno, pin from accounts;")
            z = atm.fetchall()
            for i in z:
                if x == i[0] and y == i[1]:
                    print("Account logged in successfully.")
                    acc_no = x
                    subMenu()
                    found = True
                    break
            if not found:
                print("Incorrect combination. Try again.")
    except Exception as e:
        print("Error occurred: ", e)

def chkbal():
    try:
        global acc_no
        print('''
    ===============================================================================
    +++++++++++++++++++++++ Automated Teller Machine ++++++++++++++++++++++++++++++
    ===============================================================================
        ''')
        atm.execute("SELECT balance FROM accounts WHERE acno = %s;", (acc_no,))
        x = atm.fetchone()
        if x:
            print(tabulate([[x[0]]], headers=["Balance"], tablefmt="fancy_grid"))
            subMenu()
        else:
            print("Account not found.")
    except Exception as e:
        print("Error occurred:", e)

def depo():
    try:
        global acc_no
        print('''
    ===============================================================================
    +++++++++++++++++++++++ Automated Teller Machine ++++++++++++++++++++++++++++++
    ===============================================================================
            ''')
        x = int(input("Enter amount to deposit: "))
        if x <= 0:
            print("Amount must be positive.")
            subMenu()
            return
            
        atm.execute("update accounts set balance = balance + %s where acno = %s;", (x, acc_no))
        cnxn.commit()
        
        # Fixed transaction logging
        atm.execute("insert into trans_log(account, amount, debit, credit) values (%s, %s, %s, %s);", (acc_no, x, 0, acc_no))
        cnxn.commit()
        print("Amount deposited successfully.")
        subMenu()
    except Exception as e:
        print("Error occurred: ", e)    

def withd():
    try:
        global acc_no
        print('''
    ===============================================================================
    +++++++++++++++++++++++ Automated Teller Machine ++++++++++++++++++++++++++++++
    ===============================================================================
            ''')
        x = int(input("Enter amount to withdraw: "))
        if x <= 0:
            print("Amount must be positive.")
            subMenu()
            return
            
        # Check balance before withdrawal
        atm.execute("SELECT balance FROM accounts WHERE acno = %s;", (acc_no,))
        current_balance = atm.fetchone()
        if current_balance and current_balance[0] < x:
            print(f"Insufficient balance. Available balance: {current_balance[0]}")
            subMenu()
            return
            
        atm.execute("update accounts set balance = balance - %s where acno = %s;", (x, acc_no))
        cnxn.commit()
        
        # Fixed transaction logging
        atm.execute("insert into trans_log(account, amount, debit, credit) values (%s, %s, %s, %s);", (acc_no, x, acc_no, 0))
        cnxn.commit()
        print("Amount withdrawn successfully.")
        subMenu()
    except Exception as e:
        print("Error occurred: ", e)

def trnfr():
    try:
        global acc_no
        print('''
    ===============================================================================
    +++++++++++++++++++++++ Automated Teller Machine ++++++++++++++++++++++++++++++
    ===============================================================================
            ''')
        
        # Get transfer account number
        try:
            trnfracc = int(input("Enter account number to transfer to: "))
            if trnfracc <= 0:
                print("Account number must be positive.")
                subMenu()
                return
        except ValueError:
            print("Invalid account number. Please enter a valid number.")
            subMenu()
            return
        
        # Check if transfer account exists
        atm.execute("SELECT acno FROM accounts WHERE acno = %s;", (trnfracc,))
        receiver_check = atm.fetchone()
        if receiver_check is None:
            print("Recipient account does not exist.")
            subMenu()
            return
        
        # Check if trying to transfer to same account
        if trnfracc == acc_no:
            print("Cannot transfer to the same account.")
            subMenu()
            return
        
        # Get transfer amount
        try:
            amount = float(input("Enter amount to transfer: "))
            if amount <= 0:
                print("Amount must be positive.")
                subMenu()
                return
        except ValueError:
            print("Invalid amount. Please enter a valid number.")
            subMenu()
            return
        
        # Check sender's balance
        atm.execute("SELECT balance FROM accounts WHERE acno = %s;", (acc_no,))
        sender_balance = atm.fetchone()
        if sender_balance is None:
            print("Your account does not exist.")
            subMenu()
            return
            
        if sender_balance[0] < amount:
            print(f"Insufficient balance. Available balance: {sender_balance[0]}")
            subMenu()
            return
        
        # Perform the transfer
        try:
            # Debit from sender
            atm.execute("UPDATE accounts SET balance = balance - %s WHERE acno = %s;", (amount, acc_no))
            if atm.rowcount == 0:
                raise Exception("Failed to update sender account")
            
            # Credit to receiver
            atm.execute("UPDATE accounts SET balance = balance + %s WHERE acno = %s;", (amount, trnfracc))
            if atm.rowcount == 0:
                raise Exception("Failed to update receiver account")
            
            # Log transactions
            atm.execute("INSERT INTO trans_log(account, amount, debit, credit) VALUES (%s, %s, %s, %s);", 
                       (acc_no, amount, acc_no, trnfracc))
            atm.execute("INSERT INTO trans_log(account, amount, debit, credit) VALUES (%s, %s, %s, %s);", 
                       (trnfracc, amount, acc_no, trnfracc))
            
            cnxn.commit()
            print(f"Amount {amount} transferred successfully to account {trnfracc}.")
            
        except Exception as transaction_error:
            cnxn.rollback()
            print(f"Transaction failed: {transaction_error}")
        
        subMenu()
        
    except Exception as e:
        print(f"Error occurred: {e}")
        try:
            cnxn.rollback()
        except:
            pass
        subMenu()

def tnxn():
    try:
        global acc_no
        print('''
    ===============================================================================
    +++++++++++++++++++++++ Automated Teller Machine ++++++++++++++++++++++++++++++
    ===============================================================================
        ''')
        atm.execute("SELECT * FROM trans_log WHERE account = %s ORDER BY time DESC;", (acc_no,))
        x = atm.fetchall()
        if x:
            y = ["Transaction ID", "Account", "Amount", "Account Debited", "Account Credited", "Time of Transaction"]
            print(tabulate(x, headers=y, tablefmt="fancy_grid"))
        else:
            print("No transactions found.")
        subMenu()
    except Exception as e:
        print("Error occurred:", e)
        subMenu()

mainMenu()