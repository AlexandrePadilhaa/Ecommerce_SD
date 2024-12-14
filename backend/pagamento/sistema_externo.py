from fastapi import FastAPI, HTTPException
import random

app = FastAPI()

clientes = {
    "João Silva": 200,
    "Maria Souza": 300,
    "Jose Ribeiro": 100
}    
    
# recebendo id do pedido caso a gente queira deixar isso melhor    
@app.post('/pagamento/{id_pedido}')
async def processa_pagamento(id_pedido): 
    if random.random() < 0.6:
        status = 'aprovado'
    else:
        status = 'reprovado'
        
    return {'id': id_pedido, 'status': status}

    