# Microsserviço Pagamento: responsável por gerenciar os
# pagamentos através da integração com um sistema externo de pagamento via
# Webhook. É necessário definir uma URL (isto é, um endpoint) que irá receber
# as notificações de pagamento aprovado ou recusado. Se o pagamento for
# aprovado, esse microsserviço publicará o evento no tópico
# Pagamentos_Aprovados. Caso o pagamento seja recusado, o microsserviço
# publicará o evento no tópico Pagamentos_Recusados para que o sistema
# cancele o pedido e atualize o estoque.

import pika
import json
from fastapi import FastAPI, HTTPException
import time

# from backend.utils import publish_message, get_connection, consume_messages

RABBITMQ_HOST = "localhost"
EXCHANGE = "ecommerce"

app = FastAPI()
        
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
        print(f"Pagamento: Mensagem publicada com sucesso para {routing_key}")
    except Exception as e:
        print(f"Erro ao publicar mensagem: {e}")
        
def processa_resposta_pagamento(id_pedido: int, pagamento):
    status = pagamento['status_pagamento']
    saldo = pagamento['saldo_cliente']
    try:
        time.sleep(5)
        if status == "aprovado":
            print(f'Pagamento aprovado para o pedido {id_pedido}: Saldo restante {saldo}')
            publish("Pagamentos_Aprovados", pagamento)
        else:
            print(f'Pagamento recusado para o pedido {id_pedido}: Saldo do cliente {saldo}')
            publish("Pagamentos_Recusados", pagamento)
    except Exception as e:
        print(f"Erro ao processar a resposta do pagamento: {e}")

@app.post('/pedido/{id_pedido}/pagamento/')
async def webhook_pagamento(id_pedido: int, pagamento: dict):
    try:
        print(f"Recebido Webhook para pagamento - ID do Pedido: {id_pedido}")
        processa_resposta_pagamento(id_pedido, pagamento)
    except Exception as e:
        print(f"Erro ao processar a resposta do pagamento: {e}")

def processa_pedido(ch, method, properties, body):
    try:
        message = json.loads(body)
        print(f"Recebido evento em Pagamento: Processo de Pagamento iniciado para pedido {message['id']}")
        
        pedido_id = message['id']
      
        pagamento = {
            "id_transacao": 100 + pedido_id,
            'pedido': message,
        }
        time.sleep(5)
        publish('Processar_Pagamentos', pagamento)

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
    print("Iniciando Pagamento Consumidor...")
    iniciar_consumidores()
