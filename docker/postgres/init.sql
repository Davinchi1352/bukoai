-- ===========================================
-- BUKO AI - POSTGRESQL INITIALIZATION
-- ===========================================

-- Create extensions if they don't exist
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Create database if it doesn't exist (handled by Docker)
-- CREATE DATABASE IF NOT EXISTS buko_ai;

-- Connect to the database
\c buko_ai;

-- Create schema for better organization
CREATE SCHEMA IF NOT EXISTS buko_ai;

-- Set search path
SET search_path TO buko_ai, public;

-- Create enum types
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended', 'deleted');
CREATE TYPE subscription_type AS ENUM ('free', 'starter', 'pro', 'business', 'enterprise');
CREATE TYPE book_status AS ENUM ('queued', 'processing', 'completed', 'failed', 'cancelled');
CREATE TYPE payment_status AS ENUM ('pending', 'completed', 'failed', 'cancelled', 'refunded');
CREATE TYPE book_format AS ENUM ('pdf', 'epub', 'docx', 'txt');

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone_country VARCHAR(5),
    phone_number VARCHAR(20),
    country VARCHAR(100),
    city VARCHAR(100),
    billing_address TEXT,
    subscription_type subscription_type DEFAULT 'free',
    subscription_start TIMESTAMP WITH TIME ZONE,
    subscription_end TIMESTAMP WITH TIME ZONE,
    books_used_this_month INTEGER DEFAULT 0,
    last_login TIMESTAMP WITH TIME ZONE,
    email_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    password_reset_token VARCHAR(255),
    password_reset_expires TIMESTAMP WITH TIME ZONE,
    preferred_language VARCHAR(5) DEFAULT 'es',
    timezone VARCHAR(50) DEFAULT 'UTC',
    status user_status DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Create book generations table
