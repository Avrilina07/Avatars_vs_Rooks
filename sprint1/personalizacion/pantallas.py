# pantallas.py

import pygame
import sys
import os
from constantes import ANCHO_VENTANA, ALTO_VENTANA, FPS, PANTALLA_COMPLETA
from componentes import Boton, DropdownTema, Slider
from temas import ConfiguracionTemas
from fondo import ColoresFondoDisponibles
from spotify_api import SpotifyAPI
from pantalla_musica import PantallaMusica
from pantalla_interfaz import PantallaPersonalizacionInterfaz

carpeta_actual = os.path.dirname(os.path.abspath(__file__))  # personalizacion
carpeta_sprint1 = os.path.dirname(carpeta_actual)  # sprint1
carpeta_avatars = os.path.dirname(carpeta_sprint1)  # Avatars_vs_Rooks
carpeta_juego = os.path.join(carpeta_avatars, 'sprint1', 'juego')
sys.path.insert(0, carpeta_juego)


try:
    from pantallaDificultad import PantallaDificultad
    from pantallaJuego import PantallaJuego
    print("✅ Módulos del juego importados correctamente")
except ImportError as e:
    print(f"❌ Error al importar módulos del juego: {e}")
    print(f"Asegúrate de que pantallaDificultad.py está en: {carpeta_juego}")
    sys.exit(1)


