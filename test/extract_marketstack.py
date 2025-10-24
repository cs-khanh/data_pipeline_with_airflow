import json
from datetime import datetime

# Đọc file JSON
with open('/home/khanh/MiniProject/Marketstack_eod.json', 'r') as f:
    data = json.load(f)

print("=" * 80)
print("PHÂN TÍCH CẤU TRÚC DỮ LIỆU MARKETSTACK")
print("=" * 80)

# 1. Phân tích cấu trúc tổng thể
print("\n1. CẤU TRÚC TỔNG THỂ:")
print(f"   - Có phần 'pagination': {list(data['pagination'].keys())}")
print(f"   - Có phần 'data': Mảng chứa {len(data['data'])} bản ghi")

# 2. Phân tích các trường dữ liệu
print("\n2. CÁC TRƯỜNG DỮ LIỆU TRONG MỖI RECORD:")
if data['data']:
    sample = data['data'][0]
    for key, value in sample.items():
        data_type = type(value).__name__
        print(f"   - {key:20s}: {data_type:10s} | Ví dụ: {value}")

# 3. Kiểm tra giá trị NULL
print("\n3. KIỂM TRA GIÁ TRỊ NULL:")
null_fields = {}
for record in data['data']:
    for key, value in record.items():
        if value is None:
            if key not in null_fields:
                null_fields[key] = 0
            null_fields[key] += 1

if null_fields:
    for field, count in null_fields.items():
        print(f"   - {field}: {count} null values")
else:
    print("   - Không có trường nào có giá trị NULL (trừ exchange_code)")

# 4. Đề xuất Database Schema
print("\n" + "=" * 80)
print("ĐỀ XUẤT DATABASE SCHEMA")
print("=" * 80)

print("""
OPTION 1: THIẾT KẾ ĐƠN GIẢN (1 TABLE)
─────────────────────────────────────────

Table: stock_eod_data
├── id (SERIAL PRIMARY KEY)
├── symbol (VARCHAR(10) NOT NULL)
├── name (VARCHAR(255))
├── date (TIMESTAMP NOT NULL)
├── exchange (VARCHAR(10))
├── exchange_code (VARCHAR(20))
├── asset_type (VARCHAR(20))
├── price_currency (VARCHAR(3))
│
├── open (DECIMAL(15,4))
├── high (DECIMAL(15,4))
├── low (DECIMAL(15,4))
├── close (DECIMAL(15,4))
├── volume (DECIMAL(20,2))
│
├── adj_open (DECIMAL(15,4))
├── adj_high (DECIMAL(15,4))
├── adj_low (DECIMAL(15,4))
├── adj_close (DECIMAL(15,4))
├── adj_volume (DECIMAL(20,2))
│
├── split_factor (DECIMAL(10,4))
├── dividend (DECIMAL(15,4))
│
├── created_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
└── updated_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

INDEX: idx_symbol_date ON stock_eod_data(symbol, date)
INDEX: idx_date ON stock_eod_data(date)

─────────────────────────────────────────
OPTION 2: THIẾT KẾ CHUẨN HÓA (3 TABLES)
─────────────────────────────────────────

Table: stocks
├── id (SERIAL PRIMARY KEY)
├── symbol (VARCHAR(10) UNIQUE NOT NULL)
├── name (VARCHAR(255))
├── exchange (VARCHAR(10))
├── exchange_code (VARCHAR(20))
├── asset_type (VARCHAR(20))
├── price_currency (VARCHAR(3))
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)

Table: stock_prices
├── id (SERIAL PRIMARY KEY)
├── stock_id (INTEGER REFERENCES stocks(id))
├── date (TIMESTAMP NOT NULL)
├── open (DECIMAL(15,4))
├── high (DECIMAL(15,4))
├── low (DECIMAL(15,4))
├── close (DECIMAL(15,4))
├── volume (DECIMAL(20,2))
├── created_at (TIMESTAMP)
└── UNIQUE(stock_id, date)

Table: stock_adjustments
├── id (SERIAL PRIMARY KEY)
├── stock_id (INTEGER REFERENCES stocks(id))
├── date (TIMESTAMP NOT NULL)
├── adj_open (DECIMAL(15,4))
├── adj_high (DECIMAL(15,4))
├── adj_low (DECIMAL(15,4))
├── adj_close (DECIMAL(15,4))
├── adj_volume (DECIMAL(20,2))
├── split_factor (DECIMAL(10,4))
├── dividend (DECIMAL(15,4))
├── created_at (TIMESTAMP)
└── UNIQUE(stock_id, date)

─────────────────────────────────────────
SQL CREATE STATEMENTS (OPTION 1)
─────────────────────────────────────────
""")

sql_option1 = """
CREATE TABLE stock_eod_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    name VARCHAR(255),
    date TIMESTAMP NOT NULL,
    exchange VARCHAR(10),
    exchange_code VARCHAR(20),
    asset_type VARCHAR(20),
    price_currency VARCHAR(3),
    
    open DECIMAL(15,4),
    high DECIMAL(15,4),
    low DECIMAL(15,4),
    close DECIMAL(15,4),
    volume DECIMAL(20,2),
    
    adj_open DECIMAL(15,4),
    adj_high DECIMAL(15,4),
    adj_low DECIMAL(15,4),
    adj_close DECIMAL(15,4),
    adj_volume DECIMAL(20,2),
    
    split_factor DECIMAL(10,4) DEFAULT 1.0,
    dividend DECIMAL(15,4) DEFAULT 0.0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_symbol_date ON stock_eod_data(symbol, date);
CREATE INDEX idx_date ON stock_eod_data(date);
CREATE INDEX idx_symbol ON stock_eod_data(symbol);
"""

