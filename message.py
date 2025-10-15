import tkinter as tk
import tkinter.font

BACKGROUND_COLOR = "#1a1a1a"
TEXT_COLOR_NORMAL = "white"

FONT_SIZE = 70
TICKER_HEIGHT = 144

root = None
app = None

class TickerApp:
    def __init__(self, master):
        global root, app
        root = master
        app = self

        self.master = master
        master.title("Mensagem de Ticker")

        master.geometry(f"8192x{TICKER_HEIGHT}+0+0")
        master.overrideredirect(True)
        master.attributes('-topmost', True)
        master.configure(bg=BACKGROUND_COLOR)

        self.canvas = tk.Canvas(master, bg=BACKGROUND_COLOR, height=TICKER_HEIGHT, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.custom_font = tk.font.Font(family="Arial", size=FONT_SIZE, weight="bold")

        self.message = "Czarnikow, uma gigante global no setor de comercialização de açúcar."
        self.text_id = None
        self.text_width = 0

        self.create_scrolling_message()
        self.scroll_message()

    def create_scrolling_message(self):
        # Mede a largura da mensagem
        self.text_width = self.custom_font.measure(self.message)

        # Cria a mensagem no canvas, iniciando-a fora da tela, à esquerda
        self.text_id = self.canvas.create_text(
            -self.text_width, TICKER_HEIGHT / 2,  # Posição inicial fora da tela à esquerda
            text=self.message,
            font=self.custom_font,
            fill=TEXT_COLOR_NORMAL,
            anchor="w"
        )
        
    def scroll_message(self):
        # Define a velocidade de rolagem (positivo para a direita)
        scroll_speed = 15 

        # Obtém o bounding box do texto
        bbox = self.canvas.bbox(self.text_id)

        # Move o texto na tela
        self.canvas.move(self.text_id, scroll_speed, 0)
        
        # Se o texto saiu completamente da tela pela direita, reseta a posição para a esquerda
        if bbox and bbox[0] > self.master.winfo_width():
            self.canvas.coords(self.text_id, -self.text_width, TICKER_HEIGHT / 2)

        # Chama a si mesmo novamente após um pequeno atraso para criar a animação
        self.master.after(10, self.scroll_message)

if __name__ == "__main__":
    root = tk.Tk()
    app = TickerApp(root)
    root.mainloop()