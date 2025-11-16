import pygame
import random

class Moneda:
    def __init__(self, x, y, valor=10):
        self.x = x
        self.y = y
        self.valor = valor
        self.clickeada = False
        self.radio = 15  # Radio del círculo de la moneda

    def verificarClick(self, pos_mouse, tamañoCelda, offsetX, offsetY):
        """Verifica si la moneda fue clickeada"""
        mouseX, mouseY = pos_mouse
        posX = offsetX + (self.x * tamañoCelda)
        posY = offsetY + (self.y * tamañoCelda)
        
        distancia = ((mouseX - posX) ** 2 + (mouseY - posY) ** 2) ** 0.5
        if distancia <= self.radio:
            self.clickeada = True
            return True
        return False

    def dibujar(self, pantalla, tamañoCelda, offsetX, offsetY):
        """Dibuja la moneda en la pantalla"""
        if self.clickeada:
            return
            
        posX = offsetX + (self.x * tamañoCelda)
        posY = offsetY + (self.y * tamañoCelda)
        
        # Dibujar círculo dorado
        pygame.draw.circle(pantalla, (255, 215, 0), (posX, posY), self.radio)
        
        # Borde más oscuro
        pygame.draw.circle(pantalla, (218, 165, 32), (posX, posY), self.radio, 2)

def generarMonedas(cantidad=3, gridFilas=9, gridColumnas=5):
    """Genera una lista de monedas en posiciones aleatorias dentro del grid de juego
    
    El total de monedas generadas no excederá 100 puntos de valor
    Denominaciones posibles: 25, 50, 100 puntos
    """
    monedas = []
    valores_disponibles = [25, 50, 100]
    total_valor = 0
    limite_valor = 100
    
    for _ in range(cantidad):
        # Generar dentro del grid (0 a columnas-1, 0 a filas-1)
        x = random.uniform(0.5, gridColumnas - 0.5)
        y = random.uniform(0.5, gridFilas - 0.5)
        
        # Seleccionar valor que no exceda el límite
        valor = random.choice(valores_disponibles)
        
        # Si agregar esta moneda excedería el límite, ajustar el valor
        if total_valor + valor > limite_valor:
            # Calcular cuánto valor queda disponible
            valor_restante = limite_valor - total_valor
            if valor_restante >= 25:
                valor = min(valor, valor_restante)
            else:
                continue  # No agregar más monedas si no queda valor suficiente
        
        total_valor += valor
        monedas.append(Moneda(x, y, valor))
        
        # Si alcanzamos el límite, dejar de generar monedas
        if total_valor >= limite_valor:
            break
    
    return monedas