
// Função para filtrar os produtos em tempo real (por nome, marca ou site)
function filtrarProdutos() {
    let filtro = document.getElementById('filtro').value.trim().toLowerCase();
    let cards = document.getElementsByClassName('card');

    function removerAcentos(str) {
        return str.normalize('NFD').replace(/[\u0300-\u036f]/g, "");
    }

    filtro = removerAcentos(filtro);

    for (let i = 0; i < cards.length; i++) {
        let nomeProduto = removerAcentos(cards[i].getElementsByClassName('nome-produto')[0].innerText.toLowerCase());
        let marcaProduto = removerAcentos(cards[i].getElementsByClassName('marca-produto')[0].innerText.toLowerCase());
        let siteProduto = removerAcentos(cards[i].getElementsByClassName('site-produto')[0].innerText.toLowerCase());

        if (nomeProduto.includes(filtro) || marcaProduto.includes(filtro) || siteProduto.includes(filtro)) {
            cards[i].style.display = "";
        } else {
            cards[i].style.display = "none";
        }
    }
}

// Função para ordenar os cards por preço
function ordenarPorPreco() {
    let cardsContainer = document.getElementById('cardsContainer');
    let cards = Array.from(cardsContainer.getElementsByClassName('card'));
    let ordenarCrescente = document.getElementById('ordenarPreco').checked;

    cards.sort(function(a, b) {
        let precoA = parseFloat(a.querySelector('.preco-produto').getAttribute('data-preco')) || 0;
        let precoB = parseFloat(b.querySelector('.preco-produto').getAttribute('data-preco')) || 0;
        
        return ordenarCrescente ? precoA - precoB : precoB - precoA;
    });

    // Reorganizar os cards no DOM
    cards.forEach(function(card) {
        cardsContainer.appendChild(card);
    });
}

// Função para redirecionar o usuário para a página inicial ao clicar no H1 ou logo
function redirecionarParaPaginaInicial() {
    window.location.href = '/';
}
// Função para redirecionar o usuário para a página inicial ao clicar no H1 ou logo
function redirecionarParaPaginaInicial() {
    window.location.href = '/';
}

// Função para limpar o campo de filtro
function limparFiltro() {
document.getElementById('filtro').value = '';
filtrarProdutos(); // Chama a função de filtragem para atualizar os cards
}