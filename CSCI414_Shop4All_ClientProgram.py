import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import psycopg2 as psyc
from pymongo import MongoClient
import bcrypt
import Shop4allfunctions as saf
from datetime import datetime

global main_window
global cursor
global buyerID
global change_window
global exitState
global collection


# Generic function used to change client information
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
            if change_function(cursor, buyerID, new_value) == True:
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




def view_change_client_info():
    info_window = tk.Toplevel(main_window)
    info_window.title("Client Information")
    info_window.geometry("300x425")

    cursor.execute("SELECT name, email, phone, address FROM buyers WHERE buyerID = %s;", (str(buyerID),))
    record = cursor.fetchall()
    
    label = tk.Label(info_window, text="Buyer Information", font=("Times New Roman", 16))
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

    # Special function for change password window
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
        
        # The logic for change password
        def passchange():
            new_pass = newPassword_entry.get()
            new2_pass = new2Password_entry.get()
            old_pass = oldPassword_entry.get()
            
            # Checking if passwords match
            if new_pass != new2_pass:
                messagebox.showerror("Change Failed", "Retyped Password does not match.")
                return
            
            # Updating the passwords
            cursor.execute("SELECT salt FROM buyers WHERE buyerID = %s;", (str(buyerID),))
            record = cursor.fetchall()
            
            check_password = bcrypt.hashpw(old_pass.encode('utf-8'), record[0][0].encode('utf-8'))
            cursor.execute("SELECT name FROM buyers WHERE password_hash::bytea = %s;", (check_password,))
            record = cursor.fetchall()
            if not record:
                messagebox.showerror("Change Failed", "Old password is invalid.")
                return
            else:
                cursor.execute("UPDATE buyers SET password_hash = %s WHERE buyerID = %s", (new_pass, buyerID))
                messagebox.showinfo("Success", "Operation successful. Password was changed.")
                
            

        change_button = tk.Button(change_window, text="Change", command=passchange)
        change_button.pack(pady=5)

        # Back button to close the change_window
        back_button = tk.Button(change_window, text="Back", command=change_window.destroy)
        back_button.pack(pady=10)




    # Logic for changing all client information
    def change_email():
        info_window.destroy()
        change_template("Change Email", "Enter the desired Email:", saf.change_buyer_email)
        change_window.wait_window()
        view_change_client_info()

    def change_phone():
        info_window.destroy()
        change_template("Change Phone Number", "Enter the desired phone #:", saf.change_buyer_phone)
        change_window.wait_window()
        view_change_client_info()

    def change_name():
        info_window.destroy()
        change_template("Change Name", "Enter the desired name:", saf.change_buyer_name)
        change_window.wait_window()
        view_change_client_info()

    def change_address():
        info_window.destroy()
        change_template("Change Address", "Enter the desired address:", saf.change_buyer_address)
        change_window.wait_window()
        view_change_client_info()

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



