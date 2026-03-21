from fastapi import FastAPI, HTTPException
from pymongo.mongo_client import MongoClient
from pydantic import BaseModel
import requests
from prometheus_fastapi_instrumentator import Instrumentator

import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# API monitoring
Instrumentator().instrument(app).expose(app)

# DB connection to Mongo Atlas
uri = os.getenv("MONGO_URI")
client = MongoClient(uri)
db = client["inventory_db"]
collection = db["products"]


# Pydantic model for adding new product
class Product(BaseModel):
    ProductID: int
    Name: str
    UnitPrice: float
    StockQuantity: int
    Description: str


# Helper to strip MongoDB's _id field from results
def clean(product):
    product["_id"] = str(product["_id"])
    return product


# Endpoints
@app.get("/getSingleProduct")
def get_single_product(id: int):
    product = collection.find_one({"ProductID": id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return clean(product)


@app.get("/getAll")
def get_all():
    products = list(collection.find())
    return [clean(p) for p in products]


@app.post("/addNew")
def add_new(product: Product):
    existing = collection.find_one({"ProductID": product.ProductID})
    if existing:
        raise HTTPException(status_code=400, detail="ProductID already exists")
    collection.insert_one(product.dict())
    return {"message": "Product added successfully"}


@app.delete("/deleteOne")
def delete_one(id: int):
    result = collection.delete_one({"ProductID": id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": f"Product {id} deleted successfully"}


@app.get("/startsWith")
def starts_with(letter: str):
    if len(letter) != 1 or not letter.isalpha():
        raise HTTPException(status_code=400, detail="Please provide a single letter")
    products = list(collection.find({"Name": {"$regex": f"^{letter}", "$options": "i"}}))
    return [clean(p) for p in products]


@app.get("/paginate")
def paginate(start_id: int, end_id: int):
    products = list(collection.find(
        {"ProductID": {"$gte": start_id, "$lte": end_id}}
    ).limit(10))
    return [clean(p) for p in products]


@app.get("/convert")
def convert(id: int):
    product = collection.find_one({"ProductID": id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Fetch live USD to EUR exchange rate
    response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Could not fetch exchange rate")

    rate = response.json()["rates"]["EUR"]
    price_in_euros = round(product["UnitPrice"] * rate, 2)

    return {
        "ProductID": product["ProductID"],
        "Name": product["Name"],
        "OriginalPrice_USD": product["UnitPrice"],
        "ConvertedPrice_EUR": price_in_euros,
        "ExchangeRate": rate
    }
