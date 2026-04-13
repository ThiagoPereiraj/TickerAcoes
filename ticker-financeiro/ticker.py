import tkinter as tk
from tkinter import font
import yfinance as yf
import pandas as pd
import time
import threading
import math

# --- CONFIGURAÇÕES DE DESIGN (Ajustado para 144px de altura total) ---

# Cores
COR_FUNDO_TELA = "#000000"      # Preto absoluto para fundir com o painel LED
COR_CARD_BG = "#292929"         # Fundo do card levemente mais claro
COR_TICKER = "#FFFFFF"          # Branco
COR_PRECO = "#CCCCCC"           # Cinza claro
COR_SOBE = "#4CD964"            # Verde
COR_DESCE = "#FF3B30"           # Vermelho
COR_NEUTRO = "#808080"          # Cinza escuro

# Fontes (Reduzidas para caber em 72px de altura)
FONTE_FAMILIA = "Segoe UI"      
TAMANHO_TICKER = 32             # Ajustado para altura 72
TAMANHO_DADOS = 31              # Ajustado para altura 72

# Dimensões e Velocidade
LARGURA_BLOCO_TOTAL = 650
LARGURA_TELA = 8184             
ALTURA_TICKER_POR_LINHA = 72    # <--- EXATAMENTE 72px
VELOCIDADE_ROLAGEM = 3          # Esquerda -> Direita
TEMPO_ATUALIZACAO_MIN = 1

# --- SEUS ATIVOS ---
ATIVOS_POR_LINHA = [
    # Linha 1
    [
        {'ticker': 'USDBRL=X', 'display': 'USD', 'type': 'currency', 'is_cents': False},
        {'ticker': 'EURBRL=X', 'display': 'EUR', 'type': 'currency', 'is_cents': False},
        {'ticker': 'BZ=F', 'display': 'BRENT', 'type': 'commodity', 'is_cents': False},
        {'ticker': 'SB=F', 'display': 'AÇÚCAR', 'type': 'commodity', 'is_cents': False},
        {'ticker': 'ZS=F', 'display': 'SOJA', 'type': 'commodity', 'is_cents': False},
        {'ticker': 'ZC=F', 'display': 'MILHO', 'type': 'commodity', 'is_cents': False},
        {'ticker': 'BBAS3.SA', 'display': 'BBAS3', 'type': 'stock', 'is_cents': False},
        {'ticker': 'ITSA4.SA', 'display': 'ITSA4', 'type': 'stock', 'is_cents': False},
        {'ticker': 'VALE3.SA', 'display': 'VALE3', 'type': 'stock', 'is_cents': False},
        {'ticker': 'PETR4.SA', 'display': 'PETR4', 'type': 'stock', 'is_cents': False},
        {'ticker': 'MGLU3.SA', 'display': 'MGLU3', 'type': 'stock', 'is_cents': False},
        {'ticker': 'BPAC11.SA', 'display': 'BPAC11', 'type': 'stock', 'is_cents': False},
    ],
    # Linha 2
    [
        {'ticker': 'CSAN3.SA', 'display': 'CSAN3', 'type': 'stock', 'is_cents': False},
        {'ticker': 'PRIO3.SA', 'display': 'PRIO3', 'type': 'stock', 'is_cents': False},
        {'ticker': 'JBSS32.SA', 'display': 'JBSS32', 'type': 'stock', 'is_cents': False},
        {'ticker': 'RAIL3.SA', 'display': 'RAIL3', 'type': 'stock', 'is_cents': False},
        {'ticker': 'SMTO3.SA', 'display': 'SMTO3', 'type': 'stock', 'is_cents': False},
        {'ticker': 'VAMO3.SA', 'display': 'VAMO3', 'type': 'stock', 'is_cents': False},
        {'ticker': 'AMBP3.SA', 'display': 'AMBP3', 'type': 'stock', 'is_cents': False},
        {'ticker': 'CVCB3.SA', 'display': 'CVCB3', 'type': 'stock', 'is_cents': False},
        {'ticker': 'CMIG4.SA', 'display': 'CMIG4', 'type': 'stock', 'is_cents': False},
        {'ticker': 'GGBR4.SA', 'display': 'GGBR4', 'type': 'stock', 'is_cents': False},
        {'ticker': 'GOAU4.SA', 'display': 'GOAU4', 'type': 'stock', 'is_cents': False},
        {'ticker': 'WEGE3.SA', 'display': 'WEGE3', 'type': 'stock', 'is_cents': False},
    ]
]

ALL_ASSETS = [asset for sublist in ATIVOS_POR_LINHA for asset in sublist]
stock_data = {asset['display']: {"price": "...", "change": 0.0, "color": COR_NEUTRO, "type": asset['type']} for asset in ALL_ASSETS}
app_instance = None

# --- YFINANCE ---
def fetch_stock_data():
    global app_instance
    all_tickers_list = [asset['ticker'] for asset in ALL_ASSETS]
    print(f"[{time.strftime('%H:%M:%S')}] Buscando dados...")
    
    try:
        data = yf.download(tickers=all_tickers_list, period="2d", interval="1d", progress=False)
        updated_something = False
        
        for asset in ALL_ASSETS:
            try:
                t_full = asset['ticker']
                t_disp = asset['display']
                
                if t_full not in data['Close']: continue

                closes = data['Close'][t_full].dropna()
                latest = 0.0
                change_pct = 0.0

                if not closes.empty:
                    latest = closes.iloc[-1]
                    prev = 0.0
                    if len(closes) >= 2:
                        prev = closes.iloc[-2]
                    elif asset['type'] != 'stock':
                         op = data['Open'][t_full].dropna()
                         if not op.empty: prev = op.iloc[-1]

                    if prev > 0:
                        change_pct = ((latest - prev) / prev) * 100
                
                color = COR_NEUTRO
                if change_pct > 0.00: color = COR_SOBE
                elif change_pct < -0.00: color = COR_DESCE
                
                stock_data[t_disp].update({"price": latest, "change": change_pct, "color": color})
                updated_something = True
            except Exception:
                pass

        if updated_something and app_instance:
            app_instance.master.after(10, app_instance.update_data_loop)
            
    except Exception as e:
        print(f"Erro download: {e}")
        
    threading.Timer(TEMPO_ATUALIZACAO_MIN * 60, fetch_stock_data).start()

