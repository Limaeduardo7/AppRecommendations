import streamlit as st
import os
import pandas as pd
import psycopg2
from agents import CustomAgents
from tasks import CustomTasks
from crewai import Crew
from data.data_proccessing import get_and_process_product_data, get_and_process_order_data
from dotenv import load_dotenv

load_dotenv()

def main():
    st.title("Recomendações de Produtos")

    # Obter as URLs das APIs a partir das variáveis de ambiente
    products_api_url = os.environ.get('PRODUCTS_API_URL')
    orders_api_url = os.environ.get('ORDERS_API_URL')

    # Fazendo a requisição e processando os dados dos produtos
    product_data = get_and_process_product_data(products_api_url)

    # Fazendo a requisição e processando os dados dos pedidos
    order_data = get_and_process_order_data(orders_api_url)

    # Exibindo as tabelas de produtos e pedidos
    if product_data:
        st.subheader("Tabela de Produtos")
        product_df = pd.DataFrame(product_data)
        st.write(product_df)

    if order_data:
        st.subheader("Tabela de Pedidos")
        order_df = pd.DataFrame(order_data)
        st.write(order_df)

    # Exibir tabela de recomendações do banco de dados
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

    # Seção para gerar recomendações
    st.header("Gerar Recomendações")
    generate_recommendations = st.button("Gerar Recomendações")
    if generate_recommendations:
        if product_data and order_data:
            try:
                agents = CustomAgents()
                tasks = CustomTasks()

                # Inicializar agentes e tarefas
                agent_manager = agents.agent_manager()
                agent_sales_analyst = agents.agent_sales_analyst()
                agent_inventory_analyst = agents.agent_inventory_analyst()
                agent_salesperson = agents.agent_salesperson()

                task_inventory_analysis = tasks.task_inventory_analysis(agent_inventory_analyst)
                task_recommendations = tasks.task_recommendations(agent_salesperson)

                # Iniciar o CrewAI
                crew = Crew(
                    agents=[agent_manager, agent_sales_analyst, agent_inventory_analyst, agent_salesperson],
                    tasks=[task_inventory_analysis, task_recommendations],
                    verbose=True,
                )
                result = crew.kickoff()

                # Processar o resultado das recomendações
                recommendation_result = agents.generate_recommendations(result["recommendations"])

            except Exception as e:
                st.error(f"Ocorreu um erro inesperado: {str(e)}")
        else:
            st.warning("Dados de produtos e pedidos são necessários para gerar as recomendações.")

if __name__ == "__main__":
    main()