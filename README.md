# Ecommerce_SD


## iniciar serviço
python -m uvicorn backend.principal.principal:app --reload --host 0.0.0.0 --port 8001
python -m uvicorn backend.estoque.estoque:app --reload --host 0.0.0.0 --port 8002
python -m uvicorn backend.pagamento.pagamento:app --reload --host 0.0.0.0 --port 8003
python -m uvicorn backend.notificacao.notificacao:app --reload --host 0.0.0.0 --port 8003

## iniciar microserviços
python backend/principal/principal.py
python backend/estoque/estoque.py
python backend/pagamento/pagamento.py
python backend/pagamento/sistema_externo.py
python backend/envio/envio.py
python backend/notificacao/notificacao.py

### inicia todos os microserviços
python backend/main.py

### Iniciar RabbitMQ
rabbitmq-service start

### teste postman
get 
http://localhost:8000/health
post
http://localhost:8000/pedidos/

{
  "id": 1,
  "cliente": "João Silva",
  "produtos": ["Produto A", "Produto B"],
  "total": 150.50,
  "status": "Criado"
}
{
  "id": 2,
  "cliente": "Maria Souza",
  "produtos": ["Produto C"],
  "total": 75.00,
  "status": "Criado"
}


## frontend
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

npm install -g http-server -d

npm run start
