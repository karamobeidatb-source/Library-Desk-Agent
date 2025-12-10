"""
Database connection and query functions
"""
import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from pathlib import Path

class Database:
    def __init__(self, db_path: str = "./db/library.db"):
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure database file exists"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(
                f"Database not found at {self.db_path}. "
                "Please run 'python db/init_db.py' first."
            )
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dicts"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT query and return the last inserted ID"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    # Book queries
    def find_books_by_title(self, query: str) -> List[Dict[str, Any]]:
        """Find books by title (partial match)"""
        sql = """
            SELECT isbn, title, author, price, stock 
            FROM books 
            WHERE title LIKE ? 
            ORDER BY title
        """
        return self.execute_query(sql, (f"%{query}%",))
    
    def find_books_by_author(self, query: str) -> List[Dict[str, Any]]:
        """Find books by author (partial match)"""
        sql = """
            SELECT isbn, title, author, price, stock 
            FROM books 
            WHERE author LIKE ? 
            ORDER BY author, title
        """
        return self.execute_query(sql, (f"%{query}%",))
    
    def get_book_by_isbn(self, isbn: str) -> Optional[Dict[str, Any]]:
        """Get a single book by ISBN"""
        sql = "SELECT isbn, title, author, price, stock FROM books WHERE isbn = ?"
        results = self.execute_query(sql, (isbn,))
        return results[0] if results else None
    
    def update_book_stock(self, isbn: str, quantity_change: int) -> bool:
        """Update book stock (can be positive or negative)"""
        sql = "UPDATE books SET stock = stock + ? WHERE isbn = ?"
        affected = self.execute_update(sql, (quantity_change, isbn))
        return affected > 0
    
    def update_book_price(self, isbn: str, new_price: float) -> bool:
        """Update book price"""
        sql = "UPDATE books SET price = ? WHERE isbn = ?"
        affected = self.execute_update(sql, (new_price, isbn))
        return affected > 0
    
    def get_low_stock_books(self, threshold: int = 10) -> List[Dict[str, Any]]:
        """Get books with stock below threshold"""
        sql = """
            SELECT isbn, title, author, price, stock 
            FROM books 
            WHERE stock < ? 
            ORDER BY stock ASC, title
        """
        return self.execute_query(sql, (threshold,))
    
    # Customer queries
    def get_customer(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Get customer by ID"""
        sql = "SELECT id, name, email FROM customers WHERE id = ?"
        results = self.execute_query(sql, (customer_id,))
        return results[0] if results else None
    
    # Order queries
    def create_order(self, customer_id: int) -> int:
        """Create a new order and return order ID"""
        sql = "INSERT INTO orders (customer_id, status) VALUES (?, 'completed')"
        return self.execute_insert(sql, (customer_id,))
    
    def add_order_item(self, order_id: int, isbn: str, quantity: int, price: float):
        """Add an item to an order"""
        sql = """
            INSERT INTO order_items (order_id, isbn, quantity, price_at_purchase) 
            VALUES (?, ?, ?, ?)
        """
        return self.execute_insert(sql, (order_id, isbn, quantity, price))
    
    def get_order_details(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Get order details including customer and items"""
        # Get order and customer info
        order_sql = """
            SELECT o.id, o.customer_id, o.status, o.created_at,
                   c.name as customer_name, c.email as customer_email
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            WHERE o.id = ?
        """
        order_results = self.execute_query(order_sql, (order_id,))
        if not order_results:
            return None
        
        order = order_results[0]
        
        # Get order items
        items_sql = """
            SELECT oi.isbn, oi.quantity, oi.price_at_purchase,
                   b.title, b.author
            FROM order_items oi
            JOIN books b ON oi.isbn = b.isbn
            WHERE oi.order_id = ?
        """
        items = self.execute_query(items_sql, (order_id,))
        
        order['items'] = items
        order['total'] = sum(item['quantity'] * item['price_at_purchase'] for item in items)
        
        return order
    
    # Session queries
    def create_session(self, session_id: str):
        """Create a new chat session"""
        sql = "INSERT INTO sessions (id) VALUES (?)"
        self.execute_insert(sql, (session_id,))
    
    def get_sessions(self) -> List[Dict[str, Any]]:
        """Get all sessions ordered by most recent"""
        sql = """
            SELECT id, created_at, updated_at 
            FROM sessions 
            ORDER BY updated_at DESC
        """
        return self.execute_query(sql)
    
    def update_session_timestamp(self, session_id: str):
        """Update session's updated_at timestamp"""
        sql = "UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        self.execute_update(sql, (session_id,))
    
    # Message queries
    def save_message(self, session_id: str, role: str, content: str):
        """Save a chat message"""
        sql = """
            INSERT INTO messages (session_id, role, content) 
            VALUES (?, ?, ?)
        """
        return self.execute_insert(sql, (session_id, role, content))
    
    def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a session"""
        sql = """
            SELECT id, role, content, created_at 
            FROM messages 
            WHERE session_id = ? 
            ORDER BY created_at ASC
        """
        return self.execute_query(sql, (session_id,))
    
    # Tool call queries
    def save_tool_call(self, session_id: str, tool_name: str, 
                       args_json: str, result_json: str):
        """Save a tool call"""
        sql = """
            INSERT INTO tool_calls (session_id, tool_name, args_json, result_json) 
            VALUES (?, ?, ?, ?)
        """
        return self.execute_insert(sql, (session_id, tool_name, args_json, result_json))

# Global database instance
db = Database()

