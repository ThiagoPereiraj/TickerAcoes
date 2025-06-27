import tkinter as tk
from tkinter import font
import yfinance as yf
import time
import threading
import pandas as pd

TICKERS_LIST = [
    "AMBP3.SA", "CVCB3.SA", "BBAS3.SA", "BHIA3.SA", "BPAC11.SA", "BPAN4.SA",
    "AURA33.SA", "CSAN3.SA", "POMO4.SA", "INBR32.SA", "ITSA4.SA",
    "JBSS32.SA", "MGLU3.SA", "PETR4.SA", "PETZ3.SA", "PRIO3.SA", "RAIL3.SA",
    "RAIZ4.SA", "SMTO3.SA", "UNIP6.SA", "VALE3.SA", "VAMO3.SA", "HASH11.SA"
]

DISPLAY_TICKERS = [t.replace(".SA", "") for t in TICKERS_LIST]

stock_data = {}
for ticker_display in DISPLAY_TICKERS:
    stock_data[ticker_display] = {"value": "---", "change": "---", "color": "white"}

BACKGROUND_COLOR = "#1a1a1a"
TEXT_COLOR_NORMAL = "white"
TEXT_COLOR_POSITIVE = "#00ff00"
TEXT_COLOR_NEGATIVE = "#ff0000"
SEPARATOR_COLOR = "white"

FONT_SIZE = 70
TICKER_HEIGHT = 144
SCROLL_SPEED = 1 # Velocidade de rolagem (positivo para direita, negativo para esquerda)

root = None
app = None

def fetch_stock_data():
    global stock_data, app
    current_time_sp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print(f"[{current_time_sp}] Buscando dados das ações com YFinance (requisição em lote)...")

    new_stock_data = {}

    download_period = "2d"
    download_interval = "1h"

    try:
        data = yf.download(
            TICKERS_LIST,
            period=download_period,
            interval=download_interval,
            progress=False,
            actions=False,
            auto_adjust=False
        )

        if data.empty or ('Close' not in data.columns and not isinstance(data.columns, pd.MultiIndex)):
            print(f"Erro: Requisição em lote retornou DataFrame vazio ou sem colunas esperadas. HTTP Error 404 ou similar.")
            return

        for ticker_full in TICKERS_LIST:
            ticker_display = ticker_full.replace(".SA", "")

            latest_close = None
            latest_open = None

            try:
                ticker_close_series = None
                ticker_open_series = None

                if isinstance(data.columns, pd.MultiIndex):
                    if ('Close', ticker_full) in data.columns:
                        ticker_close_series = data['Close'][ticker_full]
                    if ('Open', ticker_full) in data.columns:
                        ticker_open_series = data['Open'][ticker_full]
                elif 'Close' in data.columns and not isinstance(data.columns, pd.MultiIndex):
                    if ticker_full in data.columns and isinstance(data[ticker_full], pd.DataFrame) and 'Close' in data[ticker_full].columns:
                        ticker_close_series = data[ticker_full]['Close']
                        ticker_open_series = data[ticker_full]['Open'] if 'Open' in data[ticker_full].columns else None
                    else:
                        ticker_close_series = data['Close']
                        ticker_open_series = data['Open'] if 'Open' in data.columns else None


                if ticker_close_series is None or ticker_close_series.empty or ticker_close_series.isnull().all() or pd.isna(ticker_close_series.iloc[-1]):
                    raise ValueError(f"Nenhum 'Close' válido encontrado na Series para {ticker_display}.")

                latest_close = ticker_close_series.iloc[-1]

                if ticker_open_series is not None and not ticker_open_series.empty and not ticker_open_series.isnull().all() and not pd.isna(latest_open):
                    latest_open = ticker_open_series.iloc[-1]

                if latest_open is None or pd.isna(latest_open):
                    if not ticker_close_series.empty and not ticker_close_series.isnull().all():
                        for i in range(2, len(ticker_close_series) + 1):
                            if len(ticker_close_series) >= i:
                                prev_close_candidate = ticker_close_series.iloc[-i]
                                if not pd.isna(prev_close_candidate):
                                    latest_open = prev_close_candidate
                                    break
                    if latest_open is None or pd.isna(latest_open):
                        latest_open = latest_close

                change_percent = 0.0
                if latest_open is not None and latest_open != 0:
                    change_percent = ((latest_close - latest_open) / latest_open) * 100

                color = TEXT_COLOR_POSITIVE if change_percent >= 0 else TEXT_COLOR_NEGATIVE
                value_str = f"{latest_close:.2f}".replace('.', ',')
                change_str = f"{change_percent:+.2f}%".replace('.', ',')

                new_stock_data[ticker_display] = {
                    "value": value_str,
                    "change": change_str,
                    "color": color
                }
            except Exception as inner_e:
                print(f"Erro ao processar dados para {ticker_display} (inner): {inner_e}")
                new_stock_data[ticker_display] = stock_data.get(ticker_display, {"value": "---", "change": "---", "color": "white"})

    except Exception as e:
        print(f"Erro geral na requisição de dados em lote (outer): {e}")
        pass

    stock_data.update(new_stock_data)

    if root and app:
        root.after(10, app.update_ticker_display)
        root.after(60000, fetch_stock_data)

