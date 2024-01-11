import tkinter as tk
import psycopg2 as psyc
import bcrypt
from tkinter import messagebox
from tkinter import ttk
from tkinter import PhotoImage
from PIL import ImageFilter, ImageTk, Image
import CSCI414_Shop4All_ClientProgram as buyerProgram
import CSCI414_Shop4All_SellerProgram as sellerProgram

# DUMMY BUYER USERNAME: edwardblake@gmail.com
# DUMMY BUYER PASSWORD: password

# DUMMY SELLER USERNAME: wallyweaver@hotmail.com
# DUMMY SELLER PASSWORD: password


print("Attempting to connect to the PostgreSQL Database...")

#Connect to the database
try:
    connection = psyc.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="password"
    )
    
    cursor = connection.cursor()
    
    print("Connection successful.\n")


except (Exception, psyc.Error) as error:
    print("Error while connecting to PostgreSQL.")
    quit()

print("Connected to the PostgreSQL database.")

def authenticate(username, password, role):
    if role == "Buyer":
        cursor.execute("SELECT salt FROM buyers WHERE email = %s;", (username,))
    else:
        cursor.execute("SELECT salt FROM sellers WHERE email = %s;", (username,))
    
    record = cursor.fetchall()

    if not record:
        return False
    else:
        check_password = bcrypt.hashpw(password.encode('utf-8'), record[0][0].encode('utf-8'))
        
        if role == "Buyer":
            cursor.execute("SELECT name FROM buyers WHERE password_hash::bytea = %s;", (check_password,))
        else:
            cursor.execute("SELECT name FROM sellers WHERE password_hash::bytea = %s;", (check_password,))
        
        record = cursor.fetchall()
        if not record:
            return False
        else:
            return True

def resize_image(image_path, width, height):
    original_image = Image.open(image_path)
    resized_image = original_image.resize((width, height), Image.LANCZOS)
    return ImageTk.PhotoImage(resized_image)

def on_login_button_click():
    entered_username = username_entry.get()
    entered_password = password_entry.get()
    selected_role = role_combobox.get()

    if authenticate(entered_username, entered_password, selected_role):
        if selected_role == "Buyer":
            cursor.execute("SELECT name, buyerID FROM buyers WHERE email = %s;", (entered_username,))
        else:
            cursor.execute("SELECT name, sellerID FROM sellers WHERE email = %s;", (entered_username,))
        record = cursor.fetchall()
        
        login_message = "Welcome " + record[0][0] + "."
        # If authentication is successful, close the login window
        messagebox.showinfo("Login Successful", login_message)
        login_window.destroy()
        
        if selected_role == "Buyer":
            if buyerProgram.client_main_program(cursor, record[0][1], connection) == 1:
                connection.commit()
                print("Changes saved.")
        else:
            if sellerProgram.seller_main_program(cursor, record[0][1]) == 1:
                connection.commit()
                print("Changes saved.")
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")


# Create the main login window
login_window = tk.Tk()
login_window.title("Login")

login_window.geometry("300x420")

# Create and place widgets in the login window
tk.Label(login_window, text="Shop4All Login", font=("Times New Roman", 16)).pack(pady=20)

# The logo
logo_image = resize_image("D:\\Desktop\\Projects\\Code\\Python\\Shop4AllLogo.png", 50, 50)
tk.Label(login_window, image=logo_image, font=("Times New Roman", 16)).pack(pady=10)

tk.Label(login_window, text="Username:").pack(pady=5)
username_entry = tk.Entry(login_window, width=30)
username_entry.pack(pady=5)

tk.Label(login_window, text="Password:").pack(pady=5)
password_entry = tk.Entry(login_window, show="*", width=30)
password_entry.pack(pady=5)

label = tk.Label(login_window, text="Select Role:")
label.pack(pady=10)

# Create a Combobox with options 'buyer' and 'seller'
role_combobox = ttk.Combobox(login_window, values=['Buyer', 'Seller'])
role_combobox.pack(pady=10)
role_combobox.set('Buyer')

login_button = tk.Button(login_window, text="Login", command=on_login_button_click)
login_button.pack(pady=10)

# Start the Tkinter event loop
login_window.mainloop()