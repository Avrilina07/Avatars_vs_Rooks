# pantallaInterfaz.py

import pygame
from constantes import ANCHO_VENTANA, ALTO_VENTANA, FPS, PANTALLA_COMPLETA
from componentes import Boton, SelectorColor, BotonVolver, Slider
from fondo import ColoresFondoDisponibles


class PantallaPersonalizacionInterfaz:
    #Pantalla para personalizar los colores de la interfaz
    
    def __init__(self, pantalla, colorInicial, temaActual):
        self.pantalla = pantalla
        self.reloj = pygame.time.Clock()
        self.ejecutando = True
        self.volver = False
        
        # Color de fondo seleccionado
        self.colorFondo = colorInicial

        # Tema actual
        self.temaActual = temaActual
        
        # Obtener dimensiones de la pantalla actual
        self.ancho, self.alto = self.pantalla.get_size()    
    
        
        # Fuentes
        self.fuenteTitulo = pygame.font.SysFont('Arial', 80, bold=True)
        self.fuenteSubtitulo = pygame.font.SysFont('Arial', 30, bold=True)
        self.fuenteTexto = pygame.font.SysFont('Arial', 22)
        
        # Componentes
        self.botonVolver = BotonVolver(40, 40)
        self.selectorColores = SelectorColor(50, 200, ColoresFondoDisponibles.obtenerTodos(), columnas=10)

        # Aplicar colores al botón volver según el fondo
        self.botonVolver.colorFondo = self.colorFondo.obtenerColorBoton()
        self.botonVolver.colorHover = self.colorFondo.obtenerColorHoverBoton()
        self.botonVolver.colorBorde = self.colorFondo.obtenerColorBorde()
        self.botonVolver.colorTexto = self.colorFondo.obtenerColorTextoBoton()
        
        # Botón de ejemplo (centrado)
        self.botonEjemplo = None
        self.actualizarComponentes()
    
    def actualizarComponentes(self):
        #Actualiza los componentes con los colores actuales
        centroX = self.ancho // 2
        
        # Crear botón de ejemplo con los colores del fondo seleccionado
        self.botonEjemplo = Boton(
            centroX + 170, 
            self.alto - 530, 
            500, 
            200, 
            "BOTON EJEMPLO", 
            50
        )
        
        # Aplicar colores del tema actual al botón ejemplo
        self.botonEjemplo.colorNormal = self.colorFondo.obtenerColorBoton()
        self.botonEjemplo.colorHover = self.colorFondo.obtenerColorHoverBoton()
        self.botonEjemplo.colorBorde = self.colorFondo.obtenerColorBorde()
        self.botonEjemplo.colorTexto = self.colorFondo.obtenerColorTextoBoton()

        # Actualizar colores del botón volver
        self.botonVolver.colorFondo = self.colorFondo.obtenerColorBoton()
        self.botonVolver.colorHover = self.colorFondo.obtenerColorHoverBoton()
        self.botonVolver.colorBorde = self.colorFondo.obtenerColorBorde()
        self.botonVolver.colorTexto = self.colorFondo.obtenerColorTextoBoton()

    
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
            
            # Botón volver
            if self.botonVolver.manejarEvento(evento):
                self.volver = True
                self.ejecutando = False
            
            # Selector de colores
            colorSeleccionado = self.selectorColores.manejarEvento(evento)
            if colorSeleccionado:
                self.colorFondo = colorSeleccionado
                self.actualizarComponentes()
                print(f"Color seleccionado: {colorSeleccionado.nombre}")
            
            # Botón ejemplo (solo para hover, sin funcionalidad)
            self.botonEjemplo.manejarEvento(evento)
    
    def dibujar(self):
        #Dibuja todos los elementos de la pantalla

        # Fondo con el color seleccionado
        self.pantalla.fill(self.colorFondo.rgb)

        # Aplicar overlay del tema (opacidad) 
        overlay = pygame.Surface((self.ancho, self.alto))
        overlay.set_alpha(self.temaActual.opacidad)
        overlay.fill((0, 0, 0))
        self.pantalla.blit(overlay, (0, 0))

        
        # Título principal
        colorTitulo = self.colorFondo.obtenerColorTitulo()
        titulo = self.fuenteTitulo.render("Personalización Interfaz", True, colorTitulo)
        tituloRect = titulo.get_rect(center=(self.ancho// 2, 80))
        self.pantalla.blit(titulo, tituloRect)
        
        # Subtítulo
        subtitulo = self.fuenteSubtitulo.render("Elige el color para tú interfaz", True, colorTitulo)
        subtituloRect = subtitulo.get_rect(center=(self.ancho // 2, 140))
        self.pantalla.blit(subtitulo, subtituloRect)
        
        # Texto "Fondo"
        textoFondo = self.fuenteTexto.render("Fondo", True, colorTitulo)
        self.pantalla.blit(textoFondo, (50, 170))
        
        # Dibujar componentes
        self.botonVolver.dibujar(self.pantalla)
        self.selectorColores.dibujar(self.pantalla)
        self.botonEjemplo.dibujar(self.pantalla)
        
        pygame.display.flip()
    
    def ejecutar(self):
        #Loop principal de la pantalla
        while self.ejecutando:
            self.manejarEventos()
            self.dibujar()
            self.reloj.tick(FPS)
        return self.colorFondo if self.volver else None