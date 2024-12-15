const eventSource = new EventSource('http://localhost:8004/notificacoes');

eventSource.onmessage = (event) => {
    console.log("Notificação recebida:", event.data);
    // Atualizar o estado do frontend com as notificações recebidas
};

eventSource.onerror = (error) => {
    console.error("Erro no SSE:", error);
};
