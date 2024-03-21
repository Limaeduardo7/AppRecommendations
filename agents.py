from crewai import Agent
import psycopg2
import os
from textwrap import dedent
from langchain.llms import Ollama
from datetime import datetime, timedelta
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
            "role": "Analyze sales data and identify patterns and insights.",
            "goal": "Provide detailed analyses of sales trends and performance.",
            "backstory": "I am an experienced sales analyst with advanced skills in data analysis and visualization.",
            "llm": self.Ollama
        }
        return Agent(**agent_sales_analyst_info)

    def agent_inventory_analyst(self):
        agent_inventory_analyst_info = {
            "name": "Inventory Analyst",
            "description": "Analyzes inventory data.",
            "role": "Analyze inventory data and identify patterns and insights.",
            "goal": "Provide detailed analyses of inventory levels and identify improvement opportunities.",
            "backstory": "I am an experienced inventory analyst with solid skills in inventory management and data analysis.",
            "llm": self.Ollama
        }
        return Agent(**agent_inventory_analyst_info)

    def agent_salesperson(self):
        agent_salesperson_info = {
            "name": "Salesperson",
            "description": "Generates product recommendations for customers.",
            "role": "Analyze customer and product data to generate personalized recommendations.",
            "goal": "Provide relevant and valuable product recommendations to customers based on their preferences and purchase history.",
            "backstory": "I am an experienced salesperson with extensive knowledge of sales techniques and customer relationship skills.",
            "llm": self.Ollama
        }
        return Agent(**agent_salesperson_info)


    def generate_recommendations(self, task_result):
        try:
            recommendations = task_result.result

            if not recommendations:
                st.warning("No product recommendations to generate.")
                return

            # Criar uma lista de recomendações para inserir no banco de dados
            recommendations_to_insert = []
            for rec in recommendations:
                contact_id = rec['contact_id']
                for product in rec['recommendations']:
                    recommendations_to_insert.append({
                        'user_id': contact_id,
                        'product_id': product['id'],
                        'recommendation_date': datetime.now(),
                        'recommendation_status': 'Pending'
                    })

            table = [['Contact', 'Product ID', 'Price']]
            for rec in recommendations:
                contact = rec['contact']
                for product in rec['recommendations']:
                    table.append([contact, product['id'], product['price']])

            # Inserir dados no banco de dados
            connection = psycopg2.connect(
                user=os.environ.get("DB_USER"),
                password=os.environ.get("DB_PASSWORD"),
                host=os.environ.get("DB_HOST"),
                port=os.environ.get("DB_PORT"),
                database=os.environ.get("DB_NAME")
            )
            cursor = connection.cursor()

            # Obter os dados de produtos do banco de dados
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()

            insert_product_data(connection, cursor, products)
            insert_order_data(connection, cursor, recommendations)
            insert_recommendations(connection, cursor, recommendations_to_insert)

            connection.close()

            return "\n".join([" | ".join(map(str, row)) for row in table])
        except Exception as e:
            st.error(f"Error generating recommendations: {str(e)}")
            return None