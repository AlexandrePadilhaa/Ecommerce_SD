# Microsserviço Pagamento: responsável por gerenciar os
# pagamentos através da integração com um sistema externo de pagamento via
# Webhook. É necessário definir uma URL (isto é, um endpoint) que irá receber
# as notificações de pagamento aprovado ou recusado. Se o pagamento for
# aprovado, esse microsserviço publicará o evento no tópico
# Pagamentos_Aprovados. Caso o pagamento seja recusado, o microsserviço
# publicará o evento no tópico Pagamentos_Recusados para que o sistema
# cancele o pedido e atualize o estoque.

import pika
from fastapi import FastAPI, HTTPException
import httpx
from pydantic import BaseModel
import json
import requests
import threading
# from backend.utils import publish_message, get_connection, consume_messages

RABBITMQ_HOST = "localhost"
EXCHANGE = "ecommerce"

def publish(routing_key,message):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
        
        channel.basic_publish(
            exchange=EXCHANGE,
            routing_key=routing_key,
            body=json.dumps(message),
            properties=pika.BasicProperties(content_type="application/json")
        )
        connection.close()
        print(f"Mensagem publicada com sucesso {message}")
    except Exception as e:
        print(f"Erro ao publicar mensagem: {e}")
    
def processa_pedido(ch, method, properties, body):
    try:
        message = json.loads(body)
        print(f"Recebido evento: {message}")

        if 'id' not in message:
            print("Erro: 'id' não encontrado na mensagem")
            return
        
        pedido_id = message['id']
        
        # webhook
        response = requests.post(f"http://localhost:8002/pagamento/{pedido_id}")
        print(f"Resposta do pagamento: {response.status_code} - {response.text}")
     
        if response.status_code == 200:
            status = response.json().get("status", "unknown")
        else:
            status = "erro"

        resposta = {'id_pedido': pedido_id, 'status': status}
        publish('Pagamentos_Aprovados' if status == 'aprovado' else 'Pagamentos_Recusados', resposta)

    except Exception as e:
        print(f"Erro ao processar pedido: {e}")
    

def iniciar_consumidores():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()

        channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic', durable=True)
        channel.queue_declare(queue='pedidos_criados_pgto', durable=True)
        channel.queue_bind(exchange=EXCHANGE, queue='pedidos_criados_pgto', routing_key='Pedidos_Criados')
        channel.basic_consume(queue='pedidos_criados_pgto', on_message_callback=processa_pedido, auto_ack=True)

        print("Esperando por mensagens. Para sair, pressione CTRL+C")
        channel.start_consuming()

    except Exception as e:
        print(f"Erro ao conectar com RabbitMQ: {e}")
    # consume_messages('pedidos_criados', 'Pedidos_Criados', on_message_callback=processa_pedido, auto_ack=True)
   
if __name__ == "__main__":
    iniciar_consumidores()
