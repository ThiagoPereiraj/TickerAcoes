
# Ticker - Scripts

Este repositório contém scripts Python desenvolvidos para exibição de informações em painéis de LED com resolução customizada de 10104x144px. Este painel é dividido em três partes, onde duas são de 4092px e outra de 1920px. O projeto está dividido em duas funcionalidades principais: **monitoramento financeiro** e **exibição de avisos dinâmicos.**


---

## 📂 Estrutura de Pastas

- **ticker-financeiro/**: Script focado em cotações de mercado.
    
- **ticker-mensagem/**: Script para avisos, alertas e mensagens comemorativas.
    
- **requirements.txt**: Lista de dependências Python.

---

## 🛠️ Instalação

1. Certifique-se de ter o **Python 3.10** ou superior instalado.
    
2. No terminal, acesse a pasta do projeto e instale as bibliotecas:
    
    `pip install -r requirements.txt`

---

## 📝 Guia de Uso dos Scripts

### 1. Ticker Financeiro

Este script exibe duas linhas de rolagem com dados da B3, moedas e commodities.

- **Como executar**: `python ticker-financeiro/ticker.py`
    
- **Funcionamento**: Ele busca dados via API do Yahoo Finance a cada 1 minuto.
    
- **Como fechar**: Pressione a tecla `ESC`.


### 2. Ticker de Mensagem (Customização)

Este script é focado em textos personalizados e suporte a GIFs.

- **Como executar**: `python ticker-mensagem/message.py`

#### **Como Customizar a Mensagem:**

Abra o arquivo `message.py` em um editor de texto e localize as seguintes linhas no topo do código:

- **Alterar o Texto**: Localize `MESSAGE_TEXT`. Altere o conteúdo entre aspas para a mensagem desejada.
    
- **Alterar o GIF**: Localize a variável `GIF_FILENAME`. Coloque o nome do arquivo que está na pasta assets (ex: `"assets/aviso.gif"`). O arquivo .gif deve esta na pasta `ticker-mensagem/assets`
    
- **Posição do GIF**:
    
    - `GIF_AT_START = True`: Exibe o GIF antes do texto.
        
    - `GIF_AT_END = True`: Exibe o GIF após o texto.
        
- **Cores e Fonte**: Você pode ajustar `FONT_SIZE` (tamanho), `TEXT_COLOR` (cor do texto) e `BACKGROUND_COLOR` (cor do fundo) nas constantes globais.

---

## ⚙️ Detalhes Técnicos de Infraestrutura

- **Resolução**: O sistema força uma largura de 10104px para cobrir toda a extensão do painel.
    
- **Always on Top**: Ambos os scripts rodam com prioridade visual, ficando sempre acima de qualquer outra janela aberta no Windows/Linux.
    
- **Performance**: A versão de mensagem utiliza PySide6 (Qt) para garantir que a animação dos GIFs não sobrecarregue a CPU.

---

