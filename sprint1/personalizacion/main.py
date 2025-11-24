# main.py

import pygame
import sys
from pantallas import PantallaPersonalizacion

try:
    from ..Sockets.powerServer import startPowerServer
except Exception:
    try:
        from sprint1.Sockets.powerServer import startPowerServer
    except Exception:
        startPowerServer = None


def main():     
    #Función principal que inicia la aplicación
    # Start the power listener early so the Pico can trigger login
    try:
        from ..Sockets.server import startServer
    except Exception:
        try:
            from sprint1.Sockets.server import startServer
        except Exception:
            startServer = None

    try:
        if startServer:
            startServer()
    except Exception as e:
        print('No se pudo iniciar server:', e)

    pygame.init()
    
    app = PantallaPersonalizacion()
    app.ejecutar()
    
    sys.exit()


if __name__ == "__main__":
    main()