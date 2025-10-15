import tkinter as tk
from tkinter import font
import yfinance as yf
import pandas as pd
import time
import threading
import math

# --- CONFIGURAÇÕES GERAIS ---

# MUDANÇA 1: LARGURA FIXA PARA CADA BLOCO DE ATIVO. ESTA É A CHAVE PARA O ALINHAMENTO PERFEITO.
LARGURA_BLOCO_TOTAL = 950 # Largura total em pixels para cada ativo (nome + preço)

ATIVOS_POR_LINHA = [
    # Linha de cima
    [
        {'ticker': 'USDBRL=X', 'display': 'USD', 'type': 'currency', 'is_cents': False},
        {'ticker': 'EURBRL=X', 'display': 'EUR', 'type': 'currency', 'is_cents': False},
        {'ticker': 'BZ=F', 'display': 'BRENT', 'type': 'commodity', 'is_cents': False},
        {'ticker': 'SB=F', 'display': 'AÇÚCAR', 'type': 'commodity', 'is_cents': False},
        {'ticker': 'ZS=F', 'display': 'SOJA', 'type': 'commodity', 'is_cents': False},
        {'ticker': 'ZC=F', 'display': 'MILHO', 'type': 'commodity', 'is_cents': False},
        # {'ticker': 'ZET=F', 'display': 'ETANOL', 'type': 'commodity', 'is_cents': False},
        {'ticker': 'AMBP3.SA', 'display': 'AMBP3', 'type': 'stock', 'is_cents': False},
        {'ticker': 'CVCB3.SA', 'display': 'CVCB3', 'type': 'stock', 'is_cents': False},
        {'ticker': 'BBAS3.SA', 'display': 'BBAS3', 'type': 'stock', 'is_cents': False},
        {'ticker': 'BHIA3.SA', 'display': 'BHIA3', 'type': 'stock', 'is_cents': False},
        {'ticker': 'BPAC11.SA', 'display': 'BPAC11', 'type': 'stock', 'is_cents': False},
        {'ticker': 'BPAN4.SA', 'display': 'BPAN4', 'type': 'stock', 'is_cents': False},
        {'ticker': 'CSAN3.SA', 'display': 'CSAN3', 'type': 'stock', 'is_cents': False},
        {'ticker': 'MGLU3.SA', 'display': 'MGLU3', 'type': 'stock', 'is_cents': False},
        
    ],
    # Linha de baixo
    [
        {'ticker': 'PETR4.SA', 'display': 'PETR4', 'type': 'stock', 'is_cents': False},
        {'ticker': 'PETZ3.SA', 'display': 'PETZ3', 'type': 'stock', 'is_cents': False},
        {'ticker': 'PRIO3.SA', 'display': 'PRIO3', 'type': 'stock', 'is_cents': False},
        {'ticker': 'VALE3.SA', 'display': 'VALE3', 'type': 'stock', 'is_cents': False},
        {'ticker': 'HASH11.SA', 'display': 'HASH11', 'type': 'stock', 'is_cents': False},
        {'ticker': 'INBR32.SA', 'display': 'INBR32', 'type': 'stock', 'is_cents': False},
        {'ticker': 'ITSA4.SA', 'display': 'ITSA4', 'type': 'stock', 'is_cents': False},
        {'ticker': 'JBSS32.SA', 'display': 'JBSS32', 'type': 'stock', 'is_cents': False},
        {'ticker': 'POMO4.SA', 'display': 'POMO4', 'type': 'stock', 'is_cents': False},
        {'ticker': 'RAIL3.SA', 'display': 'RAIL3', 'type': 'stock', 'is_cents': False},
        {'ticker': 'RAIZ4.SA', 'display': 'RAIZ4', 'type': 'stock', 'is_cents': False},
        {'ticker': 'SMTO3.SA', 'display': 'SMTO3', 'type': 'stock', 'is_cents': False},
        {'ticker': 'UNIP6.SA', 'display': 'UNIP6', 'type': 'stock', 'is_cents': False},
        {'ticker': 'VAMO3.SA', 'display': 'VAMO3', 'type': 'stock', 'is_cents': False},
    ]
]
# --- FIM DA CONFIGURAÇÃO ---

