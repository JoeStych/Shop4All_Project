from faker import Faker
import random
from datetime import datetime
from pymongo import MongoClient

CATEGORIES = [
    "Electronics",
    "Clothing",
    "Home and Furniture",
    "Beauty and Personal Care",
    "Books and Media",
    "Sports and Outdoors",
    "Automotive",
    "Health and Wellness",
    "Toys and Games",
    "Jewelry and Watches",
    "Pet Supplies",
    "Office and School Supplies",
    "Food and Groceries",
    "Home Improvement",
    "Travel and Luggage",
    "Arts and Crafts",
    "Music Instruments",
    "Garden and Outdoor Living",
    "Baby and Kids",
    "Special Occasions"
]

ADJECTIVES = [
    "Elegant",
    "Spacious",
    "Luxurious",
    "Compact",
    "Stylish",
    "Modern",
    "Durable",
    "Sleek",
    "Innovative",
    "Efficient",
    "Versatile",
    "Affordable",
    "Premium",
    "High-quality",
    "Convenient",
    "Reliable",
    "Fashionable",
    "Functional",
    "Sophisticated",
    "Eco-friendly",
    "Slippery",
    "Comfortable",
    "Economical",
    "High-performance",
    "Customizable"
]

NOUNS = [
    "Car",
    "Smartphone",
    "Laptop",
    "Watch",
    "Couch",
    "Washing Machine",
    "Shoes",
    "Handbag",
    "Camera",
    "Headphones",
    "Bicycle",
    "Jewelry",
    "Sunglasses",
    "Clothing",
    "Gadget",
    "Gaming Console",
    "Sofa",
    "Dryer",
    "Fitness Equipment",
    "Vacation Package",
    "Tools",
    "Artwork",
    "Instrument",
    "Toy",
    "Home Theater System"
]

REVIEWS = [
    "This product is like a burst of energy in a box! It brought so much joy to my life. Highly recommended for an instant mood lift.",
    "I never knew a simple gadget could have such magical powers! This product practically solved all my problems. Kudos to the creators!",
    "I'm convinced this thing has secret superpowers. I can't share the details, but let's just say it made my daily routine 10 times more interesting!",
    "Not sure how I lived without this before. It's like the Swiss Army knife of products—versatile, handy, and a bit mysterious.",
    "Unexpectedly bought this, and it turned out to be a game-changer. Life before this product feels like a distant memory now.",
    "This thingamajig is a true marvel. It's so good; I might have to buy a backup, just in case it decides to take a vacation!",
    "Got this on a whim, and it feels like I stumbled upon a hidden treasure. If you're looking for that 'wow' factor, look no further.",
    "I'm pretty sure this is the missing piece to the puzzle of life. I didn't know I needed it until I got it, and now I can't imagine life without it!",
    "Honestly, I thought it was just hype, but this product exceeded all expectations. It's like having a personal assistant, but cooler.",
    "I'm not saying this product is magical, but I haven't seen any evidence to the contrary. Definitely a must-have in everyone's collection!",
    "This product made my ex lift her restraining order on me. Thanks Shop4All!",
    "I think I used this product wrong because now my kids won't return my phone calls.",
    "This product sucks! Couldn't even wash my dog with it.",
    "This product got me kicked out of my local church.",
    "Great product, but not great for bringing into government buildings.",
    "This product was so impactful to my life. I switched religions because of it.",
    "Does anyone know how to find the integral of a polynomial?",
    "This product saved me from falling into political extremism.",
    "Did anyone else just go numb in the right side of their body or just me?",
    "This product is just liberal propaganda.",
    "This product is just right-wing propaganda.",
    "Highly recommend this thing. It does all the things you want it to.",
    "Does anyone know if it's legal to sell your kidney on this site?"
]


def fake_phone():#generates fake phone numbers in the desired format
    num = ""
    for i in range(0,10):
        num += str(random.randint(0, 9))
    return num


def change_seller_address(cursor, bID, newAddress):
    try:
        cursor.execute("UPDATE sellers SET address = %s WHERE sellerID = %s;", (newAddress, str(bID)))
        return True
    except Exception as e:
        return False

def change_seller_name(cursor, bID, newName):
    try:
        cursor.execute("UPDATE sellers SET name = %s WHERE sellerID = %s;", (newName, str(bID)))
        return True
    except Exception as e:
        return False

def change_seller_phone(cursor, bID, newPhone):
    try:
        cursor.execute("UPDATE sellers SET phone = %s WHERE sellerID = %s;", (newPhone, str(bID)))
        return True
    except Exception as e:
        return False

