DROP DATABASE IF EXISTS stock_data;
CREATE DATABASE stock_data;

\c stock_data;

CREATE TABLE IF NOT EXISTS tickers_metadata (
    ticker TEXT PRIMARY KEY NOT NULL,    -- Mã cổ phiếu: AAPL, MSFT, TSLA,...
    name TEXT,                           -- Tên công ty đầy đủ
    has_intraday BOOLEAN,
    has_eod BOOLEAN,
    stock_exchange_name TEXT,            -- NASDAQ - ALL MARKETS
    acronym TEXT,                        -- NASDAQ
    mic TEXT,                            -- XNAS
    ingested_at TIMESTAMPTZ DEFAULT NOW()  -- Thời điểm nạp
);

CREATE TABLE IF NOT EXISTS stock_prices (
    ticker TEXT NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(18, 2),
    high DECIMAL(18, 2),
    low DECIMAL(18, 2),
    close DECIMAL(18, 2),
    volume BIGINT,
    asset_type TEXT,
    price_currency TEXT,

    -- 📊 Các chỉ số tính ngay khi crawl
    daily_change NUMERIC(18, 2),
    daily_return NUMERIC(10, 4),
    volatility NUMERIC(18, 2),
    avg_price NUMERIC(18, 2),
    turnover NUMERIC(18, 2),
    gap NUMERIC(18, 2),
    range_ratio NUMERIC(10, 4),

    ingested_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (ticker, date)
);

CREATE TABLE IF NOT EXISTS exchange_rates (
    date DATE NOT NULL,
    base_currency TEXT NOT NULL,
    target_currency TEXT NOT NULL,
    rate DECIMAL(18, 6),
    -- 💱 Tính ngay trong lúc crawl
    inverse_rate NUMERIC(18, 6),
    rate_change NUMERIC(10, 4),

    ingested_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (date, base_currency, target_currency)
);

CREATE TABLE IF NOT EXISTS news (
    uuid TEXT PRIMARY KEY NOT NULL,
    title TEXT,
    description TEXT,
    url TEXT,
    image_url TEXT,
    language TEXT,
    source TEXT,
    relevance_score DECIMAL(18, 4),
    symbol TEXT,
    country TEXT,
    type TEXT,
    industry TEXT,
    match_score DECIMAL(18, 6),
    sentiment_score DECIMAL(18, 4),

    -- 🧠 Các chỉ số cảm xúc tính ngay
    sentiment_label TEXT,
    impact_index DECIMAL(18, 4),
    weighted_sentiment DECIMAL(18, 4),
    
    published_at TIMESTAMPTZ,
    ingested_at TIMESTAMPTZ DEFAULT NOW()
);

