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

def generarMonedas(cantidad=3):
    """Genera una lista de monedas en posiciones aleatorias del tablero"""
    monedas = []
    for _ in range(cantidad):
        x = random.uniform(0.5, 4.5)  # Posiciones dentro del tablero 5x9
        y = random.uniform(0.5, 8.5)  # Evita bordes
        valor = random.choice([5, 10, 15])  # Valores posibles
        monedas.append(Moneda(x, y, valor))
    return monedas