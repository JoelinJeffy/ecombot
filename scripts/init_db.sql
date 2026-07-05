-- eComBot Database Initialization (Day 04)
-- This script creates tables and seeds data for orders, products, and session history.

-- Enable UUID extension if needed for session IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    eta VARCHAR(100),
    carrier VARCHAR(100),
    total_amount DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    category VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Session history table for conversation persistence
CREATE TABLE IF NOT EXISTS session_history (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT,
    tool_calls JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session_id (session_id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- Seed orders data
INSERT INTO orders (order_id, customer_name, status, eta, carrier, total_amount) VALUES
    ('ORD-001', 'Priya Sharma', 'Shipped', '8 Jul 2026', 'BlueDart', 2499.99),
    ('ORD-002', 'Rahul Verma', 'Processing', '10 Jul 2026', 'DTDC', 1299.50),
    ('ORD-003', 'Ananya Singh', 'Delivered', 'Already delivered', 'FedEx', 3499.00),
    ('ORD-004', 'Vikram Patel', 'Cancelled', NULL, NULL, 999.99),
    ('ORD-005', 'Sneha Reddy', 'Shipped', '9 Jul 2026', 'DHL', 5299.00)
ON CONFLICT (order_id) DO NOTHING;

-- Seed products data
INSERT INTO products (product_id, product_name, description, price, stock_quantity, category, is_active) VALUES
    ('PRD-101', 'Dell XPS 15 Laptop', 'High-performance laptop with 16GB RAM, 512GB SSD, Intel i7 processor', 89999.00, 15, 'Laptops', TRUE),
    ('PRD-102', 'Sony WH-1000XM5 Headphones', 'Premium noise-cancelling wireless headphones', 29999.00, 42, 'Audio', TRUE),
    ('PRD-103', 'Samsung Galaxy S24', 'Latest flagship smartphone with 256GB storage', 74999.00, 0, 'Phones', TRUE),
    ('PRD-104', 'Apple Magic Keyboard', 'Wireless keyboard for Mac and iPad', 12999.00, 28, 'Accessories', TRUE),
    ('PRD-105', 'Logitech MX Master 3', 'Advanced wireless mouse', 8999.00, 55, 'Accessories', TRUE),
    ('PRD-106', 'Discontinued Product', 'No longer available', 4999.00, 0, 'Legacy', FALSE)
ON CONFLICT (product_id) DO NOTHING;

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_product_name ON products(product_name);
CREATE INDEX IF NOT EXISTS idx_order_customer ON orders(customer_name);
