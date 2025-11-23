import pygame
import random
from clasesAvatarsRooks import Avatars, Rooks 

class Torre:
    """Representa una torre colocada en el tablero"""
    
    # Mapeo de 'tipo' a nombre de archivo (usado para cargar la imagen de la torre)
    TORRE_IMAGEN_MAP = {
        "T1": "Torre_arena",
        "T2": "Torre_roca",
        "T3": "Torre_fuego",
        "T4": "Torre_agua"
    }
    
    def __init__(self, tipo, fila, columna, datosTorre, gridConfig, torre_imagenes=None):

        self.tipo = tipo
        self.fila = fila
        self.columna = columna
        
        self.vidaMax = datosTorre["vida"]
        self.vidaActual = datosTorre["vida"]
        self.daño = datosTorre["daño"]
        self.valor = datosTorre["valor"]
        self.duracionAtaque = random.randint(
            datosTorre.get("duracion_ataque_min", 1),
            datosTorre.get("duracion_ataque_max", 5)
        )
        
        self.viva = True
        self.tiempoAtaque = 0
        self.proyectiles = []
        self.rangoAtaque = 1 

        # Cargar imagen de la torre
        self.imagen = None
        nombre_base = self.TORRE_IMAGEN_MAP.get(self.tipo)
        if nombre_base and torre_imagenes:
            self.imagen = torre_imagenes.get(nombre_base)
            if self.imagen:
                # MODIFICACIÓN AQUÍ: Aumentar el tamaño de la torre
                radio_visual = 90
                self.imagen = pygame.transform.scale(self.imagen, (radio_visual, radio_visual))

        self.calcularPosicion(gridConfig)

    def calcularPosicion(self, gridConfig):
        """Calcula la posición visual central en la casilla"""
        gridX = gridConfig["gridX"]
        gridY = gridConfig["gridY"]
        anchoCasilla = gridConfig["anchoCasilla"]
        altoCasilla = gridConfig["altoCasilla"]
        
        self.x = gridX + self.columna * anchoCasilla + anchoCasilla / 2
        self.y = gridY + self.fila * altoCasilla + altoCasilla / 2

    def dentroRango(self, avatar):
        """Verifica si un avatar está dentro del rango de ataque (cualquier casilla inferior en la misma columna)"""
        # El avatar debe estar en la misma columna Y en una fila MAYOR (más abajo) que la torre.
        return avatar.columna == self.columna and avatar.fila > self.fila
            
    def recibirDaño(self, daño):
        """Reduce la vida y verifica si muere"""
        self.vidaActual -= daño
        if self.vidaActual <= 0:
            self.vidaActual = 0
            self.viva = False

    def dibujarBarraVida(self, pantalla, radio):
        """Dibuja la barra de vida sobre la torre"""
        if self.vidaActual == self.vidaMax:
            return

        anchoBarra = radio * 2
        altoBarra = 5
        
        # Fondo rojo
        barraFondo = pygame.Rect(self.x - anchoBarra / 2, self.y - radio - 10, anchoBarra, altoBarra)
        pygame.draw.rect(pantalla, (255, 0, 0), barraFondo)

        # Vida verde
        anchoVida = (self.vidaActual / self.vidaMax) * anchoBarra
        barraVida = pygame.Rect(self.x - anchoBarra / 2, self.y - radio - 10, anchoVida, altoBarra)
        pygame.draw.rect(pantalla, (0, 255, 0), barraVida)

    def dibujar(self, pantalla):
        """Dibuja la torre y sus proyectiles, usando imagen si existe"""
        if not self.viva:
            return
        
        radio = 30 # Este es el radio para el dibujo de los círculos (si no hay imagen), no para la imagen.
        
        if self.imagen:
            rect = self.imagen.get_rect(center=(int(self.x), int(self.y)))
            pantalla.blit(self.imagen, rect)
            
            # Pasar el radio visual que se usó para escalar la imagen
            self.dibujarBarraVida(pantalla, 30) # Asumiendo que 30 es el radio efectivo para la barra de vida
        else:
            # Dibujar el círculo por defecto
            colores = {
                "T1": (194, 178, 128), "T2": (128, 128, 128),  
                "T3": (255, 100, 0), "T4": (0, 100, 255)    
            }
            color = colores.get(self.tipo, (255, 255, 255))
            pygame.draw.circle(pantalla, color, (int(self.x), int(self.y)), radio)
            pygame.draw.circle(pantalla, (0, 0, 0), (int(self.x), int(self.y)), radio, 3)
            self.dibujarBarraVida(pantalla, radio)
        
        # Dibujar proyectiles
        for proyectil in self.proyectiles:
            proyectil.dibujar(pantalla)
