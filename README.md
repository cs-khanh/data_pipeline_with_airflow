# Stock Data Pipeline Project

Dự án này là một pipeline tự động thu thập dữ liệu chứng khoán sử dụng Apache Airflow, bao gồm:
- Dữ liệu giá cổ phiếu (EOD - End of Day)
- Tỷ giá hối đoái
- Tin tức liên quan đến cổ phiếu
- Metadata của các mã cổ phiếu

## 🏗️ Kiến trúc hệ thống

- **Apache Airflow**: Orchestration và scheduling
- **PostgreSQL**: Database lưu trữ dữ liệu
- **Docker & Docker Compose**: Containerization
- **APIs**: MarketStack, ExchangeRate-API, NewsAPI
- **Slack**: Thông báo trạng thái pipeline

## 📋 Yêu cầu hệ thống

- Docker và Docker Compose
- Tối thiểu 4GB RAM
- Tối thiểu 2 CPU cores
- Tối thiểu 10GB dung lượng ổ cứng

## 🚀 Hướng dẫn cài đặt và chạy

### 1. Clone repository
```bash
git clone <repository-url>
cd MiniProject
```

### 2. Tạo file environment variables
Tạo file `.env` trong thư mục gốc với nội dung sau:

```env
# Database Configuration
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=airflow
POSTGRES_DB_STOCK=stock_data

# Airflow Configuration
AIRFLOW_UID=50000
AIRFLOW_PORT=8080
AIRFLOW_WWW_USER_USERNAME=airflow
AIRFLOW_WWW_USER_PASSWORD=airflow

# API Keys (Cần đăng ký để lấy API keys)
BASE_URL_MARKETSTACK=http://api.marketstack.com/v1
MARKETSTACK_API_KEY=your_marketstack_api_key
SYMBOLS_EOD=AAPL,MSFT,GOOGL,TSLA,AMZN

BASE_URL_EXCHANGERATE=https://api.exchangerate-api.com/v4
EXCHANGERATE_API_KEY=your_exchangerate_api_key
CURRENCIES=USD,EUR,GBP,JPY

BASE_URL_NEWS=https://newsapi.org/v2
NEWS_API_KEY=your_news_api_key

# Slack Configuration
URL_WEBHOOK_SLACK=https://hooks.slack.com/services/your/slack/webhook
SLACK_WEBHOOK_TOKEN=your_slack_token

# Pipeline Configuration
TARGET_DATE=2025-01-01
```

### 3. Khởi động hệ thống
```bash
# Khởi động tất cả services
docker compose up -d
#Chạy lệnh để cấp quyền để có permission cho DB
sudo chmod -R 777 ./database
sudo chmod -R 777 ./logs
# Kiểm tra trạng thái containers
docker compose ps

# Khởi chạy tạo Database
docker exec -it miniproject-postgres-1 psql -U airflow -d airflow
\i /docker-entrypoint-initdb.d/init_db.sql
```

### 4. Truy cập Airflow Web UI
- Mở trình duyệt và truy cập: `http://localhost:8080`
- Username: `airflow`
- Password: `airflow`

### 5. Kích hoạt DAG
1. Trong Airflow UI, tìm DAG `stock_pipeline_dag`
2. Click vào toggle switch để kích hoạt DAG
3. DAG sẽ chạy theo lịch trình mỗi 30 phút

## 📊 Cấu trúc Database

Pipeline tạo ra 4 bảng chính:

### `tickers_metadata`
- Lưu thông tin metadata của các mã cổ phiếu
- Bao gồm: ticker, name, stock_exchange_name, etc.

### `stock_prices`
- Lưu dữ liệu giá cổ phiếu theo ngày
- Bao gồm: ticker, date, open, high, low, close, volume

### `exchange_rates`
- Lưu tỷ giá hối đoái
- Bao gồm: date, base_currency, target_currency, rate

### `news`
- Lưu tin tức liên quan đến cổ phiếu
- Bao gồm: title, description, url, sentiment_score, etc.

## 🔧 Cấu hình Pipeline
```
   * * * * *
   │ │ │ │ └── Thứ trong tuần (0 - 6, Chủ nhật = 0)
   │ │ │ └──── Tháng (1 - 12)
   │ │ └────── Ngày trong tháng (1 - 31)
   │ └──────── Giờ (0 - 23)
   └────────── Phút (0 - 59)
```

