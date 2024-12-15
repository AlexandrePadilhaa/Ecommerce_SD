// URL da API (substitua pela correta)
const API_URL = "http://localhost:8001/estoque/";

console.log("teste")
// Função para buscar produtos da API
async function fetchProducts() {
  try {
    const response = await fetch(API_URL);
    if (!response.ok) throw new Error("Erro ao buscar produtos");
    const products = await response.json();
    console.log(products)
    displayProducts(products);
  } catch (error) {
    console.error(error);
    document.getElementById("product-list").innerHTML = "<p>Erro ao carregar produtos.</p>";
  }
}

async function fetchProductsTest() {
  const fakeProducts = [
    { nome: "Produto A", preco: 10.0, image: "https://via.placeholder.com/150" },
    { nome: "Produto B", preco: 20.0, image: "https://via.placeholder.com/150" },
    { nome: "Produto C", preco: 30.0, image: "https://via.placeholder.com/150" },
  ];
  console.log(fakeProducts)
  displayProducts(fakeProducts);
}


// Função para exibir produtos na página
function displayProducts(products) {
  const productList = document.getElementById("product-list");
  productList.innerHTML = products
    .map(
      (product) => `
      <div class="product">
        <img src="${product.image || 'placeholder.jpg'}" alt="${product.nome}">
        <h2>${product.nome}</h2>
        <p>Preço: R$ ${product.preco.toFixed(2)}</p>
      </div>
    `
    )
    .join("");
}

// Iniciar o carregamento

console.log("a")
fetchProductsTest();
console.log("b")
//fetchProducts();

