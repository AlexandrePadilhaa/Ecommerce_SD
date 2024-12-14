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

# Principal publica em Pedidos_Criados
# Principal consome de Pagamentos_Aprovados, Pagamentos_Recusados e Pedidos_Enviados 

# TODO
# PRODUTOS
# vizualizar

# CARRINHO
# inserir
# atualizar
# remover

# PEDIDOS
# realizar
# consultar
# excluir

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pika
import json

from ..utils import publish_message

app = FastAPI()

RABBITMQ_HOST = "localhost"
EXCHANGE = "ecommerce"


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

# Endpoint para teste de saúde
@app.get("/health")
def health_check():
    return {"status": "ok"}
