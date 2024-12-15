import subprocess

def iniciar_consumidor(nome, caminho):
    """Inicia apenas consumidores de eventos."""
    print(f"Iniciando consumidor: {nome}")
    return subprocess.Popen(["python", caminho])

def main():
    consumidores = [
        {"nome": "Principal Consumidor", "caminho": "backend/principal/principal.py"},
        {"nome": "Estoque Consumidor", "caminho": "backend/estoque/estoque.py"},
        {"nome": "Pagamento Consumidor", "caminho": "backend/pagamento/pagamento.py"},
        {"nome": "Sistema Externo Pagamento", "caminho": "backend/pagamento/sistema_externo.py"},
        {"nome": "Envio Consumidor", "caminho": "backend/envio/envio.py"},
        {"nome": "Entrega Consumidor", "caminho": "backend/entrega/entrega.py"}
    ]


    processos = []

    # Iniciar consumidores
    for consumidor in consumidores:
        processo = iniciar_consumidor(consumidor["nome"], consumidor["caminho"])
        processos.append(processo)

    try:
        print("Todos os consumidores foram iniciados. Pressione Ctrl+C para encerrar.")
        for processo in processos:
            processo.wait()
    except KeyboardInterrupt:
        print("\nEncerrando consumidores...")
        for processo in processos:
            processo.terminate()
        print("Todos os consumidores foram encerrados.")

if __name__ == "__main__":
    main()
