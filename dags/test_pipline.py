from datetime import datetime, timedelta, timezone
now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
import os
from airflow import DAG
from utils.api_metadata import fetch_marketstack_metadata, update_marketstack_metadata, metadata_exits
from utils.api_eod import fetch_marketstack_eod, update_marketstack_eod
from utils.api_exchangerate import fetch_exchangerate, update_exchangerate
from utils.api_news import fetch_news, update_news
from utils.api_slack import send_slack_message

from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.models import Variable
from airflow.utils.task_group import TaskGroup

from dotenv import load_dotenv

load_dotenv()
SLACK_URL = os.getenv("URL_WEBHOOK_SLACK")
symbols = os.getenv("SYMBOLS_EOD")
date = os.getenv("TARGET_DATE", "2025-10-01")
SLACK_CONN_ID = "slack_connection"
try:
    Variable.get("TARGET_DATE")
except:
    Variable.set("TARGET_DATE", date)
    print(f"Target date not found, setting to {date}")
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}
with DAG(
    dag_id='stock_pipeline_dag',
    default_args=default_args,
    schedule_interval="*/5 * * * *", 
    catchup=False,
    tags=['marketstack', 'pipeline']
) as dag:
    def start_task():
        message = f" {now} - Starting stock pipeline at {Variable.get('TARGET_DATE')}"
        message+="\n"
        # message+="Check Var Environment: "+Variable.get("TARGET_DATE")
        # message+="\n"
        # message+="Check Envirionment: "+ os.getenv("TARGET_DATE")
        # message+="\n"
        # env_vars = {
        #     "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        #     "POSTGRES_HOST": os.getenv("POSTGRES_HOST"),
        #     "POSTGRES_PORT": os.getenv("POSTGRES_PORT"),
        #     "POSTGRES_DB": os.getenv("POSTGRES_DB"),
        #     "POSTGRES_DB_STOCK": os.getenv("POSTGRES_DB_STOCK"),
        #     "URL_WEBHOOK_SLACK": os.getenv("URL_WEBHOOK_SLACK"),
        #     "BASE_URL_MARKETSTACK": os.getenv("BASE_URL_MARKETSTACK"),
        #     "MARKETSTACK_API_KEY": os.getenv("MARKETSTACK_API_KEY"),
        #     "SYMBOLS_EOD": os.getenv("SYMBOLS_EOD"),
        #     "BASE_URL_EXCHANGERATE": os.getenv("BASE_URL_EXCHANGERATE"),
        #     "EXCHANGERATE_API_KEY": os.getenv("EXCHANGERATE_API_KEY"),
        #     "CURRENCIES": os.getenv("CURRENCIES"),
        #     "BASE_URL_NEWS": os.getenv("BASE_URL_NEWS"),
        #     "NEWS_API_KEY": os.getenv("NEWS_API_KEY"),
        #     "SLACK_WEBHOOK_TOKEN": os.getenv("SLACK_WEBHOOK_TOKEN"),
        # }
        # message+="\n"
        # for key, value in env_vars.items():
        #     message+="\n"
        #     message+=f"{key}: {value}"
        send_slack_message(message)
    start = PythonOperator(
        task_id='start',
        python_callable=start_task,
    )

    def metadata_task():
        if not metadata_exits():
            metadata = fetch_marketstack_metadata()
            count = update_marketstack_metadata(metadata)
            message = f"Loaded {count} rows into table tickers_metadata"
            send_slack_message(message)
        else:
            message = "Metadata already exists"
            send_slack_message(message)

    load_metadata = PythonOperator(
        task_id='load_metadata',
        python_callable=metadata_task,
    )


    def eod_task():
        try:
            eod = fetch_marketstack_eod(Variable.get("TARGET_DATE"))
            count = update_marketstack_eod(eod)
            message = f"Loaded {count} rows into table stock_prices"
            send_slack_message(message)
        except Exception as e:
            message = f"Error fetching marketstack eod: {e}, Task: eod_task, Date: {Variable.get('TARGET_DATE')}, Time: {now}"
            send_slack_message(message)

    def exchangerate_task():
        try:
            exchangerate = fetch_exchangerate(Variable.get("TARGET_DATE"))
            count = update_exchangerate(exchangerate)
            message = f"Loaded {count} rows into table exchange_rates"
            send_slack_message(message)
        except Exception as e:
            message = f"Error fetching exchangerate: {e}, Task: exchangerate_task, Date: {Variable.get('TARGET_DATE')}, Time: {now}"
            send_slack_message(message)

    def news_task():
        try:
            for symbol in symbols.split(','): 
                news = fetch_news(symbol, Variable.get("TARGET_DATE"))
                count = update_news(news)
                message = f"Loaded {count} rows into table news"
                send_slack_message(message)
        except Exception as e:
            message = f"Error fetching news: {e}, Task: news_task, Date: {Variable.get('TARGET_DATE')}, Time: {now}"
            send_slack_message(message)

    def next_date_task():
        try:
            date_str = Variable.get("TARGET_DATE")
            dt = datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)
            Variable.set("TARGET_DATE", dt.strftime("%Y-%m-%d"))
            message = f"Next date: {dt.strftime('%Y-%m-%d')}"
            send_slack_message(message)
        except Exception as e:
            message = f"Error fetching next date: {e}, Task: next_date_task, Date: {Variable.get('TARGET_DATE')}, Time: {now}"
            send_slack_message(message)


    next_date = PythonOperator(
        task_id='next_date',
        python_callable=next_date_task,
    )

    def send_slack_message_task():
        message = f":white_check_mark: Stock pipeline completed successfully for {Variable.get('TARGET_DATE')}, Time: {now}"
        send_slack_message(message)

    send_slack = PythonOperator(
        task_id='send_slack_message',
        python_callable=send_slack_message_task,
    )

    end = EmptyOperator(task_id="end")

    with TaskGroup("extract_data", tooltip="Fetch EOD, ExchangeRate, and News data") as extract_data:
        load_eod = PythonOperator(
            task_id='load_eod',
            python_callable=eod_task,
        )
        load_exchangerate = PythonOperator(
            task_id='load_exchangerate',
            python_callable=exchangerate_task,  
        )
        load_news = PythonOperator(
            task_id='load_news',
            python_callable=news_task,
        )
        [load_eod, load_exchangerate, load_news]
    
        start >> load_metadata >> extract_data >> send_slack >> next_date >> end