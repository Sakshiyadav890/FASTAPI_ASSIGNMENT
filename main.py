from fastapi import FastAPI, Query, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# -----------------------
# DATA
# -----------------------
menu = [
    {"id": 1, "name": "Pizza", "price": 200, "category": "Pizza", "is_available": True},
    {"id": 2, "name": "Burger", "price": 120, "category": "Burger", "is_available": True},
    {"id": 3, "name": "Pasta", "price": 180, "category": "Pizza", "is_available": False},
    {"id": 4, "name": "Coke", "price": 50, "category": "Drink", "is_available": True},
    {"id": 5, "name": "Cake", "price": 150, "category": "Dessert", "is_available": True},
    {"id": 6, "name": "Sandwich", "price": 100, "category": "Burger", "is_available": True},
]

orders = []
order_counter = 1
cart = []

# -----------------------
# HELPERS
# -----------------------
def find_menu_item(item_id):
    for item in menu:
        if item["id"] == item_id:
            return item
    return None

def calculate_bill(price, quantity, order_type="delivery"):
    total = price * quantity
    if order_type == "delivery":
        total += 30
    return total

# -----------------------
# MODELS
# -----------------------
class OrderRequest(BaseModel):
    customer_name: str = Field(min_length=2)
    item_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=20)
    delivery_address: str = Field(min_length=5)
    order_type: str = "delivery"

class NewMenuItem(BaseModel):
    name: str
    price: int
    category: str
    is_available: bool = True

# -----------------------
# GET APIs
# -----------------------
@app.get("/")
def home():
    return {"message": "Welcome to Food Delivery API"}

@app.get("/menu")
def get_menu():
    return {"total": len(menu), "items": menu}

@app.get("/menu/summary")
def summary():
    available = [i for i in menu if i["is_available"]]
    return {
        "total": len(menu),
        "available": len(available),
        "categories": list(set(i["category"] for i in menu))
    }

@app.get("/menu/{item_id}")
def get_item(item_id: int):
    item = find_menu_item(item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    return item

# -----------------------
# POST ORDER
# -----------------------
@app.post("/orders")
def create_order(order: OrderRequest):
    global order_counter

    item = find_menu_item(order.item_id)
    if not item:
        raise HTTPException(404, "Item not found")

    if not item["is_available"]:
        raise HTTPException(400, "Item not available")

    total = calculate_bill(item["price"], order.quantity, order.order_type)

    new_order = {
        "order_id": order_counter,
        "customer": order.customer_name,
        "item": item["name"],
        "total": total
    }

    orders.append(new_order)
    order_counter += 1

    return new_order

# -----------------------
# CRUD MENU
# -----------------------
@app.post("/menu", status_code=201)
def add_menu(item: NewMenuItem):
    new_id = len(menu) + 1
    new_item = {"id": new_id, **item.dict()}
    menu.append(new_item)
    return new_item

@app.put("/menu/{item_id}")
def update_menu(item_id: int, price: Optional[int] = None):
    item = find_menu_item(item_id)
    if not item:
        raise HTTPException(404, "Not found")

    if price:
        item["price"] = price

    return item

@app.delete("/menu/{item_id}")
def delete_menu(item_id: int):
    item = find_menu_item(item_id)
    if not item:
        raise HTTPException(404, "Not found")

    menu.remove(item)
    return {"message": "Deleted"}

# -----------------------
# SEARCH / SORT / PAGINATION
# -----------------------
@app.get("/menu/search")
def search(keyword: str):
    result = [i for i in menu if keyword.lower() in i["name"].lower()]
    return {"results": result}

@app.get("/menu/sort")
def sort(order: str = "asc"):
    return sorted(menu, key=lambda x: x["price"], reverse=(order=="desc"))

@app.get("/menu/page")
def paginate(page: int = 1, limit: int = 3):
    start = (page-1)*limit
    return menu[start:start+limit]