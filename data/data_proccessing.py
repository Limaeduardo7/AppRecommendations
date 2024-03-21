import requests

def get_and_process_product_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Processar os dados dos produtos
        processed_data = []
        for item in data:
            processed_data.append({
                'Product ID': item['product_id'],
                'Name': item['name'],
                'Description': item['description'],
                'Category': item['category'],
                'Price': item['price'],
                'Stock': 0  # 0 para estoque inicial
            })
        return processed_data
    else:
        print(f"Erro ao fazer a requisição dos produtos: {response.status_code}")

def get_and_process_order_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Processar os dados dos pedidos
        processed_data = []
        for item in data:
            for product in item.get('items', []):
                processed_data.append({
                    'User ID': item['user_id'],
                    'Product ID': product['product_id'],
                    'Quantity': product['quantity'],
                    'Purchase Date': 'now()'
                })
        return processed_data
    else:
        print(f"Erro ao fazer a requisição dos pedidos: {response.status_code}")