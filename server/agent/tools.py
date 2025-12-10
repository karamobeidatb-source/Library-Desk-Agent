"""
LangChain Tools for Library Desk Agent
"""
from langchain.tools import tool
from typing import List, Dict, Any, Literal
from pydantic import BaseModel, Field
import json
from server.database.db import db


# Tool Input Schemas
class FindBooksInput(BaseModel):
    """Input for finding books"""
    q: str = Field(description="Search query string")
    by: Literal["title", "author"] = Field(description="Search by 'title' or 'author'")


class OrderItem(BaseModel):
    """Item in an order"""
    isbn: str = Field(description="Book ISBN")
    qty: int = Field(description="Quantity to order", gt=0)


class CreateOrderInput(BaseModel):
    """Input for creating an order"""
    customer_id: int = Field(description="Customer ID")
    items: List[OrderItem] = Field(description="List of items to order")


class RestockBookInput(BaseModel):
    """Input for restocking a book"""
    isbn: str = Field(description="Book ISBN")
    qty: int = Field(description="Quantity to add to stock", gt=0)


class UpdatePriceInput(BaseModel):
    """Input for updating book price"""
    isbn: str = Field(description="Book ISBN")
    price: float = Field(description="New price", gt=0)


class OrderStatusInput(BaseModel):
    """Input for checking order status"""
    order_id: int = Field(description="Order ID")


# Tool Implementations
@tool
def find_books(q: str, by: Literal["title", "author"]) -> str:
    """
    Find books in the library inventory.
    
    Args:
        q: Search query string
        by: Search by 'title' or 'author'
    
    Returns:
        JSON string with list of matching books
    """
    try:
        if by == "title":
            books = db.find_books_by_title(q)
        elif by == "author":
            books = db.find_books_by_author(q)
        else:
            return json.dumps({"error": "Invalid search type. Use 'title' or 'author'"})
        
        if not books:
            return json.dumps({
                "message": f"No books found matching '{q}' by {by}",
                "books": []
            })
        
        return json.dumps({
            "message": f"Found {len(books)} book(s)",
            "books": books
        }, indent=2)
    
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def create_order(customer_id: int, items: List[Dict[str, Any]]) -> str:
    """
    Create a new order for a customer and reduce stock accordingly.
    
    Args:
        customer_id: Customer ID
        items: List of items with 'isbn' and 'qty' keys
    
    Returns:
        JSON string with order details
    """
    try:
        # Validate customer exists
        customer = db.get_customer(customer_id)
        if not customer:
            return json.dumps({"error": f"Customer ID {customer_id} not found"})
        
        # Validate all books exist and have sufficient stock
        order_books = []
        for item in items:
            isbn = item.get("isbn")
            qty = item.get("qty", 0)
            
            if not isbn or qty <= 0:
                return json.dumps({"error": "Invalid item format. Need 'isbn' and 'qty' > 0"})
            
            book = db.get_book_by_isbn(isbn)
            if not book:
                return json.dumps({"error": f"Book with ISBN {isbn} not found"})
            
            if book["stock"] < qty:
                return json.dumps({
                    "error": f"Insufficient stock for '{book['title']}'. Available: {book['stock']}, Requested: {qty}"
                })
            
            order_books.append({
                "isbn": isbn,
                "qty": qty,
                "book": book
            })
        
        # Create order
        order_id = db.create_order(customer_id)
        
        # Add items and reduce stock
        total = 0
        for order_book in order_books:
            isbn = order_book["isbn"]
            qty = order_book["qty"]
            book = order_book["book"]
            
            db.add_order_item(order_id, isbn, qty, book["price"])
            db.update_book_stock(isbn, -qty)
            
            total += qty * book["price"]
        
        # Get updated stock info
        updated_books = []
        for order_book in order_books:
            updated_book = db.get_book_by_isbn(order_book["isbn"])
            updated_books.append({
                "title": updated_book["title"],
                "isbn": updated_book["isbn"],
                "quantity_ordered": order_book["qty"],
                "new_stock": updated_book["stock"]
            })
        
        return json.dumps({
            "message": "Order created successfully",
            "order_id": order_id,
            "customer": customer["name"],
            "items": updated_books,
            "total": round(total, 2)
        }, indent=2)
    
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def restock_book(isbn: str, qty: int) -> str:
    """
    Restock a book by adding quantity to current stock.
    
    Args:
        isbn: Book ISBN
        qty: Quantity to add (must be positive)
    
    Returns:
        JSON string with updated stock info
    """
    try:
        if qty <= 0:
            return json.dumps({"error": "Quantity must be positive"})
        
        # Check book exists
        book = db.get_book_by_isbn(isbn)
        if not book:
            return json.dumps({"error": f"Book with ISBN {isbn} not found"})
        
        old_stock = book["stock"]
        
        # Update stock
        success = db.update_book_stock(isbn, qty)
        if not success:
            return json.dumps({"error": "Failed to update stock"})
        
        # Get updated book
        updated_book = db.get_book_by_isbn(isbn)
        
        return json.dumps({
            "message": "Book restocked successfully",
            "title": updated_book["title"],
            "isbn": isbn,
            "old_stock": old_stock,
            "added": qty,
            "new_stock": updated_book["stock"]
        }, indent=2)
    
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def update_price(isbn: str, price: float) -> str:
    """
    Update the price of a book.
    
    Args:
        isbn: Book ISBN
        price: New price (must be positive)
    
    Returns:
        JSON string with updated price info
    """
    try:
        if price <= 0:
            return json.dumps({"error": "Price must be positive"})
        
        # Check book exists
        book = db.get_book_by_isbn(isbn)
        if not book:
            return json.dumps({"error": f"Book with ISBN {isbn} not found"})
        
        old_price = book["price"]
        
        # Update price
        success = db.update_book_price(isbn, price)
        if not success:
            return json.dumps({"error": "Failed to update price"})
        
        return json.dumps({
            "message": "Price updated successfully",
            "title": book["title"],
            "isbn": isbn,
            "old_price": old_price,
            "new_price": price
        }, indent=2)
    
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def order_status(order_id: int) -> str:
    """
    Get the status and details of an order.
    
    Args:
        order_id: Order ID
    
    Returns:
        JSON string with order details
    """
    try:
        order = db.get_order_details(order_id)
        if not order:
            return json.dumps({"error": f"Order ID {order_id} not found"})
        
        return json.dumps({
            "order_id": order["id"],
            "customer": {
                "id": order["customer_id"],
                "name": order["customer_name"],
                "email": order["customer_email"]
            },
            "status": order["status"],
            "created_at": order["created_at"],
            "items": order["items"],
            "total": round(order["total"], 2)
        }, indent=2)
    
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def inventory_summary() -> str:
    """
    Get a summary of inventory, highlighting low-stock items.
    
    Returns:
        JSON string with inventory summary
    """
    try:
        low_stock_books = db.get_low_stock_books(threshold=10)
        
        if not low_stock_books:
            return json.dumps({
                "message": "All books are well-stocked",
                "low_stock_books": []
            })
        
        return json.dumps({
            "message": f"Found {len(low_stock_books)} book(s) with low stock (< 10)",
            "low_stock_books": low_stock_books
        }, indent=2)
    
    except Exception as e:
        return json.dumps({"error": str(e)})


# List of all tools
ALL_TOOLS = [
    find_books,
    create_order,
    restock_book,
    update_price,
    order_status,
    inventory_summary
]

