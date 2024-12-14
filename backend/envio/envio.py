# Microsserviço Entrega: responsável por gerenciar a emissão
# de notas e entrega dos produtos. Este serviço consome eventos do tópico
# Pagamentos_Aprovados e publica no tópico Pedidos_Enviados.

import pika
import json
import time
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
    
def envia_pedido(ch, method, properties, body):
    try:
        message = json.loads(body)
        print(f"Recebido evento: {message}")

        pedido_id = message['id_pedido']
        
        time.sleep(3)
        resposta = {'id_pedido': pedido_id, 'status': 'Enviado'}
        print(f'Pedido {pedido_id} enviado')
        publish('Pedidos_Enviados', resposta)

    except Exception as e:
        print(f"Erro ao processar pedido: {e}")
    
def iniciar_consumidores():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()

        channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic', durable=True)
        channel.queue_declare(queue='pgtos_aprovados_envio', durable=True)
        channel.queue_bind(exchange=EXCHANGE, queue='pgtos_aprovados_envio', routing_key='Pagamentos_Aprovados')
        channel.basic_consume(queue='pgtos_aprovados_envio', on_message_callback=envia_pedido, auto_ack=True)

        print("Esperando por mensagens. Para sair, pressione CTRL+C")
        channel.start_consuming()

    except Exception as e:
        print(f"Erro ao conectar com RabbitMQ: {e}")
    # consume_messages('pedidos_criados', 'Pedidos_Criados', on_message_callback=processa_pedido, auto_ack=True)
   
if __name__ == "__main__":
    iniciar_consumidores()
