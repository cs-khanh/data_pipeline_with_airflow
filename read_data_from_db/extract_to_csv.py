import psycopg2
from psycopg2 import sql
import csv
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

def connect_to_db():
    dbname=os.getenv("POSTGRES_DB_STOCK")
    user=os.getenv("POSTGRES_USER")
    password=os.getenv("POSTGRES_PASSWORD")
    host=os.getenv("POSTGRES_HOST")
    port=os.getenv("POSTGRES_PORT", "5432")
    
    # If host is "postgres" (Docker service name), try localhost when running from host
    if host == "postgres":
        try:
            # Try connecting to postgres first (works inside Docker)
            conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port, connect_timeout=2)
            print(f"Connected to {host}:{port}")
            return conn
        except psycopg2.OperationalError:
            # If that fails, try localhost with port 5433 (container port mapped to host)
            print(f"Could not connect to {host}, trying localhost:5433...")
            host = "localhost"
            port = "5433"  # Container port 5432 is mapped to host port 5433
    
    print(f"Connecting to {host}:{port} (db: {dbname}, user: {user})")
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    return conn

def get_all_tables(cursor):
    """Lấy danh sách tất cả các table trong database"""
    query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]

def export_table_to_csv(cursor, table_name, output_dir):
    """Export một table ra file CSV"""
    # Lấy tất cả dữ liệu từ table (sử dụng sql.Identifier để tránh SQL injection)
    query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # Lấy tên các cột
    column_names = [desc[0] for desc in cursor.description]
    
    # Tạo thư mục output nếu chưa có
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Tạo file CSV
    csv_file_path = output_dir / f"{table_name}.csv"
    
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Ghi header
        writer.writerow(column_names)
        # Ghi dữ liệu
        writer.writerows(rows)
    
    print(f"✓ Exported {len(rows)} rows from '{table_name}' to '{csv_file_path}'")
    return csv_file_path

def main():
    # Kết nối database
    conn = connect_to_db()
    cursor = conn.cursor()
    
    try:
        # Lấy danh sách tất cả các table
        print("\n📋 Getting list of tables...")
        tables = get_all_tables(cursor)
        print(f"Found {len(tables)} tables: {', '.join(tables)}")
        
        # Tạo thư mục output
        output_dir = Path(__file__).parent / "csv_exports"
        output_dir.mkdir(exist_ok=True)
        print(f"\n📁 Output directory: {output_dir}\n")
        
        # Export từng table ra CSV
        exported_files = []
        for table in tables:
            try:
                csv_file = export_table_to_csv(cursor, table, output_dir)
                exported_files.append(csv_file)
            except Exception as e:
                print(f"✗ Error exporting table '{table}': {e}")
        
        print(f"\n✅ Successfully exported {len(exported_files)} tables to CSV files!")
        print(f"📂 All files saved in: {output_dir}")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()