ALL_ASSETS = [asset for sublist in ATIVOS_POR_LINHA for asset in sublist]

LARGURA_TELA = 8184
ALTURA_TICKER_POR_LINHA = 72
COR_FUNDO = "#000000"
COR_TEXTO_NOME = "white"
COR_TEXTO_ALTA = "#00ff00"
COR_TEXTO_BAIXA = "#ff0000"
COR_TEXTO_NEUTRO = "#c8c8c8"
FONTE_FAMILIA = "Consolas"
FONTE_TAMANHO = 45
VELOCIDADE_ROLAGEM = 3
TEMPO_ATUALIZACAO_MIN = 1

stock_data = {asset['display']: {"price": "---", "change": "---", "color": COR_TEXTO_NEUTRO, "type": asset['type']} for asset in ALL_ASSETS}
app_instance = None

# --- LÓGICA DE DADOS (YFINANCE) ---
def fetch_stock_data():
    global app_instance
    all_tickers_list = [asset['ticker'] for asset in ALL_ASSETS]
    print(f"[{time.strftime('%H:%M:%S')}] Buscando dados com yfinance para {len(all_tickers_list)} ativos...")
    try:
        data = yf.download(tickers=all_tickers_list, period="2d", interval="1d", progress=False)
        updated_something = False
        for asset in ALL_ASSETS:
            ticker_display = asset['display']
            ticker_full = asset['ticker']
            asset_type = asset['type']
            try:
                if asset_type == 'stock':
                    ticker_history = data['Close'][ticker_full]
                    valid_closes = ticker_history.dropna()
                    if len(valid_closes) >= 2:
                        latest_close = valid_closes.iloc[-1]
                        previous_close = valid_closes.iloc[-2]
                        change_percent = ((latest_close - previous_close) / previous_close) * 100
                    elif len(valid_closes) == 1:
                        latest_close = valid_closes.iloc[-1]
                        change_percent = 0.0
                    else:
                        latest_close = "N/A"
                        change_percent = 0.0
                else: 
                    latest_close = data['Close'][ticker_full].dropna().iloc[-1]
                    open_price = data['Open'][ticker_full].dropna().iloc[-1]
                    if open_price and open_price != 0 and not pd.isna(open_price) and not pd.isna(latest_close):
                        change_percent = ((latest_close - open_price) / open_price) * 100
                    else:
                        change_percent = 0.0
                
                color = COR_TEXTO_NEUTRO
                if change_percent > 0.01: color = COR_TEXTO_ALTA
                elif change_percent < -0.01: color = COR_TEXTO_BAIXA
                stock_data[ticker_display].update({"price": latest_close, "change": change_percent, "color": color})
                updated_something = True
            except Exception as e:
                print(f"    -> Erro ao processar dados individuais para {ticker_display}: {e}")
        if updated_something and app_instance:
            app_instance.master.after(10, app_instance.update_data_loop)
    except Exception as e:
        print(f"Erro geral ao buscar dados com yfinance: {e}")
    threading.Timer(TEMPO_ATUALIZACAO_MIN * 60, fetch_stock_data).start()