### Lịch trình chạy
- DAG chạy mỗi 30 phút: `*/30 * * * *`
- Có thể thay đổi trong file `dags/test_pipline.py`

### Workflow
1. **start**: Khởi tạo pipeline và gửi thông báo Slack
2. **load_metadata**: Tải metadata của các mã cổ phiếu (chỉ chạy lần đầu)
3. **extract_data** (TaskGroup):
   - `load_eod`: Tải dữ liệu giá cổ phiếu
   - `load_exchangerate`: Tải tỷ giá hối đoái
   - `load_news`: Tải tin tức
4. **send_slack_message**: Gửi thông báo hoàn thành
5. **next_date**: Cập nhật ngày tiếp theo
6. **end**: Kết thúc pipeline

## 🛠️ Quản lý và Monitoring

### Xem logs
```bash
# Xem logs của tất cả services
docker-compose logs -f

# Xem logs của service cụ thể
docker compose logs -f airflow-scheduler
docker compose logs -f airflow-webserver
```

### Dừng hệ thống
```bash
# Dừng tất cả services
docker compose down

# Dừng và xóa volumes (CẢNH BÁO: Sẽ mất dữ liệu)
docker compose down -v
```

### Restart service
```bash
# Restart service cụ thể
docker compose restart airflow-scheduler

# Restart tất cả services
docker compose restart
```

## 🔑 Lấy API Keys

### MarketStack API
1. Truy cập: https://marketstack.com/
2. Đăng ký tài khoản miễn phí
3. Lấy API key từ dashboard

### ExchangeRate API
1. Truy cập: https://exchangerate-api.com/
2. Đăng ký tài khoản miễn phí
3. Lấy API key từ dashboard

### News API
1. Truy cập: https://newsapi.org/
2. Đăng ký tài khoản miễn phí
3. Lấy API key từ dashboard

### Slack Webhook
1. Truy cập Slack workspace
2. Tạo Incoming Webhook: https://api.slack.com/messaging/webhooks
3. Copy webhook URL

## 🐛 Troubleshooting

### Lỗi thường gặp

1. **Permission denied khi khởi động**
   ```bash
   # Set quyền cho thư mục
   sudo chown -R 50000:0 ./logs ./dags ./plugins
   ```

2. **Database connection failed**
   - Kiểm tra PostgreSQL container đã chạy chưa
   - Kiểm tra environment variables trong `.env`

3. **API rate limit exceeded**
   - Kiểm tra API keys có hợp lệ không
   - Tăng thời gian interval giữa các lần gọi API

4. **DAG không chạy**
   - Kiểm tra DAG đã được kích hoạt chưa
   - Xem logs trong Airflow UI

### Kiểm tra trạng thái
```bash
# Kiểm tra containers
docker compose ps

# Kiểm tra logs
docker compose logs airflow-scheduler
docker compose logs airflow-webserver

# Kiểm tra database connection
docker compose exec postgres psql -U airflow -d stock_data -c "\dt"
```

## 📈 Mở rộng

### Thêm mã cổ phiếu mới
Chỉnh sửa biến `SYMBOLS_EOD` trong file `.env`:
```env
SYMBOLS_EOD=AAPL,MSFT,GOOGL,TSLA,AMZN,NVDA,META
```

### Thêm loại tiền tệ mới
Chỉnh sửa biến `CURRENCIES` trong file `.env`:
```env
CURRENCIES=USD,EUR,GBP,JPY,CNY,VND
```

### Thay đổi lịch trình
Chỉnh sửa `schedule_interval` trong file `dags/test_pipline.py`:
```python
schedule_interval="0 9 * * *",  # Chạy lúc 9h sáng mỗi ngày
```

## 📝 Ghi chú

- Pipeline được thiết kế để chạy liên tục và tự động cập nhật dữ liệu
- Dữ liệu được lưu trữ trong PostgreSQL và có thể truy xuất qua SQL queries
- Thông báo Slack giúp theo dõi trạng thái pipeline
- Có thể mở rộng thêm các nguồn dữ liệu khác bằng cách thêm tasks mới

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## 📄 License

MIT License
