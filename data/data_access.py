import requests

def get_data(api_url, headers=None, params=None):
    """
    Fetches data from an API endpoint using a GET request.

    Args:
        api_url (str): The URL of the API endpoint.
        headers (dict, optional): Headers to include in the request.
        params (dict, optional): Parameters to include in the request.

    Returns:
        dict: A dictionary containing the fetched data, or None on error.
    """
    try:
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()  # Raises an exception for non-2xx status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {str(e)}")
        return None