print(sql_option1)

print("""
─────────────────────────────────────────
SQL CREATE STATEMENTS (OPTION 2)
─────────────────────────────────────────
""")

sql_option2 = """
CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255),
    exchange VARCHAR(10),
    exchange_code VARCHAR(20),
    asset_type VARCHAR(20),
    price_currency VARCHAR(3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE stock_prices (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    date TIMESTAMP NOT NULL,
    open DECIMAL(15,4),
    high DECIMAL(15,4),
    low DECIMAL(15,4),
    close DECIMAL(15,4),
    volume DECIMAL(20,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, date)
);

CREATE TABLE stock_adjustments (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    date TIMESTAMP NOT NULL,
    adj_open DECIMAL(15,4),
    adj_high DECIMAL(15,4),
    adj_low DECIMAL(15,4),
    adj_close DECIMAL(15,4),
    adj_volume DECIMAL(20,2),
    split_factor DECIMAL(10,4) DEFAULT 1.0,
    dividend DECIMAL(15,4) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, date)
);

CREATE INDEX idx_stock_prices_date ON stock_prices(date);
CREATE INDEX idx_stock_adjustments_date ON stock_adjustments(date);
"""

print(sql_option2)

print("""
─────────────────────────────────────────
SO SÁNH 2 PHƯƠNG ÁN
─────────────────────────────────────────

OPTION 1 (1 Table):
✓ Ưu điểm: Đơn giản, dễ query, phù hợp cho ứng dụng nhỏ
✗ Nhược điểm: Trùng lặp thông tin stock, khó maintain

OPTION 2 (3 Tables - Normalized):
✓ Ưu điểm: Chuẩn hóa, không trùng lặp, dễ scale, dễ maintain
✗ Nhược điểm: Phức tạp hơn, cần JOIN khi query

KHUYẾN NGHỊ: 
- Dùng OPTION 2 cho production, long-term project
- Dùng OPTION 1 cho prototype, testing, hoặc ứng dụng đơn giản
""")

# 5. Tạo sample INSERT statements
print("\n" + "=" * 80)
print("SAMPLE INSERT STATEMENTS")
print("=" * 80)

sample_record = data['data'][0]

# Option 1
print("\n-- OPTION 1: Insert vào 1 table")
print(f"""
INSERT INTO stock_eod_data (
    symbol, name, date, exchange, exchange_code, asset_type, price_currency,
    open, high, low, close, volume,
    adj_open, adj_high, adj_low, adj_close, adj_volume,
    split_factor, dividend
) VALUES (
    '{sample_record['symbol']}', '{sample_record['name']}', '{sample_record['date']}',
    '{sample_record['exchange']}', {'NULL' if sample_record['exchange_code'] is None else f"'{sample_record['exchange_code']}'"}, 
    '{sample_record['asset_type']}', '{sample_record['price_currency']}',
    {sample_record['open']}, {sample_record['high']}, {sample_record['low']}, 
    {sample_record['close']}, {sample_record['volume']},
    {sample_record['adj_open']}, {sample_record['adj_high']}, {sample_record['adj_low']}, 
    {sample_record['adj_close']}, {sample_record['adj_volume']},
    {sample_record['split_factor']}, {sample_record['dividend']}
);
""")

# Option 2
print("-- OPTION 2: Insert vào 3 tables")
print(f"""
-- Bước 1: Insert stock info
INSERT INTO stocks (symbol, name, exchange, exchange_code, asset_type, price_currency)
VALUES ('{sample_record['symbol']}', '{sample_record['name']}', '{sample_record['exchange']}',
        {'NULL' if sample_record['exchange_code'] is None else f"'{sample_record['exchange_code']}'"}, 
        '{sample_record['asset_type']}', '{sample_record['price_currency']}')
ON CONFLICT (symbol) DO NOTHING
RETURNING id;

-- Bước 2: Insert price data (giả sử stock_id = 1)
INSERT INTO stock_prices (stock_id, date, open, high, low, close, volume)
VALUES (1, '{sample_record['date']}', {sample_record['open']}, {sample_record['high']}, 
        {sample_record['low']}, {sample_record['close']}, {sample_record['volume']});

-- Bước 3: Insert adjustment data
INSERT INTO stock_adjustments (stock_id, date, adj_open, adj_high, adj_low, 
                                adj_close, adj_volume, split_factor, dividend)
VALUES (1, '{sample_record['date']}', {sample_record['adj_open']}, {sample_record['adj_high']}, 
        {sample_record['adj_low']}, {sample_record['adj_close']}, {sample_record['adj_volume']},
        {sample_record['split_factor']}, {sample_record['dividend']});
""")

print("\n" + "=" * 80)
print("HOÀN THÀNH PHÂN TÍCH")
print("=" * 80)

