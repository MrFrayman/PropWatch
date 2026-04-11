CREATE TABLE buildings (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    zip_code VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE units (
    id SERIAL PRIMARY KEY,
    building_id INTEGER NOT NULL,
    unit_number VARCHAR(50) NOT NULL,
    floor INTEGER NOT NULL,
    bedrooms INTEGER NOT NULL,
    bathrooms INTEGER NOT NULL,
    square_feet INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (building_id) REFERENCES buildings(id) ON DELETE CASCADE
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    unit_id INTEGER NOT NULL,
    transaction_type VARCHAR(50) NOT NULL, -- e.g., "sale", "rent"
    price DECIMAL(15, 2) NOT NULL,
    transaction_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE
);

CREATE TABLE listings (
    id SERIAL PRIMARY KEY,
    unit_id INTEGER NOT NULL,
    listing_type VARCHAR(50) NOT NULL, -- e.g., "sale", "rent"
    price DECIMAL(15, 2) NOT NULL,
    listed_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE
);

CREATE TABLE inference_results (
    id SERIAL PRIMARY KEY,
    unit_id INTEGER NOT NULL,
    inferred_price DECIMAL(15, 2) NOT NULL,
    confidence_score DECIMAL(5, 2) NOT NULL,
    inference_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE
);

-- This schema establishes the core entities and their relationships, 
-- with a focus on buildings and their associated units, transactions, listings, and inference results. 
-- Each table includes timestamps for tracking creation and updates, 
-- and foreign key constraints ensure referential integrity.