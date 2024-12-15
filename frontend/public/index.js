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
  } catch (error) {
      console.error(error);
  }
}

function displayProducts(products) {
  const productList = document.getElementById('product-list');
  productList.innerHTML = ''; 

  products.map(product => {
      const productElement = document.createElement('div');
      productElement.className = 'product';
      productElement.innerHTML = `
          <h2>${product.nome}</h2>
          <img src="${'https://via.placeholder.com/150' || 'placeholder.jpg'}" alt="${product.nome}">
          <p>Preço: R$${product.preco.toFixed(2)}</p>
          <p>Disponível: ${product.quantidade_disponivel}</p>
      `;
      productList.appendChild(productElement);
  });
}

fetchProducts();