# View product window logic
def view_products():
    shopping_cart = {}
    
    # Create the product window
    product_window = tk.Toplevel(main_window)
    product_window.title("Product Page")
    product_window.geometry("800x500")
    
    label = tk.Label(product_window, text="Product Listing", font=("Times New Roman", 14))
    label.pack(side=tk.TOP, padx=45, pady=15, anchor=tk.W)

    # Create a listbox to display products
    product_listbox = tk.Listbox(product_window, selectmode=tk.SINGLE, width=80, height=15)
    product_listbox.pack(side=tk.LEFT, padx=10, pady=10)

    cursor.execute(f"SELECT p.name, p.stock, p.price, c.name FROM products p, categories c WHERE c.categoryid = p.categoryid;")
    record = cursor.fetchall()

    for i in range(20):
        if record[i][1] >= 0:
            product_details = record[i][0] + " | Stock: " + str(record[i][1]) + " | $" + str(record[i][2]) + " | Category: " + record[i][3]
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
        category = role_combobox.get()
        product_listbox.delete(0, tk.END)  # Clear the listbox
        
        # Handling searches of different kinds
        if search_term == "":
            if category == "Any":
                search_query = f"SELECT p.name, p.stock, p.price, c.name FROM products p, categories c WHERE c.categoryid = p.categoryid;"
            else:
                search_query = f'''
                SELECT p.name, p.stock, p.price, c.name FROM products p, categories c WHERE p.name ILIKE '%{search_term}%' AND c.name = '{category}' AND p.categoryid = c.categoryid;
                '''
        elif category == "Any":
            search_query = f'''
            SELECT p.name, p.stock, p.price, c.name FROM products p, categories c WHERE p.name ILIKE '%{search_term}%' AND c.categoryid = p.categoryid;
            '''
        else:
            search_query = f'''
            SELECT p.name, p.stock, p.price, c.name FROM products p, categories c WHERE p.name ILIKE '%{search_term}%' AND c.name = '{category}' AND p.categoryid = c.categoryid;
            '''
        
        # Refreshing the listbox with the new search
        cursor.execute(search_query)
        record = cursor.fetchall()
        
        for i in range(min(50, len(record))):
            if record[i][1] >= 0:
                product_details = record[i][0] + " | Stock: " + str(record[i][1]) + " | $" + str(record[i][2]) + " | Category: " + record[i][3]
                product_listbox.insert(tk.END, product_details)

    details_label = tk.Label(details_frame, text="Category:", font=("Times New Roman", 10))
    details_label.pack(pady=10)
    
    role_combobox = ttk.Combobox(details_frame, values=(saf.CATEGORIES + ["Any"]))
    role_combobox.pack(pady=10)
    role_combobox.set('Any')

    search_button = tk.Button(details_frame, text="Search", command=search_products)
    search_button.pack(pady=5)

    # View the reviews of a product
    def view_reviews():
        global collection # Used to interact with MongoDB
        selected_product = product_listbox.get(tk.ACTIVE)
        selected_product = selected_product.split('|')[0].strip()
        
        # Create a window
        review_window = tk.Toplevel(main_window)
        review_window.title("Product Page")
        review_window.geometry("500x600")
        
        label = tk.Label(review_window, text=("Reviews for " + selected_product), font=("Times New Roman", 14))
        label.pack(pady=15)
        
        cursor.execute("SELECT productid FROM products WHERE name = %s", (selected_product,))
        record = cursor.fetchone()[0]
        
        reviews_cursor = collection.find({"product_id": str(record)})
        
        # Fill text widget with review information
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


    # Button to add selected product to cart
    def add_to_cart():
        selected_product = product_listbox.get(tk.ACTIVE)
        if selected_product:
            quantity_window = tk.Toplevel(product_window)
            quantity_window.title("Quantity Page")
            quantity_window.geometry("300x200")
            
            label = tk.Label(quantity_window, text="Enter Desired Quantity", font=("Times New Roman", 12))
            label.pack(pady=10)

            quantity_entry = tk.Entry(quantity_window, width=30)
            quantity_entry.insert(0, "1")
            quantity_entry.pack(pady=10)
            
            def confirm_quantity():
                quan = quantity_entry.get()
                if int(quan) > 0:
                    nonlocal selected_product
                    selected_product = selected_product.split('|')[0].strip()
                    cursor.execute("SELECT productid FROM products WHERE name = %s", (selected_product,))
                    record = cursor.fetchall()
                    shopping_cart.update({record[0][0] : int(quan)})
                    quantity_window.destroy()
                    messagebox.showinfo("Add to Cart", f"Added to cart: {selected_product}")
                    product_window.focus_set()
                else:
                    messagebox.showinfo("Add to Cart Failed", "You must enter a quantity of at least 1.")
                    product_window.focus_set()
            
            confirm_button = tk.Button(quantity_window, text="Add to Cart", command=confirm_quantity)
            confirm_button.pack(pady=5)
        
        else:
            messagebox.showinfo("Add to Cart Failed", "You must select an item to add it to cart.")
            product_window.focus_set()
        
        

        

    add_to_cart_button = tk.Button(details_frame, text="Add to Cart", command=add_to_cart)
    add_to_cart_button.pack(pady=5)
    
    
    # All the logic and GUI of the shopping cart.
    def view_cart():
        cart_window = tk.Toplevel(product_window)
        cart_window.title("Product Page")
        cart_window.geometry("800x400")
        
        label = tk.Label(cart_window, text="Your Cart", font=("Times New Roman", 14))
        label.pack(side=tk.TOP, padx=45, pady=15, anchor=tk.W)
        
        cart_listbox = tk.Listbox(cart_window, selectmode=tk.SINGLE, width=80, height=15)
        cart_listbox.pack(side=tk.LEFT, padx=10, pady=10)
        
        for productid, quantity in shopping_cart.items():
            cursor.execute(f"SELECT p.name, p.stock, p.price, c.name FROM products p, categories c WHERE c.categoryid = p.categoryid AND p.productid = {productid};")
            record = cursor.fetchall()
            product_details = record[0][0] + " | Quantity: " + str(quantity) + " | Total: $" + str(record[0][2] * quantity) + " | Category: " + record[0][3]
            cart_listbox.insert(tk.END, product_details)
        
        # Create a scrollbar for the listbox
        cart_scrollbar = tk.Scrollbar(cart_window, orient=tk.VERTICAL)
        cart_scrollbar.config(command=cart_listbox.yview)
        cart_scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        cart_listbox.config(yscrollcommand=cart_scrollbar.set)
        
        # Create a frame to hold product details and buttons
        cart_details_frame = tk.Frame(cart_window)
        cart_details_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        def remove_from_cart():
            # Retreive item id and remove it
            selected_product = cart_listbox.get(tk.ACTIVE)
            if selected_product:
                selected_product = selected_product.split('|')[0].strip()
                cursor.execute("SELECT productid FROM products WHERE name = %s", (selected_product,))
                record = cursor.fetchall()
                shopping_cart.pop(record[0][0], None)
                
                # Regenerate the listbox
                cart_listbox.delete(0, tk.END)
                for productid, quantity in shopping_cart.items():
                    cursor.execute(f"SELECT p.name, p.stock, p.price, c.name FROM products p, categories c WHERE c.categoryid = p.categoryid AND p.productid = {productid};")
                    record = cursor.fetchall()
                    product_details = record[0][0] + " | Quantity: " + str(quantity) + " | Total: $" + str(record[0][2] * quantity) + " | Category: " + record[0][3]
                    cart_listbox.insert(tk.END, product_details)
                messagebox.showinfo("Remove from Cart", "Item has been removed from Cart")
                cart_window.focus_set()
            else:
                messagebox.showinfo("Remove from Cart Failed", "You must select an item to remove it from cart.")
                cart_window.focus_set()
        
        delete_button = tk.Button(cart_details_frame, text="Remove from Cart", command=remove_from_cart)
        delete_button.pack(pady=5)
        
        # Logic for changing the quantity of an item in the cart
        def cq_cart():
            selected_product = cart_listbox.get(tk.ACTIVE)
            quantity_window = tk.Toplevel(product_window)
            quantity_window.title("Quantity Page")
            quantity_window.geometry("300x200")
            
            label = tk.Label(quantity_window, text="Enter Desired Quantity", font=("Times New Roman", 12))
            label.pack(pady=10)

            quantity_entry = tk.Entry(quantity_window, width=30)
            quantity_entry.insert(0, "1")
            quantity_entry.pack(pady=10)
            
            def confirm_quantity():
                quan = quantity_entry.get()
                if int(quan) > 0: # Check for invalid entries
                    nonlocal selected_product
                    selected_product = selected_product.split('|')[0].strip()
                    cursor.execute("SELECT productid FROM products WHERE name = %s", (selected_product,))
                    record = cursor.fetchall()
                    shopping_cart.update({record[0][0] : int(quan)})
                    quantity_window.destroy()
                    
                    # Regenerate the listbox
                    cart_listbox.delete(0, tk.END)
                    for productid, quantity in shopping_cart.items():
                        cursor.execute(f"SELECT p.name, p.stock, p.price, c.name FROM products p, categories c WHERE c.categoryid = p.categoryid AND p.productid = {productid};")
                        record = cursor.fetchall()
                        product_details = record[0][0] + " | Quantity: " + str(quantity) + " | Total: $" + str(record[0][2] * quantity) + " | Category: " + record[0][3]
                        cart_listbox.insert(tk.END, product_details)
                    
                    
                    messagebox.showinfo("Updated Quantity", f"Quantity updated for: {selected_product}")
                    cart_window.focus_set()
                else:
                    messagebox.showinfo("Add to Cart Failed", "You must enter a quantity of at least 1.")
                    cart_window.focus_set()
            
            confirm_button = tk.Button(quantity_window, text="Add to Cart", command=confirm_quantity)
            confirm_button.pack(pady=5)
            
        
        cq_button = tk.Button(cart_details_frame, text="Change Quantity", command=cq_cart)
        cq_button.pack(pady=5)
        
        def confirm_order():
            current_timestamp = datetime.now()
            cursor.execute(f"INSERT INTO orders (date, buyerID) VALUES (%s, %s) RETURNING orderID;", (current_timestamp, buyerID))
            
            orderID = cursor.fetchone()[0]
            for productid, quantity in shopping_cart.items():
                cursor.execute("SELECT price FROM products WHERE productid = %s;", (productid,))
                record = cursor.fetchone()[0]
                price = record * quantity
                cursor.execute("INSERT INTO orderitems VALUES (%s, %s, %s, %s);", (str(orderID), str(productid), str(quantity), str(price)))
            
            cart_window.destroy()
            messagebox.showinfo("Order Successfully Placed", "You have successfully placed your order.")
            product_window.focus_set()
        
        confirm_button = tk.Button(cart_details_frame, text="Confirm Order", command=confirm_order)
        confirm_button.pack(pady=5)
        
        back_button = tk.Button(cart_details_frame, text="Back", command=cart_window.destroy)
        back_button.pack(pady=10)
        
        
    
    add_to_cart_button = tk.Button(details_frame, text="View / Modify Cart", command=view_cart)
    add_to_cart_button.pack(pady=5)
    
    
    back_button = tk.Button(details_frame, text="Back", command=product_window.destroy)
    back_button.pack(pady=10)