class TickerApp:
    def __init__(self, master):
        global root, app
        root = master
        app = self

        self.master = master
        master.title("Ticker de Ações B3")

        master.geometry(f"8192x{TICKER_HEIGHT}+0+0")
        master.overrideredirect(True)
        master.attributes('-topmost', True)
        master.configure(bg=BACKGROUND_COLOR)

        self.canvas = tk.Canvas(master, bg=BACKGROUND_COLOR, height=TICKER_HEIGHT, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.custom_font = font.Font(family="Arial", size=FONT_SIZE, weight="bold")

        self.ticker_blocks = []
        self.single_set_width = 0

        self.create_initial_ticker_items()
        self.scroll_ticker()

        threading.Thread(target=fetch_stock_data, daemon=True).start()

    def _measure_text_width(self, text):
        return self.custom_font.measure(text)

    def create_initial_ticker_items(self):
        self.canvas.delete("all")
        self.ticker_blocks = []

        overall_current_pos_x = 0

        SPACE_AFTER_TICKER_NAME = 25
        SPACE_AFTER_VALUE = 190
        SPACE_AFTER_CHANGE = 250
        SEPARATOR_AND_GAP_WIDTH = 70
        INTER_ITEM_PADDING = 5

        for i, ticker_display in enumerate(DISPLAY_TICKERS):
            data = stock_data[ticker_display]
            block_start_x = overall_current_pos_x

            center_y = TICKER_HEIGHT / 2

            ticker_id = self.canvas.create_text(
                overall_current_pos_x, center_y,
                text=f"{ticker_display}",
                font=self.custom_font,
                fill=TEXT_COLOR_NORMAL,
                anchor="w",
                tags=f"ticker_name_{ticker_display}_0"
            )
            overall_current_pos_x += self._measure_text_width(f"{ticker_display}") + SPACE_AFTER_TICKER_NAME

            value_id = self.canvas.create_text(
                overall_current_pos_x, center_y,
                text=f" {data['value']}",
                font=self.custom_font,
                fill=TEXT_COLOR_NORMAL,
                anchor="w",
                tags=f"ticker_value_{ticker_display}_0"
            )
            overall_current_pos_x += self._measure_text_width(f" {data['value']}") + SPACE_AFTER_VALUE

            change_id = self.canvas.create_text(
                overall_current_pos_x, center_y,
                text=f" {data['change']}",
                font=self.custom_font,
                fill=data['color'],
                anchor="w",
                tags=f"ticker_change_{ticker_display}_0"
            )
            overall_current_pos_x += self._measure_text_width(f" {data['change']}") + SPACE_AFTER_CHANGE

            separator_id = None
            if i < len(DISPLAY_TICKERS) - 1:
                separator_id = self.canvas.create_line(
                    overall_current_pos_x, 15, overall_current_pos_x, TICKER_HEIGHT - 15,
                    fill=SEPARATOR_COLOR,
                    width=1,
                    tags=f"ticker_separator_{ticker_display}_0"
                )
                overall_current_pos_x += SEPARATOR_AND_GAP_WIDTH

            overall_current_pos_x += INTER_ITEM_PADDING

            block_width_consumed = overall_current_pos_x - block_start_x

            self.ticker_blocks.append({
                "display_name": ticker_display,
                "ticker_id": ticker_id,
                "value_id": value_id,
                "change_id": change_id,
                "separator_id": separator_id,
                "width": block_width_consumed
            })

        self.single_set_width = overall_current_pos_x

        offset_x = self.single_set_width

        for block_data_original in self.ticker_blocks[:len(DISPLAY_TICKERS)]:
            coords_ticker = self.canvas.coords(block_data_original["ticker_id"])
            coords_value = self.canvas.coords(block_data_original["value_id"])
            coords_change = self.canvas.coords(block_data_original["change_id"])

            new_ticker_id = self.canvas.create_text(
                coords_ticker[0] + offset_x, coords_ticker[1],
                text=self.canvas.itemcget(block_data_original["ticker_id"], 'text'),
                font=self.custom_font,
                fill=self.canvas.itemcget(block_data_original["ticker_id"], 'fill'),
                anchor="w",
                tags=f"ticker_name_{block_data_original['display_name']}_1"
            )

            new_value_id = self.canvas.create_text(
                coords_value[0] + offset_x, coords_value[1],
                text=self.canvas.itemcget(block_data_original["value_id"], 'text'),
                font=self.custom_font,
                fill=self.canvas.itemcget(block_data_original["value_id"], 'fill'),
                anchor="w",
                tags=f"ticker_value_{block_data_original['display_name']}_1"
            )

            new_change_id = self.canvas.create_text(
                coords_change[0] + offset_x, coords_change[1],
                text=self.canvas.itemcget(block_data_original["change_id"], 'text'),
                font=self.custom_font,
                fill=self.canvas.itemcget(block_data_original["change_id"], 'fill'),
                anchor="w",
                tags=f"ticker_change_{block_data_original['display_name']}_1"
            )

            new_separator_id = None
            if block_data_original["separator_id"]:
                coords_separator = self.canvas.coords(block_data_original["separator_id"])
                new_separator_id = self.canvas.create_line(
                    coords_separator[0] + offset_x, coords_separator[1],
                    coords_separator[2] + offset_x, coords_separator[3],
                    fill=self.canvas.itemcget(block_data_original["separator_id"], 'fill'),
                    width=self.canvas.itemcget(block_data_original["separator_id"], 'width'),
                    tags=f"ticker_separator_{block_data_original['display_name']}_1"
                )

            self.ticker_blocks.append({
                "display_name": block_data_original["display_name"],
                "ticker_id": new_ticker_id,
                "value_id": new_value_id,
                "change_id": new_change_id,
                "separator_id": new_separator_id,
                "width": block_data_original["width"]
            })

        # Removido o posicionamento inicial para que o ticker comece do lado esquerdo
        # self.canvas.move("all", self.master.winfo_width(), 0)

    def scroll_ticker(self):
        # Move todos os itens para a direita (SCROLL_SPEED é positivo)
        self.canvas.move("all", SCROLL_SPEED, 0)

        for block in self.ticker_blocks:
            bbox = self.canvas.bbox(block["ticker_id"])

            # Verifica se o bloco saiu completamente da tela pelo lado direito
            if bbox and bbox[0] > self.master.winfo_width():
                # Move o bloco para o lado esquerdo, antes do início da fila de rolagem
                move_amount = -(self.single_set_width * 2)
                self.canvas.move(block["ticker_id"], move_amount, 0)
                self.canvas.move(block["value_id"], move_amount, 0)
                self.canvas.move(block["change_id"], move_amount, 0)
                if block["separator_id"]:
                    self.canvas.move(block["separator_id"], move_amount, 0)

        self.master.after(10, self.scroll_ticker)

    def update_ticker_display(self):
        for block in self.ticker_blocks:
            ticker_display_name = block["display_name"]
            data = stock_data.get(ticker_display_name, {"value": "---", "change": "---", "color": "white"})

            self.canvas.itemconfigure(block["value_id"], text=f" {data['value']}")
            self.canvas.itemconfigure(block["change_id"], text=f" {data['change']}", fill=data['color'])

if __name__ == "__main__":
    root = tk.Tk()
    app = TickerApp(root)
    root.mainloop()
