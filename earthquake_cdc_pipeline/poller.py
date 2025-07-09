import requests
from datetime import datetime, timedelta
import mysql.connector
import time
import json

def get_db_connection():
    return mysql.connector.connect(
        host="localhost", # Or "127.0.0.1"
        user="root",
        password="root",
        database="earthquake_db"
    )

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS earthquake_minute (
        id VARCHAR(255) PRIMARY KEY,
        time DATETIME,
        geometry JSON,
        properties JSON,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def fetch_earthquakes():
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=1)
    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_time.isoformat()}&endtime={end_time.isoformat()}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['features']
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def store_earthquakes(quakes):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for quake in quakes:
        try:
            cursor.execute("""
            INSERT INTO earthquake_minute (id, time, geometry, properties)
            VALUES (%s, FROM_UNIXTIME(%s/1000), %s, %s)
            ON DUPLICATE KEY UPDATE 
                geometry = VALUES(geometry),
                properties = VALUES(properties),
                last_updated = CURRENT_TIMESTAMP
            """, (
                quake['id'],
                quake['properties']['time'],
                json.dumps(quake['geometry']),
                json.dumps(quake['properties'])
            ))
        except Exception as e:
            print(f"Error storing quake {quake['id']}: {e}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("CDC Pipeline started.")
    
    try:
        while True:
            quakes = fetch_earthquakes()
            if quakes:
                print(f"Processing {len(quakes)} new quakes")
                store_earthquakes(quakes)
            time.sleep(60)  # Poll every minute
    except KeyboardInterrupt:
        print("Pipeline stopped")
