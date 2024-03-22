# tasks.py
from typing import Dict, List
import os
from crewai import Task
from textwrap import dedent
from agents import CustomAgents

class CustomTasks:

    def __init__(self):
        self.agents = CustomAgents()
        self.tip_section = dedent("""
            If you do an excellent job, I will give you a $10,000 commission!
        """)

    def parse_webhook_data(self, raw_data: str) -> Dict[str, List[Dict[str, any]]]:
        # Implement webhook data parsing logic
        pass

    def task_inventory_analysis(self, *args):  # Aceita um número arbitrário de argumentos
        """
        Defines a CrewAI task for analyzing inventory data.

        Returns:
            A CrewAI Task object for inventory data analysis.
        """

        agent = self.agents.agent_inventory_analyst()
        description = dedent(f"""
            Hello, Inventory Analyst Agent! Your task is to perform a detailed analysis of the inventory data in our PostgreSQL database. Follow these step-by-step instructions carefully:

            1. Connect to the PostgreSQL database using the connection string provided in the data source:
               postgresql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}

               Make sure to use the correct credentials defined in the 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', and 'DB_NAME' environment variables.

            2. Execute the following SQL query to retrieve all products currently in stock:

               SELECT 
                   p.product_id AS id,
                   p.price AS preco, 
                   p.stock AS quantidade
               FROM
                   products p
               WHERE
                   p.stock > 0;

               Ensure to include the following details for each product:
                - product_id (a unique identifier for the product, renamed as 'id')
                - price (the current selling price of the product, renamed as 'preco')
                - stock (the number of units of this product currently in stock, renamed as 'quantidade')

            3. Carefully validate the retrieved data. Handle any missing or invalid values as follows:
                - Ignore products with missing or invalid IDs (e.g., empty, null, or non-numeric)
                - Replace missing or invalid prices (e.g., empty, null, or non-numeric) with 0
                - Assume the stock quantity is 0 if the value is missing, null, or non-numeric

            4. Organize the validated data into a list of Python dictionaries, where each dictionary represents a product and contains the keys 'id', 'preco', and 'quantidade'.

            5. Return this list as the task output. {self.tip_section}
        """)

        return Task(
            description=description,
            agent=agent,
            expected_output="A list of products currently in stock, with details of ID, price, and quantity."
        )

    def task_recommendations(self, *args):  # Aceita um número arbitrário de argumentos

        agent = self.agents.agent_salesperson()
        description = dedent(f"""
            Hello, Salesperson Agent! Your task is to generate personalized product recommendations for our customers. Follow these step-by-step instructions carefully:

            1. Connect to the PostgreSQL database using the connection string provided in the data source:
               postgresql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}

               Make sure to use the correct credentials defined in the 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', and 'DB_NAME' environment variables.

            2. Execute the following SQL query to retrieve data for all customers who have not made purchases in the last 30 days:

               SELECT 
                   u.user_id,
                   u.name AS customer_name,
                   u.email AS customer_email
               FROM
                   users u
               WHERE
                   u.user_id NOT IN (
                       SELECT 
                           pur.user_id
                       FROM
                           purchases pur
                       WHERE
                           pur.purchase_date >= NOW() - INTERVAL '30 day'
                   );

               For each customer, retrieve the user_id, name (renamed as customer_name), and email (renamed as customer_email).

            3. Execute another SQL query to retrieve data for all products currently in stock:

               SELECT
                   p.product_id,
                   p.name AS product_name,
                   p.category AS product_category,
                   p.price AS product_price,
                   p.stock AS product_quantity
               FROM
                   products p
               WHERE 
                   p.stock > 0;

               For each product, retrieve the product_id, name (renamed as product_name), category (renamed as product_category), price (renamed as product_price), and stock (renamed as product_quantity).

            4. For each eligible customer (who has not purchased in the last 30 days), generate up to 5 product recommendations that match their preferences and are in stock. Follow these criteria:
                - Limit the total number of recommendations generated to a maximum of 30 per day.
                - Prioritize products that the customer is likely to prefer based on the customer_preferences information.
                - If there is not enough information about the customer's preferences, recommend popular products (with high product_quantity) or high-quality products (with high product_category).

            5. For each generated recommendation, insert a new row into the 'product_recommendations' table with the following values:
                - recommendation_id: Generate a unique identifier for the recommendation (e.g., using a UUID or an auto-incrementing sequence).
                - user_id: The user_id of the customer for whom the recommendation is made.
                - client_email: The email address of the customer for whom the recommendation is made.
                - product_id: The product_id of the recommended product.
                - recommendation_date: The current date and time when the recommendation is generated.
                - recommendation_status: Set the initial status of the recommendation to 'pending' or any other appropriate default value.

               Use an SQL INSERT statement like the following to insert each recommendation:

               INSERT INTO product_recommendations (recommendation_id, user_id, client_email, product_id, recommendation_date, recommendation_status)
               VALUES (generate_unique_id(), user_id_value, client_email_value, product_id_value, current_timestamp, 'pending');

               Replace 'generate_unique_id()' with the appropriate function or logic to generate a unique identifier for the recommendation_id column.

            6. Carefully validate the data and handle any missing or invalid values appropriately (e.g., ignore or replace with default values) before inserting into the database.

            7. After successfully inserting all recommendations into the 'product_recommendations' table, return a success message as the task output. {self.tip_section}
        """)

        return Task(
            description=description,
            agent=agent,
            expected_output="A success message after inserting up to 30 recommendations (up to 5 per customer) into the 'product_recommendations' table for customers who have not made purchases in the last 30 days."
        )