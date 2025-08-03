-- Cash Flow Forecasting Tool - Database Schema
-- PostgreSQL 15+ Compatible

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "timescaledb" CASCADE;

-- Create custom types
CREATE TYPE user_role AS ENUM ('admin', 'user', 'viewer', 'api_user');
CREATE TYPE account_type AS ENUM ('checking', 'savings', 'credit_card', 'loan', 'investment', 'other');
CREATE TYPE transaction_type AS ENUM ('income', 'expense', 'transfer');
CREATE TYPE integration_status AS ENUM ('active', 'inactive', 'error', 'pending');
CREATE TYPE forecast_status AS ENUM ('draft', 'active', 'archived');
CREATE TYPE confidence_level AS ENUM ('low', 'medium', 'high');

-- Organizations table
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    size_category VARCHAR(50), -- 'small', 'medium', 'large', 'enterprise'
    timezone VARCHAR(50) DEFAULT 'UTC',
    currency_code CHAR(3) DEFAULT 'USD',
    fiscal_year_start INTEGER DEFAULT 1, -- Month (1-12)
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role user_role DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    email_verified_at TIMESTAMPTZ,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- API Keys table
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) NOT NULL UNIQUE,
    permissions JSONB DEFAULT '{}',
    last_used_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Bank Accounts table
CREATE TABLE bank_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    external_id VARCHAR(255), -- From banking API
    account_name VARCHAR(255) NOT NULL,
    account_number VARCHAR(50),
    account_type account_type NOT NULL,
    bank_name VARCHAR(255),
    currency_code CHAR(3) DEFAULT 'USD',
    current_balance DECIMAL(15,2) DEFAULT 0,
    available_balance DECIMAL(15,2),
    last_synced_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Transactions table (hypertable for TimescaleDB)
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    bank_account_id UUID REFERENCES bank_accounts(id) ON DELETE SET NULL,
    external_id VARCHAR(255), -- From banking API
    transaction_date DATE NOT NULL,
    posted_date DATE,
    amount DECIMAL(15,2) NOT NULL,
    currency_code CHAR(3) DEFAULT 'USD',
    transaction_type transaction_type NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    description TEXT,
    merchant_name VARCHAR(255),
    reference_number VARCHAR(100),
    is_recurring BOOLEAN DEFAULT FALSE,
    recurring_pattern JSONB,
    tags TEXT[],
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('transactions', 'transaction_date', if_not_exists => TRUE);

-- Categories table
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    type transaction_type NOT NULL,
    parent_id UUID REFERENCES categories(id),
    color VARCHAR(7), -- Hex color
    icon VARCHAR(50),
    is_system BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(organization_id, name, type)
);

-- Budgets table
CREATE TABLE budgets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    category_id UUID REFERENCES categories(id),
    amount DECIMAL(15,2) NOT NULL,
    period VARCHAR(20) NOT NULL, -- 'monthly', 'quarterly', 'yearly'
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Forecasts table
CREATE TABLE forecasts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    forecast_start_date DATE NOT NULL,
    forecast_end_date DATE NOT NULL,
    status forecast_status DEFAULT 'draft',
    model_version VARCHAR(50),
    confidence confidence_level DEFAULT 'medium',
    parameters JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Forecast Data Points table (hypertable)
