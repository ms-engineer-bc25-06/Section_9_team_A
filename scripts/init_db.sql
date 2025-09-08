-- Bridge Line Database Initialization Script
-- This script initializes the database with basic tables and data
-- Create database if not exists (PostgreSQL will handle this automatically)
-- The database is created by the POSTGRES_DB environment variable
-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create basic tables (these will be managed by Alembic migrations)
-- This file is mainly for initial setup and any pre-migration data
-- Insert any initial data here if needed
-- For example:
-- INSERT INTO users (id, email, username) VALUES 
--   (uuid_generate_v4(), 'admin@example.com', 'admin')
-- ON CONFLICT (email) DO NOTHING;
-- Note: Most table creation is handled by Alembic migrations
-- This file is primarily for initial setup and extensions