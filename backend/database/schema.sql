-- PostgreSQL
-- This script is inteded to run in PostgreSQL

-- Table for training data
CREATE TABLE IF NOT EXISTS historical_car_listing (
    manufacturer TEXT NOT NULL,
    price NUMERIC(13,2) NOT NULL
);

-- Table for new input data
CREATE TABLE IF NOT EXISTS prediction_logs (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    year INTEGER NOT NULL,
    manufacturer TEXT NOT NULL,
    model TEXT NOT NULL,
    condition TEXT,
    cylinders TEXT,
    fuel TEXT NOT NULL,
    odometer BIGINT NOT NULL,
    title_status TEXT NOT NULL,
    transmission TEXT NOT NULL,
    drive TEXT,
    size TEXT,
    type TEXT,
    estimated_price NUMERIC(13,2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);