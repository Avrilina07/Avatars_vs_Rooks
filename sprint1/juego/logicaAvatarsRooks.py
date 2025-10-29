# ---MANEJO DE TODA LA LÓGICA DE FUNCIONAMIENTO DE AVATARS Y TORRES---

import pygame
import random
from clasesAvatarsRooks import Avatars, Rooks


class Proyectil:
    """Representa un proyectil disparado por un avatar"""
    
    def __init__(self, x, y, daño, tipo):
        
        self.x = x
        self.y = y
        self.daño = daño
        self.tipo = tipo # tipo de avatar que lo disparó (para color)
        self.activo = True
        
        # Velocidad del proyectil (píxeles por frame)
        self.velocidad = -5  # Negativo = hacia arriba
        
        # Tamaño del proyectil
        self.radio = 5
    
    def actualizar(self):
        """Mueve el proyectil hacia arriba"""
        if self.activo:
            self.y += self.velocidad
            
            # ⚙️ AJUSTAR: Desactivar si sale de pantalla
            if self.y < 0:
                self.activo = False
    
    def dibujar(self, pantalla):
        """Dibuja el proyectil"""
        if not self.activo:
            return
        
        # ⚙️ AJUSTAR: Color del proyectil según tipo de avatar
        colores = {
            "flechador": (255, 215, 0),    # Dorado
            "escudero": (135, 206, 250),   # Azul claro
            "lenador": (210, 105, 30),     # Chocolate
            "canibal": (255, 69, 0)        # Rojo naranja
        }
        
        color = colores.get(self.tipo, (255, 255, 255))
        
        # Dibujar proyectil circular
        pygame.draw.circle(pantalla, color, (int(self.x), int(self.y)), self.radio)
        pygame.draw.circle(pantalla, (255, 255, 255), (int(self.x), int(self.y)), self.radio, 1)
    
    def colisionaConTorre(self, torre):
        """
        Verifica colisión con una torre
        
        Args:
            torre: objeto Torre
            
        Returns:
            bool: True si hay colisión
        """
        if not self.activo or not torre.viva:
            return False
        
        # ⚙️ AJUSTAR: Radio de colisión de torre
        radioTorre = 25
        
        # Distancia entre proyectil y torre
        distancia = ((self.x - torre.x)**2 + (self.y - torre.y)**2)**0.5
        
        return distancia < (self.radio + radioTorre)


