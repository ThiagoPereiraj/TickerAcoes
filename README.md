
# 🚀 Ticker LED Display Scripts

Este repositório contém scripts Python desenvolvidos para exibição de informações em painéis de LED com resolução customizada de 8184x144px. + 1920 O projeto está dividido em duas funcionalidades principais: monitoramento financeiro e exibição de avisos dinâmicos.

---

## 📂 Estrutura do Repositório

* **ticker-financeiro/**: Contém o script `ticker.py` que utiliza `Tkinter` e `yfinance` para exibir cotações de ações, moedas e commodities.
* **ticker-mensagem/**: Contém o script `message.py` que utiliza `PySide6` para exibir mensagens de texto personalizadas com suporte a GIFs animados.
* **requirements.txt**: Arquivo com as dependências necessárias para rodar ambos os projetos.

---

## 🛠️ Requisitos e Instalação

### Dependências
As bibliotecas necessárias para o funcionamento são:
* `yfinance` e `pandas` (para os dados financeiros).
* `PySide6` (para a interface com GIFs).

### Instalação
1. Instale o Python 3.10 ou superior.
2. Na raiz do projeto, execute:
```bash
   pip install -r requirements.txt
```

---

## 🖥️ Como Utilizar

### Ticker Financeiro

- **Localização**: `ticker-financeiro/ticker.py`
    
- **Função**: Exibe duas linhas de 72px cada.
    
- **Comandos**: Pressione `ESC` para fechar a aplicação.

### Ticker de Mensagem

- **Localização**: `ticker-mensagem/message.py`
    
- **Função**: Exibe texto corrido com GIFs (configuráveis via código nas variáveis `GIF_AT_START` e `GIF_AT_END`).
    
- **Comandos**: Pressione `ESC` para fechar a aplicação.

---

## ⚙️ Notas Técnicas de Infraestrutura

- **Resolução**: Configurado para largura de 8184px e altura total de 144px.
    
- **Sobreposição**: Ambos os scripts utilizam configurações para permanecerem no topo das outras janelas (Always on Top).
    
- **Rede**: A versão financeira exige acesso à internet para consultar a API do Yahoo Finance.


````

---
### 2. requirements.txt
Crie um arquivo chamado `requirements.txt` na raiz da pasta e cole isto:

text
yfinance
pandas
PySide6
````

---

### 3. .gitignore

Crie um arquivo chamado `.gitignore` na raiz da pasta e cole isto:

Plaintext

```
__pycache__/
*.pyc
venv/
.env
.vscode/
.idea/
```

---

### 💡 Lembrete de Organização de Pastas

Para que tudo funcione conforme o README acima, organize seus arquivos assim:

1. **Pasta Raiz**: Coloque o `README.md`, `requirements.txt` e `.gitignore`.
    
2. **Pasta `ticker-financeiro/`**: Coloque o arquivo `ticker.py`.
    
3. **Pasta `ticker-mensagem/`**: Coloque o arquivo `message.py`.
    
4. **Pasta `ticker-mensagem/assets/`**: Coloque todos os seus arquivos `.gif`.
    
    - _Nota: No seu arquivo `message.py`, lembre-se de atualizar o nome do arquivo para `GIF_FILENAME = "assets/corinthians.gif"` (ou o GIF de sua preferência)._