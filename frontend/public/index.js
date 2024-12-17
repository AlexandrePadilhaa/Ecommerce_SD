// URL da API (substitua pela correta)
const API_URL = "http://localhost:8001/estoque/";

console.log("teste")
async function fetchProductsTest() {
  const fakeProducts = [
    { nome: "Produto A", preco: 10.0, image: "https://via.placeholder.com/150" },
    { nome: "Produto B", preco: 20.0, image: "https://via.placeholder.com/150" },
    { nome: "Produto C", preco: 30.0, image: "https://via.placeholder.com/150" },
  ];
  console.log(fakeProducts)
  displayProducts(fakeProducts);
}

// Função para buscar produtos da API
async function fetchProducts() {
  try {
      const response = await fetch(API_URL);
      if (!response.ok) throw new Error('Erro ao obter produtos!');
      
      const data = await response.json(); // Recebe o JSON
      console.log(data)
      displayProducts(data.estoque); // Acessa a propriedade `estoque`
      adicionarEventosBotoes(data.estoque);
  } catch (error) {
      console.error(error);
  }
}

function displayProducts(products) {
  const productList = document.getElementById('product-list');
  productList.innerHTML = ''; 
 // <p>Disponível: ${product.quantidade_disponivel}</p>
  products.map(product => {
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

fetchProducts();

function listarProdutosNoCarrinho(idsSelecionados, estoque) {
  console.log("aqui")
  const carrinhoContainer = document.querySelector('.produtos.selecionados');
  carrinhoContainer.innerHTML = ""; 
  const produtosSelecionados = estoque.filter(produto =>
    idsSelecionados.includes(produto.id_produto)
  );

  produtosSelecionados.forEach(produto => {
    const produtoDiv = document.createElement('div');
    produtoDiv.classList.add('produto-selecionado');
    produtoDiv.textContent = produto.nome;
    carrinhoContainer.appendChild(produtoDiv);
  });
}

const produtos = [];
var botoesProduto = document.querySelectorAll(".botao-produto");
const orderButton = document.getElementById("fazer-pedido")
function adicionarEventosBotoes(estoque) {
  botoesProduto = document.querySelectorAll(".botao-produto");
  // Seleciona todos os botões com a classe 'botao-produto'


  // Adiciona o evento de clique a cada botão
  botoesProduto.forEach((botao) => {
    botao.addEventListener("click", () => {
      const produtoId = botao.getAttribute("id"); // Pega o ID do produto
      //console.log(`Produto ${produtoId} adicionado ao carrinho.`);
      produtos.push(produtoId); // Adiciona o ID do produto à lista
      //console.log("Lista de produtos:", produtos);
      listarProdutosNoCarrinho(produtos, estoque)
    });
  });
  
}


//simula pedido
orderButton.addEventListener("click", () => {
  console.log("Carrinho enviado:");
  console.log("botoes:",botoesProduto)
  alert("Pedido realizado com sucesso! Veja o console para detalhes.");

});

