import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import psycopg2 as psyc
from pymongo import MongoClient
import bcrypt
import Shop4allfunctions as saf
from datetime import datetime

global cursor
global sellerID
global main_window
global exitState



# Generic function used to change seller information
def change_template(title, label_text, change_function):
    # Create a new window for changing client information
    global change_window
    change_window = tk.Toplevel(main_window)
    change_window.title(title)
    change_window.geometry("300x300")

    # Label for what we're changing
    label = tk.Label(change_window, text=label_text, font=("Times New Roman", 12))
    label.pack(pady=10)

    # Entry field for the new value
    entry = tk.Entry(change_window, width=30)
    entry.pack(pady=10)

    # Change button
    def change():
        new_value = entry.get()
        if new_value:
            if change_function(cursor, sellerID, new_value) == True:
                messagebox.showinfo("Success", f"{title} operation was successful!")
                change_window.destroy()
            else:
                messagebox.showinfo("Failure", "Operation failed for an unknown reason.")
        else:
            messagebox.showwarning("Warning", "Please enter a new value.")

    change_button = tk.Button(change_window, text="Change", command=change)
    change_button.pack(pady=5)

    # Back button to close the change_window
    back_button = tk.Button(change_window, text="Back", command=change_window.destroy)
    back_button.pack(pady=10)


# Window that views and changes seller's information
def view_change_seller_info():
    info_window = tk.Toplevel(main_window)
    info_window.title("Client Information")
    info_window.geometry("300x425")

    # Getting required items from the database.
    cursor.execute("SELECT name, email, phone, address FROM sellers WHERE sellerID = %s;", (str(sellerID),))
    record = cursor.fetchall()
    
    label = tk.Label(info_window, text="Seller Information", font=("Times New Roman", 16))
    label.pack(pady=15)
    
    client_info = {
        'Name': record[0][0],
        'Email': record[0][1],
        'Phone': record[0][2],
        'Address': record[0][3],
    }

    for key, value in client_info.items():
        label = tk.Label(info_window, text=f"{key}: {value}")
        label.pack(pady=5)

    # Special function for change password
    def change_password():
        change_window = tk.Toplevel(main_window)
        change_window.title("Change Password")
        change_window.geometry("300x300")

        label = tk.Label(change_window, text="Enter Old Password", font=("Times New Roman", 12))
        label.pack(pady=10)

        oldPassword_entry = tk.Entry(change_window, width=30, show="*")
        oldPassword_entry.pack(pady=10)
        
        
        label = tk.Label(change_window, text="Enter New Password", font=("Times New Roman", 12))
        label.pack(pady=10)

        newPassword_entry = tk.Entry(change_window, width=30, show="*")
        newPassword_entry.pack(pady=10)
        
        label = tk.Label(change_window, text="Retype New Password", font=("Times New Roman", 12))
        label.pack(pady=10)

        new2Password_entry = tk.Entry(change_window, width=30, show="*")
        new2Password_entry.pack(pady=10)
        
        # Special function for changing the password because it's different than the others
        def passchange():
            new_pass = newPassword_entry.get()
            new2_pass = new2Password_entry.get()
            old_pass = oldPassword_entry.get()
            
            # Checking if entered passwords match
            if new_pass != new2_pass:
                messagebox.showerror("Change Failed", "Retyped Password does not match.")
                return
            
            cursor.execute("SELECT salt FROM sellers WHERE sellerID = %s;", (str(sellerID),))
            record = cursor.fetchall()
            
            check_password = bcrypt.hashpw(old_pass.encode('utf-8'), record[0][0].encode('utf-8'))
            cursor.execute("SELECT name FROM sellers WHERE password_hash::bytea = %s;", (check_password,))
            record = cursor.fetchall()
            if not record:
                messagebox.showerror("Change Failed", "Old password is invalid.")
                return
            else:
                cursor.execute("UPDATE sellers SET password_hash = %s WHERE sellerID = %s", (new_pass, sellerID))
                messagebox.showinfo("Success", "Operation successful. Password was changed.")
                
            

        change_button = tk.Button(change_window, text="Change", command=passchange)
        change_button.pack(pady=5)

        # Back button to close the change_window
        back_button = tk.Button(change_window, text="Back", command=change_window.destroy)
        back_button.pack(pady=10)




    # Logic for changing all client information
    def change_email():
        info_window.destroy()
        change_template("Change Email", "Enter the desired Email:", saf.change_seller_email)
        change_window.wait_window()
        view_change_seller_info()

    def change_phone():
        info_window.destroy()
        change_template("Change Phone Number", "Enter the desired phone #:", saf.change_seller_phone)
        change_window.wait_window()
        view_change_seller_info()

    def change_name():
        info_window.destroy()
        change_template("Change Name", "Enter the desired name:", saf.change_seller_name)
        change_window.wait_window()
        view_change_seller_info()

    def change_address():
        info_window.destroy()
        change_template("Change Address", "Enter the desired address:", saf.change_seller_address)
        change_window.wait_window()
        view_change_seller_info()

    password_button = tk.Button(info_window, text="Change Password", command=change_password)
    password_button.pack(pady=5)

    email_button = tk.Button(info_window, text="Change Email", command=change_email)
    email_button.pack(pady=5)

    phone_button = tk.Button(info_window, text="Change Phone", command=change_phone)
    phone_button.pack(pady=5)

    name_button = tk.Button(info_window, text="Change Name", command=change_name)
    name_button.pack(pady=5)

    address_button = tk.Button(info_window, text="Change Address", command=change_address)
    address_button.pack(pady=5)
    
    # Back button to close the info_window
    back_button = tk.Button(info_window, text="Back", command=info_window.destroy)
    back_button.pack(pady=10)




