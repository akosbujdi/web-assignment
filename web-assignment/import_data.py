import csv
from pymongo.mongo_client import MongoClient

uri = "mongodb+srv://akodini04_db_user:6kiVmm1WtkOtLpWn@products.wgphcdi.mongodb.net/?appName=products"

client = MongoClient(uri)

# Create database called 'inventory_db' and collection called 'products'
db = client["inventory_db"]
collection = db["products"]

# Clear existing data so you don't get duplicates if you run it twice
collection.drop()

with open("products.csv", newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    products = []
    for row in reader:
        product = {
            "ProductID": int(row["ProductID"]),
            "Name": row["Name"],
            "UnitPrice": float(row["UnitPrice"]),
            "StockQuantity": int(row["StockQuantity"]),
            "Description": row["Description"]
        }
        products.append(product)

collection.insert_many(products)
print(f"Inserted {len(products)} products into MongoDB successfully!")