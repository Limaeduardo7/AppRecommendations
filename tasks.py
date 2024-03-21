from typing import Dict, List
import os
from crewai import Task
from textwrap import dedent


class CustomTasks:

    def __init__(self):
        self.tip_section = dedent("""
            If you do an excellent job, I'll give you a $10,000 commission!
        """)

    def parse_webhook_data(self, raw_data: str) -> Dict[str, List[Dict[str, any]]]:
        # Implementar a lógica de parsing dos dados de webhook
        pass

    def task_inventory_analysis(self, agent):
        """
        Define uma tarefa CrewAI para analisar dados de inventário.

        Args:
            agent: O agente CrewAI para atribuir a tarefa.

        Returns:
            Um objeto CrewAI Task para análise de dados de inventário.
        """

        description = dedent(f"""
            Analise os dados de inventário executando consultas SQL diretamente no banco de dados. Extraia uma lista de produtos atualmente disponíveis em estoque, incluindo os seguintes detalhes para cada produto:

            - ID do produto
            - Preço do produto
            - Quantidade disponível em estoque

            Certifique-se de validar cuidadosamente os dados e lidar com quaisquer valores ausentes ou inválidos de forma apropriada. {self.tip_section}
        """)

        return Task(
            description=description,
            agent=agent,
            expected_output="Uma lista de produtos atualmente disponíveis em estoque, com detalhes de ID, preço e quantidade.",
            data_sources=[
                {
                    "type": "postgres",
                    "connection_string": f"postgresql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}"
                }
            ]
        )

    def task_recommendations(self, agent):
        """
        Define uma tarefa CrewAI para gerar recomendações de produtos.

        Args:
            agent: O agente CrewAI para atribuir a tarefa.

        Returns:
            Um objeto CrewAI Task para gerar recomendações de produtos.
        """

        description = dedent(f"""
            Use consultas SQL para recuperar dados de clientes e produtos do banco de dados e gerar uma tabela real com cada contato elegível e até 5 
            recomendações de produtos ao lado, considerando as seguintes condições:

            1. Considere apenas contatos que não fizeram compras nos últimos 30 dias.
            2. Limite o número total de recomendações geradas a no máximo 30 por dia.
            3. Para cada contato elegível, recomende até 5 produtos com base nas preferências do contato e na disponibilidade em estoque.
            4. A tabela final deve conter as seguintes colunas:
                - Nome do contato
                - ID do produto recomendado
                - Preço do produto recomendado

            Certifique-se de validar cuidadosamente os dados, lidar com quaisquer valores ausentes ou inválidos de forma apropriada e seguir todas as regras mencionadas. {self.tip_section}
        """)

        return Task(
            description=description,
            agent=agent,
            expected_output="Uma tabela com até 30 contatos e até 5 recomendações de produtos para cada, com base em suas preferências e nos produtos em estoque, limitado a contatos que não fizeram compras nos últimos 30 dias.",
            data_sources=[
                {
                    "type": "postgres",
                    "connection_string": f"postgresql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}"
                }
            ]
        )

