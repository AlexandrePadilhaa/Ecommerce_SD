console.log("teste")

const API_URL = "http://localhost:8001/pedidos"; // URL da API

let produtos = []; 

let pedidos = 0;

// Simula produtos (ou use a função fetchProducts para buscar da API)
const fakeProducts = [
  { id_produto: 1, nome: "Produto A", preco: 10.0, image: "https://via.placeholder.com/150" },
  { id_produto: 2, nome: "Produto B", preco: 20.0, image: "https://via.placeholder.com/150" },
  { id_produto: 3, nome: "Produto C", preco: 30.0, image: "https://via.placeholder.com/150" },
];

console.log(fakeProducts);
displayProducts(fakeProducts);

// exibir os produtos na tela
function displayProducts(products) {
  const productList = document.getElementById('product-list');
  productList.innerHTML = '';
  products.forEach(product => {
    const productElement = document.createElement('div');
    productElement.className = 'product';
    productElement.innerHTML = `
      <h2>${product.nome}</h2>
      <img src="${'https://via.placeholder.com/150' || 'placeholder.jpg'}" alt="${product.nome}">
      <p>Preço: R$${product.preco.toFixed(2)}</p>
      <button id=${product.id_produto} class="botao-produto">Adicionar ao carrinho</button>
    `;
    productList.appendChild(productElement);
  });
}

// evento botões de adicionar ao carrinho
function adicionarEventosBotoes() {
  const botoesProduto = document.querySelectorAll(".botao-produto");
  botoesProduto.forEach((botao) => {
    botao.addEventListener("click", () => {
      const produtoId = parseInt(botao.getAttribute("id"));
      produtos.push(produtoId); // Adiciona o ID do produto à lista
      listarProdutosNoCarrinho(produtos);
    });
  });
}

// Exibe os produtos no carrinho
function listarProdutosNoCarrinho(idsSelecionados) {
  const carrinhoContainer = document.querySelector('.produtos.selecionados');
  carrinhoContainer.innerHTML = "";
  const produtosSelecionados = fakeProducts.filter(produto =>
    idsSelecionados.includes(produto.id_produto)
  );

  produtosSelecionados.forEach(produto => {
    const produtoDiv = document.createElement('div');
    produtoDiv.classList.add('produto-selecionado');
    produtoDiv.textContent = produto.nome;
    carrinhoContainer.appendChild(produtoDiv);
  });
}

// calcular o total do pedido?
function calcularTotal() {
  return produtos.reduce((total, produtoId) => {
    const produto = fakeProducts.find(p => p.id_produto === produtoId);
    return total + produto.preco;
  }, 0);
}

// enviar o pedido para o servidor
document.getElementById("fazer-pedido").addEventListener("click", async () => {
  const clienteNome = document.getElementById("cliente-nome").value;
  if (!clienteNome || produtos.length === 0) {
    alert("Por favor, insira seu nome e selecione pelo menos um produto.");
    return;
  }

  const pedido = {
    id: pedidos,
    cliente: clienteNome,
    produtos: produtos,
    total: calcularTotal(),
    status: "Criado"
  };

  pedidos = pedidos + 1;

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(pedido),
    });

    if (response.ok) {
      const data = await response.json();
      console.log("Pedido enviado com sucesso:", data);
      alert("Pedido realizado com sucesso!");
      produtos = []; // Limpar o carrinho após o pedido
      listarProdutosNoCarrinho(produtos);
    } else {
      console.error("Erro ao enviar pedido");
      alert("Ocorreu um erro ao realizar o pedido.");
    }
  } catch (error) {
    console.error("Erro ao enviar pedido:", error);
    alert("Erro ao tentar enviar o pedido.");
  }
});

// inicializar eventos nos botões de adicionar ao carrinho
adicionarEventosBotoes();
