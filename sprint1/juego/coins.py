import pygame
import random

class Coin:
    def __init__(self, x, y, valor):
        """
        Inicializa una moneda clickeable
        
        Args:
            x: Posición x en la intersección (0-6 para 7 columnas)
            y: Posición y en la intersección (0-8 para 9 filas)
            valor: Valor de la moneda (25, 50 o 100)
        """
        self.gridX = x
        self.gridY = y
        self.valor = valor
        self.radio = 18
        self.color = (255, 215, 0)  # Amarillo dorado
        self.bordeColor = (218, 165, 32)  # Borde dorado oscuro
        self.textoColor = (139, 69, 19)  # Marrón para el texto
        self.clickeada = False
        self.sombraColor = (200, 150, 0, 128)  # Sombra semitransparente
        
    def dibujar(self, pantalla, tamañoCelda, offsetX=0, offsetY=0):
        """
        Dibuja la moneda en la pantalla (en las intersecciones entre casillas)
        
        Args:
            pantalla: Superficie de pygame donde dibujar
            tamañoCelda: Tamaño de cada celda de la cuadrícula
            offsetX: Desplazamiento en X para centrar la cuadrícula
            offsetY: Desplazamiento en Y para centrar la cuadrícula
        """
        if not self.clickeada:
            # Calcular posición en las intersecciones (bordes de las celdas)
            centroX = offsetX + (self.gridX * tamañoCelda)
            centroY = offsetY + (self.gridY * tamañoCelda)
            
            # Dibujar sombra sutil
            pygame.draw.circle(pantalla, self.bordeColor, (centroX + 2, centroY + 2), self.radio + 2)
            
            # Dibujar borde exterior
            pygame.draw.circle(pantalla, self.bordeColor, (centroX, centroY), self.radio + 2)
            # Dibujar moneda principal
            pygame.draw.circle(pantalla, self.color, (centroX, centroY), self.radio)
            
            # Dibujar brillo interno (círculo más claro en la parte superior)
            brilloColor = (255, 235, 100)
            pygame.draw.circle(pantalla, brilloColor, (centroX - 3, centroY - 3), self.radio // 3)
            
            # Dibujar valor en el centro
            fuente = pygame.font.Font(None, 22)
            texto = fuente.render(str(self.valor), True, self.textoColor)
            textoRect = texto.get_rect(center=(centroX, centroY))
            pantalla.blit(texto, textoRect)
    
    def verificarClick(self, posicionMouse, tamañoCelda, offsetX=0, offsetY=0):
        """
        Verifica si el mouse hizo click en la moneda
        
        Args:
            posicionMouse: Tupla (x, y) de la posición del mouse
            tamañoCelda: Tamaño de cada celda de la cuadrícula
            offsetX: Desplazamiento en X para centrar la cuadrícula
            offsetY: Desplazamiento en Y para centrar la cuadrícula
            
        Returns:
            True si se hizo click en la moneda, False en caso contrario
        """
        if self.clickeada:
            return False
            
        # Calcular posición en las intersecciones
        centroX = offsetX + (self.gridX * tamañoCelda)
        centroY = offsetY + (self.gridY * tamañoCelda)
        
        # Calcular distancia entre el mouse y el centro de la moneda
        distancia = ((posicionMouse[0] - centroX) ** 2 + (posicionMouse[1] - centroY) ** 2) ** 0.5
        
        if distancia <= self.radio:
            self.clickeada = True
            return True
        return False


def generarMonedas():
    """
    Genera una combinación aleatoria de monedas que sumen 100 puntos
    Las monedas se colocan en las intersecciones entre casillas (sin incluir bordes)
    
    Returns:
        Lista de objetos Coin
    """
    # Definir todas las combinaciones posibles que suman 100
    combinaciones = [
        [100],                  # 1 moneda de 100
        [50, 50],              # 2 monedas de 50
        [50, 25, 25],          # 1 de 50 y 2 de 25
        [25, 25, 25, 25]       # 4 monedas de 25
    ]
    
    # Elegir una combinación aleatoria
    combinacionElegida = random.choice(combinaciones)
    
    # Generar todas las posiciones posibles en las intersecciones internas
    # Para una cuadrícula de 7x9, hay 6x8 intersecciones internas (sin bordes)
    todasIntersecciones = [(x, y) for x in range(1, 7) for y in range(1, 9)]
    
    # Seleccionar posiciones aleatorias para las monedas
    posicionesElegidas = random.sample(todasIntersecciones, len(combinacionElegida))
    
    # Crear las monedas
    monedas = []
    for i, valor in enumerate(combinacionElegida):
        x, y = posicionesElegidas[i]
        monedas.append(Coin(x, y, valor))
    
    return monedas