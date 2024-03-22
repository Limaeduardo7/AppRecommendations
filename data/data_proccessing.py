from .data_access import get_data

def get_and_process_product_data(url):
    data = get_data(url)
    if data:
        processed_data = []
        for item in data:
            processed_data.append({
                'product_id': item['product_id'],
                'name': item['name'],
                'description': item['description'],
                'category': item['category'],
                'price': item['price'],
            })
        return processed_data
    else:
        print(f"Erro ao obter dados dos produtos.")
        return None

def get_and_process_order_data(url):
    data = get_data(url)
    if data:
        processed_data = []
        for item in data:
            for product in item.get('items', []):
                processed_data.append({
                    'user_id': item['user_id'],
                    'product_id': product['product_id'],
                    'quantity': product['quantity'],
                    'purchase_date': 'NOW()'
                })
        return processed_data
    else:
        print(f"Erro ao obter dados dos pedidos.")
        return None