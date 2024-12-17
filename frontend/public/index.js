let ultimoId = 1; 
let produtos = [];

const produtoListaDiv = document.getElementById("product-list");
const pedidoListaDiv = document.getElementById("pedido-lista");
const clienteNomeInput = document.getElementById("cliente-nome");
const carrinhoContainer = document.querySelector('.produtos.selecionados');

// exibir os produtos disponíveis
async function fetchProducts() {
  const fakeProducts = [
    { nome: "Produto A", preco: 10.0, id_produto: 1 },
    { nome: "Produto B", preco: 20.0, id_produto: 2 },
    { nome: "Produto C", preco: 30.0, id_produto: 3 }
  ];
  displayProducts(fakeProducts);
}

// exibir os produtos na tela
function displayProducts(products) {
  produtoListaDiv.innerHTML = '';
  products.map(product => {
    const productElement = document.createElement('div');
    productElement.className = 'product';
    productElement.innerHTML = `
      <h2>${product.nome}</h2>
      <p>Preço: R$${product.preco.toFixed(2)}</p>
      <button class="botao-produto" data-id="${product.id_produto}">Adicionar ao carrinho</button>
    `;
    produtoListaDiv.appendChild(productElement);
  });

  // evento botões de adicionar ao carrinho
  document.querySelectorAll(".botao-produto").forEach(button => {
    button.addEventListener("click", () => {
      const produtoId = button.getAttribute("data-id");
      if (!produtos.includes(produtoId)) {
        produtos.push(produtoId);
        listarProdutosNoCarrinho();
      }
    });
  });
}

// listar os produtos no carrinho
function listarProdutosNoCarrinho() {
  carrinhoContainer.innerHTML = "";
  produtos.forEach(id => {
    const produtoDiv = document.createElement('div');
    produtoDiv.textContent = `Produto #${id}`;
    carrinhoContainer.appendChild(produtoDiv);
  });
}

// listar os pedidos na tela
async function listarPedidos() {
  try {
    const response = await fetch("http://localhost:8001/pedidos/");
    if (response.ok) {
      const data = await response.json();
      const pedidos = data.pedidos;

      pedidoListaDiv.innerHTML = "";  

      pedidos.forEach(pedido => {
        const pedidoDiv = document.createElement("div");
        pedidoDiv.classList.add("pedido");
        // é pra redirecionar
        pedidoDiv.innerHTML = `
          <h3><a href="/detalhes_pedido.html?id=${pedido.id}">Pedido #${pedido.id} - ${pedido.cliente}</a></h3> 
          <p>Status: ${pedido.status}</p>
        `;
        pedidoListaDiv.appendChild(pedidoDiv);
      });
    } else {
      console.log("Nenhum pedido encontrado.");
    }
  } catch (error) {
    console.error("Erro ao listar pedidos:", error);
  }
}

// fazer o pedido
document.getElementById("fazer-pedido").addEventListener("click", async () => {
  const clienteNome = clienteNomeInput.value;

  if (!clienteNome || produtos.length === 0) {
    alert("Por favor, insira seu nome e selecione pelo menos um produto.");
    return;
  }

  const pedido = {
    id: ultimoId,
    cliente: clienteNome,
    produtos: produtos,
    total: calcularTotal(),
    status: "Criado"
  };

  ultimoId = ultimoId + 1;

  try {
    const response = await fetch("http://localhost:8001/pedidos/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(pedido)
    });

    if (response.ok) {
      alert("Pedido realizado com sucesso!");
      produtos = [];  // Limpa o carrinho
      listarProdutosNoCarrinho();  // Atualiza o carrinho na tela
      listarPedidos();  // Atualiza a lista de pedidos
    } else {
      alert("Erro ao realizar o pedido.");
    }
  } catch (error) {
    alert("Erro ao tentar enviar o pedido.");
  }
});

// Função para calcular o total do pedido (exemplo simples)
function calcularTotal() {
  return produtos.length * 20; // Aqui poderia ser mais elaborado, considerando o preço dos produtos
}

// Chama a função para listar os pedidos ao carregar a página
listarPedidos();

// Inicia a lista de produtos disponíveis
fetchProducts();