class PantallaPersonalizacion:
    #Pantalla principal de personalización
    
    def __init__(self):
        # Configurar pantalla
        if PANTALLA_COMPLETA:
            self.pantalla = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            info = pygame.display.Info()
            self.ancho = info.current_w
            self.alto = info.current_h
        else:
            self.pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA), pygame.RESIZABLE)
            self.ancho = ANCHO_VENTANA
            self.alto = ALTO_VENTANA
        
        pygame.display.set_caption("Personalización")
        self.reloj = pygame.time.Clock()
        self.ejecutando = True
        
        # Inicializar API de Spotify para control de volumen
        self.spotify = SpotifyAPI()
        
        # Tema actual
        self.temaActual = ConfiguracionTemas.CLARO
        
        # Color de fondo personalizado (por defecto el rojo inicial)
        self.colorFondoPersonalizado = ColoresFondoDisponibles.ROJO_MUY_OSCURO_3
        
        # Fuentes
        self.fuenteTitulo = pygame.font.SysFont('Arial', 90, bold=True)
        self.fuenteTexto = pygame.font.SysFont('Arial', 24)
        
        # Crear componentes (se actualizarán en actualizarPosiciones)
        self.botonInterfaz = None
        self.botonCancion = None
        self.dropdownTema = None
        self.botonJuego = None
        self.sliderVolumen = None
        
        self.actualizarPosiciones()
    
    def cambiarVolumenSpotify(self, volumen):
        #Callback que se ejecuta cuando el slider cambia
        self.spotify.cambiarVolumen(volumen)
    
    def actualizarPosiciones(self):
        #Actualiza las posiciones de los componentes según el tamaño de la ventana

        # Calcular posiciones relativas al centro
        centroX = self.ancho // 2
        centroY = self.alto // 2
        
        # Botones más grandes (310x90 en vez de 280x80)
        self.botonInterfaz = Boton(centroX - 155, centroY - 150, 310, 90, "¡PERSONALIZA TÚ INTERFAZ!", 20)
        self.botonCancion = Boton(centroX - 155, centroY - 40, 310, 90, "¡ELIGE LA CANCIÓN!", 26)
        self.dropdownTema = DropdownTema(centroX - 155, centroY + 70, 310, 55)
        
        # Botón juego a la derecha
        self.botonJuego = Boton(centroX + 180, centroY - 40, 250, 90, "¡VAMOS AL JUEGO!", 25)
        
        # Aplicar colores del fondo personalizado a todos los botones
        for boton in [self.botonInterfaz, self.botonCancion, self.botonJuego]:
            boton.colorNormal = self.colorFondoPersonalizado.obtenerColorBoton()
            boton.colorHover = self.colorFondoPersonalizado.obtenerColorHoverBoton()
            boton.colorBorde = self.colorFondoPersonalizado.obtenerColorBorde()
            boton.colorTexto = self.colorFondoPersonalizado.obtenerColorTextoBoton()
        
        # Aplicar colores al dropdown
        self.dropdownTema.colorFondo = self.colorFondoPersonalizado.obtenerColorBoton()
        self.dropdownTema.colorHover = self.colorFondoPersonalizado.obtenerColorHoverBoton()
        self.dropdownTema.colorBorde = self.colorFondoPersonalizado.obtenerColorBorde()
        self.dropdownTema.colorTexto = self.colorFondoPersonalizado.obtenerColorTextoBoton()
        
        # Slider de volumen en esquina inferior izquierda con callback
        margen = 40
        self.sliderVolumen = Slider(margen, self.alto - 80, 300, 25, 50, callback=self.cambiarVolumenSpotify)
        
        # Aplicar colores al slider según el fondo
        self.sliderVolumen.colorRelleno = self.colorFondoPersonalizado.obtenerColorBoton()
        self.sliderVolumen.colorBoton = self.colorFondoPersonalizado.obtenerColorBoton()
        self.sliderVolumen.colorBordeBoton = self.colorFondoPersonalizado.obtenerColorBorde()
    
    def manejarEventos(self):
        #Maneja todos los eventos de la pantalla
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.ejecutando = False
            
            # Detectar cambio de tamaño de ventana
            elif evento.type == pygame.VIDEORESIZE:
                self.ancho = evento.w
                self.alto = evento.h
                self.actualizarPosiciones()
            
            # Tecla ESC para salir de pantalla completa
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.ejecutando = False
            
            # Manejar eventos de botones
            if self.botonInterfaz.manejarEvento(evento):
                self.abrirPantallaInterfaz()
            
            if self.botonCancion.manejarEvento(evento):
                self.abrirPantallaMusica()
            
            # AQUÍ ESTÁ LA NUEVA FUNCIONALIDAD DEL BOTÓN "VAMOS AL JUEGO"
            if self.botonJuego.manejarEvento(evento):
                self.abrirPantallaDificultad()
            
            # Manejar dropdown
            temaSeleccionado = self.dropdownTema.manejarEvento(evento)
            if temaSeleccionado:
                self.temaActual = temaSeleccionado
                print(f"Tema seleccionado: {temaSeleccionado.nombre}")
            
            # Manejar slider
            self.sliderVolumen.manejarEvento(evento)
    
    def abrirPantallaInterfaz(self):
        #Abre la pantalla de personalización de interfaz
        pantallaInterfaz = PantallaPersonalizacionInterfaz(
            self.pantalla, 
            self.colorFondoPersonalizado,
            self.temaActual  
        )
        nuevoColor = pantallaInterfaz.ejecutar()
    
        if nuevoColor:
            self.colorFondoPersonalizado = nuevoColor
            self.actualizarPosiciones()

    def abrirPantallaMusica(self):
        #Abre la pantalla de selección de música
        pantallaMusica = PantallaMusica(
            self.pantalla, 
            self.colorFondoPersonalizado,
            self.temaActual  
        )
        pantallaMusica.ejecutar()
    
    def abrirPantallaDificultad(self):
        """
        Abre la pantalla de selección de dificultad y luego el juego
        Nueva funcionalidad para el botón "Vamos al juego"
        """
        print("Abriendo pantalla de dificultad...")
        
        # Crear y ejecutar la pantalla de dificultad con los colores personalizados
        pantallaDificultad = PantallaDificultad(
            self.pantalla,
            self.colorFondoPersonalizado,
            self.temaActual
        )
        
        # Ejecutar la pantalla de dificultad y obtener la acción del usuario
        accion, dificultad = pantallaDificultad.ejecutar()
        
        # Manejar la respuesta del usuario
        if accion == 'JUGAR':
            print(f"Iniciando juego con dificultad: {dificultad}")
            
            # Crear la pantalla del juego con los ajustes personalizados
            pantallaJuego = PantallaJuego(
                self.pantalla,
                self.colorFondoPersonalizado,
                self.temaActual
            )
            
            # Pasar la dificultad seleccionada al juego
            # (Puedes usar esto en el juego para ajustar la IA, velocidad, etc.)
            pantallaJuego.dificultad = dificultad
            
            # Ejecutar el juego
            volverAlMenu = pantallaJuego.ejecutar()
            
            # Si el usuario volvió del juego, continuar en personalización
            if volverAlMenu:
                print("Volviendo a personalización desde el juego...")
                # No hacer nada, simplemente continuar el loop de personalización
        
        elif accion == 'VOLVER':
            # El usuario volvió desde la pantalla de dificultad
            print("Volviendo a personalización desde dificultad...")
            # No hacer nada, simplemente continuar en personalización
        
        else:  # accion == 'QUIT'
            # El usuario quiere salir completamente
            self.ejecutando = False

    def dibujar(self):
        #Dibuja todos los elementos de la pantalla

        # Fondo base con el color personalizado
        self.pantalla.fill(self.colorFondoPersonalizado.rgb)
        
        # Aplicar overlay del tema (opacidad)
        overlay = pygame.Surface((self.ancho, self.alto))
        overlay.set_alpha(self.temaActual.opacidad)
        overlay.fill((0, 0, 0))
        self.pantalla.blit(overlay, (0, 0))
        
        # Título con color según el fondo
        colorTitulo = self.colorFondoPersonalizado.obtenerColorTitulo()
        titulo = self.fuenteTitulo.render("Personalización", True, colorTitulo)
        tituloRect = titulo.get_rect(center=(self.ancho // 2, 150))
        self.pantalla.blit(titulo, tituloRect)
        
        # Dibujar componentes
        self.botonInterfaz.dibujar(self.pantalla)
        self.botonCancion.dibujar(self.pantalla)
        self.dropdownTema.dibujar(self.pantalla)
        self.botonJuego.dibujar(self.pantalla)
        
        # Texto de volumen (esquina inferior izquierda) con color según el fondo
        margen = 40
        textoVolumen = self.fuenteTexto.render("Ajustar volumen", True, colorTitulo)
        self.pantalla.blit(textoVolumen, (margen, self.alto - 110))
        
        self.sliderVolumen.dibujar(self.pantalla)
        
        # Mostrar valor del volumen
        valorTexto = self.fuenteTexto.render(f"{self.sliderVolumen.valor}%", True, colorTitulo)
        self.pantalla.blit(valorTexto, (margen + 310, self.alto - 78))
        
        pygame.display.flip()
    
    def ejecutar(self):
        #Loop principal de la pantalla
        while self.ejecutando:
            self.manejarEventos()
            self.dibujar()
            self.reloj.tick(FPS)
        
        pygame.quit()