from fastapi import FastAPI, Query

app = FastAPI()

# -------------------------
# Products Data
# -------------------------
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics"},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery"},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics"},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery"},
]

orders = []
order_counter = 1


# ==================================================
# Q1 — SEARCH PRODUCTS
# ==================================================
@app.get("/products/search")
def search_products(keyword: str = Query(...)):
    results = [p for p in products if keyword.lower() in p["name"].lower()]

    if not results:
        return {"message": f"No products found for: {keyword}"}

    return {"keyword": keyword, "total_found": len(results), "products": results}


# ==================================================
# Q2 — SORT PRODUCTS
# ==================================================
@app.get("/products/sort")
def sort_products(sort_by: str = "price", order: str = "asc"):
    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    reverse = (order == "desc")
    result = sorted(products, key=lambda p: p[sort_by], reverse=reverse)

    return {"sort_by": sort_by, "order": order, "products": result}


# ==================================================
# Q3 — PAGINATION
# ==================================================
@app.get("/products/page")
def paginate_products(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    total_pages = -(-len(products) // limit)

    return {
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "products": products[start:start + limit],
    }


# ==================================================
# CREATE ORDER (Needed for Q4)
# ==================================================
@app.post("/orders")
def create_order(customer_name: str, product_id: int):
    global order_counter

    order = {
        "order_id": order_counter,
        "customer_name": customer_name,
        "product_id": product_id,
    }

    orders.append(order)
    order_counter += 1

    return {"message": "Order created", "order": order}


# ==================================================
# Q4 — SEARCH ORDERS
# ==================================================
@app.get("/orders/search")
def search_orders(customer_name: str = Query(...)):
    results = [
        o for o in orders if customer_name.lower() in o["customer_name"].lower()
    ]

    if not results:
        return {"message": f"No orders found for: {customer_name}"}

    return {
        "customer_name": customer_name,
        "total_found": len(results),
        "orders": results,
    }


# ==================================================
# Q5 — SORT BY CATEGORY THEN PRICE
# ==================================================
@app.get("/products/sort-by-category")
def sort_by_category():
    result = sorted(products, key=lambda p: (p["category"], p["price"]))

    return {"total": len(result), "products": result}


# ==================================================
# Q6 — SEARCH + SORT + PAGINATE
# ==================================================
@app.get("/products/browse")
def browse_products(
    keyword: str = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 4,
):
    result = products

    # Search
    if keyword:
        result = [p for p in result if keyword.lower() in p["name"].lower()]

    # Sort
    if sort_by in ["price", "name"]:
        result = sorted(
            result, key=lambda p: p[sort_by], reverse=(order == "desc")
        )

    # Pagination
    total = len(result)
    start = (page - 1) * limit
    paged = result[start:start + limit]

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total,
        "total_pages": -(-total // limit),
        "products": paged,
    }


# ==================================================
# BONUS — PAGINATE ORDERS
# ==================================================
@app.get("/orders/page")
def paginate_orders(page: int = 1, limit: int = 3):
    start = (page - 1) * limit

    return {
        "page": page,
        "limit": limit,
        "total": len(orders),
        "total_pages": -(-len(orders) // limit),
        "orders": orders[start:start + limit],
    }