import pymysql
from tabulate import tabulate

cnxn = pymysql.connect(host="localhost", user="root", password="tiger", db="atm")
atm = cnxn.cursor()

def subMenu():
    try:
        global acc_no
        print('''
    ===============================================================================
    +++++++++++++++++++++++ Automated Tellar Machine ++++++++++++++++++++++++++++++
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
        print("Error occured: ", e)

def mainMenu():
    try:
        global acc_no
        print('''
    ===============================================================================
    +++++++++++++++++++++++ Automated Tellar Machine ++++++++++++++++++++++++++++++
    ===============================================================================
            ''')
        while True:
            x = int(input("Enter your account number: "))
            y = int(input("Enter yout pin: "))
            atm.execute("select acno, pin from accounts;")
            z = atm.fetchall()
            for i in z:
                if x == z[0] and y == z[1]:
                    print("Account logged in successfuly.")
                    acc_no = x
                    subMenu()
                else:
                    print("Incorrect combination. Try again.")
    except Exception as e:
        print("Error occured: ", e)

def chkbal():
    try:
        global acc_no
        print('''
    ===============================================================================
    +++++++++++++++++++++++ Automated Tellar Machine ++++++++++++++++++++++++++++++
    ===============================================================================
            ''')
        atm.execute("select balance from accounts where acno = %s;", acc_no)
        x = atm.fetchone()
        y = ["Balance"]
        print(tabulate(x, headers=y, tablefmt="fancy_grid"))
    except Exception as e:
        print("Error occured: ", e)

def depo():
    try:
        global acc_no
        print('''
    ===============================================================================
    +++++++++++++++++++++++ Automated Tellar Machine ++++++++++++++++++++++++++++++
    ===============================================================================
            ''')
        x = int(input("Enter amount to deosit: "))
        atm.execute("update accounts set balance = balance + %s where acno = %s;", (x, acc_no))
        cnxn.commit()
        dr = "None"
        cr = "Yes"
        atm.execute("insert into trans_log(account, amount, debit, credit) values (%s, %s, %s, %s);", (acc_no, x, cr, dr))
        cnxn.commit()
        print("Amount deposited successfuly.")
    except Exception as e:
        print("Error occured: ", e)    

def withd():
    try:
        global acc_no
        print('''
    ===============================================================================
    +++++++++++++++++++++++ Automated Tellar Machine ++++++++++++++++++++++++++++++
    ===============================================================================
            ''')
        x = int(input("Enter amount to withdraw: "))
        atm.execute("update accounts set balance = balance - %s where acno = %s;", (x, acc_no))
        cnxn.commit()
        dr = "Yes"
        cr = "None"
        atm.execute("insert into trans_log(account, amount, debit, credit) values (%s, %s, %s, %s);", (acc_no, x, dr, cr))
        cnxn.commit()
        print("Amount withdrawn successfuly.")
    except Exception as e:
        print("Error occurred: ", e)

def trnfr():
    try:
        global acc_no
        global trnfracc
        print('''
    ===============================================================================
    +++++++++++++++++++++++ Automated Tellar Machine ++++++++++++++++++++++++++++++
    ===============================================================================
            ''')
        while True:
            trnfracc = int(input("Enter account number to transfer: "))
            atm.execute("select acno from accounts;")
            y = atm.fetchone()
            for i in y:
                if trnfracc == y[i]:
                    trnfrmain()
                else:
                    print("No valid account entered. Try again.")
    except Exception as e:
        print("Error occured: ", e)

def trnfrmain():
    try:
        global acc_no
        global trnfracc
        print('''
    ===============================================================================
    +++++++++++++++++++++++ Automated Tellar Machine ++++++++++++++++++++++++++++++
    ===============================================================================
            ''')
        x = int(input("Enter account to transfer: "))
        atm.execute("update accounts set balance = balance - %s where acno = %s;", (x, acc_no))
        cnxn.commit()
        atm.execute("update accounts set balance = balance + %s where acno = %s;", (x, trnfracc))
        cnxn.commit()
        dr = "You"
        cr = trnfracc
        atm.execute("insert into trans_log(account, amount, debit, credit) values (%s, %s, %s, %s);", (acc_no, x, dr, cr))
        cnxn.commit()
        atm.execute("insert into trans_log(account, amount, debit, credit) values (%s, %s, %s, %s);", (cr, x, cr, acc_no))
        print("Amount transfered successfuly.")
    except Exception as e:
        print("Error occred: ", e)

def tnxn():
    try:
        global acc_no
        print('''
    ===============================================================================
    +++++++++++++++++++++++ Automated Tellar Machine ++++++++++++++++++++++++++++++
    ===============================================================================
            ''')
        atm.execute("select * from trans_log where account = %s;", acc_no)
        x = atm.fetchall()
        y = ["Transaction ID", "Account", "Amount", "Account Debited", "Account Credited", "Time of transaction"]
        print(tabulate(x, headers=y, tablefmt="fancy_grid"))
    except Exception as e:
        print("Error occured: ", e)

mainMenu()