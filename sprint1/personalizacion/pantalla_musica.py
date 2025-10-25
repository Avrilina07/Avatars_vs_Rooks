# pantallaMusica.py

import pygame
from constantes import ANCHO_VENTANA, ALTO_VENTANA, FPS, PANTALLA_COMPLETA
from componentes import BotonVolver, Slider
from spotify_api import SpotifyAPI


class PantallaMusica:
    #Pantalla para buscar y seleccionar música de Spotify
    
    def __init__(self, pantalla, colorFondo, temaActual):
        self.pantalla = pantalla
        self.reloj = pygame.time.Clock()
        self.ejecutando = True
        self.volver = False
        self.colorFondo = colorFondo
        
        # Tema actual
        self.temaActual = temaActual  
        # Obtener dimensiones de la pantalla actual
        self.ancho, self.alto = self.pantalla.get_size()            
        
        # Inicializar API de Spotify
        self.spotify = SpotifyAPI()
        
        # Variables de búsqueda
        self.textoBusqueda = ""
        self.resultados = []
        
        # Fuentes
        self.fuenteTitulo = pygame.font.SysFont('Arial', 52, bold=True)
        self.fuenteTexto = pygame.font.SysFont('Arial', 24)
        self.fuenteResultados = pygame.font.SysFont('Arial', 20)
        
        # Componentes
        self.botonVolver = BotonVolver(40, 40)
        # Aplicar colores al botón volver según el fondo
        self.botonVolver.colorFondo = self.colorFondo.obtenerColorBoton()
        self.botonVolver.colorHover = self.colorFondo.obtenerColorHoverBoton()
        self.botonVolver.colorBorde = self.colorFondo.obtenerColorBorde()
        self.botonVolver.colorTexto = self.colorFondo.obtenerColorTextoBoton()

        # Campo de búsqueda
        self.rectBusqueda = pygame.Rect(self.ancho // 2 - 250, 250, 500, 50)
        self.activo = False
        
        # Slider de volumen
        margen = 40
        self.sliderVolumen = Slider(margen, self.alto - 80, 300, 25, 50, callback=self.cambiarVolumenSpotify)
        
        # Aplicar colores al slider
        self.sliderVolumen.colorRelleno = self.colorFondo.obtenerColorBoton()
        self.sliderVolumen.colorBoton = self.colorFondo.obtenerColorBoton()
        self.sliderVolumen.colorBordeBoton = self.colorFondo.obtenerColorBorde()
    
    def cambiarVolumenSpotify(self, volumen):
        #Callback que se ejecuta cuando el slider cambia
        self.spotify.cambiarVolumen(volumen)
    
    def buscar(self):
        #Busca canciones usando la API de Spotify
        if self.textoBusqueda.strip():
            self.resultados = self.spotify.buscarCanciones(self.textoBusqueda)
    
    def manejarEventos(self):
        #Maneja todos los eventos de la pantalla
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.ejecutando = False
                self.volver = False
            
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.volver = True
                    self.ejecutando = False
                
                elif self.activo:
                    if evento.key == pygame.K_RETURN:
                        # Buscar al presionar Enter
                        self.buscar()
                    elif evento.key == pygame.K_BACKSPACE:
                        self.textoBusqueda = self.textoBusqueda[:-1]
                    else:
                        # Agregar caracteres
                        self.textoBusqueda += evento.unicode
            
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                # Activar/desactivar campo de búsqueda
                if self.rectBusqueda.collidepoint(evento.pos):
                    self.activo = True
                else:
                    self.activo = False
                
                # Detectar clic en resultados
                if self.resultados:
                    for i in range(len(self.resultados)):
                        rectResultado = pygame.Rect(
                            self.ancho // 2 - 250,
                            350 + i * 60,
                            500,
                            50
                        )
                        if rectResultado.collidepoint(evento.pos):
                            track = self.resultados[i]
                            nombre, artista, uri = self.spotify.obtenerInfoCancion(track)
                            
                            # Reproducir canción
                            if self.spotify.reproducirCancion(uri):
                                print(f"Reproduciendo: {nombre} - {artista}")
            
            # Botón volver
            if self.botonVolver.manejarEvento(evento):
                self.volver = True
                self.ejecutando = False
            
            # Manejar slider de volumen
            self.sliderVolumen.manejarEvento(evento)
    
    def dibujar(self):
        #Dibuja todos los elementos de la pantalla
        
        # Fondo
        self.pantalla.fill(self.colorFondo.rgb)

        # Aplicar overlay del tema (opacidad) 
        overlay = pygame.Surface((self.ancho, self.alto))
        overlay.set_alpha(self.temaActual.opacidad)
        overlay.fill((0, 0, 0))
        self.pantalla.blit(overlay, (0, 0))

        
        # Color de texto según el fondo
        colorTexto = self.colorFondo.obtenerColorTitulo()
        
        # Título
        titulo = self.fuenteTitulo.render("¡ELIGE LA CANCIÓN!", True, colorTexto)
        tituloRect = titulo.get_rect(center=(self.ancho // 2, 150))
        self.pantalla.blit(titulo, tituloRect)
        
        # Campo de búsqueda
        colorCampo = (255, 255, 255) if self.activo else (240, 240, 240)
        pygame.draw.rect(self.pantalla, colorCampo, self.rectBusqueda, border_radius=10)
        pygame.draw.rect(self.pantalla, (0, 0, 0), self.rectBusqueda, 2, border_radius=10)
        
        # Texto en el campo de búsqueda
        if self.textoBusqueda:
            textoSurface = self.fuenteTexto.render(self.textoBusqueda, True, (0, 0, 0))
        else:
            textoSurface = self.fuenteTexto.render("Buscar canción...", True, (150, 150, 150))
        
        self.pantalla.blit(textoSurface, (self.rectBusqueda.x + 15, self.rectBusqueda.y + 12))
        
        # Dibujar resultados
        if self.resultados:
            for i, track in enumerate(self.resultados):
                rectResultado = pygame.Rect(
                    self.ancho // 2 - 250,
                    350 + i * 60,
                    500,
                    50
                )
                
                # Fondo del resultado
                pygame.draw.rect(self.pantalla, (255, 255, 255), rectResultado, border_radius=5)
                pygame.draw.rect(self.pantalla, (0, 0, 0), rectResultado, 2, border_radius=5)
                
                # Texto del resultado
                nombre, artista, _ = self.spotify.obtenerInfoCancion(track)
                textoResultado = f"{i+1}. {nombre} - {artista}"
                
                # Truncar si es muy largo
                if len(textoResultado) > 50:
                    textoResultado = textoResultado[:47] + "..."
                
                textoSurface = self.fuenteResultados.render(textoResultado, True, (0, 0, 0))
                self.pantalla.blit(textoSurface, (rectResultado.x + 10, rectResultado.y + 15))
        
        # Botón volver
        self.botonVolver.dibujar(self.pantalla)
        
        # Texto de volumen en esquina inferior izquierda
        margen = 40
        textoVolumen = self.fuenteTexto.render("Ajustar volumen", True, colorTexto)
        self.pantalla.blit(textoVolumen, (margen, self.alto - 110))
        
        # Slider de volumen
        self.sliderVolumen.dibujar(self.pantalla)
        
        # Mostrar valor del volumen
        valorTexto = self.fuenteTexto.render(f"{self.sliderVolumen.valor}%", True, colorTexto)
        self.pantalla.blit(valorTexto, (margen + 310, self.alto - 78))
        
        pygame.display.flip()
    
    def ejecutar(self):
        #Loop principal de la pantalla
        while self.ejecutando:
            self.manejarEventos()
            self.dibujar()
            self.reloj.tick(FPS)
        
        return self.volver