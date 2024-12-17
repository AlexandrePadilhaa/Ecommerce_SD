let ultimoId = 1; 
let produtos = [];

const produtoListaDiv = document.getElementById("product-list");
const pedidoListaDiv = document.getElementById("pedido-lista");
const clienteNomeInput = document.getElementById("cliente-nome");
const carrinhoContainer = document.querySelector('.produtos.selecionados');

async function fetchProducts() {
  try {
    const response = await fetch("http://localhost:8001/estoque"); 
    if (response.ok) {
      const data = await response.json();
      const produtosDisponiveis = data.estoque.filter(product => product.quantidade_disponivel > 0); 
      displayProducts(produtosDisponiveis);  
    } else {
      console.log("Erro ao carregar produtos do estoque.");
    }
  } catch (error) {
    console.error("Erro ao buscar produtos:", error);
  }
}

// exibir os produtos no HTML
function displayProducts(products) {
  produtoListaDiv.innerHTML = '';
  products.forEach(product => {
    const productElement = document.createElement('div');
    productElement.className = 'product';
    productElement.innerHTML = `
      <h2>${product.nome}</h2>
      <img src="https://via.placeholder.com/150" alt="${product.nome}">
      <p>Preço: R$${product.preco.toFixed(2)}</p>
      <p>Disponível: ${product.quantidade_disponivel} unidades</p>
      <button class="botao-produto" data-id="${product.id_produto}" data-nome="${product.nome}" data-preco="${product.preco}">Adicionar ao carrinho</button>
    `;
    produtoListaDiv.appendChild(productElement);
  });

  // adicionar ao carrinho
  document.querySelectorAll(".botao-produto").forEach(button => {
    button.addEventListener("click", () => {
      const produtoId = button.getAttribute("data-id");
      const produtoNome = button.getAttribute("data-nome");
      const produtoPreco = parseFloat(button.getAttribute("data-preco"));
      if (!produtos.some(item => item.id_produto === produtoId)) {
        produtos.push({ id_produto: produtoId, nome: produtoNome, preco: produtoPreco });
        listarProdutosNoCarrinho();
      }
    });
  });
}

// listar os produtos no carrinho
function listarProdutosNoCarrinho() {
  carrinhoContainer.innerHTML = "";
  produtos.forEach(produto => {
    const produtoDiv = document.createElement('div');
    produtoDiv.innerHTML = `
      <p>${produto.nome} - R$${produto.preco.toFixed(2)}</p>
    `;
    carrinhoContainer.appendChild(produtoDiv);
  });

  const totalDiv = document.createElement('div');
  totalDiv.textContent = `Total: R$${calcularTotal().toFixed(2)}`;
  carrinhoContainer.appendChild(totalDiv);
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

  ultimoId ++;

  try {
    const response = await fetch("http://localhost:8001/pedidos/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(pedido)
    });
    log(pedido)
    if (response.ok) {
      alert("Pedido realizado com sucesso!");
      produtos = [];  
      listarProdutosNoCarrinho();  
      listarPedidos(); 
    } else {
      alert("Erro ao realizar o pedido.");
    }
  } catch (error) {
    alert("Erro ao tentar enviar o pedido.");
  }
});

function calcularTotal() {
  return produtos.reduce((total, produto) => total + produto.preco, 0);
}

listarPedidos();
fetchProducts();
