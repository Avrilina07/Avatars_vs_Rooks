# pantallaJuego.py
# Pantalla de colocación de torres para Avatars VS Rooks
# Versión limpia desde cero - CON MATRIZ AJUSTADA AL GRID

import pygame
import sys
import os

# Importar desde personalizacion
carpeta_actual = os.path.dirname(os.path.abspath(__file__))
carpeta_padre = os.path.dirname(carpeta_actual)
carpeta_personalizacion = os.path.join(carpeta_padre, 'personalizacion')
sys.path.insert(0, carpeta_personalizacion)

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
        # IMPORTANTE: Ahora es 5 filas × 9 columnas (vertical)
        self.filas = 9      # ← Ahora 9 filas (vertical)
        self.columnas = 5   # ← Ahora 5 columnas (horizontal)
        
        # Tamaño y posición del tablero 
        self.anchoTablero = 750  
        self.altoTablero = 900    
        
        # Posición
        self.tableroX = 0       
        self.tableroY = 0
        
        # Tamaño de cada casilla
        self.anchoCasilla = self.anchoTablero / self.columnas  # ~105px
        self.altoCasilla = self.altoTablero / self.filas  # ~110px
        
        # === AJUSTES MANUALES DEL GRID (para alinear con la imagen) ===
        # Estos valores te permiten mover el grid independientemente
        self.gridOffsetX = 130      # ← Mueve el grid a la derecha (+) o izquierda (-)
        self.gridOffsetY = 200      # ← Mueve el grid abajo (+) o arriba (-)
        self.gridAnchoExtra = -50   # ← Ajusta el ancho de las casillas (+/-)
        self.gridAltoExtra = -25    # ← Ajusta el alto de las casillas (+/-)
        
        # Cargar imagen del tablero
        self.imagenTablero = self.cargarImagenTablero()
        
        # === MATRIZ DEL JUEGO ===
        # None = casilla vacía
        # "T1", "T2", "T3", "T4" = torre colocada
        self.matriz = [[None for _ in range(self.columnas)] for _ in range(self.filas)]
        
        # Torre actualmente seleccionada
        self.torreSeleccionada = None
        
        # === FUENTES ===
        self.fuenteTitulo = pygame.font.SysFont('Arial', 65, bold=True)
        self.fuenteTorre = pygame.font.SysFont('Arial', 32, bold=True)
        
        # === BOTONES DE TORRES ===
        self.botonesTorres = self.crearBotonesTorres()
        
        # === BOTÓN INICIAR JUEGO ===
        self.botonIniciar = self.crearBotonIniciar()
        # ===  Dinero inicial ===
        self.dinero = 000  

    
    def cargarImagenTablero(self):
        """Carga y escala la imagen del tablero"""
        try:
            rutaImagen = os.path.join(os.path.dirname(__file__), 'imagenes', 'Tablero.png')
            imagen = pygame.image.load(rutaImagen)
            imagen = pygame.transform.scale(imagen, (self.anchoTablero, self.altoTablero))
            return imagen
        except Exception as e:
            print(f"❌ Error al cargar Tablero.png: {e}")
            return None
    
    def crearBotonesTorres(self):
        botones = []

        # Coordenadas base del panel de torres
        baseX = 850   # posición X del primer botón (columna izquierda)
        baseY = 250   # posición Y de la primera fila
        espacioX = 240  # más separación horizontal
        espacioY = 120  # más separación vertical

        # Crear los 4 botones en cuadrícula 2x2
        for i in range(4):
            columna = i % 2
            fila = i // 2
            boton = Boton(
                baseX + columna * espacioX,
                baseY + fila * espacioY,
                220,   # 🔼 más ancho
                90,    # 🔼 más alto
                f"Torre {i+1}",
                28     # fuente un poquito más grande
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
        AHORA USANDO LOS MISMOS OFFSETS QUE EL GRID VISUAL
        
        Args:
            mouseX: Coordenada X del click
            mouseY: Coordenada Y del click
            
        Returns:
            (fila, columna) o None si está fuera del tablero
        """
        # Usar las mismas coordenadas que el grid visual
        gridX = self.tableroX + self.gridOffsetX
        gridY = self.tableroY + self.gridOffsetY
        
        # Usar el mismo tamaño de casillas que el grid visual
        anchoCasillaGrid = self.anchoCasilla + self.gridAnchoExtra
        altoCasillaGrid = self.altoCasilla + self.gridAltoExtra
        
        # Calcular límites del grid ajustado
        gridAncho = self.columnas * anchoCasillaGrid
        gridAlto = self.filas * altoCasillaGrid
        
        # Verificar si está dentro del grid ajustado
        if not (gridX <= mouseX <= gridX + gridAncho and
                gridY <= mouseY <= gridY + gridAlto):
            return None
        
        # Calcular posición en la matriz usando el grid ajustado
        columna = int((mouseX - gridX) / anchoCasillaGrid)
        fila = int((mouseY - gridY) / altoCasillaGrid)
        
        # Validar que esté dentro del rango
        if 0 <= fila < self.filas and 0 <= columna < self.columnas:
            return (fila, columna)
        
        return None
    
    def colocarTorre(self, fila, columna):
        """Coloca la torre seleccionada en la casilla"""
        if self.torreSeleccionada and self.matriz[fila][columna] is None:
            self.matriz[fila][columna] = self.torreSeleccionada
            print(f"✅ {self.torreSeleccionada} colocada en ({fila}, {columna})")
    
    def quitarTorre(self, fila, columna):
        """Quita la torre de la casilla"""
        if self.matriz[fila][columna] is not None:
            torreQuitada = self.matriz[fila][columna]
            self.matriz[fila][columna] = None
            print(f"🗑️ {torreQuitada} removida de ({fila}, {columna})")
    
    def manejarEventos(self):
        """Procesa todos los eventos de entrada"""
        for evento in pygame.event.get():
            # Cerrar ventana
            if evento.type == pygame.QUIT:
                self.ejecutando = False
                self.volver = False
            
            # Tecla ESC para salir (temporal para testing)
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.ejecutando = False
                    self.volver = True
            
            # Click del mouse
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = evento.pos
                
                # Verificar click en botones de torres
                for boton in self.botonesTorres:
                    if boton.manejarEvento(evento):
                        self.torreSeleccionada = boton.idTorre
                        print(f"🎯 Torre seleccionada: {self.torreSeleccionada}")
                
                # Verificar click en botón Iniciar Juego
                if self.botonIniciar.manejarEvento(evento):
                    print("🎮 INICIAR JUEGO clickeado (sin funcionalidad aún)")
                    # Aquí irá la lógica para iniciar el juego
                
                # Verificar click en el tablero
                casilla = self.obtenerCasillaClick(mouseX, mouseY)
                if casilla:
                    fila, columna = casilla
                    
                    # Si la casilla está vacía y hay torre seleccionada → colocar
                    if self.matriz[fila][columna] is None and self.torreSeleccionada:
                        self.colocarTorre(fila, columna)
                    
                    # Si la casilla tiene una torre → quitar
                    elif self.matriz[fila][columna] is not None:
                        self.quitarTorre(fila, columna)
            
            # Hover de botones
            elif evento.type == pygame.MOUSEMOTION:
                for boton in self.botonesTorres:
                    boton.manejarEvento(evento)
                self.botonIniciar.manejarEvento(evento)  # Hover para Iniciar Juego
    
    def dibujar(self):
        """Dibuja todos los elementos en pantalla"""
        # 1. Fondo con color personalizado
        self.pantalla.fill(self.colorFondo.rgb)
        
        # 2. Overlay de tema (opacidad)
        overlay = pygame.Surface((self.ancho, self.alto))
        overlay.set_alpha(self.temaActual.opacidad)
        overlay.fill((0, 0, 0))
        self.pantalla.blit(overlay, (0, 0))
        
        # 3. Título
        colorTexto = self.colorFondo.obtenerColorTitulo()
        titulo = self.fuenteTitulo.render("Avatars VS Rooks", True, colorTexto)
        tituloRect = titulo.get_rect(center=(self.ancho -350, 100))
        self.pantalla.blit(titulo, tituloRect)
        
        # 4. Imagen del tablero
        if self.imagenTablero:
            self.pantalla.blit(self.imagenTablero, (self.tableroX, self.tableroY))
        
        # 5. GRID ROJO PARA DEBUG (para ajustar la matriz)
        self.dibujarGridDebug()
        
        # 6. Torres colocadas en el tablero
        self.dibujarTorres()
        
        # 7. Botones de selección de torres
        for boton in self.botonesTorres:
            boton.dibujar(self.pantalla)
            
            # Indicador visual de torre seleccionada (borde dorado)
            if boton.idTorre == self.torreSeleccionada:
                pygame.draw.rect(self.pantalla, (255, 215, 0), boton.rect, 5)
        
        # 8. Botón Iniciar Juego
        self.botonIniciar.dibujar(self.pantalla)

        #9 Dinero
        self.dibujarDinero()

        
        # Actualizar pantalla
        pygame.display.flip()
    def dibujarDinero(self):
        """Muestra el dinero actual del jugador debajo del botón Iniciar Juego"""
        texto = f"Dinero: ${self.dinero}"
        color = self.colorFondo.obtenerColorTitulo()
        fuenteDinero = pygame.font.SysFont('Arial', 36, bold=True)
        render = fuenteDinero.render(texto, True, color)

        # Colocar debajo del botón iniciar
        x = self.botonIniciar.rect.centerx
        y = self.botonIniciar.rect.bottom + 40  # espacio debajo del botón
        rect = render.get_rect(center=(x, y))
        self.pantalla.blit(render, rect)

    def dibujarGridDebug(self):
        """
        Dibuja un grid rojo para debug - para ver dónde caen las casillas
        
        AJUSTA ESTOS VALORES MANUALMENTE EN __init__:
        - gridOffsetX: mueve el grid horizontalmente (+derecha, -izquierda)
        - gridOffsetY: mueve el grid verticalmente (+abajo, -arriba)
        - gridAnchoExtra: ajusta ancho de casillas (+más ancho, -más estrecho)
        - gridAltoExtra: ajusta alto de casillas (+más alto, -más bajo)
        
        Ejemplo:
        self.gridOffsetX = 50    # Mueve grid 50px a la derecha
        self.gridOffsetY = -20   # Mueve grid 20px arriba
        self.gridAnchoExtra = 5  # Casillas 5px más anchas
        """
        colorGrid = (255, 0, 0)  # Rojo brillante
        grosor = 3  # Más grueso para ver mejor
        
        # Calcular posición del grid con offsets
        gridX = self.tableroX + self.gridOffsetX
        gridY = self.tableroY + self.gridOffsetY
        
        # Calcular tamaño de casillas con ajustes
        anchoCasillaGrid = self.anchoCasilla + self.gridAnchoExtra
        altoCasillaGrid = self.altoCasilla + self.gridAltoExtra
        
        # Líneas verticales (columnas)
        for col in range(self.columnas + 1):
            x = int(gridX + (col * anchoCasillaGrid))
            pygame.draw.line(
                self.pantalla,
                colorGrid,
                (x, gridY),
                (x, int(gridY + (self.filas * altoCasillaGrid))),
                grosor
            )
        
        # Líneas horizontales (filas)
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
        # Usar las mismas coordenadas que el grid visual
        gridX = self.tableroX + self.gridOffsetX
        gridY = self.tableroY + self.gridOffsetY
        
        # Usar el mismo tamaño de casillas que el grid visual
        anchoCasillaGrid = self.anchoCasilla + self.gridAnchoExtra
        altoCasillaGrid = self.altoCasilla + self.gridAltoExtra
        
        for fila in range(self.filas):
            for columna in range(self.columnas):
                torre = self.matriz[fila][columna]
                
                if torre:  # Si hay una torre en esta casilla
                    # Calcular centro de la casilla USANDO EL GRID AJUSTADO
                    centroX = int(gridX + (columna * anchoCasillaGrid) + (anchoCasillaGrid / 2))
                    centroY = int(gridY + (fila * altoCasillaGrid) + (altoCasillaGrid / 2))
                    
                    # Círculo de fondo (ajustado al tamaño de la casilla)
                    radio = min(int(anchoCasillaGrid * 0.35), int(altoCasillaGrid * 0.35))
                    pygame.draw.circle(self.pantalla, (50, 50, 50), (centroX, centroY), radio)
                    pygame.draw.circle(self.pantalla, (255, 255, 255), (centroX, centroY), radio, 3)
                    
                    # Texto de la torre
                    textoTorre = self.fuenteTorre.render(torre, True, (255, 255, 255))
                    textoRect = textoTorre.get_rect(center=(centroX, centroY))
                    self.pantalla.blit(textoTorre, textoRect)
    
    def ejecutar(self):
        """
        Loop principal de la pantalla
        
        Returns:
            bool: True si debe volver a pantalla anterior
        """
        while self.ejecutando:
            self.manejarEventos()
            self.dibujar()
            self.reloj.tick(FPS)
        
        return self.volver


# ============================================================================
# Para testing directo (opcional)
# ============================================================================
if __name__ == "__main__":
    print("⚠️ Este archivo debe ser importado desde otra pantalla")
    print("Para probar, usa el archivo testJuego.py")