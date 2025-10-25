# test.py

import pygame
import sys
import os

# Configurar imports para acceder a personalizacion
carpeta_actual = os.path.dirname(os.path.abspath(__file__))  # /juego
carpeta_sprint1 = os.path.dirname(carpeta_actual)  # /sprint1
carpeta_personalizacion = os.path.join(carpeta_sprint1, 'personalizacion')
sys.path.insert(0, carpeta_personalizacion)

from fondo import ColoresFondoDisponibles
from temas import ConfiguracionTemas
from constantes import PANTALLA_COMPLETA
from pantallaJuego import PantallaJuego  # Import local desde la misma carpeta

# Inicializar pygame
pygame.init()

# Crear ventana en pantalla completa
if PANTALLA_COMPLETA:
    pantalla = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
else:
    pantalla = pygame.display.set_mode((1200, 700))

# Crear instancia del juego
colorFondo = ColoresFondoDisponibles.ROJO_MUY_OSCURO_3
tema = ConfiguracionTemas.CLARO

juego = PantallaJuego(pantalla, colorFondo, tema)
juego.ejecutar()

pygame.quit()