# All the logic for viewing a seller's own products
def view_my_products():
    # Create the product window
    product_window = tk.Toplevel(main_window)
    product_window.title("My Products Page")
    product_window.geometry("800x500")
    
    label = tk.Label(product_window, text="Product Listing", font=("Times New Roman", 14))
    label.pack(side=tk.TOP, padx=45, pady=15, anchor=tk.W)

    # Create a listbox to display products
    product_listbox = tk.Listbox(product_window, selectmode=tk.SINGLE, width=80, height=15)
    product_listbox.pack(side=tk.LEFT, padx=10, pady=10)

    # Getting seller's product information and putting it into the listbox
    cursor.execute(f"SELECT name, stock, price, productid FROM products WHERE sellerID = %s;", (sellerID,))
    record = cursor.fetchall()

    select_query = f'''
    SELECT oi.productid, COUNT(*) AS item_count
    FROM orderItems oi
    JOIN products p ON oi.productid = p.productid
    WHERE p.sellerid = '{sellerID}'
    GROUP BY oi.productid;
    '''
    cursor.execute(select_query)
    product_sales = cursor.fetchall()

    for item in record:
        success = False
        for i in range(len(product_sales)):
            if item[3] == product_sales[i][0]:
                success = True;
                break
        if success == True:
            product_details = item[0] + " | Stock: " + str(item[1]) + " | $" + str(item[2]) + " | Sold " + str(product_sales[i][1]) + " times."
        else:
            product_details = item[0] + " | Stock: " + str(item[1]) + " | $" + str(item[2]) + " | Sold 0 times."
        
        product_listbox.insert(tk.END, product_details)

    # Create a scrollbar for the listbox
    scrollbar = tk.Scrollbar(product_window, orient=tk.VERTICAL)
    scrollbar.config(command=product_listbox.yview)
    scrollbar.pack(side=tk.LEFT, fill=tk.Y)

    product_listbox.config(yscrollcommand=scrollbar.set)

    # Create a frame to hold product details and buttons
    details_frame = tk.Frame(product_window)
    details_frame.pack(side=tk.LEFT, padx=10, pady=10)

    # Label to display product details
    details_label = tk.Label(details_frame, text="Product Name Search", font=("Times New Roman", 14))
    details_label.pack(pady=10)

    # Entry for search
    search_entry = tk.Entry(details_frame, width=30)
    search_entry.pack(pady=10)

    # Button to search products
    def search_products():
        search_term = search_entry.get()
        product_listbox.delete(0, tk.END)  # Clear the listbox
        
        search_query = f'''
            SELECT p.name, p.stock, p.price FROM products WHERE name ILIKE '%{search_term}%' AND sellerid = '{sellerID}';
            '''
        
        cursor.execute(search_query)
        record = cursor.fetchall()

        # Getting specified items from the database
        select_query = f'''
        SELECT oi.productid, COUNT(*) AS item_count
        FROM orderItems oi
        JOIN products p ON oi.productid = p.productid
        WHERE p.sellerid = '{sellerID}'
        GROUP BY oi.productid;
        '''
        cursor.execute(select_query)
        product_sales = cursor.fetchall()

        for item in record:
            success = False
            for i in range(len(product_sales)):
                if item[3] == product_sales[i][0]:
                    success = True;
                    break
            if success == True:
                product_details = item[0] + " | Stock: " + str(item[1]) + " | $" + str(item[2]) + " | Sold " + str(product_sales[i][1]) + " times."
            else:
                product_details = item[0] + " | Stock: " + str(item[1]) + " | $" + str(item[2]) + " | Sold 0 times."
            
            product_listbox.insert(tk.END, product_details)


    search_button = tk.Button(details_frame, text="Search", command=search_products)
    search_button.pack(pady=5)
    
    
    # View the reviews of a product
    def view_reviews():
        global collection # Variable used to access the MongoDB
        selected_product = product_listbox.get(tk.ACTIVE)
        selected_product = selected_product.split('|')[0].strip()
        review_window = tk.Toplevel(main_window)
        review_window.title("Product Page")
        review_window.geometry("500x600")
        
        label = tk.Label(review_window, text=("Reviews for " + selected_product), font=("Times New Roman", 14))
        label.pack(pady=15)
        
        cursor.execute("SELECT productid FROM products WHERE name = %s", (selected_product,))
        record = cursor.fetchone()[0]
        
        reviews_cursor = collection.find({"product_id": str(record)})
        
        text_widget = tk.Text(review_window, wrap="word", width=40, height=40)
        text_widget.pack(side=tk.LEFT, padx=10, pady=10)
        
        for review in reviews_cursor:
            cursor.execute("SELECT name FROM buyers WHERE buyerid = %s;", (review['customer_id'],))
            buyer_name = cursor.fetchone()[0]
            text_widget.insert(tk.END, f"Name: " + buyer_name + " | Rating: " + str(review['rating']) + "\n" + review['comment'] + "\n\n")
        
        text_widget.config(state=tk.DISABLED)
        scrollbar = tk.Scrollbar(review_window, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        back_button = tk.Button(review_window, text="Back", command=review_window.destroy)
        back_button.pack(pady=10, side=tk.BOTTOM)
    
    reviews_button = tk.Button(details_frame, text="View Product Reviews", command=view_reviews)
    reviews_button.pack(pady=5)
    
    # Window for adding a new product to the store
    def add_product():
        change_window = tk.Toplevel(main_window)
        change_window.title("Add New Product")
        change_window.geometry("300x450")


        label = tk.Label(change_window, text="Product Name", font=("Times New Roman", 12))
        label.pack(pady=10)

        name_entry = tk.Entry(change_window, width=30)
        name_entry.pack(pady=10)
        
        
        label = tk.Label(change_window, text="Product Stock", font=("Times New Roman", 12))
        label.pack(pady=10)
        
        stock_entry = tk.Entry(change_window, width=30)
        stock_entry.pack(pady=10)
        
        
        label = tk.Label(change_window, text="Product Price", font=("Times New Roman", 12))
        label.pack(pady=10)

        price_entry = tk.Entry(change_window, width=30)
        price_entry.pack(pady=10)
        
        
        label = tk.Label(change_window, text="Product Category", font=("Times New Roman", 12))
        label.pack(pady=10)
        
        role_combobox = ttk.Combobox(change_window, values=(saf.CATEGORIES))
        role_combobox.pack(pady=10)

        # Logic for adding new product to the store
        def add_new_product():
            # Getting entered data from all fields
            p_name = name_entry.get()
            p_stock = stock_entry.get()
            p_price = price_entry.get()
            p_category = role_combobox.get()
            
            # Checking for empty fields
            if p_name == "" or p_stock == "" or p_price == "":
                messagebox.showinfo("Failure", "You must fill all fields to add a product.")
                change_window.focus_set()
                return
            
            # Checking for duplicate names
            cursor.execute("SELECT name FROM products WHERE name = %s", (p_name,))
            record = cursor.fetchall()
            
            if len(record) > 0:
                messagebox.showinfo("Failure", "There is already a product by that name.")
                change_window.focus_set()
                return
            
            # Fetching the category ID of the selected category
            cursor.execute("SELECT categoryid FROM categories WHERE name = %s", (p_category,))
            categoryID = cursor.fetchone()[0]
            
            # Product insertion
            insert_query = f'''
            INSERT INTO products (name, stock, price, sellerid, categoryid)
            VALUES ('{p_name}', '{p_stock}', '{p_price}', '{sellerID}', '{categoryID}');
            '''
            cursor.execute(insert_query)
            
            change_window.destroy()
            messagebox.showinfo("Success", "You have successfully added your product to the market.")
            product_window.focus_set()
            
            # Refreshing the listbox to see the new product
            product_listbox.delete(0, tk.END)  # Clear the listbox
            
            cursor.execute(f"SELECT name, stock, price, productid FROM products WHERE sellerID = %s;", (sellerID,))
            record = cursor.fetchall()

            select_query = f'''
            SELECT oi.productid, COUNT(*) AS item_count
            FROM orderItems oi
            JOIN products p ON oi.productid = p.productid
            WHERE p.sellerid = '{sellerID}'
            GROUP BY oi.productid;
            '''
            cursor.execute(select_query)
            product_sales = cursor.fetchall()

            for item in record:
                success = False
                for i in range(len(product_sales)):
                    if item[3] == product_sales[i][0]:
                        success = True;
                        break
                if success == True:
                    product_details = item[0] + " | Stock: " + str(item[1]) + " | $" + str(item[2]) + " | Sold " + str(product_sales[i][1]) + " times."
                else:
                    product_details = item[0] + " | Stock: " + str(item[1]) + " | $" + str(item[2]) + " | Sold 0 times."
                
                product_listbox.insert(tk.END, product_details)
            
            
            
        change_button = tk.Button(change_window, text="Add", command=add_new_product)
        change_button.pack(pady=5)

        # Back button to close the change_window
        back_button = tk.Button(change_window, text="Back", command=change_window.destroy)
        back_button.pack(pady=10)
    
    add_product_btn = tk.Button(details_frame, text="Add a New Product", command=add_product)
    add_product_btn.pack(pady=5)
    
    
    # Logic for removing a product
    def remove_product():
        selected_product = product_listbox.get(tk.ACTIVE)
        # Getting confirmation on whether to remove the product.
        if messagebox.askyesno("Are you sure?", "Are you sure you want to remove" + selected_product + "?") == True:
            # Setting the product stock to -1 to remove it from buyer lists.
            selected_product = selected_product.split('|')[0].strip()
            cursor.execute("UPDATE products SET stock = -1 WHERE name = %s", (selected_product,))
            messagebox.showinfo("Success", "You have successfully removed your product from the market.")
            product_window.focus_set()
            
            # Refreshing the listbox to see our changes
            product_listbox.delete(0, tk.END)  # Clear the listbox
            
            cursor.execute(f"SELECT name, stock, price, productid FROM products WHERE sellerID = %s;", (sellerID,))
            record = cursor.fetchall()

            select_query = f'''
            SELECT oi.productid, COUNT(*) AS item_count
            FROM orderItems oi
            JOIN products p ON oi.productid = p.productid
            WHERE p.sellerid = '{sellerID}'
            GROUP BY oi.productid;
            '''
            cursor.execute(select_query)
            product_sales = cursor.fetchall()

            for item in record:
                success = False
                for i in range(len(product_sales)):
                    if item[3] == product_sales[i][0]:
                        success = True;
                        break
                if success == True:
                    product_details = item[0] + " | Stock: " + str(item[1]) + " | $" + str(item[2]) + " | Sold " + str(product_sales[i][1]) + " times."
                else:
                    product_details = item[0] + " | Stock: " + str(item[1]) + " | $" + str(item[2]) + " | Sold 0 times."
                
                product_listbox.insert(tk.END, product_details)
        
        
    remove_btn = tk.Button(details_frame, text="Remove Selected Product", command=remove_product)
    remove_btn.pack(pady=5)
    
    # Window for changing product information
    def update_product():
        selected_product = product_listbox.get(tk.ACTIVE)
        selected_product = selected_product.split('|')[0].strip()
        
        # Getting all necessary information from the db
        select_query = f'''
        SELECT p.name, p.stock, p.price, c.name, p.productid
        FROM products p
        JOIN categories c ON p.categoryid = c.categoryid
        WHERE p.name = '{selected_product}' AND p.sellerid = '{sellerID}'
        GROUP BY p.name, p.stock, p.price, c.name, p.productid;
        '''
        
        cursor.execute(select_query)
        record = cursor.fetchall()
        p_stock = record[0][1]
        p_price = record[0][2]
        p_category = record[0][3]
        p_productID = record[0][4]
        
        change_window = tk.Toplevel(main_window)
        change_window.title("Update Product")
        change_window.geometry("300x450")


        label = tk.Label(change_window, text="Product Name", font=("Times New Roman", 12))
        label.pack(pady=10)

        name_entry = tk.Entry(change_window, width=30)
        name_entry.pack(pady=10)
        name_entry.insert(0, selected_product)
        
        
        label = tk.Label(change_window, text="Product Stock", font=("Times New Roman", 12))
        label.pack(pady=10)
        
        stock_entry = tk.Entry(change_window, width=30)
        stock_entry.pack(pady=10)
        stock_entry.insert(0, p_stock)
        
        
        label = tk.Label(change_window, text="Product Price", font=("Times New Roman", 12))
        label.pack(pady=10)

        price_entry = tk.Entry(change_window, width=30)
        price_entry.pack(pady=10)
        price_entry.insert(0, p_price)
        
        label = tk.Label(change_window, text="Product Category", font=("Times New Roman", 12))
        label.pack(pady=10)
        
        role_combobox = ttk.Combobox(change_window, values=(saf.CATEGORIES))
        role_combobox.pack(pady=10)
        role_combobox.set(p_category)
        
        # Logic for changing the product information
        def change_seller_item():
            p_name = name_entry.get()
            p_stock = stock_entry.get()
            p_price = price_entry.get()
            
            # Error checking
            if p_name == "" or p_stock == "" or p_price == "":
                messagebox.showinfo("Failure", "You must fill all fields to update a product.")
                change_window.focus_set()
                return
            
            cursor.execute("SELECT name FROM products WHERE name = %s AND productid != %s;", (p_name, p_productID))
            record = cursor.fetchall()
            
            if len(record) > 0:
                messagebox.showinfo("Failure", "There is already a product by that name.")
                change_window.focus_set()
                return
            
            # Structuring and executing the update
            update_query = f'''
            UPDATE products
            SET name = '{p_name}', stock = '{p_stock}', price = '{p_price}'
            WHERE name = '{selected_product}' AND sellerid = '{sellerID}';
            '''
            
            cursor.execute(update_query)
            
            change_window.destroy()
            messagebox.showinfo("Success", "You have successfully updated your product.")
            product_window.focus_set()
            
            # Refreshing the listbox to view our changes
            product_listbox.delete(0, tk.END)  # Clear the listbox
            
            cursor.execute(f"SELECT name, stock, price, productid FROM products WHERE sellerID = %s;", (sellerID,))
            record = cursor.fetchall()

            select_query = f'''
            SELECT oi.productid, COUNT(*) AS item_count
            FROM orderItems oi
            JOIN products p ON oi.productid = p.productid
            WHERE p.sellerid = '{sellerID}'
            GROUP BY oi.productid;
            '''
            cursor.execute(select_query)
            product_sales = cursor.fetchall()

            for item in record:
                success = False
                for i in range(len(product_sales)):
                    if item[3] == product_sales[i][0]:
                        success = True;
                        break
                if success == True:
                    product_details = item[0] + " | Stock: " + str(item[1]) + " | $" + str(item[2]) + " | Sold " + str(product_sales[i][1]) + " times."
                else:
                    product_details = item[0] + " | Stock: " + str(item[1]) + " | $" + str(item[2]) + " | Sold 0 times."
                
                product_listbox.insert(tk.END, product_details)
                
        
        change_button = tk.Button(change_window, text="Change", command=change_seller_item)
        change_button.pack(pady=5)

        # Back button to close the change_window
        back_button = tk.Button(change_window, text="Back", command=change_window.destroy)
        back_button.pack(pady=10)
    
    
    update_btn = tk.Button(details_frame, text="Update", command=update_product)
    update_btn.pack(pady=5)
    
    
    back_button = tk.Button(details_frame, text="Back", command=product_window.destroy)
    back_button.pack(pady=10)




# Sends the exit state back to parent program
def exit_state():
    global exitState
    exitState = 1
    main_window.destroy()

# What is first called by the login program
def seller_main_program(psycursor, sID):
    global cursor
    global sellerID
    global main_window
    global exitState
    
    cursor = psycursor
    sellerID = sID
    main_window = tk.Tk()
    exitState = 0
    
    # Initializing the MongoDB connection
    global collection
    
    client = MongoClient("mongodb://localhost:27017/")
    database = client["Shop4All_Reviews"]
    collection = database["reviews"]

    cursor.execute("SELECT name FROM sellers WHERE sellerID = %s;", (str(sellerID),))
    record = cursor.fetchall()
    buyer_greeting = "Logged in as " + record[0][0]
    
    
    
    # Create the main window
    main_window.title("Shop4All")
    main_window.geometry("400x300")

    # Create and place widgets in the main window
    tk.Label(main_window, text="Shop4All Seller Main Menu", font=("Times New Roman", 16)).pack(pady=15)
    tk.Label(main_window, text=buyer_greeting, font=("Times New Roman", 12)).pack(pady=10)

    # Button to view/change client info
    btn_client_info = tk.Button(main_window, text="View / Change Client Info", command=view_change_seller_info)
    btn_client_info.pack(pady=10)

    # Button to view products
    btn_view_products = tk.Button(main_window, text="View Products", command=view_my_products)
    btn_view_products.pack(pady=10)
    
    # Button to save and exit
    btn_save = tk.Button(main_window, text="Save and Exit", command=exit_state)
    btn_save.pack(pady=10)

    # Start the Tkinter event loop
    main_window.mainloop()

    # Function doesn't return until the window is closed
    return exitState