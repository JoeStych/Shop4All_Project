# Shop4All_Project
A project created for a class at Saint Cloud State. It is an Ebay style application with users that are buyers and sellers of products. It uses PostgreSQL and MongoDB for data storage, Python for the application.

# Shop4All_Login.py
The initial program state. This is the login for both Sellers and Buyers. After authentication, it will open the corresponding program.

# Shop4All_ClientProgram.py
The application for the buyer. Contains features for changing client info (like passwords, addresses, etc.), browsing products by search or catagory, viewing previous orders, and viewing/leaving reviews. Reviews can only be left for products purchased.

# Shop4All_SellerProgram.py
The application for the seller of products. Contains features for changing Seller info (passwords, addresses, etc.), changing product info, viewing how products are selling, and viewing product reviews.

# Shop4All_SQL_DB.txt
Contains the structure for the SQL database.

# Shop4All_Tablefiller.py
A Python program designed to fill the SQL and MongoDB databases with dummy values for program testing.

# MongoDB Information
MongoDB was managed by using the GUI application. MongoDB was used to contain the product reviews. Each review had customerID, productID, a score out of 5, and review text.
