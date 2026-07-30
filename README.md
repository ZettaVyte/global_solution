# RecomendaIAgro 🌾

**IA que fortalece a comunicação humana no agronegócio**

Este repositório contém a solução desenvolvida para o Global Solution 2025 (Fase 1TSCOB) da FIAP, focada no desafio de utilizar inovação e tecnologia para o "futuro do trabalho" alinhado aos Objetivos de Desenvolvimento Sustentável (ODS) da ONU.

## 📌 Visão Geral do Projeto

O agronegócio brasileiro enfrenta desafios de modernização comercial, onde decisões frequentemente ainda são guiadas por intuição e dados fragmentados. O **RecomendaIAgro** foi concebido como um parceiro digital inteligente para apoiar equipes comerciais e de pós-venda. 

A solução atua ao lado do vendedor, centralizando informações e oferecendo recomendações estratégicas que potencializam o contato humano qualificado, evitando a rejeição de interações automatizadas comuns no setor agro.

O projeto é estruturado em dois pilares principais:
1. **Sistema de Recomendação Inteligente** (Algoritmo Apriori)
2. **Painel Unificado para Vendedores** (Visão 360° do Cliente)

## 🛠️ Arquitetura da Solução e Tecnologias

A arquitetura foi desenhada em nuvem (AWS) e focada em escalabilidade:

*   **Ingestão:** AWS Transfer Family para recebimento de dados (ERP, CRM e Catálogos de Produtos).
*   **Armazenamento (Data Lake):** Amazon S3 estruturado em camadas (Raw, Processed e Curated).
*   **Processamento & Machine Learning:** AWS Glue e PySpark para ETL e execução do Algoritmo Apriori.
*   **Governança:** AWS Glue Data Catalog.
*   **Data Lakehouse / Consultas:** Amazon Athena.
*   **Consumo & API:** AWS Lambda e API Gateway.
*   **Front-End MVP:** Aplicação construída em **Python + Streamlit**.

## 🧠 Modelagem de Dados: Algoritmo Apriori

O sistema utiliza o algoritmo de Machine Learning de regras de associação (Apriori) para descobrir o comportamento de compra dos clientes do agronegócio. 

O motor de IA calcula três métricas essenciais:
*   **Suporte:** Frequência com que itens aparecem nas cestas de compra.
*   **Confiança:** Probabilidade de um produto B ser comprado dado que o A foi adquirido.
*   **Lift:** A força da correlação, demonstrando o aumento na probabilidade de compra conjunta.

## 📊 Estrutura do Painel (Visão 360°)

A interface do vendedor fornece:
*   **Perfil do Cliente e Contatos:** Dados consolidados do produtor rural (Área, Cultura, Pragas, etc).
*   **Perfil Comercial:** Ticket Médio, Valor Potencial, Curva ABC por Categoria.
*   **Recomendações da IA:** Lista de produtos com *Lift Score* indicando o motivo da recomendação baseada nos hábitos de clientes similares.
*   **Cockpit de Ação:** Botões para ação imediata (Ligar, Enviar WhatsApp ou Agendar Visita) integrados à interface.

## 🌍 Impacto e Conexão com os ODS da ONU

Este projeto está alinhado às diretrizes do Fórum Econômico Mundial sobre a evolução e requalificação do trabalho, onde a IA eleva a produtividade humana.

Impactos direcionados aos ODS:
*   **ODS 8 (Trabalho Decente e Crescimento Econômico):** Modernização comercial e eficiência via tecnologia e dados.
*   **ODS 9 (Inovação e Infraestrutura):** Aplicação prática de IA e nuvem no agro.
*   **ODS 10 (Redução das Desigualdades):** Democratização de dados e insights técnicos.
*   **ODS 12 (Consumo Responsável):** Recomendações assertivas que reduzem o desperdício de insumos.

## 👥 Equipe Desenvolvedora

*   Carlos Vinícius Rodrigues Silva (RM564607)
*   Gabriela Sena da Silva (RM565118)
*   Gustavo Almeira Scardini (RM565374)
*   Tatiana Espinola (RM564907)
*   Vitor Fernandes Antunes (RM563053)

---
*Projeto FIAP Global Solutions 2025 | 1TSCOB*
