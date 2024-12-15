from fastapi import FastAPI, HTTPException
import random
from pydantic import BaseModel
import requests
import pika
import json

RABBITMQ_HOST = "localhost"
EXCHANGE = "ecommerce"
    
# sempre passam no debito
clientes_limite = {
    "João Silva": 200,
    "Maria Souza": 300,
    "Jose Ribeiro": 100
}    

def processa_pedido(ch, method, properties, body):
    try:
        message = json.loads(body)
        print(f"Recebido evento: {message}")

        pedido_id = message['pedido']['id']
        cliente = message['pedido']['cliente']
        valor = message['pedido']['total']
        
        # Verifica o limite de crédito do cliente
        lim_cliente = clientes_limite.get(cliente)
        if lim_cliente is None:
            print(f"Cliente {cliente} não encontrado.")
            return

        # Simula o processo de pagamento (verifica se o valor é suficiente)
        if valor > lim_cliente:
            status = "recusado"
        else:
            status = "aprovado"
            clientes_limite[cliente] -= valor

        # Envia a notificação do pagamento via POST para o microsserviço de pagamento
        message['status_pagamento'] = status
        message['saldo_cliente'] = clientes_limite
            

        response = requests.post(f"http://localhost:8003/pedido/{pedido_id}/pagamento", json=message)
        if response.status_code == 200:
            print(f'Pagamento {status} para {cliente}')

    except Exception as e:
        print(f"Erro ao processar pedido: {e}")
        
def iniciar_consumidores():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()

        channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic', durable=True)
        channel.queue_declare(queue='processar_pagamento', durable=True)
        channel.queue_bind(exchange=EXCHANGE, queue='processar_pagamento', routing_key='Processar_Pagamentos')
        channel.basic_consume(queue='processar_pagamento', on_message_callback=processa_pedido, auto_ack=True)

        print("Esperando por mensagens. Para sair, pressione CTRL+C")
        channel.start_consuming()

    except Exception as e:
        print(f"Erro ao conectar com RabbitMQ: {e}")
    # consume_messages('pedidos_criados', 'Pedidos_Criados', on_message_callback=processa_pedido, auto_ack=True)
   
if __name__ == "__main__":
    iniciar_consumidores()
