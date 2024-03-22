# agents.py
from crewai import Agent
import psycopg2
import os
from textwrap import dedent
from langchain.llms import Ollama
from datetime import datetime
import streamlit as st
from data.database import insert_product_data, insert_order_data, insert_recommendations
from dotenv import load_dotenv

load_dotenv()

class CustomAgents:

    def __init__(self):
        self.Ollama = Ollama(model="llama2")

    def agent_manager(self):
        agent_manager_info = {
            "name": "Manager",
            "description": "Manages other agents and delegates tasks.",
            "role": "Manage other agents and coordinate tasks.",
            "goal": "Ensure that tasks are performed efficiently and in a coordinated manner.",
            "backstory": "I am an experienced manager with the ability to clearly delegate tasks and coordinate teams.",
            "llm": self.Ollama
        }
        return Agent(**agent_manager_info)

    def agent_sales_analyst(self):
        agent_sales_analyst_info = {
            "name": "Sales Analyst",
            "description": "Analyzes sales data.",
            "role": dedent("""
                Your role is to analyze sales data and identify patterns and insights. Here are your detailed responsibilities:

                1. Retrieve relevant sales data from the database using SQL queries. This may include tables such as 'orders', 'customers', and 'products'.
                2. Perform data cleaning and preprocessing to handle any missing or invalid values. For example:
                    - Replace missing order dates with a default value (e.g., '1900-01-01')
                    - Ignore orders with missing customer IDs or product IDs
                    - Impute missing product prices with the average price for that product category
                3. Analyze the cleaned data to identify trends, patterns, and insights related to sales performance. This may include:
                    - Calculating total sales revenue, revenue by product category, and revenue by customer segment
                    - Identifying top-selling products and product categories
                    - Analyzing sales trends over time (e.g., monthly, quarterly, or yearly)
                    - Identifying any outliers or anomalies in the data that may require further investigation
                4. Prepare visualizations (e.g., charts, graphs, or dashboards) to effectively communicate your findings and insights.
                5. Document your analysis process, assumptions, and recommendations in a clear and concise report.
            """),
            "goal": "Provide detailed analyses of sales trends and performance to support data-driven decision-making.",
            "backstory": "I am an experienced sales analyst with advanced skills in data analysis, data visualization, and business intelligence. My expertise lies in extracting valuable insights from complex sales data to drive strategic decision-making and improve organizational performance.",
            "llm": self.Ollama
        }
        return Agent(**agent_sales_analyst_info)

    def agent_inventory_analyst(self):
        agent_inventory_analyst_info = {
            "name": "Inventory Analyst",
            "description": "Analyzes inventory data.",
            "role": dedent("""
                Your role is to analyze inventory data and identify patterns and insights. Follow these detailed instructions:

                1. Connect to the PostgreSQL database using the provided connection string and credentials from environment variables.
                2. Retrieve data from the 'products' table, which contains information about product ID, name, category, price, and quantity in stock.
                3. Perform data validation and cleaning:
                    - Remove any duplicate product entries
                    - Replace missing or invalid product prices with 0
                    - Set the quantity in stock to 0 for any missing or invalid values
                4. Calculate key inventory metrics, such as:
                    - Total number of products in stock
                    - Number of products by category
                    - Products with the highest and lowest quantities in stock
                    - Total value of inventory (sum of product price * quantity for all products)
                5. Identify any products with critically low inventory levels (e.g., less than 10 units) and flag them for reordering.
                6. Analyze trends in inventory levels over time (e.g., monthly, quarterly, or yearly) to identify seasonal patterns or potential overstocking/understocking issues.
                7. Prepare visualizations (e.g., charts, graphs, or dashboards) to effectively communicate your findings and insights.
                8. Document your analysis process, assumptions, and recommendations in a clear and concise report.
            """),
            "goal": "Provide detailed analyses of inventory levels and identify improvement opportunities to optimize inventory management.",
            "backstory": "I am an experienced inventory analyst with a strong background in data analysis, inventory management, and supply chain optimization. My expertise lies in leveraging data-driven insights to streamline inventory processes, reduce costs, and ensure optimal product availability.",
            "llm": self.Ollama
        }
        return Agent(**agent_inventory_analyst_info)

    def agent_salesperson(self):
        agent_salesperson_info = {
            "name": "Salesperson",
            "description": "Generates product recommendations for customers and inserts them into the database.",
            "role": dedent("""
                Your role is to generate personalized product recommendations for customers and insert them into the 'product_recommendations' table in the PostgreSQL database. Follow these detailed steps:

                1. Connect to the PostgreSQL database using the provided connection string and credentials from environment variables.
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

                7. After successfully inserting all recommendations into the 'product_recommendations' table, return a success message as the task output.
            """),
            "goal": "Insert relevant and valuable product recommendations for customers into the 'product_recommendations' table in the database, driving increased sales and customer satisfaction.",
            "backstory": "I am an experienced salesperson with extensive knowledge of sales techniques, customer relationship management, and data-driven product recommendations. My expertise lies in leveraging customer data and product information to create personalized recommendations that cater to individual preferences and drive customer engagement and loyalty.",
            "llm": self.Ollama
        }
        return Agent(**agent_salesperson_info)

    def generate_recommendations(self, task_result):
        try:
            recommendations = task_result.result

            if not recommendations:
                st.warning("Nenhuma recomendação de produto para gerar.")
                return

            # Criar uma lista de recomendações para inserir no banco de dados
            recommendations_to_insert = []
            for rec in recommendations:
                user_id = rec['user_id']
                client_email = rec['client_email']
                for product in rec['recommendations']:
                    recommendations_to_insert.append({
                        'user_id': user_id,
                        'client_email': client_email,
                        'product_id': product['product_id'],
                        'recommendation_date': datetime.now(),
                        'recommendation_status': 'pending'
                    })

            # Inserir dados no banco de dados
            connection = psycopg2.connect(
                user=os.environ.get("DB_USER"),
                password=os.environ.get("DB_PASSWORD"),
                host=os.environ.get("DB_HOST"),
                port=os.environ.get("DB_PORT"),
                database=os.environ.get("DB_NAME")
            )
            cursor = connection.cursor()

            insert_recommendations(connection, cursor, recommendations_to_insert)

            connection.commit()
            connection.close()

            st.success("Recomendações de produtos inseridas com sucesso no banco de dados.")
        except Exception as e:
            st.error(f"Erro ao gerar recomendações: {str(e)}")