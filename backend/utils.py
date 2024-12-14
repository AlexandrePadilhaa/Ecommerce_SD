import pika
import json

RABBITMQ_HOST = "localhost"
EXCHANGE = "ecommerce"


def get_connection():
    return pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))

def declare_exchange_and_queue(channel, exchange=EXCHANGE, queue=None, routing_key=None):
    channel.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)
    if queue:
        channel.queue_declare(queue=queue, durable=True)
        channel.queue_bind(exchange=exchange, queue=queue, routing_key=routing_key)

def publish_message(routing_key, message, exchange= EXCHANGE,):
    print(f"Exchange: {exchange}, Routing Key: {routing_key}, Message: {message}")
    try:
        connection = get_connection()
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)
        
        channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=json.dumps(message),
            properties=pika.BasicProperties(content_type="application/json")
        )
        connection.close()
        print(f"Mensagem publicada com sucesso")
    except Exception as e:
        print(f"Erro ao publicar mensagem: {e}")

def consume_messages(queue, routing_key, callback, exchange= EXCHANGE):
    try:
        connection = get_connection()
        channel = connection.channel()
        
        declare_exchange_and_queue(channel, exchange, queue, routing_key)
        
        channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
        print(f" [*] Consumindo mensagens da fila '{queue}' com routing key '{routing_key}'.")
        channel.start_consuming()
    except Exception as e:
        print(f"Erro ao consumir mensagens: {e}")