def change_seller_email(cursor, bID, newPhone):
    try:
        cursor.execute("UPDATE sellers SET email = %s WHERE sellerID = %s;", (newPhone, str(bID)))
        return True
    except Exception as e:
        return False


def change_buyer_address(cursor, bID, newAddress):
    try:
        cursor.execute("UPDATE buyers SET address = %s WHERE buyerID = %s;", (newAddress, str(bID)))
        return True
    except Exception as e:
        return False

def change_buyer_name(cursor, bID, newName):
    try:
        cursor.execute("UPDATE buyers SET name = %s WHERE buyerID = %s;", (newName, str(bID)))
        return True
    except Exception as e:
        return False

def change_buyer_phone(cursor, bID, newPhone):
    try:
        cursor.execute("UPDATE buyers SET phone = %s WHERE buyerID = %s;", (newPhone, str(bID)))
        return True
    except Exception as e:
        return False

def change_buyer_email(cursor, bID, newPhone):
    try:
        cursor.execute("UPDATE buyers SET email = %s WHERE buyerID = %s;", (newPhone, str(bID)))
        return True
    except Exception as e:
        return False

def create_fake_review(buyerid, productid):
    dummy_review = {
            "product_id": f"{productid}",
            "customer_id": f"{buyerid}",
            "rating": random.randint(0, 5),
            "comment": REVIEWS[random.randint(0, 22)],
            "timestamp": datetime.now(),
        }
    return dummy_review


def fill_tables(cursor):#put fake data into the tables
    fake = Faker()
    
    #fill buyers
    for i in range(0, 200):
        name = fake.name()
        address = fake.address()
        number = fake_phone()
        email = fake.email()
        password = NOUNS[random.randint(0,24)] + str(random.randint(1000, 9999))
        
        insert_query = f'''
            INSERT INTO buyers (name, address, phone, email, password_hash)
            VALUES ('{name}', '{address}', '{number}', '{email}', '{password}');
        '''
        #cursor.execute(insert_query)
        print(i)

    print("Done insert...")

    #fill sellers
    for i in range(0, 10):
        name = fake.name()
        address = fake.address()
        number = fake_phone()
        email = fake.email()
        password = NOUNS[random.randint(0,24)] + str(random.randint(1000, 9999))
        
        insert_query = f'''
            INSERT INTO sellers (name, address, phone, email, password_hash)
            VALUES ('{name}', '{address}', '{number}', '{email}', '{password}');
        '''
        #cursor.execute(insert_query)
        print(i)

    print("Done insert...")

    #fill catagories
    for n in CATEGORIES:
        insert_query = f'''
        INSERT INTO categories
        VALUES ('{n}');
        '''
        #cursor.execute(insert_query)

    #fill products
    cursor.execute("SELECT sellerID FROM sellers")
    sID_record = cursor.fetchall()
    print(sID_record)
    cursor.execute("SELECT categoryID FROM categories")
    cID_record = cursor.fetchall()
    
    print(sID_record[random.randint(0, len(sID_record)-1)][0])
    
    x = 0
    y = 0
    for i in range(0, 500):
        product = ADJECTIVES[x] + " " + NOUNS[y]
        stock = random.randint(5, 50)
        price = round(random.uniform(5.0, 200.0), 2)
        sellerID = sID_record[random.randint(0, len(sID_record)-1)][0]
        categoryID = cID_record[random.randint(0, len(cID_record)-1)][0]

        insert_query = f'''
        INSERT INTO products (name, stock, price, sellerID, categoryID)
        VALUES ('{product}', '{stock}', '{price}', '{sellerID}', '{categoryID}');
        '''
        #cursor.execute(insert_query)
        print("Product: " + str(i))
        x += 1
        if x % 24 == 0:
            x = 0
            y += 1
    
    #fill reviews
    client = MongoClient("mongodb://localhost:27017/")
    database = client["Shop4All_Reviews"]
    collection = database["reviews"]
    
    cursor.execute("SELECT productid FROM products;")
    product_records = cursor.fetchall()
    
    cursor.execute("SELECT buyerid FROM buyers;")
    buyer_records = cursor.fetchall()
    
    for productid in product_records:
        count = random.randint(1, 5)
        for i in range(count):
            collection.insert_one(create_fake_review(buyer_records[random.randint(0, (len(buyer_records) - 1))][0], productid[0]))
            print("Inserted review #" + str(i) + " for product " + str(productid[0]) + ".")
    
    
    print("Items added to tables.")
            

