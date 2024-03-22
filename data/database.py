import psycopg2
from psycopg2 import Error
from datetime import datetime

def insert_product_data(connection, cursor, product_data):
    for product in product_data:
        try:
            cursor.execute("""
                INSERT INTO products (name, description, category, price, stock)
                VALUES (%s, %s, %s, %s, %s)
            """, (product['name'], product['description'], product['category'], product['price'], product['stock']))
            connection.commit()
        except Error as e:
            print(f"Erro ao inserir dados na tabela de produtos: {e}")

def insert_order_data(connection, cursor, order_data):
    for order in order_data:
        user_id = order['user_id']
        for product in order['recommendations']:
            try:
                cursor.execute("""
                    INSERT INTO purchases (user_id, product_id, purchase_date, quantity)
                    VALUES (%s, %s, NOW(), 1)
                """, (user_id, product['product_id']))
                connection.commit()
            except Error as e:
                print(f"Erro ao inserir dados na tabela de compras: {e}")

def insert_recommendations(connection, cursor, recommendations):
    for recommendation in recommendations:
        try:
            cursor.execute("""
                INSERT INTO product_recommendations (recommendation_id, user_id, client_email, product_id, recommendation_date, recommendation_status)
                VALUES (DEFAULT, %s, %s, %s, %s, %s)
            """, (recommendation['user_id'], recommendation['client_email'], recommendation['product_id'], recommendation['recommendation_date'], recommendation['recommendation_status']))
            connection.commit()
        except Error as e:
            print(f"Erro ao inserir recomendação na tabela product_recommendations: {e}")