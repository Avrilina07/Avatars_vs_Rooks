import pygame
import sys
import os

# Configurar rutas para los imports
carpeta_actual = os.path.dirname(os.path.abspath(__file__))
carpeta_sprint1 = os.path.dirname(carpeta_actual)

# Agregar carpeta de personalización al path
carpeta_personalizacion = os.path.join(carpeta_sprint1, 'personalizacion')
sys.path.insert(0, carpeta_personalizacion)

# Agregar carpeta de salón de la fama al path
carpeta_salon_fama = os.path.join(carpeta_sprint1, 'salonDeFama')
sys.path.insert(0, carpeta_salon_fama)

# Agregar carpeta sprint1 al path para encontrar el módulo juego
sys.path.insert(0, carpeta_sprint1)

from personalizacion.fondo import ColoresFondoDisponibles
from personalizacion.temas import ConfiguracionTemas
from personalizacion.constantes import PANTALLA_COMPLETA
from juego.pantallaJuego import PantallaJuego

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

# Cambiar dificultad para probar
dificultad = "Facil"  # "Facil", "Intermedio", "Dificil"

# Crear instancia del juego con dificultad
juego = PantallaJuego(pantalla, colorFondo, tema, dificultad)
juego.ejecutar()

pygame.quit()