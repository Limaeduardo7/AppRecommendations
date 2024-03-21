import os
import streamlit as st
from crewai import Agent, Crew
from langchain.llms import Ollama
from textwrap import dedent
from agents import CustomAgents
from tasks import CustomTasks
from data.data_proccessing import get_and_process_product_data, get_and_process_order_data

class CustomCrew:
    def __init__(self):
        self.agents = CustomAgents()
        self.tasks = CustomTasks()

    def run(self):
        agent_manager = self.agents.agent_manager()
        agent_sales_analyst = self.agents.agent_sales_analyst()
        agent_inventory_analyst = self.agents.agent_inventory_analyst()
        agent_salesperson = self.agents.agent_salesperson()

        # Obter as URLs das APIs a partir das variáveis de ambiente
        products_api_url = os.environ.get('PRODUCTS_API_URL')
        orders_api_url = os.environ.get('ORDERS_API_URL')

        # Fazendo a requisição e processando os dados dos produtos
        product_data = get_and_process_product_data(products_api_url)

        # Fazendo a requisição e processando os dados dos pedidos
        order_data = get_and_process_order_data(orders_api_url)

        task_inventory_analysis = self.tasks.task_inventory_analysis(agent_inventory_analyst, product_data)
        task_recommendations = self.tasks.task_recommendations(agent_salesperson, order_data, product_data)

        crew = Crew(
            agents=[agent_manager, agent_sales_analyst, agent_inventory_analyst, agent_salesperson],
            tasks=[task_inventory_analysis, task_recommendations],
            verbose=True,
        )
        result = crew.kickoff()

        print("\n\n########################")
        print("## Recommendation Results:")
        print("########################\n")
        print(result)

if __name__ == "__main__":
    custom_crew = CustomCrew()
    custom_crew.run()