import requests
import pika
import json
import csv

RABBITMQ_HOST = "localhost"
EXCHANGE = "ecommerce"
    
def ler_limites_csv():
    limites = {}
    with open('backend/pagamento/limite_clientes.csv', mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            row['limite'] = float(row['limite']) 
            limites[row['cliente']] = row['limite']
    return limites

def atualiza_limites(limite_clientes):
    with open('backend/pagamento/limite_clientes.csv', mode='r', encoding='utf-8') as file:
        rows = list(csv.DictReader(file))

    for row in rows:
        if row['cliente'] in limite_clientes:
            row['limite'] = limite_clientes[row['cliente']] 

    with open('backend/pagamento/limite_clientes.csv', mode='w', encoding='utf-8', newline='') as file:
        fieldnames = ['cliente', 'limite']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
def processa_pedido(ch, method, properties, body):
    try:
        message = json.loads(body)
        print(f"Recebido evento no Sistema Externo de Pagamento: pedido {message['pedido']['id']}")

        pedido_id = message['pedido']['id']
        cliente = message['pedido']['cliente']
        valor = message['pedido']['total']
        
        clientes_limite = ler_limites_csv()
        
        # Verifica o limite do cliente
        lim_cliente = clientes_limite[cliente]
        
        if lim_cliente is None:
            print(f"Cliente {cliente} não encontrado.")
            return
        if valor > lim_cliente:
            status = "recusado"
        else:
            status = "aprovado"
            clientes_limite[cliente] -= valor

        # Envia a notificação do pagamento via POST para o microsserviço de pagamento
        message['status_pagamento'] = status
        message['saldo_cliente'] = clientes_limite
            

        response = requests.post(f"http://localhost:8003/pedido/{pedido_id}/pagamento/", json=message)
        print(response.status_code)
        if response.status_code == 200:
            print(f'Pagamento {status} para {cliente}')
            
        atualiza_limites(clientes_limite)

    except Exception as e:
        print(f"Erro ao processar pedido: {e}")
        
def iniciar_consumidores():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()

        channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic', durable=True)
        channel.queue_declare(queue='processar_pagamento', durable=True)
        channel.queue_bind(exchange=EXCHANGE, queue='processar_pagamento', routing_key='Processar_Pagamentos')
        channel.basic_consume(queue='processar_pagamento', on_message_callback=processa_pedido, auto_ack=True)

        print("Esperando por mensagens. Para sair, pressione CTRL+C")
        channel.start_consuming()

    except Exception as e:
        print(f"Erro ao conectar com RabbitMQ: {e}")
    # consume_messages('pedidos_criados', 'Pedidos_Criados', on_message_callback=processa_pedido, auto_ack=True)
   
if __name__ == "__main__":
    print("Iniciando Sistema Externo Pagamento...")
    iniciar_consumidores()
