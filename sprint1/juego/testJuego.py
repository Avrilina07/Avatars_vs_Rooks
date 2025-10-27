# test.py

import pygame
import sys
import os

# Configurar imports
carpeta_actual = os.path.dirname(os.path.abspath(__file__))
carpeta_sprint1 = os.path.dirname(carpeta_actual)
carpeta_personalizacion = os.path.join(carpeta_sprint1, 'personalizacion')
sys.path.insert(0, carpeta_personalizacion)

from fondo import ColoresFondoDisponibles
from temas import ConfiguracionTemas
from constantes import PANTALLA_COMPLETA
from pantallaJuego import PantallaJuego
from botones import Boton

# Inicializar pygame
pygame.init()

# Crear ventana
if PANTALLA_COMPLETA:
    pantalla = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
else:
    pantalla = pygame.display.set_mode((1200, 700))

pygame.display.set_caption("Avatars VS Rooks - Test")

# Configuración
colorFondo = ColoresFondoDisponibles.ROJO_MUY_OSCURO_3
tema = ConfiguracionTemas.CLARO

# ⚙️ AJUSTAR: Cambiar dificultad para probar
dificultad = "Facil"  # "Facil", "Intermedio", "Dificil"

# Crear instancia del juego con dificultad
juego = PantallaJuego(pantalla, colorFondo, tema, dificultad)
juego.ejecutar()

pygame.quit()