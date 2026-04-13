import os
import sys
import math
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QColor, QFont, QFontMetricsF, QKeyEvent, QMovie
from PySide6.QtCore import Qt, QTimer, QRectF, QPoint, QSize

# --- CONSTANTES GLOBAIS ---
FONT_SIZE = 70 
BACKGROUND_COLOR = QColor("#000000")
TEXT_COLOR = QColor("#FFFFFF")
TICKER_HEIGHT = 144 
FONT_FAMILY = "Arial" 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

GIF_FILENAME = os.path.join(BASE_DIR, "assets/trofeu.gif")
MESSAGE_TEXT = "Mensagem exibida no ticker "
GIF_AT_START = True  
GIF_AT_END = True   

class TickerWidget(QWidget):
    def __init__(self, parent=None, width=None, height=TICKER_HEIGHT):
        super().__init__(parent)
        
        # Verificar se o arquivo existe para te ajudar no debug
        if not os.path.exists(GIF_FILENAME):
            print(f"ALERTA: O arquivo {GIF_FILENAME} NÃO foi encontrado na pasta!")

        self.repetitions = 0
        self.segment_width = 0
        self.gif_scaled_width = 0

        self.setWindowTitle("Ticker com Qt")
        screen_width = QApplication.primaryScreen().size().width()
        final_width = width if width is not None else screen_width
        self.setFixedSize(final_width, height)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAutoFillBackground(True)
        
        p = self.palette()
        p.setColor(self.backgroundRole(), BACKGROUND_COLOR)
        self.setPalette(p)
        
        self.font = self.font()
        self.font.setFamily(FONT_FAMILY)
        self.font.setPointSize(FONT_SIZE)
        self.font.setBold(True) 
        self.setFont(self.font)

        # --- CONFIGURAÇÃO DO GIF ---
        self.movie = QMovie(GIF_FILENAME)
        if self.movie.isValid():
            self.movie.start()
            self.movie.frameChanged.connect(self.update)
            
            # Pegar o tamanho real do frame do GIF
            self.movie.jumpToFrame(0)
            rect = self.movie.currentPixmap().rect()
            
            self.gif_scaled_height = height * 0.8 
            self.gif_scaled_width = int(rect.width() * (self.gif_scaled_height / rect.height()))
        else:
            print(f"Erro ao carregar o arquivo GIF: {GIF_FILENAME}. Verifique se é um GIF válido.")
            self.gif_scaled_width = 0 
        
        self.text_segment = MESSAGE_TEXT
        self.spacing = "          "
        
        metrics = QFontMetricsF(self.font)
        text_part_width = metrics.horizontalAdvance(self.text_segment)
        spacing_width = metrics.horizontalAdvance(self.spacing)

        gif_width = self.gif_scaled_width
        gif_count = (1 if GIF_AT_START else 0) + (1 if GIF_AT_END else 0)
            
        self.segment_width = text_part_width + (gif_count * gif_width) + spacing_width
        self.repetitions = math.ceil(final_width / self.segment_width) + 2
        
        self.scroll_x = -self.segment_width 
        self.scroll_speed = 2 
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.scroll_message)
        self.timer.start(10)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.close() 

    def paintEvent(self, event):
        if self.repetitions == 0: return 

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(self.font)
        painter.setPen(TEXT_COLOR) 
        
        metrics = QFontMetricsF(self.font)
        baseline_y = int((self.height() / 2) + (metrics.ascent() / 2))
        gif_y = (self.height() - self.gif_scaled_height) / 2
        
        for i in range(self.repetitions + 1): 
            current_x = self.scroll_x + (i * self.segment_width)
            
            # 1. GIF Início
            if GIF_AT_START and self.movie.isValid():
                pixmap = self.movie.currentPixmap()
                if not pixmap.isNull():
                    painter.drawPixmap(int(current_x), int(gif_y), int(self.gif_scaled_width), int(self.gif_scaled_height), pixmap)
                current_x += self.gif_scaled_width
            
            # 2. Texto
            painter.drawText(int(current_x), baseline_y, self.text_segment)
            current_x += metrics.horizontalAdvance(self.text_segment)
            
            # 3. GIF Fim
            if GIF_AT_END and self.movie.isValid():
                pixmap = self.movie.currentPixmap()
                if not pixmap.isNull():
                    painter.drawPixmap(int(current_x), int(gif_y), int(self.gif_scaled_width), int(self.gif_scaled_height), pixmap)

    def scroll_message(self):
        self.scroll_x += self.scroll_speed
        if self.scroll_x >= 0:
            self.scroll_x -= self.segment_width 
        self.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ticker = TickerWidget(width=8184)
    ticker.move(0, 0)
    ticker.show()
    sys.exit(app.exec())