# --- VISUAL ---
class TickerLine:
    def __init__(self, master, assets):
        self.master = master
        self.assets = assets
        # pady=0 garante que não haja espaço extra entre as linhas
        self.canvas = tk.Canvas(master, bg=COR_FUNDO_TELA, height=ALTURA_TICKER_POR_LINHA, highlightthickness=0)
        self.canvas.pack(fill=tk.X, pady=0) 
        
        self.font_ticker = font.Font(family=FONTE_FAMILIA, size=TAMANHO_TICKER, weight="bold")
        self.font_data = font.Font(family=FONTE_FAMILIA, size=TAMANHO_DADOS, weight="normal")
        
        self.ticker_blocks = []
        self.single_set_width = LARGURA_BLOCO_TOTAL * len(self.assets)
        
        self.setup_canvas_objects()
        self.scroll()

    def setup_canvas_objects(self):
        self.canvas.delete("all")
        self.ticker_blocks = []
        if not self.assets: return

        num_copies = math.ceil(LARGURA_TELA / self.single_set_width) + 2
        current_x = -LARGURA_BLOCO_TOTAL 
        
        for _ in range(num_copies):
            for asset in self.assets:
                # Retângulo ajustado: Margem superior/inferior de 4px (5 até Height-5 era para 80px)
                # Para 72px, vamos usar margem de 4px para ficar elegante
                rect_id = self.canvas.create_rectangle(
                    current_x + 5, 4, 
                    current_x + LARGURA_BLOCO_TOTAL - 5, ALTURA_TICKER_POR_LINHA - 4,
                    fill=COR_CARD_BG, outline="", width=0
                )
                
                # Texto centralizado verticalmente (ALTURA / 2)
                y_center = ALTURA_TICKER_POR_LINHA / 2
                
                nome_id = self.canvas.create_text(
                    current_x + 30, y_center, 
                    text=asset['display'], font=self.font_ticker, fill=COR_TICKER, anchor='w'
                )

                price_id = self.canvas.create_text(
                    current_x + LARGURA_BLOCO_TOTAL - 260, y_center,
                    text="---", font=self.font_data, fill=COR_PRECO, anchor='e' 
                )
                
                var_id = self.canvas.create_text(
                    current_x + LARGURA_BLOCO_TOTAL - 30, y_center,
                    text="0.00%", font=self.font_data, fill=COR_NEUTRO, anchor='e'
                )

                self.ticker_blocks.append({
                    "ids": [rect_id, nome_id, price_id, var_id],
                    "asset": asset
                })
                current_x += LARGURA_BLOCO_TOTAL
        
        self.update_text_content()

    def update_text_content(self):
        for block in self.ticker_blocks:
            data = stock_data[block["asset"]['display']]
            ids = block["ids"]
            
            val = data['price']
            if isinstance(val, (int, float)):
                if block["asset"].get('is_cents', False): val /= 100
                prefix = "R$ " if data['type'] == 'stock' else "$ "
                p_text = f"{prefix}{val:,.2f}"
            else:
                p_text = "..."

            change = data['change']
            color = data['color']
            seta = "▲" if color == COR_SOBE else "▼" if color == COR_DESCE else ""
            var_text = f"{seta} {abs(change):.2f}%"

            self.canvas.itemconfig(ids[2], text=p_text)
            self.canvas.itemconfig(ids[3], text=var_text, fill=color)

    def scroll(self):
        # Move para DIREITA
        self.canvas.move("all", VELOCIDADE_ROLAGEM, 0)
        
        if self.ticker_blocks:
            last_block_rect = self.ticker_blocks[-1]["ids"][0]
            coords = self.canvas.coords(last_block_rect)
            
            if coords and coords[0] > LARGURA_TELA:
                popped_block = self.ticker_blocks.pop()
                first_block_rect = self.ticker_blocks[0]["ids"][0]
                first_coords = self.canvas.coords(first_block_rect)
                
                target_x = first_coords[0] - LARGURA_BLOCO_TOTAL
                delta = target_x - coords[0]
                
                for item_id in popped_block["ids"]:
                    self.canvas.move(item_id, delta, 0)
                
                self.ticker_blocks.insert(0, popped_block)

        self.master.after(20, self.scroll)

# --- APP ---
class MainApplication:
    def __init__(self, master):
        global app_instance
        app_instance = self
        self.master = master
        master.title("Ticker 144px")
        
        # GEOMETRIA EXATA: 144 PIXELS DE ALTURA
        master.geometry(f"{LARGURA_TELA}x144+0+0")
        
        master.overrideredirect(True)
        master.attributes('-topmost', True)
        master.configure(bg=COR_FUNDO_TELA)
        master.bind("<Escape>", lambda e: master.destroy())
        
        self.line1 = TickerLine(master, ATIVOS_POR_LINHA[0])
        self.line2 = TickerLine(master, ATIVOS_POR_LINHA[1])
        
        self.master.after(1000, fetch_stock_data)

    def update_data_loop(self):
        self.line1.update_text_content()
        self.line2.update_text_content()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()