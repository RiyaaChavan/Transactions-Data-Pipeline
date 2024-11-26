import pandas as pd
from kafka import KafkaConsumer
import psycopg2
from psycopg2.extras import execute_batch
import json
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

# Kafka Consumer configuration
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:29092')
KAFKA_TOPIC = 'financial_transactions'  # Ensure this matches the producer
GROUP_ID = 'financial-consumer-group'

# TimescaleDB connection configuration
DB_HOST = os.getenv('POSTGRES_HOST', 'timescaledb')
DB_NAME = os.getenv('POSTGRES_DB', 'financial_transactions')
DB_USER = os.getenv('POSTGRES_USER', 'admin')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password')

# Connect to TimescaleDB
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

# Insert data into TimescaleDB (using batch insert for efficiency)
def insert_data_to_timescaledb(data_frame):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Prepare data for insertion
    records = data_frame.to_dict(orient='records')
    
    # Convert list of dicts to list of tuples in the correct order
    records = [
        (
            record['id'],
            record['date'],
            record['client_id'],
            record['card_id'],
            record['amount'],
            record['use_chip'],
            record['merchant_id'],
            record['merchant_city'],
            record['merchant_state'],
            record['zip'],
            datetime.now()  # processing_timestamp
        )
        for record in records
    ]

    insert_query = """
        INSERT INTO transactions (
            id, date, client_id, card_id, amount, use_chip,
            merchant_id, merchant_city, merchant_state, zip,
            processing_timestamp
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    try:
        # Execute batch insert
        execute_batch(cursor, insert_query, records)
        
        # Commit and close
        conn.commit()
        logging.info(f"Inserted {len(records)} records into TimescaleDB.")
    except Exception as e:
        logging.error(f"Error inserting data into TimescaleDB: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# Kafka Consumer: Consume messages from the Kafka topic
def consume_and_process():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        group_id=GROUP_ID,
        bootstrap_servers=[KAFKA_BROKER],
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    logging.info(f"Consumer connected to Kafka broker at {KAFKA_BROKER}")
    try:
        for message in consumer:
            logging.info("Received a message from Kafka.")
            transaction = message.value
            
            # Validate transaction data
            required_fields = ['id', 'date', 'client_id', 'card_id', 'amount', 'use_chip', 'merchant_id', 'merchant_city', 'merchant_state', 'zip']
            if not all(field in transaction for field in required_fields):
                logging.warning(f"Missing fields in transaction: {transaction}")
                continue  # Skip this record
            
            # Create a DataFrame (ensure 'date' is datetime)
            df = pd.DataFrame([transaction])
            df['date'] = pd.to_datetime(df['date'])
    
            # Insert processed data into TimescaleDB
            insert_data_to_timescaledb(df)
    
            logging.info(f"Inserted transaction ID: {transaction['id']}")
    except Exception as e:
        logging.error(f"Error in consumer: {e}")
    finally:
        consumer.close()
        logging.info("Kafka consumer closed.")

# Run the consumer
if __name__ == '__main__':
    consume_and_process()