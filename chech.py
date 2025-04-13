import sqlite3
from datetime import datetime

def insert_credit_data():
    # Data to be inserted
    credit_data = {
        'id': 4,
        'monthly_surplus': 8000.0,
        'financial_diversity': 3,
        'merchant_txns': 15,
        'geo_stability': 4,
        'business_docs': 5,
        'score': None,
        'last_updated': '2025-04-12 21:54:26'
    }

    try:
        # Connect to the database
        conn = sqlite3.connect('credit.db')
        cursor = conn.cursor()

        # Insert data into the credit table
        cursor.execute('''
            INSERT INTO credit (id, monthly_surplus, financial_diversity, merchant_txns, geo_stability, business_docs, score, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            credit_data['id'],
            credit_data['monthly_surplus'],
            credit_data['financial_diversity'],
            credit_data['merchant_txns'],
            credit_data['geo_stability'],
            credit_data['business_docs'],
            credit_data['score'],
            credit_data['last_updated']
        ))

        # Commit the transaction
        conn.commit()
        print(f"Data inserted successfully for user_id {credit_data['id']}")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        # Close the database connection
        conn.close()

# Call the function to insert the data
insert_credit_data()