CREATE TABLE IF NOT EXISTS book_generations (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    genre VARCHAR(100),
    target_audience VARCHAR(200),
    tone VARCHAR(100),
    key_topics TEXT,
    chapter_count INTEGER DEFAULT 10,
    page_count INTEGER DEFAULT 50,
    format_size VARCHAR(20) DEFAULT 'A4',
    language VARCHAR(5) DEFAULT 'es',
    additional_instructions TEXT,
    include_toc BOOLEAN DEFAULT TRUE,
    include_introduction BOOLEAN DEFAULT TRUE,
    include_conclusion BOOLEAN DEFAULT TRUE,
    writing_style VARCHAR(200),
    parameters JSONB,
    content TEXT,
    thinking_content TEXT,
    thinking_length INTEGER DEFAULT 0,
    status book_status DEFAULT 'queued',
    queue_position INTEGER,
    priority INTEGER DEFAULT 0,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    thinking_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    estimated_cost DECIMAL(10,4) DEFAULT 0.0000,
    streaming_stats JSONB,
    final_pages INTEGER,
    final_words INTEGER,
    file_paths JSONB,
    cover_url VARCHAR(500),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create subscriptions table
CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_type subscription_type NOT NULL,
    status payment_status DEFAULT 'pending',
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    trial_start TIMESTAMP WITH TIME ZONE,
    trial_end TIMESTAMP WITH TIME ZONE,
    paypal_subscription_id VARCHAR(255),
    mp_subscription_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create payments table
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id INTEGER REFERENCES subscriptions(id) ON DELETE SET NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status payment_status DEFAULT 'pending',
    payment_method VARCHAR(50),
    payment_provider VARCHAR(50),
    provider_payment_id VARCHAR(255),
    provider_transaction_id VARCHAR(255),
    invoice_id VARCHAR(255),
    description TEXT,
    metadata JSONB,
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create system logs table
CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(200) NOT NULL,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'success',
    error_message TEXT,
    execution_time INTERVAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create book downloads table
CREATE TABLE IF NOT EXISTS book_downloads (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    book_id INTEGER NOT NULL REFERENCES book_generations(id) ON DELETE CASCADE,
    format book_format NOT NULL,
    file_path VARCHAR(500),
    file_size BIGINT,
    download_count INTEGER DEFAULT 0,
    last_downloaded_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create email templates table
CREATE TABLE IF NOT EXISTS email_templates (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    name VARCHAR(100) UNIQUE NOT NULL,
    subject VARCHAR(255) NOT NULL,
    html_content TEXT NOT NULL,
    text_content TEXT,
    variables JSONB,
    language VARCHAR(5) DEFAULT 'es',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create referrals table
CREATE TABLE IF NOT EXISTS referrals (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    referrer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    referred_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    referral_code VARCHAR(20),
    commission_rate DECIMAL(5,4) DEFAULT 0.1000,
    commission_earned DECIMAL(10,2) DEFAULT 0.00,
    commission_paid DECIMAL(10,2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_subscription_type ON users(subscription_type);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

CREATE INDEX IF NOT EXISTS idx_book_generations_user_id ON book_generations(user_id);
CREATE INDEX IF NOT EXISTS idx_book_generations_status ON book_generations(status);
CREATE INDEX IF NOT EXISTS idx_book_generations_created_at ON book_generations(created_at);
CREATE INDEX IF NOT EXISTS idx_book_generations_queue_position ON book_generations(queue_position);

CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_current_period_end ON subscriptions(current_period_end);

CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at);

CREATE INDEX IF NOT EXISTS idx_system_logs_user_id ON system_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_system_logs_action ON system_logs(action);
CREATE INDEX IF NOT EXISTS idx_system_logs_created_at ON system_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_book_downloads_user_id ON book_downloads(user_id);
CREATE INDEX IF NOT EXISTS idx_book_downloads_book_id ON book_downloads(book_id);

-- Create full-text search indexes
CREATE INDEX IF NOT EXISTS idx_book_generations_title_fts ON book_generations USING gin(to_tsvector('spanish', title));
CREATE INDEX IF NOT EXISTS idx_book_generations_content_fts ON book_generations USING gin(to_tsvector('spanish', content));

-- Create trigger function for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_book_generations_updated_at BEFORE UPDATE ON book_generations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_book_downloads_updated_at BEFORE UPDATE ON book_downloads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_email_templates_updated_at BEFORE UPDATE ON email_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_referrals_updated_at BEFORE UPDATE ON referrals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to reset monthly book usage
CREATE OR REPLACE FUNCTION reset_monthly_book_usage()
RETURNS void AS $$
BEGIN
    UPDATE users 
    SET books_used_this_month = 0
    WHERE DATE_TRUNC('month', CURRENT_DATE) > DATE_TRUNC('month', updated_at);
END;
$$ LANGUAGE plpgsql;

-- Create view for user statistics
CREATE OR REPLACE VIEW user_statistics AS
SELECT 
    u.id,
    u.email,
    u.first_name,
    u.last_name,
    u.subscription_type,
    u.created_at,
    COUNT(bg.id) as total_books_generated,
    COUNT(CASE WHEN bg.status = 'completed' THEN 1 END) as completed_books,
    COUNT(CASE WHEN bg.status = 'failed' THEN 1 END) as failed_books,
    SUM(bg.estimated_cost) as total_costs,
    MAX(bg.created_at) as last_book_generated
FROM users u
LEFT JOIN book_generations bg ON u.id = bg.user_id
GROUP BY u.id, u.email, u.first_name, u.last_name, u.subscription_type, u.created_at;

-- Grant permissions
GRANT USAGE ON SCHEMA buko_ai TO PUBLIC;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA buko_ai TO PUBLIC;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA buko_ai TO PUBLIC;

-- Insert default email templates
INSERT INTO email_templates (name, subject, html_content, text_content, variables, language) VALUES
('welcome', 'Bienvenido a Buko AI', 
'<h1>¡Bienvenido a Buko AI!</h1><p>Hola {{first_name}},</p><p>Gracias por registrarte en Buko AI. ¡Estamos emocionados de ayudarte a crear libros increíbles!</p>',
'¡Bienvenido a Buko AI! Hola {{first_name}}, Gracias por registrarte en Buko AI. ¡Estamos emocionados de ayudarte a crear libros increíbles!',
'{"first_name": "string"}', 'es'),
('book_completed', 'Tu libro está listo',
'<h1>¡Tu libro está listo!</h1><p>Hola {{first_name}},</p><p>Tu libro "{{book_title}}" ha sido generado exitosamente. Puedes descargarlo desde tu dashboard.</p>',
'¡Tu libro está listo! Hola {{first_name}}, Tu libro "{{book_title}}" ha sido generado exitosamente. Puedes descargarlo desde tu dashboard.',
'{"first_name": "string", "book_title": "string"}', 'es'),
('password_reset', 'Restablece tu contraseña',
'<h1>Restablece tu contraseña</h1><p>Hola {{first_name}},</p><p>Haz clic en el siguiente enlace para restablecer tu contraseña: <a href="{{reset_link}}">Restablecer contraseña</a></p>',
'Restablece tu contraseña. Hola {{first_name}}, Haz clic en el siguiente enlace para restablecer tu contraseña: {{reset_link}}',
'{"first_name": "string", "reset_link": "string"}', 'es');

-- Log the initialization
INSERT INTO system_logs (action, details, status) VALUES
('database_init', '{"message": "Database initialized successfully", "version": "1.0"}', 'success');