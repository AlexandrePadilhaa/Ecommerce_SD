# (valor 0,5) Microsserviço Principal (API REST ou gRPC): responsável
# por receber as requisições REST do frontend para visualizar produtos, inserir,
# atualizar e remover produtos do carrinho, realizar, excluir e consultar pedidos.
# Cada novo pedido recebido será publicado (publisher) como um evento no
# tópico Pedidos_Criados, cujas mensagens serão consumidas pelos
# microsserviços Estoque e Pagamento. O microsserviço Principal consumirá
# eventos (subscriber) dos tópicos Pagamentos_Aprovados,
# Pagamentos_Recusados e Pedidos_Enviados para atualizar o status de
# cada Pedido. Quando um cliente excluir um pedido ou quando o pagamento de
# um pedido for recusado, o microsserviço Principal publicará no tópico
# Pedidos_Excluídos.

# Principal publica em Pedidos_Criados e Pedidos_Excluidos
# Principal consome de Pagamentos_Aprovados, Pagamentos_Recusados e Pedidos_Enviados 

# excluir

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import threading
import pika
import json
from pathlib import Path
from functools import partial
# import sys
# import os
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname('utils.py'), '..')))
# from backend.utils import publish_message, consume_messages

app = FastAPI()

RABBITMQ_HOST = "localhost"
EXCHANGE = "ecommerce"

# Endpoint para teste de saúde
@app.get("/health")
def health_check():
    return {"status": "ok"}

class Pedido(BaseModel):
    id: int
    id_pedido: int
    cliente: str
    produtos: list
    total: float
    status: str

pedidos = []
    
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
        print(f"Mensagem publicada com sucesso")
    except Exception as e:
        print(f"Erro ao publicar mensagem: {e}")
        
# Endpoint para criar um pedido
@app.post("/pedidos/", status_code=201)
def criar_pedido(pedido: Pedido):
    try:
        mensagem = {
            "id": pedido.id,
            "cliente": pedido.cliente,
            "produtos": pedido.produtos,
            "total": pedido.total,
            "status": pedido.status
        }
        publish("Pedidos_Criados", mensagem)
        pedidos.append(pedido)
        return {"mensagem": "Pedido criado com sucesso", "pedido": mensagem}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar pedido: {str(e)}")

@app.get("/pedidos/")
def listar_pedidos():
    if len(pedidos)>0:
        return {'pedidos': pedidos}
    raise HTTPException(status_code=204, detail="Sem pedidos")

@app.get("/pedidos/{id}/estoque")
async def consultar_estoque_pedido(id: int):
    pedido = next((pedido for pedido in pedidos if pedido.id == id), None)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    async with httpx.AsyncClient() as client:
        produtos_estoque = []
        for produto_id in pedido.produtos:
            response = await client.get(f"http://localhost:8001/estoque/{produto_id}")
            if response.status_code == 404:
                produtos_estoque.append({"produto_id": produto_id, "erro": "Produto não encontrado"})
            else:
                produtos_estoque.append(response.json())

    return {"estoque_produtos": produtos_estoque}

@app.get("/pedidos/{id}")
def consultar_pedido(id: int):
    print('consultando pedido: ',id)
    for pedido in pedidos:
        if pedido['id'] == id:
            return {'pedido': pedido}
    raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
# Exclusão de pedidos
@app.delete("/pedidos/{id}")
def excluir_pedido(id: int):
    pedido = pedidos.pop(id, None)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    atualiza_status(id,'cancelado')
    
    # Publica no tópico Pedidos_Excluídos
    publish(exchange="ecommerce", routing_key="Pedidos_Excluidos", message={"id": id})
    return {"mensagem": "Pedido excluído com sucesso"}    
    
def atualiza_status(id_pedido,status):
    for pedido in pedidos:
        if pedido['id'] == id_pedido:
            pedido['status'] = status
    print(f'Status do pedido {id_pedido} atualizado')
            
def recebe_notificacao(ch, method, properties,body,tipo):
    try:
        message = json.loads(body)
        print(f"Recebido evento: {message}")
        
        if tipo != 'envio':
            id = message['pedido']['id']
            status = message['pedido']['status']
        else:
            id = message['id_pedido']
            status = message['status']
        
        if tipo != 'exclusao':
            atualiza_status(id,status)
    except Exception as e:
        print(f"Erro ao processar pedido: {e}")
        
def iniciar_consumidores():
    # consume_messages('pedidos_aprovados','Pedidos_Aprovados',atualiza_status)
    # consume_messages('pedidos_recusados','Pedidos_Recusados',excluir_pedido)
    # pedido enviado
    
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()

        channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic', durable=True)

        channel.queue_declare(queue='pgtos_aprovados', durable=True)
        channel.queue_declare(queue='pgtos_recusados', durable=True)
        channel.queue_declare(queue='pedidos_enviados', durable=True)

        channel.queue_bind(exchange=EXCHANGE, queue='pgtos_aprovados', routing_key='Pagamentos_Aprovados')
        channel.queue_bind(exchange=EXCHANGE, queue='pgtos_recusados', routing_key='Pagamentos_Recusados')
        channel.queue_bind(exchange=EXCHANGE, queue='pedidos_enviados', routing_key='Pedidos_Enviados')
        
        channel.basic_consume(queue='pgtos_aprovados', on_message_callback=partial(recebe_notificacao, tipo='aprovacao'), auto_ack=True)
        channel.basic_consume(queue='pgtos_recusados', on_message_callback=partial(recebe_notificacao, tipo='exclusao'), auto_ack=True)
        channel.basic_consume(queue='pedidos_enviados', on_message_callback=partial(recebe_notificacao, tipo='envio'),auto_ack=True)

        print("Esperando por mensagens. Para sair, pressione CTRL+C")
        channel.start_consuming()

    except Exception as e:
        print(f"Erro ao conectar com RabbitMQ: {e}")


if __name__ == '__main__':
    print("Iniciando Principal Consumidor...")
    iniciar_consumidores()