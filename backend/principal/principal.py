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
import threading
import pika
import json

from backend.utils import publish_message, get_connection

app = FastAPI()

RABBITMQ_HOST = "localhost"
EXCHANGE = "ecommerce"

# Endpoint para teste de saúde
@app.get("/health")
def health_check():
    return {"status": "ok"}

class Pedido(BaseModel):
    id: int
    cliente: str
    produtos: list
    total: float

# Endpoint para criar um pedido
@app.post("/pedidos/", status_code=201)
def criar_pedido(pedido: Pedido):
    try:
        mensagem = {
            "id": pedido.id,
            "cliente": pedido.cliente,
            "produtos": pedido.produtos,
            "total": pedido.total
        }
        publish_message("Pedidos_Criados", mensagem)
        return {"mensagem": "Pedido criado com sucesso", "pedido": mensagem}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar pedido: {str(e)}")


#test
pedidos = {
    1: {
        "id": 1,
        "cliente": "João Silva",
        "produtos": ["Produto A", "Produto B"],
        "total": 150.50,
        "status": "Criado"
    },
    2: {
        "id": 2,
        "cliente": "Maria Souza",
        "produtos": ["Produto C"],
        "total": 75.00,
        "status": "Criado"
    }
}
@app.get("/pedidos/")
def listar_pedidos():
    return {"pedidos": list(pedidos.values())}

@app.get("/pedidos/{id}")
def consultar_pedido(id: int):
    pedido = pedidos.get(id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedido

# Exclusão de pedidos
@app.delete("/pedidos/{id}")
def excluir_pedido(id: int):
    pedido = pedidos.pop(id, None)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    # Publica no tópico Pedidos_Excluídos
    publish_message(exchange="ecommerce", routing_key="Pedidos_Excluidos", message={"id": id})
    return {"mensagem": "Pedido excluído com sucesso"}

