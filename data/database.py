import psycopg2
from psycopg2 import Error

def insert_product_data(connection, cursor, product_data):
    for product in product_data:
        try:
            cursor.execute("""
                INSERT INTO products (name, description, category, price, stock)
                VALUES (%s, %s, %s, %s, %s)
            """, (product['Name'], product['Description'], product['Category'], product['Price'], product['Stock']))
            connection.commit()
        except Error as e:
            print(f"Erro ao inserir dados na tabela de produtos: {e}")

def insert_order_data(connection, cursor, order_data):
    for order in order_data:
        # Inserir o pedido na tabela purchases
        for product in order.get('items', []):
            try:
                cursor.execute("""
                    INSERT INTO purchases (user_id, product_id, quantity, purchase_date)
                    VALUES (%s, %s, %s, now())
                """, (order['User ID'], product['product_id'], product['quantity']))
                connection.commit()
            except Error as e:
                print(f"Erro ao inserir dados na tabela de compras: {e}")
                
def insert_recommendations(connection, cursor, recommendations):
    for recommendation in recommendations:
        try:
            cursor.execute("""
                INSERT INTO product_recommendations (user_id, product_id, recommendation_date, recommendation_status)
                VALUES (%s, %s, %s, %s)
            """, (recommendation['user_id'], recommendation['product_id'], recommendation['recommendation_date'], recommendation['recommendation_status']))
            connection.commit()
        except Error as e:
            print(f"Error inserting recommendation into product_recommendations table: {e}")