CREATE TABLE forecast_data_points (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    forecast_id UUID NOT NULL REFERENCES forecasts(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    predicted_inflow DECIMAL(15,2) DEFAULT 0,
    predicted_outflow DECIMAL(15,2) DEFAULT 0,
    predicted_balance DECIMAL(15,2) DEFAULT 0,
    confidence_score DECIMAL(5,4), -- 0.0000 to 1.0000
    model_features JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable('forecast_data_points', 'date', if_not_exists => TRUE);

-- Scenarios table
CREATE TABLE scenarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    forecast_id UUID NOT NULL REFERENCES forecasts(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    adjustments JSONB DEFAULT '{}', -- Percentage changes, fixed amounts, etc.
    is_baseline BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Integrations table
CREATE TABLE integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    provider VARCHAR(100) NOT NULL, -- 'quickbooks', 'xero', 'plaid', etc.
    provider_account_id VARCHAR(255),
    credentials_encrypted TEXT, -- Encrypted tokens/credentials
    status integration_status DEFAULT 'pending',
    last_sync_at TIMESTAMPTZ,
    sync_frequency INTEGER DEFAULT 3600, -- seconds
    error_message TEXT,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Alerts table
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    type VARCHAR(50) NOT NULL, -- 'low_balance', 'large_transaction', 'forecast_change'
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'info', -- 'info', 'warning', 'error', 'critical'
    is_read BOOLEAN DEFAULT FALSE,
    action_url VARCHAR(500),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit Log table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_organizations_active ON organizations(is_active);
CREATE INDEX idx_users_organization_id ON users(organization_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_bank_accounts_organization_id ON bank_accounts(organization_id);
CREATE INDEX idx_transactions_organization_id ON transactions(organization_id);
CREATE INDEX idx_transactions_bank_account_id ON transactions(bank_account_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);
CREATE INDEX idx_transactions_category ON transactions(category);
CREATE INDEX idx_categories_organization_id ON categories(organization_id);
CREATE INDEX idx_budgets_organization_id ON budgets(organization_id);
CREATE INDEX idx_forecasts_organization_id ON forecasts(organization_id);
CREATE INDEX idx_forecast_data_points_forecast_id ON forecast_data_points(forecast_id);
CREATE INDEX idx_forecast_data_points_date ON forecast_data_points(date);
CREATE INDEX idx_scenarios_forecast_id ON scenarios(forecast_id);
CREATE INDEX idx_integrations_organization_id ON integrations(organization_id);
CREATE INDEX idx_alerts_organization_id ON alerts(organization_id);
CREATE INDEX idx_alerts_user_id ON alerts(user_id);
CREATE INDEX idx_audit_logs_organization_id ON audit_logs(organization_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bank_accounts_updated_at BEFORE UPDATE ON bank_accounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_budgets_updated_at BEFORE UPDATE ON budgets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_forecasts_updated_at BEFORE UPDATE ON forecasts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_scenarios_updated_at BEFORE UPDATE ON scenarios FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_integrations_updated_at BEFORE UPDATE ON integrations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default categories
INSERT INTO categories (id, organization_id, name, type, is_system) VALUES
(uuid_generate_v4(), '00000000-0000-0000-0000-000000000000', 'Sales Revenue', 'income', TRUE),
(uuid_generate_v4(), '00000000-0000-0000-0000-000000000000', 'Service Revenue', 'income', TRUE),
(uuid_generate_v4(), '00000000-0000-0000-0000-000000000000', 'Investment Income', 'income', TRUE),
(uuid_generate_v4(), '00000000-0000-0000-0000-000000000000', 'Other Income', 'income', TRUE),
(uuid_generate_v4(), '00000000-0000-0000-0000-000000000000', 'Cost of Goods Sold', 'expense', TRUE),
(uuid_generate_v4(), '00000000-0000-0000-0000-000000000000', 'Salaries & Wages', 'expense', TRUE),
(uuid_generate_v4(), '00000000-0000-0000-0000-000000000000', 'Rent & Utilities', 'expense', TRUE),
(uuid_generate_v4(), '00000000-0000-0000-0000-000000000000', 'Marketing & Advertising', 'expense', TRUE),
(uuid_generate_v4(), '00000000-0000-0000-0000-000000000000', 'Professional Services', 'expense', TRUE),
(uuid_generate_v4(), '00000000-0000-0000-0000-000000000000', 'Insurance', 'expense', TRUE),
(uuid_generate_v4(), '00000000-0000-0000-0000-000000000000', 'Travel & Entertainment', 'expense', TRUE),
(uuid_generate_v4(), '00000000-0000-0000-0000-000000000000', 'Office Supplies', 'expense', TRUE),
(uuid_generate_v4(), '00000000-0000-0000-0000-000000000000', 'Technology', 'expense', TRUE),
(uuid_generate_v4(), '00000000-0000-0000-0000-000000000000', 'Other Expenses', 'expense', TRUE);

-- Create views for common queries
CREATE VIEW current_cash_position AS
SELECT 
    ba.organization_id,
    SUM(ba.current_balance) as total_balance,
    COUNT(ba.id) as account_count,
    MAX(ba.last_synced_at) as last_sync
FROM bank_accounts ba
WHERE ba.is_active = TRUE
GROUP BY ba.organization_id;

CREATE VIEW monthly_cash_flow AS
SELECT 
    t.organization_id,
    DATE_TRUNC('month', t.transaction_date) as month,
    SUM(CASE WHEN t.transaction_type = 'income' THEN t.amount ELSE 0 END) as total_inflow,
    SUM(CASE WHEN t.transaction_type = 'expense' THEN t.amount ELSE 0 END) as total_outflow,
    SUM(CASE WHEN t.transaction_type = 'income' THEN t.amount ELSE -t.amount END) as net_flow
FROM transactions t
WHERE t.transaction_date >= DATE_TRUNC('year', CURRENT_DATE)
GROUP BY t.organization_id, DATE_TRUNC('month', t.transaction_date)
ORDER BY month DESC;
