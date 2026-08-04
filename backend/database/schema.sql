-- PostgreSQL
-- This script is inteded to run in PostgreSQL

-- Table for training data
CREATE TABLE IF NOT EXISTS historical_car_listing (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    brand VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year INTEGER NOT NULL
);

-- Table for new input data
CREATE TABLE IF NOT EXISTS prediction_logs (
    id BIGSERIAL PRIMARY KEY,
    input_brand VARCHAR(50) NOT NULL,
    input_model VARCHAR(50) NOT NULL,
    input_year INTEGER NOT NULL
);