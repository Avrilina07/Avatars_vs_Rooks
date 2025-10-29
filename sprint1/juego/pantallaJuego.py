# pantallaJuego.py
# Pantalla de colocación de torres para Avatars VS Rooks
# Versión con botón redondo integrado sin clase auxiliar

import pygame
import sys
import os

# Importar desde personalizacion
# Configuración para que el módulo encuentre las carpetas de 'personalizacion'
carpeta_actual = os.path.dirname(os.path.abspath(__file__))
carpeta_padre = os.path.dirname(carpeta_actual)
carpeta_personalizacion = os.path.join(carpeta_padre, 'personalizacion')
sys.path.insert(0, carpeta_personalizacion)

# Se necesita Boton (para los botones rectangulares) y constantes
from constantes import FPS
from componentes import Boton  


class PantallaJuego:
    """Pantalla de colocación de torres en el tablero 9x5"""
    
    def __init__(self, pantalla, colorFondo, temaActual):
        """
        Inicializa la pantalla de juego
        
        Args:
            pantalla: Surface de pygame (pantalla completa)
            colorFondo: Objeto ColorFondo con configuración de colores
            temaActual: Objeto Tema con opacidad
        """
        self.pantalla = pantalla
        self.reloj = pygame.time.Clock()
        self.ejecutando = True
        self.volver = False
        
        # Configuración de colores
        self.colorFondo = colorFondo
        self.temaActual = temaActual
        
        # Dimensiones de pantalla
        self.ancho, self.alto = self.pantalla.get_size()
        
        # === CONFIGURACIÓN DEL TABLERO ===
        self.filas = 9      
        self.columnas = 5   
        self.anchoTablero = 750  
        self.altoTablero = 900    
        self.tableroX = 0       
        self.tableroY = 0
        self.anchoCasilla = self.anchoTablero / self.columnas  
        self.altoCasilla = self.altoTablero / self.filas  
        self.gridOffsetX = 123      
        self.gridOffsetY = 192      
        self.gridAnchoExtra = -50   
        self.gridAltoExtra = -25    
        self.imagenTablero = self.cargarImagenTablero()
        self.matriz = [[None for _ in range(self.columnas)] for _ in range(self.filas)]
        self.torreSeleccionada = None
        
        # === FUENTES ===
        self.fuenteTitulo = pygame.font.SysFont('Arial', 65, bold=True)
        self.fuenteTorre = pygame.font.SysFont('Arial', 32, bold=True)
        self.dinero = 000
        
        # === BOTONES RECTANGULARES ===
        self.botonesTorres = self.crearBotonesTorres()
        self.botonIniciar = self.crearBotonIniciar()
        
        # === DEFINICIÓN DEL BOTÓN "USUARIO"  ===
        margen = 60
        self.usuarioRadio = 35
        self.usuarioCentroX = self.ancho - margen
        self.usuarioCentroY = margen
        self.usuarioTexto = "USER"
        self.usuarioHover = False # Variable de estado para el hover
        
        # Colores para el botón de usuario 
        self.colorUsuarioNormal = self.colorFondo.obtenerColorBoton()
        self.colorUsuarioHover = self.colorFondo.obtenerColorHoverBoton()
        self.colorUsuarioBorde = self.colorFondo.obtenerColorBorde()
        self.colorUsuarioTexto = self.colorFondo.obtenerColorTextoBoton()
        self.fuenteUsuario = pygame.font.SysFont('Arial', 18, bold=True)
    
    
    def cargarImagenTablero(self):
        """Carga y escala la imagen del tablero"""
        try:
            rutaImagen = os.path.join(os.path.dirname(__file__), 'imagenes', 'Tablero.png')
            imagen = pygame.image.load(rutaImagen)
            imagen = pygame.transform.scale(imagen, (self.anchoTablero, self.altoTablero))
            return imagen
        except Exception as e:
            print(f"Error al cargar Tablero.png: {e}")
            return None
    
    def crearBotonesTorres(self):
        botones = []

        baseX = 850   
        baseY = 250   
        espacioX = 240  
        espacioY = 120  

        for i in range(4):
            columna = i % 2
            fila = i // 2
            boton = Boton(
                baseX + columna * espacioX,
                baseY + fila * espacioY,
                220,   
                90,    
                f"Torre {i+1}",
                28     
            )

            # Colores del tema
            boton.colorNormal = self.colorFondo.obtenerColorBoton()
            boton.colorHover = self.colorFondo.obtenerColorHoverBoton()
            boton.colorBorde = self.colorFondo.obtenerColorBorde()
            boton.colorTexto = self.colorFondo.obtenerColorTextoBoton()

            boton.idTorre = f"T{i+1}"
            botones.append(boton)

        return botones
    
    def crearBotonIniciar(self):
        boton = Boton(
            925,
            480,
            300,
            80,
            "INICIAR JUEGO",
            32
        )

        boton.colorNormal = self.colorFondo.obtenerColorBoton()
        boton.colorHover = self.colorFondo.obtenerColorHoverBoton()
        boton.colorBorde = self.colorFondo.obtenerColorBorde()
        boton.colorTexto = self.colorFondo.obtenerColorTextoBoton()

        return boton

    
    def obtenerCasillaClick(self, mouseX, mouseY):
        """
        Convierte coordenadas del mouse a posición en la matriz
        """
        gridX = self.tableroX + self.gridOffsetX
        gridY = self.tableroY + self.gridOffsetY
        
        anchoCasillaGrid = self.anchoCasilla + self.gridAnchoExtra
        altoCasillaGrid = self.altoCasilla + self.gridAltoExtra
        
        gridAncho = self.columnas * anchoCasillaGrid
        gridAlto = self.filas * altoCasillaGrid
        
        if not (gridX <= mouseX <= gridX + gridAncho and
                gridY <= mouseY <= gridY + gridAlto):
            return None
        
        columna = int((mouseX - gridX) / anchoCasillaGrid)
        fila = int((mouseY - gridY) / altoCasillaGrid)
        
        if 0 <= fila < self.filas and 0 <= columna < self.columnas:
            return (fila, columna)
        
        return None
    
    def colocarTorre(self, fila, columna):
        """Coloca la torre seleccionada en la casilla"""
        if self.torreSeleccionada and self.matriz[fila][columna] is None:
            self.matriz[fila][columna] = self.torreSeleccionada
            print(f"{self.torreSeleccionada} colocada en ({fila}, {columna})")
    
    def quitarTorre(self, fila, columna):
        """Quita la torre de la casilla"""
        if self.matriz[fila][columna] is not None:
            torreQuitada = self.matriz[fila][columna]
            self.matriz[fila][columna] = None
            print(f"{torreQuitada} removida de ({fila}, {columna})")
    
    def manejarEventos(self):
        """Procesa todos los eventos de entrada"""
        for evento in pygame.event.get():
            # Cerrar ventana
            if evento.type == pygame.QUIT:
                self.ejecutando = False
                self.volver = False
            
            # Tecla ESC para volver
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.ejecutando = False
                    self.volver = True

            # Obtener posición del mouse y calcular distancia para el botón redondo
            mouseX, mouseY = pygame.mouse.get_pos()
            distancia = ((mouseX - self.usuarioCentroX) ** 2 + 
                         (mouseY - self.usuarioCentroY) ** 2) ** 0.5
            esta_sobre_usuario = distancia <= self.usuarioRadio

            if evento.type == pygame.MOUSEMOTION:
                # Hover del botón redondo
                self.usuarioHover = esta_sobre_usuario
                
                # Hover de los botones rectangulares
                for boton in self.botonesTorres:
                    boton.manejarEvento(evento)
                self.botonIniciar.manejarEvento(evento)

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                
                # Lógica de click de botones rectangulares
                for boton in self.botonesTorres:
                    if boton.manejarEvento(evento):
                        self.torreSeleccionada = boton.idTorre
                        print(f"Torre seleccionada: {self.torreSeleccionada}")
                
                if self.botonIniciar.manejarEvento(evento):
                    print("INICIAR JUEGO clickeado ")

                # Lógica de click en el tablero
                casilla = self.obtenerCasillaClick(mouseX, mouseY)
                if casilla:
                    fila, columna = casilla
                    
                    if self.matriz[fila][columna] is None and self.torreSeleccionada:
                        self.colocarTorre(fila, columna)
                    
                    elif self.matriz[fila][columna] is not None:
                        self.quitarTorre(fila, columna)
    
    def dibujar(self):
        """Dibuja todos los elementos en pantalla"""
        # 1. Fondo, overlay, título
        self.pantalla.fill(self.colorFondo.rgb)
        overlay = pygame.Surface((self.ancho, self.alto))
        overlay.set_alpha(self.temaActual.opacidad)
        overlay.fill((0, 0, 0))
        self.pantalla.blit(overlay, (0, 0))
        colorTexto = self.colorFondo.obtenerColorTitulo()
        titulo = self.fuenteTitulo.render("Avatars VS Rooks", True, colorTexto)
        tituloRect = titulo.get_rect(center=(self.ancho -350, 100))
        self.pantalla.blit(titulo, tituloRect)
        
        # 2. Tablero, grid, torres
        if self.imagenTablero:
            self.pantalla.blit(self.imagenTablero, (self.tableroX, self.tableroY))
        self.dibujarGridDebug()
        self.dibujarTorres()
        
        # 3. Botones rectangulares
        for boton in self.botonesTorres:
            boton.dibujar(self.pantalla)
            if boton.idTorre == self.torreSeleccionada:
                pygame.draw.rect(self.pantalla, (255, 215, 0), boton.rect, 5)
        
        self.botonIniciar.dibujar(self.pantalla)
        self.dibujarDinero()

        # DIBUJO DEL BOTÓN "USUARIO"
        color = self.colorUsuarioHover if self.usuarioHover else self.colorUsuarioNormal
        
        # 1. Círculo relleno
        pygame.draw.circle(self.pantalla, color, (self.usuarioCentroX, self.usuarioCentroY), self.usuarioRadio)
        
        # 2. Borde circular
        pygame.draw.circle(self.pantalla, self.colorUsuarioBorde, 
                           (self.usuarioCentroX, self.usuarioCentroY), self.usuarioRadio, 3)
        
        # 3. Texto centrado
        textoSurface = self.fuenteUsuario.render(self.usuarioTexto, True, self.colorUsuarioTexto)
        textoRect = textoSurface.get_rect(center=(self.usuarioCentroX, self.usuarioCentroY))
        self.pantalla.blit(textoSurface, textoRect)
        
        # Actualizar pantalla
        pygame.display.flip()
        
    def dibujarDinero(self):
        """Muestra el dinero actual del jugador debajo del botón Iniciar Juego"""
        texto = f"Dinero: ${self.dinero}"
        color = self.colorFondo.obtenerColorTitulo()
        fuenteDinero = pygame.font.SysFont('Arial', 36, bold=True)
        render = fuenteDinero.render(texto, True, color)

        x = self.botonIniciar.rect.centerx
        y = self.botonIniciar.rect.bottom + 40  
        rect = render.get_rect(center=(x, y))
        self.pantalla.blit(render, rect)

    def dibujarGridDebug(self):
        """Dibuja un grid rojo para debug - para ver dónde caen las casillas"""
        colorGrid = (255, 0, 0)  
        grosor = 3 
        
        gridX = self.tableroX + self.gridOffsetX
        gridY = self.tableroY + self.gridOffsetY
        
        anchoCasillaGrid = self.anchoCasilla + self.gridAnchoExtra
        altoCasillaGrid = self.altoCasilla + self.gridAltoExtra
        
        for col in range(self.columnas + 1):
            x = int(gridX + (col * anchoCasillaGrid))
            pygame.draw.line(
                self.pantalla,
                colorGrid,
                (x, gridY),
                (x, int(gridY + (self.filas * altoCasillaGrid))),
                grosor
            )
        
        for fila in range(self.filas + 1):
            y = int(gridY + (fila * altoCasillaGrid))
            pygame.draw.line(
                self.pantalla,
                colorGrid,
                (gridX, y),
                (int(gridX + (self.columnas * anchoCasillaGrid)), y),
                grosor
            )
    
    def dibujarTorres(self):
        """Dibuja las torres colocadas en el tablero - ALINEADAS CON EL GRID AJUSTADO"""
        gridX = self.tableroX + self.gridOffsetX
        gridY = self.tableroY + self.gridOffsetY
        
        anchoCasillaGrid = self.anchoCasilla + self.gridAnchoExtra
        altoCasillaGrid = self.altoCasilla + self.gridAltoExtra
        
        for fila in range(self.filas):
            for columna in range(self.columnas):
                torre = self.matriz[fila][columna]
                
                if torre:  
                    centroX = int(gridX + (columna * anchoCasillaGrid) + (anchoCasillaGrid / 2))
                    centroY = int(gridY + (fila * altoCasillaGrid) + (altoCasillaGrid / 2))
                    
                    radio = min(int(anchoCasillaGrid * 0.35), int(altoCasillaGrid * 0.35))
                    pygame.draw.circle(self.pantalla, (50, 50, 50), (centroX, centroY), radio)
                    pygame.draw.circle(self.pantalla, (255, 255, 255), (centroX, centroY), radio, 3)
                    
                    textoTorre = self.fuenteTorre.render(torre, True, (255, 255, 255))
                    textoRect = textoTorre.get_rect(center=(centroX, centroY))
                    self.pantalla.blit(textoTorre, textoRect)
    
    def ejecutar(self):
        """
        Loop principal de la pantalla
        """
        while self.ejecutando:
            self.manejarEventos()
            self.dibujar()
            self.reloj.tick(FPS)
        
        return self.volver