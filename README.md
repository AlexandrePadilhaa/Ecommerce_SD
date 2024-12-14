# Ecommerce_SD


## iniciar serviço
uvicorn backend.principal.principal:app --reload --host 0.0.0.0 --port 8000
uvicorn backend.estoque.estoque:app --reload --host 0.0.0.0 --port 8001


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
  "total": 150.50
}
