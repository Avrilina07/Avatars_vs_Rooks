
import pygame
import random
from clasesAvatarsRooks import Avatars, Rooks 


class Proyectil:
    """Representa un proyectil disparado por un avatar o torre"""
    
    def __init__(self, x, y, daño, tipo, esAvatar=True, imagenes=None):
        self.x = x
        self.y = y
        self.daño = daño
        self.tipo = tipo
        self.activo = True
        self.esAvatar = esAvatar
        
        self.velocidad = -5 if esAvatar else 5
        self.radio = 5 
        
        # Configuración de imagen (solo para proyectiles de torre)
        self.imagen = None
        if not self.esAvatar and imagenes:
            # ✅ CORRECCIÓN FINAL: Se asume que la clave de la imagen es el TIPO de la torre ("T1", "T2", etc.)
            self.imagen = imagenes.get(self.tipo) 
            if self.imagen:
                self.imagen = pygame.transform.scale(self.imagen, (10, 10)) 

    def actualizar(self):
        """Mueve el proyectil y verifica límites de pantalla"""
        if self.activo:
            self.y += self.velocidad
            
            # Arreglo de límite de pantalla
            if self.y < 0 or self.y > 900: 
                self.activo = False
        
        # 🗑️ Se eliminó el bloque de código 'actualizar' duplicado que causó el error de indentación anterior.
    
    def dibujar(self, pantalla):
        """Dibuja el proyectil, usando imagen si existe, o círculo por defecto"""
        if not self.activo:
            return
        
        if self.imagen:
            # Dibujar imagen centrada
            rect = self.imagen.get_rect(center=(int(self.x), int(self.y)))
            pantalla.blit(self.imagen, rect)
        else:
            # Dibujo por defecto (proyectiles de avatars y torres sin imagen)
            if self.esAvatar:
                colores = {
                    "flechador": (255, 215, 0), "escudero": (100, 149, 237),
                    "lenador": (139, 69, 19), "canibal": (220, 20, 60)
                }
            else: # Colores por defecto para proyectiles de torre si no hay imagen
                 colores = {
                    "T1": (194, 178, 128), "T2": (128, 128, 128),  
                    "T3": (255, 100, 0), "T4": (0, 100, 255)    
                }

            color = colores.get(self.tipo, (255, 255, 255))
            pygame.draw.circle(pantalla, color, (int(self.x), int(self.y)), self.radio)
            pygame.draw.circle(pantalla, (0, 0, 0), (int(self.x), int(self.y)), self.radio, 1)
            
    def colisionaConTorre(self, torre):
        """Verifica si el proyectil colisiona con una torre (solo si es de Avatar)"""
        if self.esAvatar and torre.viva:
            distancia = ((self.x - torre.x) ** 2 + (self.y - torre.y) ** 2) ** 0.5
            return distancia < self.radio + 25 
        return False

    def colisionaConAvatar(self, avatar):
        """Verifica si el proyectil colisiona con un avatar (solo si es de Torre)"""
        if not self.esAvatar and avatar.vivo and not avatar.apareciendo:
            distancia = ((self.x - avatar.x) ** 2 + (self.y - avatar.y) ** 2) ** 0.5
            return distancia < self.radio + 20
        return False
