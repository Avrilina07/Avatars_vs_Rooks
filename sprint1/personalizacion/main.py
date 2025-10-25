# main.py

import pygame
import sys
from pantallas import PantallaPersonalizacion


def main():     
    #Función principal que inicia la aplicación
    pygame.init()
    
    app = PantallaPersonalizacion()
    app.ejecutar()
    
    sys.exit()


if __name__ == "__main__":
    main()