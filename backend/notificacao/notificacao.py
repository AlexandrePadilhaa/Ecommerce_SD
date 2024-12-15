from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import pika
import json
from functools import partial
import asyncio

RABBITMQ_HOST = "localhost"
EXCHANGE = "ecommerce"

app = FastAPI()

# Adicionando o middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500","http://127.0.0.1:8080"],  # Permite apenas essa origem específica
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

# Fila de notificacoes
notificacoes = asyncio.Queue()

# Envia notificacao toda vez que recebe
async def envia_notificacao():
    while True:
        if not notificacoes.empty():
            notificacao = await notificacoes.get()
            print(f'notificacao: {notificacao}')  # Verifique se está chegando aqui
            yield f'event: Notificacao\ndata: {notificacao}\n\n'
        else:
            await asyncio.sleep(1)  

@app.get('/notificacao')
async def stream_notificacoes():
    return StreamingResponse(envia_notificacao(), media_type="text/event-stream")
    
def recebe_evento(ch, method, properties, body, tipo):
    try:
        message = json.loads(body)
        print(f'Recebido evento em Notificacao: atualização de {tipo}')

        if tipo in ['criacao', 'envio']:
            id = message['id']
            status = message['status']
            notificacao = f'Pedido {id} {status}'
        else:
            id = message['pedido']['id']
            status = message['status_pagamento']
            notificacao = f'Pedido {id}: pagamento {status}'

        # Coloca a notificação na fila
        notificacoes.put_nowait(notificacao)
        print(f'Notificação enviada para fila: {notificacao}') 
        print(f'fila {notificacoes}')
    except Exception as e:
        print(f"Erro ao processar pedido: {e}")

def iniciar_consumidores():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()

        channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic', durable=True)

        channel.queue_declare(queue='pedidos_criados_not', durable=True)
        channel.queue_declare(queue='pgtos_aprovados_not', durable=True)
        channel.queue_declare(queue='pgtos_recusados_not', durable=True)
        channel.queue_declare(queue='pedidos_enviados_not', durable=True)

        channel.queue_bind(exchange=EXCHANGE, queue='pedidos_criados_not', routing_key='Pedidos_Criados')
        channel.queue_bind(exchange=EXCHANGE, queue='pgtos_aprovados_not', routing_key='Pagamentos_Aprovados')
        channel.queue_bind(exchange=EXCHANGE, queue='pgtos_recusados_not', routing_key='Pagamentos_Recusados')
        channel.queue_bind(exchange=EXCHANGE, queue='pedidos_enviados_not', routing_key='Pedidos_Enviados')

        channel.basic_consume(queue='pedidos_criados_not', on_message_callback=partial(recebe_evento, tipo='criacao'), auto_ack=True)
        channel.basic_consume(queue='pgtos_aprovados_not', on_message_callback=partial(recebe_evento, tipo='aprovacao'), auto_ack=True)
        channel.basic_consume(queue='pgtos_recusados_not', on_message_callback=partial(recebe_evento, tipo='exclusao'), auto_ack=True)
        channel.basic_consume(queue='pedidos_enviados_not', on_message_callback=partial(recebe_evento, tipo='envio'), auto_ack=True)

        print("Esperando por mensagens. Para sair, pressione CTRL+C")
        channel.start_consuming()

    except Exception as e:
        print(f"Erro ao conectar com RabbitMQ: {e}")

if __name__ == '__main__':
    print("Iniciando Notificacao Consumidor...")
    iniciar_consumidores()
