-- Seed Data for Library Desk Agent

-- Books (10 books)
INSERT INTO books (isbn, title, author, price, stock) VALUES
('978-0132350884', 'Clean Code', 'Robert C. Martin', 42.99, 15),
('978-0201616224', 'The Pragmatic Programmer', 'Andrew Hunt', 45.50, 8),
('978-0134685991', 'Effective Java', 'Joshua Bloch', 48.00, 12),
('978-0596007126', 'Head First Design Patterns', 'Eric Freeman', 39.99, 20),
('978-0135957059', 'The Mythical Man-Month', 'Frederick Brooks', 35.00, 5),
('978-1449355739', 'Designing Data-Intensive Applications', 'Martin Kleppmann', 55.99, 10),
('978-0321125215', 'Domain-Driven Design', 'Eric Evans', 52.00, 7),
('978-0137081073', 'The Clean Coder', 'Robert C. Martin', 40.00, 18),
('978-0321534460', 'Introduction to Algorithms', 'Thomas Cormen', 89.99, 4),
('978-0984782857', 'Cracking the Coding Interview', 'Gayle McDowell', 49.95, 25);

-- Customers (6 customers)
INSERT INTO customers (name, email) VALUES
('Alice Johnson', 'alice.johnson@email.com'),
('Bob Smith', 'bob.smith@email.com'),
('Charlie Brown', 'charlie.brown@email.com'),
('Diana Prince', 'diana.prince@email.com'),
('Eve Davis', 'eve.davis@email.com'),
('Frank Miller', 'frank.miller@email.com');

-- Orders (4 orders)
INSERT INTO orders (customer_id, status, created_at) VALUES
(1, 'completed', datetime('now', '-5 days')),
(2, 'completed', datetime('now', '-3 days')),
(3, 'completed', datetime('now', '-2 days')),
(4, 'completed', datetime('now', '-1 days'));

-- Order Items
INSERT INTO order_items (order_id, isbn, quantity, price_at_purchase) VALUES
-- Order 1: Alice bought 2 books
(1, '978-0132350884', 1, 42.99),
(1, '978-0201616224', 1, 45.50),
-- Order 2: Bob bought 1 book
(2, '978-0134685991', 2, 48.00),
-- Order 3: Charlie bought 3 books
(3, '978-0596007126', 1, 39.99),
(3, '978-0132350884', 1, 42.99),
(3, '978-0984782857', 1, 49.95),
-- Order 4: Diana bought 1 book
(4, '978-1449355739', 1, 55.99);