# View orders made
def view_orders():
    order_window = tk.Toplevel(main_window)
    order_window.title("Orders Page")
    order_window.geometry("750x400")
    
    label = tk.Label(order_window, text="Your Orders", font=("Times New Roman", 14))
    label.pack(side=tk.TOP, padx=45, pady=15, anchor=tk.W)
    
    order_listbox = tk.Listbox(order_window, selectmode=tk.SINGLE, width=80, height=15)
    order_listbox.pack(side=tk.LEFT, padx=10, pady=10)

    cursor.execute(f"SELECT orderid FROM orders WHERE buyerid = %s;", (buyerID,))
    order_record = cursor.fetchall()

    for orderid in order_record:
        cursor.execute("SELECT productid, quantity, total_price FROM orderitems WHERE orderid = %s;", (orderid,))
        record = cursor.fetchall()
        order_listbox.insert(tk.END, ("ORDER NUMBER: " + str(orderid[0])))
        for i in range (len(record)):
            cursor.execute("SELECT name FROM products WHERE productid = %s", (record[i][0],))
            product_name = cursor.fetchone()[0]
            order_details = product_name + " | Quantity: " + str(record[i][1]) + " | Total Pricce: $" + str(record[i][2])
            order_listbox.insert(tk.END, ("\t" + order_details))

    # Create a scrollbar for the listbox
    scrollbar = tk.Scrollbar(order_window, orient=tk.VERTICAL)
    scrollbar.config(command=order_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    order_listbox.config(yscrollcommand=scrollbar.set)
    
    back_button = tk.Button(order_window, text="Back", command=order_window.destroy)
    back_button.pack(pady=10, side=tk.BOTTOM, anchor=tk.W)
    
    def leave_review():
        selected_product = order_listbox.get(tk.ACTIVE)
        if selected_product.startswith("ORDER NUMBER"):
            messagebox.showinfo("Failure", "Please select a product to leave a review.")
            order_window.focus_set()
        else:
            selected_product = selected_product.split('|')[0].strip()
            cursor.execute("SELECT productid FROM products WHERE name = %s", (selected_product,))
            productid = cursor.fetchall()[0]
            leave_review_window = tk.Toplevel(main_window)
            leave_review_window.title("Leave a Review")
            leave_review_window.geometry("300x450")
            
            label = tk.Label(leave_review_window, text="Enter a Rating 0-5.", font=("Times New Roman", 12))
            label.pack(pady=10)
            
            rating_entry = tk.Entry(leave_review_window, width=30)
            rating_entry.pack(pady=10)

            label = tk.Label(leave_review_window, text="Enter your review below.", font=("Times New Roman", 12))
            label.pack(pady=10)

            text_widget = tk.Text(leave_review_window, wrap="word", width=40, height=10)
            text_widget.pack(padx=10, pady=10)
            
            def post_review():
                text_content = text_widget.get("1.0", tk.END)
                rating = rating_entry.get()
                if int(rating) < 0 or int(rating) > 5:
                    messagebox.showinfo("Failure", "Please enter a valid rating.")
                    return

                inserted_review = {
                    "product_id": f"{productid[0]}",
                    "customer_id": f"{buyerID}",
                    "rating": rating,
                    "comment": f"{text_content}",
                    "timestamp": datetime.now(),
                }
                
                collection.insert_one(inserted_review)
                messagebox.showinfo("Success", "Your review was successfully posted.")
                leave_review_window.destroy()
                order_window.focus_set()

            retrieve_button = tk.Button(leave_review_window, text="Post Review", command=post_review)
            retrieve_button.pack(pady=10)
            
            back_button = tk.Button(leave_review_window, text="Back", command=leave_review_window.destroy)
            back_button.pack(pady=15)
            
        
    
    leave_review_button = tk.Button(order_window, text="Leave Review for Selected Product", command=leave_review)
    leave_review_button.pack(pady=10, side=tk.BOTTOM, anchor=tk.W)
    



# Ensures that login program calls connection.commit() to save changes
def exit_state():
    global exitState
    exitState = 1
    main_window.destroy()



# Function called by login program
def client_main_program(psycursor, bID, conn):
    global cursor
    global buyerID
    global main_window
    global exitState
    
    cursor = psycursor
    buyerID = bID
    main_window = tk.Tk()
    exitState = 0
    
    # Initializing the MongoDB connection
    global collection
    
    client = MongoClient("mongodb://localhost:27017/")
    database = client["Shop4All_Reviews"]
    collection = database["reviews"]

    cursor.execute("SELECT name FROM buyers WHERE buyerID = %s;", (str(buyerID),))
    record = cursor.fetchall()
    buyer_greeting = "Logged in as " + record[0][0]
    
    
    
    # Create the main window
    main_window.title("Shop4All")
    main_window.geometry("400x300")

    # Create and place widgets in the main window
    tk.Label(main_window, text="Shop4All Buyer Main Menu", font=("Times New Roman", 16)).pack(pady=15)
    tk.Label(main_window, text=buyer_greeting, font=("Times New Roman", 12)).pack(pady=10)

    # Button to view/change client info
    btn_client_info = tk.Button(main_window, text="View / Change Client Info", command=view_change_client_info)
    btn_client_info.pack(pady=10)

    # Button to view products
    btn_view_products = tk.Button(main_window, text="View Products", command=view_products)
    btn_view_products.pack(pady=10)

    # Button to view orders
    btn_view_orders = tk.Button(main_window, text="View Orders", command=view_orders)
    btn_view_orders.pack(pady=10)
    
    # Button to save and exit
    btn_save = tk.Button(main_window, text="Save and Exit", command=exit_state)
    btn_save.pack(pady=10)

    # Start the Tkinter event loop
    main_window.mainloop()

    # Function doesn't return until the window is closed
    return exitState