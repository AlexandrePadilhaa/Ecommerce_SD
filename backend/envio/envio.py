# Microsserviço Entrega: responsável por gerenciar a emissão
# de notas e entrega dos produtos. Este serviço consome eventos do tópico
# Pagamentos_Aprovados e publica no tópico Pedidos_Enviados.

import pika
import json
import time
import os
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

def cria_nf(pedido):
    id_pedido = pedido['id']
    cliente = pedido['cliente']
    valor_total = pedido['total']
    produtos = pedido['produtos']
    produtos_str = "\n".join([f"{produto}" for produto in produtos])
    
    nota_fiscal = f"""
    ================================
            NOTA FISCAL SIMULADA
    ================================
    ID do Pedido: {id_pedido}
    Cliente: {cliente}
    
    Produtos:
        {produtos_str}
    
    Valor Total: R${valor_total:.2f}
    
    ================================
    """

    diretório = f'backend/envio/nfs'
    
    # Verificar se o diretório existe, senão, criar
    if not os.path.exists(diretório):
        os.makedirs(diretório)
    
    # Caminho completo do arquivo
    arquivo = f'{diretório}/nota_fiscal_{id_pedido}.txt'
    
    # Salvar a nota fiscal no arquivo
    with open(arquivo, 'w',encoding='utf-8') as f:
        f.write(nota_fiscal)  # Escreve a nota fiscal no arquivo

    print(f"Nota fiscal salva em: {arquivo}")
    
    
def envia_pedido(ch, method, properties, body):
    try:
        message = json.loads(body)
        print(f"Recebido evento em Envio: pedido {message['pedido']['id']}")

        pedido_id = message['pedido']['id']
        
        time.sleep(10)
        resposta = {'id': pedido_id, 'status': 'Enviado'}
        print(f'Pedido {pedido_id} enviado')
        cria_nf(message['pedido'])
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
    print("Iniciando Envio Consumidor...")
    iniciar_consumidores()
