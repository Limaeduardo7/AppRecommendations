import os
import psycopg2
import pandas as pd
import streamlit as st
from crewai import Crew
from agents import CustomAgents
from tasks import CustomTasks
from data.data_proccessing import get_and_process_product_data, get_and_process_order_data

class CustomCrew:
    def __init__(self):
        self.agents = CustomAgents()
        self.tasks = CustomTasks()

    def run(self):
        # Obter as URLs das APIs a partir das variáveis de ambiente
        products_api_url = os.environ.get('PRODUCTS_API_URL')
        orders_api_url = os.environ.get('ORDERS_API_URL')

        # Fazendo a requisição e processando os dados dos produtos
        product_data = get_and_process_product_data(products_api_url)

        # Fazendo a requisição e processando os dados dos pedidos
        order_data = get_and_process_order_data(orders_api_url)

        agent_manager = self.agents.agent_manager()
        agent_sales_analyst = self.agents.agent_sales_analyst()
        agent_inventory_analyst = self.agents.agent_inventory_analyst()
        agent_salesperson = self.agents.agent_salesperson()

        task_inventory_analysis = self.tasks.task_inventory_analysis()
        task_recommendations = self.tasks.task_recommendations()

        # Iniciar o CrewAI
        crew = Crew(
            agents=[agent_manager, agent_sales_analyst, agent_inventory_analyst, agent_salesperson],
            tasks=[task_inventory_analysis, task_recommendations],
            verbose=True,
        )
        result = crew.kickoff()

        # Processar o resultado das recomendações
        recommendation_result = self.agents.generate_recommendations(result["recommendations"])

        # Executar o aplicativo Streamlit
        app = App(product_data, order_data, recommendation_result)
        app.run()

class App:
    def __init__(self, product_data, order_data, recommendation_result):
        self.product_data = product_data
        self.order_data = order_data
        self.recommendation_result = recommendation_result

    def run(self):
        st.title("Recomendações de Produtos")

        # Exibir tabelas de produtos e pedidos
        self.display_product_table()
        self.display_order_table()

        # Exibir tabela de recomendações do banco de dados
        self.display_database_recommendations()

        # Exibir recomendações geradas
        self.display_generated_recommendations()

    def display_product_table(self):
        if self.product_data:
            st.subheader("Tabela de Produtos")
            product_df = pd.DataFrame(self.product_data)
            st.write(product_df)

    def display_order_table(self):
        if self.order_data:
            st.subheader("Tabela de Pedidos")
            order_df = pd.DataFrame(self.order_data)
            st.write(order_df)

    def display_database_recommendations(self):
        st.subheader("Tabela de Recomendações")
        connection = psycopg2.connect(
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            host=os.environ.get("DB_HOST"),
            port=os.environ.get("DB_PORT"),
            database=os.environ.get("DB_NAME")
        )
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM product_recommendations")
        recommendations_data = cursor.fetchall()
        connection.close()

        if recommendations_data:
            recommendations_df = pd.DataFrame(recommendations_data, columns=['recommendation_id', 'user_id', 'client_email', 'product_id', 'recommendation_date', 'recommendation_status'])
            st.write(recommendations_df)
        else:
            st.write("Não há recomendações disponíveis ainda.")

    def display_generated_recommendations(self):
        if self.recommendation_result:
            st.subheader("Recomendações Geradas")
            recommendations_df = pd.DataFrame(self.recommendation_result)
            relevant_columns = ["Contato", "ID do produto recomendado"]
            recommendations_df = recommendations_df[relevant_columns]
            st.write(recommendations_df)
        else:
            st.warning("Nenhuma recomendação gerada.")

if __name__ == "__main__":
    custom_crew = CustomCrew()
    custom_crew.run()