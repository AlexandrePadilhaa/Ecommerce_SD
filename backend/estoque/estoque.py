#estoque.py

# Microsserviço Estoque: responsável por gerenciar o estoque
# de produtos. Ele consumirá eventos dos tópicos Pedidos_Criados e
# Pedidos_Excluídos. Quando um pedido for criado ou excluído, esse
# microsserviço precisará atualizar o estoque. Ele responderá requisições REST
# ou gRPC do Principal para enviar dados dos produtos em estoque.

#TODO Responder a requisições do principal com atualizacao do estoque

import csv
import pika
import json
import logging
from fastapi import FastAPI
from pydantic import BaseModel

RABBITMQ_HOST = "localhost"
EXCHANGE = "ecommerce"

app = FastAPI()

def ler_estoque_csv():
    estoque = []
    with open('backend/estoque/database.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            row['quantidade_disponivel'] = int(row['quantidade_disponivel'])
            row['quantidade_reservada'] = int(row['quantidade_reservada'])
            row['preco'] = float(row['preco'])
            estoque.append(row)
    return estoque

@app.get("/estoque/")
def consultar_estoque():
    estoque = ler_estoque_csv()  
    return {"estoque": estoque}

@app.get("/estoque/{produto_id}")
def consultar_produtos(produto_id):
    estoque = ler_estoque_csv() 
    produto = next((item for item in estoque if item['nome'] == str(produto_id)), None)
    if produto:
        return produto  
    else:
        return {"erro": produto,
                "produto_id": produto_id}  

def get_rabbitmq_connection():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    return connection
        
def pedido_criado(ch, method, properties, body):
    try:
        message = json.loads(body)
        print(f"Recebido evento: {message}")
        for produto_id in message['produtos']:
            atualizar_estoque(produto_id, "reservar")
    except Exception as e:
        print(f"Erro ao processar a mensagem: {e}")

def pedido_excluido(ch, method, properties, body):
    try:
        message = json.loads(body)
        print(f"Recebido evento: {message}")
        for produto_id in message['produtos']:
            atualizar_estoque(produto_id, "cancelar")        
    except Exception as e:
        print(f"Erro ao processar a mensagem: {e}")

def atualizar_estoque(produto_id, acao):
    # Carrega os dados do CSV
    produtos = []
    with open('backend/estoque/database.csv', mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            produtos.append(row)
    
    # Encontra o produto no estoque
    for produto in produtos:
        if int(produto['id_produto']) == produto_id:
            if acao == "reservar":
                if int(produto['quantidade_disponivel']) > 0:
                    produto['quantidade_disponivel'] = str(int(produto['quantidade_disponivel']) - 1)
                    produto['quantidade_reservada'] = str(int(produto['quantidade_reservada']) + 1)
                    print(f"Produto {produto['nome']} reservado. Estoque atualizado.")
                else:
                    print(f"Produto {produto['nome']} não disponível para reserva.")
            elif acao == "cancelar":
                if int(produto['quantidade_reservada']) > 0:
                    produto['quantidade_disponivel'] = str(int(produto['quantidade_disponivel']) + 1)
                    produto['quantidade_reservada'] = str(int(produto['quantidade_reservada']) - 1)
                    print(f"Produto {produto['nome']} liberado. Estoque atualizado.")
                else:
                    print(f"Produto {produto['nome']} não tem reserva para ser liberada.")
            
            # Atualiza os dados no arquivo CSV após a alteração
            with open('backend/estoque/database.csv', mode='w', newline='') as file:
                fieldnames = ['id_produto', 'nome', 'quantidade_disponivel', 'quantidade_reservada', 'preco']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                writer.writeheader()
                for p in produtos:
                    writer.writerow(p)
            break
        
def iniciar_consumidores():
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()

        channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic', durable=True)

        channel.queue_declare(queue='pedidos_criados', durable=True)
        channel.queue_declare(queue='pedidos_excluidos', durable=True)

        channel.queue_bind(exchange=EXCHANGE, queue='pedidos_criados', routing_key='Pedidos_Criados')
        channel.queue_bind(exchange=EXCHANGE, queue='pedidos_excluidos', routing_key='Pedidos_Excluídos')

        channel.basic_consume(queue='pedidos_criados', on_message_callback=pedido_criado, auto_ack=True)
        channel.basic_consume(queue='pedidos_excluidos', on_message_callback=pedido_excluido, auto_ack=True)

        print("Esperando por mensagens. Para sair, pressione CTRL+C")
        channel.start_consuming()

    except Exception as e:
        print(f"Erro ao conectar com RabbitMQ: {e}")

if __name__ == "__main__":
    print("Iniciando Estoque Consumidor...")
    iniciar_consumidores()