# --- CLASSE DA APLICAÇÃO (TKINTER) ---
class TickerLine:
    def __init__(self, master, assets):
        self.master = master
        self.canvas = tk.Canvas(master, bg=COR_FUNDO, height=ALTURA_TICKER_POR_LINHA, highlightthickness=0)
        self.canvas.pack(fill=tk.X)
        self.assets = assets
        self.custom_font = font.Font(family=FONTE_FAMILIA, size=FONTE_TAMANHO, weight="bold")
        
        self.single_set_width = LARGURA_BLOCO_TOTAL * len(self.assets)
        self.full_content_width = 0
        self.ticker_blocks = []

        self.create_ticker_text()
        self.scroll()

    def create_ticker_text(self):
        self.canvas.delete("all")
        self.ticker_blocks = []
        current_x = 0
        if self.single_set_width == 0: return

        num_copies = math.ceil(LARGURA_TELA / self.single_set_width) + 1
        self.full_content_width = self.single_set_width * num_copies

        for i in range(int(num_copies)):
            for asset in self.assets:
                block_items = []
                block_start_x = current_x
                block_end_x = current_x + LARGURA_BLOCO_TOTAL

                # MUDANÇA 2: Cria os itens de texto com alinhamento oposto dentro do bloco
                nome_id = self.canvas.create_text(block_start_x + 10, ALTURA_TICKER_POR_LINHA / 2, text="", font=self.custom_font, fill=COR_TEXTO_NOME, anchor='w') # Alinhado à esquerda
                valor_id = self.canvas.create_text(block_end_x - 10, ALTURA_TICKER_POR_LINHA / 2, text="", font=self.custom_font, anchor='e') # Alinhado à direita
                
                current_x += LARGURA_BLOCO_TOTAL
                block_items.extend([nome_id, valor_id])
                self.ticker_blocks.append(block_items)
        
        self.update_text_content() # Preenche o texto pela primeira vez

    def update_text_content(self):
        """Preenche ou atualiza o conteúdo dos itens de texto já existentes."""
        num_assets = len(self.assets)
        for i, block in enumerate(self.ticker_blocks):
            asset = self.assets[i % num_assets]
            
            ticker_display = asset['display']
            data = stock_data[ticker_display]
            
            nome_str = ticker_display
            
            price_val = data['price']
            price_str = "---"
            if isinstance(price_val, (int, float)):
                display_price = price_val / 100.0 if asset.get('is_cents', False) else price_val
                prefix = "R$ " if data['type'] == 'stock' else "$ "
                price_str = f"{prefix}{display_price:.2f}"

            change_val = data['change']
            change_str = '(N/A)'
            if isinstance(change_val, (int, float)):
                change_str = f"({change_val:+.2f}%)"
            
            sinal = '▲' if data['color'] == COR_TEXTO_ALTA else '▼' if data['color'] == COR_TEXTO_BAIXA else ''
            
            # Atualiza o texto dos itens do canvas
            self.canvas.itemconfig(block[0], text=nome_str)
            self.canvas.itemconfig(block[1], text=f"{price_str} {change_str} {sinal}", fill=data['color'])

    def scroll(self):
        self.canvas.move("all", VELOCIDADE_ROLAGEM, 0)
        # Lógica de teletransporte de blocos
        for block in self.ticker_blocks:
            try:
                coords = self.canvas.coords(block[0])
                if coords and coords[0] > LARGURA_TELA:
                    # Move o bloco inteiro para o final da fila
                    self.canvas.move(block[0], -self.full_content_width, 0)
                    self.canvas.move(block[1], -self.full_content_width, 0)
            except tk.TclError:
                # O item pode ter sido deletado durante a atualização, ignora o erro
                pass
        self.master.after(20, self.scroll)

class MainApplication:
    def __init__(self, master):
        global app_instance
        app_instance = self
        self.master = master
        master.title("Ticker de Ativos")
        master.geometry(f"{LARGURA_TELA}x{ALTURA_TICKER_POR_LINHA * 2}+0+0")
        master.overrideredirect(True)
        master.attributes('-topmost', True)
        master.configure(bg=COR_FUNDO)
        master.bind("<Escape>", lambda e: master.destroy())
        
        self.line1 = TickerLine(master, ATIVOS_POR_LINHA[0])
        self.line2 = TickerLine(master, ATIVOS_POR_LINHA[1])
        
        self.master.after(2000, fetch_stock_data)

    def update_data_loop(self):
        print(f"[{time.strftime('%H:%M:%S')}] Atualizando a interface com novos dados.")
        
        self.line1.update_text_content()
        self.line2.update_text_content()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()