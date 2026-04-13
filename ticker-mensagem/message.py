from PySide6.QtWidgets import (
    QApplication, QWidget
)
from PySide6.QtGui import (
    QPainter, QColor, QFont, QFontMetricsF, QKeyEvent, QFontDatabase, QMovie
)
from PySide6.QtCore import (
    Qt, QTimer, QRectF, QPoint, QSize
)
import sys
import math

# --- CONSTANTES GLOBAIS ---
FONT_SIZE = 70 
BACKGROUND_COLOR = QColor("#000000")
TEXT_COLOR = QColor("white")
TICKER_HEIGHT = 144 
FONT_FAMILY = "Arial" 

# CONFIGURAÇÃO DO GIF
GIF_FILENAME = "corinthians.gif" #colocar o nome do arquivo do GIF aqui (deve estar na mesma pasta do script ou fornecer o caminho completo)

# 🎯 CONTROLE DE POSIÇÃO: Altere aqui para definir onde o GIF aparece
GIF_AT_START = True  # Coloca o GIF antes da mensagem
GIF_AT_END = True   # Coloca o GIF depois da mensagem

class TickerWidget(QWidget):
    def __init__(self, parent=None, width=None, height=TICKER_HEIGHT):
        super().__init__(parent)
        
        self.repetitions = 0
        self.segment_width = 0
        self.gif_scaled_width = 0

        self.setWindowTitle("Ticker com Qt")
        
        screen_width = QApplication.primaryScreen().size().width()
        final_width = width if width is not None else screen_width
        
        self.setFixedSize(final_width, height)
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        self.setAutoFillBackground(True)
        
        p = self.palette(); p.setColor(self.backgroundRole(), BACKGROUND_COLOR); self.setPalette(p)
        
        # --- Configuração da Fonte ---
        self.font = self.font()
        self.font.setFamily(FONT_FAMILY); self.font.setPointSize(FONT_SIZE); self.font.setBold(True) 
        self.setFont(self.font)

        # --- CONFIGURAÇÃO DO GIF ---
        self.movie = QMovie(GIF_FILENAME)
        if self.movie.isValid():
            self.movie.start()
            self.movie.frameChanged.connect(self.update)
            self.gif_size = QSize(self.movie.frameRect().width(), self.movie.frameRect().height())
            self.gif_scaled_height = height * 0.8 
            self.gif_scaled_width = int(self.gif_size.width() * (self.gif_scaled_height / self.gif_size.height()))
        else:
            print(f"Erro ao carregar o arquivo GIF: {GIF_FILENAME}. Usando texto de fallback.")
            self.gif_scaled_width = 0 
        
        # --- Configuração do Ticker e Medição de Largura (CORRIGIDA) ---
        self.text_segment = "Mensagem Exibida no Ticker - aceita emojis e caracteres especiais! "
        self.spacing = "                "
        
        metrics = QFontMetricsF(self.font)
        text_part_width = metrics.horizontalAdvance(self.text_segment)
        spacing_width = metrics.horizontalAdvance(self.spacing)

        # Determina quantos GIFs serão desenhados por segmento
        gif_width = self.gif_scaled_width if self.movie.isValid() else 0
        gif_count = 0
        if GIF_AT_START:
            gif_count += 1
        if GIF_AT_END:
            gif_count += 1
            
        # O width do segmento é a soma de todos os componentes
        self.segment_width = (
            text_part_width + 
            (gif_count * gif_width) + 
            spacing_width
        )

        self.repetitions = math.ceil(final_width / self.segment_width) + 2
        
        self.scroll_x = -self.segment_width 
        self.scroll_speed = 2 
        
        self.timer = QTimer(self); self.timer.timeout.connect(self.scroll_message); self.timer.start(10)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.close() 
        else:
            super().keyPressEvent(event)

    def paintEvent(self, event):
        if self.repetitions == 0:
            return 

        painter = QPainter(self)
        painter.setFont(self.font)
        painter.setPen(TEXT_COLOR) 
        
        text_y_center = self.height() / 2
        gif_y = (self.height() - self.gif_scaled_height) / 2 if self.gif_scaled_width > 0 else 0
        metrics = QFontMetricsF(self.font)
        baseline_y = int(text_y_center + metrics.ascent() / 2)
        
        gif_width = self.gif_scaled_width if self.movie.isValid() else 0

        # Desenha a mensagem longa repetida
        for i in range(self.repetitions + 1): 
            
            base_x = self.scroll_x + (i * self.segment_width)
            current_x = base_x
            
            # 1. Desenha o GIF NO INÍCIO (Se GIF_AT_START for True)
            if GIF_AT_START and self.movie.isValid():
                current_frame = self.movie.currentPixmap()
                
                painter.drawPixmap(
                    int(current_x), 
                    int(gif_y), 
                    int(self.gif_scaled_width), 
                    int(self.gif_scaled_height), 
                    current_frame
                )
                current_x += gif_width 
            
            # 2. Desenha o TEXTO
            text_width = metrics.horizontalAdvance(self.text_segment)
            painter.drawText(int(current_x), baseline_y, self.text_segment)
            current_x += text_width 
            
            # 3. Desenha o GIF NO FINAL (Se GIF_AT_END for True)
            if GIF_AT_END and self.movie.isValid():
                current_frame = self.movie.currentPixmap()
                
                painter.drawPixmap(
                    int(current_x), 
                    int(gif_y), 
                    int(self.gif_scaled_width), 
                    int(self.gif_scaled_height), 
                    current_frame
                )
                current_x += gif_width 

    def scroll_message(self):
        self.scroll_x += self.scroll_speed

        if self.scroll_x >= 0:
            self.scroll_x -= self.segment_width 
        
        self.update()

# --- Bloco de Execução ---
if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    
    APP_WIDTH = 8184 
    
    ticker = TickerWidget(width=APP_WIDTH, height=TICKER_HEIGHT)
    
    ticker.move(QPoint(0, 0))
    
    ticker.show()
    
    sys.exit(app.exec())