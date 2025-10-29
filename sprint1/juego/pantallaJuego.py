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
from clasesAvatarsRooks import Avatars, Rooks
from logicaAvatarsRooks import GestorAvatars, GestorTorres

class PantallaJuego:
    """Pantalla de colocación de torres en el tablero 9x5"""
    
    def __init__(self, pantalla, colorFondo, temaActual, dificultad):
        """
        Inicializa la pantalla de juego
        
        Args:
            pantalla: Surface de pygame (pantalla completa)
            colorFondo: Objeto ColorFondo con configuración de colores
            temaActual: Objeto Tema con opacidad
            dificultad: str - "Facil", "Intermedio", "Dificil"
        """
        self.pantalla = pantalla
        self.reloj = pygame.time.Clock()
        self.ejecutando = True
        self.volver = False
        
        # Configuración de colores
        self.colorFondo = colorFondo
        self.temaActual = temaActual
        
        # Dificultad seleccionada
        self.dificultad = dificultad
        
        # Dimensiones de pantalla
        self.ancho, self.alto = self.pantalla.get_size()
        
        # === CONFIGURACIÓN DEL TABLERO ===
        self.filas = 9      
        self.columnas = 5   
        
        # Tamaño y posición del tablero 
        self.anchoTablero = 750  
        self.altoTablero = 900    
        self.tableroX = 0       
        self.tableroY = 0
        
        # Tamaño de cada casilla
        self.anchoCasilla = self.anchoTablero / self.columnas
        self.altoCasilla = self.altoTablero / self.filas
        
        # === AJUSTES MANUALES DEL GRID ===
        self.gridOffsetX = 130
        self.gridOffsetY = 200
        self.gridAnchoExtra = -50
        self.gridAltoExtra = -25
        
        # Cargar imagen del tablero
        self.imagenTablero = self.cargarImagenTablero()
        
        # === MATRIZ DEL JUEGO ===
        self.matriz = [[None for _ in range(self.columnas)] for _ in range(self.filas)]
        self.torreSeleccionada = None
        
        # === FUENTES ===
        self.fuenteTitulo = pygame.font.SysFont('Arial', 65)
        self.fuenteTorre = pygame.font.SysFont('Arial', 32)
        self.fuenteInfo = pygame.font.SysFont('Arial', 28)
        
        # === INSTANCIAR CLASES DE JUEGO === 
        self.rooks = Rooks()
        self.avatars = Avatars()
        
        # === MAPEO DE TORRES === 
        self.datosTorres = {
            "T1": self.rooks.torreArena,
            "T2": self.rooks.torreRoca,
            "T3": self.rooks.torreFuego,
            "T4": self.rooks.torreAgua
        }
        
        # === DINERO INICIAL ===
        self.dinero = 500  
        
        # === BOTONES DE TORRES === 
        self.botonesTorres = self.crearBotonesTorres()
        self.botonIniciar = self.crearBotonIniciar()
        
        # === GESTORES DE JUEGO ===
        self.gestorAvatars = None
        self.gestorTorres = None
        self.juegoIniciado = False
    
    def cargarImagenTablero(self):
        """Carga y escala la imagen del tablero"""
        try:
            rutaImagen = os.path.join(carpeta_actual, 'imagenes', 'Tablero.png')
            imagen = pygame.image.load(rutaImagen)
            imagen = pygame.transform.scale(imagen, (self.anchoTablero, self.altoTablero))
            return imagen
        except Exception as e:
            print(f"⚠️ Error cargando imagen del tablero: {e}")
            return None
    
    def crearBotonesTorres(self):
        """Crea los botones de las 4 torres"""
        botones = []
        startX = 850
        startY = 100
        spacing = 120
        
        infoBotones = [
            ("T1", "Arena", self.rooks.torreArena["valor"]),
            ("T2", "Roca", self.rooks.torreRoca["valor"]),
            ("T3", "Fuego", self.rooks.torreFuego["valor"]),
            ("T4", "Agua", self.rooks.torreAgua["valor"])
        ]
        
        for i, (id, nombre, valor) in enumerate(infoBotones):
            texto = f"{nombre}\n₡{valor}"
            # Usar solo los parámetros que acepta el constructor actual
            boton = Boton(startX, startY + (i * spacing), 250, 100, texto)
            
            # Configurar colores después de crear el botón
            try:
                boton.colorNormal = self.colorFondo.obtenerColorBoton()
                boton.colorTexto = self.colorFondo.obtenerColorTextoBoton()
            except:
                pass  # Mantener colores por defecto si hay error
            
            boton.id_torre = id
            botones.append(boton)
        
        return botones
    
    def crearBotonIniciar(self):
        """Crea el botón de iniciar juego"""
        # Usar solo los parámetros que acepta el constructor actual
        boton = Boton(
            850, 
            600,
            250, 
            80,
            "INICIAR"
        )
        
        # Configurar colores después de crear el botón
        try:
            boton.colorNormal = (0, 200, 0)  # Verde
            boton.colorTexto = (255, 255, 255)  # Blanco
        except:
            pass  # Mantener colores por defecto si hay error
        
        return boton
    
    def obtenerCasillaClick(self, mouseX, mouseY):
        """Convierte coordenadas de mouse a fila/columna"""
        gridX = self.tableroX + self.gridOffsetX
        gridY = self.tableroY + self.gridOffsetY
        anchoCasilla = self.anchoCasilla + self.gridAnchoExtra
        altoCasilla = self.altoCasilla + self.gridAltoExtra
        
        if mouseX < gridX or mouseX > gridX + (anchoCasilla * self.columnas):
            return None
        if mouseY < gridY or mouseY > gridY + (altoCasilla * self.filas):
            return None
        
        columna = int((mouseX - gridX) / anchoCasilla)
        fila = int((mouseY - gridY) / altoCasilla)
        
        if 0 <= fila < self.filas and 0 <= columna < self.columnas:
            return (fila, columna)
        
        return None
    
    def colocarTorre(self, fila, columna):
        """Coloca una torre en la casilla si es posible"""

        if self.matriz[fila][columna] is not None:
            print("⚠️ Ya hay una torre ahí")
            return
        
        if self.torreSeleccionada is None:
            print("⚠️ Selecciona una torre primero")
            return
        
        costo = self.datosTorres[self.torreSeleccionada]["valor"]
        
        if self.dinero >= costo:
            self.matriz[fila][columna] = self.torreSeleccionada
            self.dinero -= costo
            print(f"✅ Torre {self.torreSeleccionada} colocada en ({fila}, {columna})")
            
            # ✅ Si el juego ya inició, agregar torre inmediatamente al gestor
            if self.juegoIniciado and self.gestorTorres:
                self.gestorTorres.agregarTorre(self.torreSeleccionada, fila, columna)
        else:
            print(f"⚠️ Dinero insuficiente (necesitas ${costo})")
    
    def quitarTorre(self, fila, columna):
        """Quita una torre y devuelve el dinero"""
        
        if self.matriz[fila][columna] is not None:
            idTorre = self.matriz[fila][columna]
            valorDevolver = self.datosTorres[idTorre]["valor"]
            self.dinero += valorDevolver
            self.matriz[fila][columna] = None
            print(f"🔄 Torre {idTorre} removida, +${valorDevolver}")
            
            # Si el juego ya inició, eliminar del gestor también
            if self.juegoIniciado and self.gestorTorres:
                self.gestorTorres.eliminarTorre(fila, columna)
    
    def manejarEventos(self):
        """Maneja eventos de pygame"""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.ejecutando = False
                pygame.quit()
                sys.exit()
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.ejecutando = False
                    self.volver = True
            
            # Clicks en botones de torres
            for boton in self.botonesTorres:
                if boton.manejarEvento(evento):
                    self.torreSeleccionada = boton.id_torre
                    print(f"🎯 Torre seleccionada: {self.torreSeleccionada}")
            
            # Click en botón Iniciar
            if not self.juegoIniciado:
                if self.botonIniciar.manejarEvento(evento):
                    self.iniciarJuego()
            
            # Clicks en el tablero
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                casilla = self.obtenerCasillaClick(mouseX, mouseY)
                
                if casilla:
                    fila, columna = casilla
                    
                    if evento.button == 1:  # Click izquierdo
                        self.colocarTorre(fila, columna)
                    elif evento.button == 3:  # Click derecho
                        self.quitarTorre(fila, columna)
    
    def iniciarJuego(self):
        """Inicia el juego (crea gestores y comienza spawneo)"""
        # Crear configuración del grid
        gridConfig = {
            "gridX": self.tableroX + self.gridOffsetX,
            "gridY": self.tableroY + self.gridOffsetY,
            "anchoCasilla": self.anchoCasilla + self.gridAnchoExtra,
            "altoCasilla": self.altoCasilla + self.gridAltoExtra
        }
        
        # Crear gestor de torres desde la matriz
        self.gestorTorres = GestorTorres(self.matriz, self.datosTorres, gridConfig)
        
        # Crear gestor de avatars con dificultad
        self.gestorAvatars = GestorAvatars(gridConfig, self.dificultad, FPS)
        self.gestorAvatars.iniciar()
        
        self.juegoIniciado = True
        print(f"🎮 ¡Juego iniciado en dificultad {self.dificultad}!")
    
    def actualizarJuego(self):
        """Actualiza la lógica del juego cada frame"""
        if not self.juegoIniciado:
            return
        
        # Actualizar avatars (movimiento, spawn, disparos)
        self.gestorAvatars.actualizar(self.gestorTorres.torres)
        
        # Actualizar torres (ataques a avatars)
        self.gestorTorres.actualizar(self.gestorAvatars.avatarsActivos, FPS)
        
        # Verificar fin del juego
        stats = self.gestorAvatars.obtenerEstadisticas()
        
        if stats["perdio"]:
            print(f"💀 ¡PERDISTE! {stats['resultado']}")
            # Se puede mostrar pantalla de derrota
        
        if stats["gano"]:
            print(f"🎉 ¡GANASTE! {stats['resultado']}")
            # Se puede mostrar pantalla de victoria
    
    def dibujar(self):
        """Dibuja todos los elementos en pantalla"""
        # 1. Fondo 
        self.pantalla.fill(self.colorFondo.rgb)
        
        # 2. Imagen del tablero
        if self.imagenTablero:
            self.pantalla.blit(self.imagenTablero, (self.tableroX, self.tableroY))
        
        # 3. Grid de debug (opcional)
        self.dibujarGridDebug()
        
        # 4. Torres colocadas (si no ha iniciado el juego)
        if not self.juegoIniciado:
            self.dibujarTorresMatriz()
        
        # 5. Torres activas (si ya inició)
        if self.juegoIniciado and self.gestorTorres:
            self.gestorTorres.dibujar(self.pantalla)
        
        # 6. Avatars
        if self.juegoIniciado and self.gestorAvatars:
            self.gestorAvatars.dibujar(self.pantalla)
        
        # 7. Título
        self.dibujarTitulo()
        
        # 8. Botones de torres
        for boton in self.botonesTorres:
            boton.dibujar(self.pantalla)
        
        # 9. Botón iniciar
        if not self.juegoIniciado:
            self.botonIniciar.dibujar(self.pantalla)
        
        # 10. Dinero
        self.dibujarDinero()
        
        # 11. Estadísticas del juego
        if self.juegoIniciado:
            self.dibujarEstadisticas()
        
        # 12. Indicador de torre seleccionada
        if self.torreSeleccionada:
            self.dibujarTorreSeleccionada()
        
        # Actualizar pantalla
        pygame.display.flip()
    
    def dibujarTitulo(self):
        """Dibuja el título del juego"""
        texto = "AVATARS VS ROOKS"
        color = self.colorFondo.obtenerColorTitulo()
        render = self.fuenteTitulo.render(texto, True, color)
        rect = render.get_rect(center=(self.ancho // 2, 50))
        self.pantalla.blit(render, rect)
    
    def dibujarDinero(self):
        """Dibuja el dinero disponible"""
        texto = f"Dinero: ${self.dinero}"
        color = self.colorFondo.obtenerColorTitulo()
        render = self.fuenteInfo.render(texto, True, color)
        # Ajustar posición Y según si hay botón Iniciar
        y = 550 if not self.juegoIniciado else 700
        self.pantalla.blit(render, (850, y))
    
    def dibujarTorreSeleccionada(self):
        """Dibuja indicador de torre seleccionada"""
        texto = f"Seleccionada: {self.torreSeleccionada}"
        color = (255, 255, 0)
        render = self.fuenteInfo.render(texto, True, color)
        self.pantalla.blit(render, (850, 50))
    
    def dibujarEstadisticas(self):
        """Dibuja información del juego en curso"""
        if not self.juegoIniciado:
            return
        
        stats = self.gestorAvatars.obtenerEstadisticas()
        
        color = self.colorFondo.obtenerColorTitulo()
        y = 50
        
        # Dificultad
        textoDif = f"Dificultad: {stats['dificultad']}"
        renderDif = self.fuenteInfo.render(textoDif, True, color)
        self.pantalla.blit(renderDif, (850, y))
        y += 40
        
        # Tiempo restante
        textoTiempo = f"Tiempo: {stats['tiempoRestanteStr']}"
        colorTiempo = (255, 0, 0) if stats['tiempoRestante'] < 10 else color
        renderTiempo = self.fuenteInfo.render(textoTiempo, True, colorTiempo)
        self.pantalla.blit(renderTiempo, (850, y))
        y += 40
        
        # Enemigos vivos
        textoEnemigos = f"Enemigos: {stats['avatarsVivos']}"
        renderEnemigos = self.fuenteInfo.render(textoEnemigos, True, color)
        self.pantalla.blit(renderEnemigos, (850, y))
        y += 40
        
        # Torres restantes
        textoTorres = f"Torres: {len(self.gestorTorres.torres)}"
        renderTorres = self.fuenteInfo.render(textoTorres, True, color)
        self.pantalla.blit(renderTorres, (850, y))
    
    def dibujarGridDebug(self):
        """Dibuja el grid de debug (para ajustar posiciones)"""
        gridX = self.tableroX + self.gridOffsetX
        gridY = self.tableroY + self.gridOffsetY
        anchoCasilla = self.anchoCasilla + self.gridAnchoExtra
        altoCasilla = self.altoCasilla + self.gridAltoExtra
        
        for fila in range(self.filas + 1):
            y = gridY + fila * altoCasilla
            pygame.draw.line(self.pantalla, (255, 0, 0), 
                           (gridX, y), 
                           (gridX + anchoCasilla * self.columnas, y), 2)
        
        for columna in range(self.columnas + 1):
            x = gridX + columna * anchoCasilla
            pygame.draw.line(self.pantalla, (255, 0, 0), 
                           (x, gridY), 
                           (x, gridY + altoCasilla * self.filas), 2)
    
    def dibujarTorresMatriz(self):
        """Dibuja las torres colocadas (antes de iniciar)"""
        gridX = self.tableroX + self.gridOffsetX
        gridY = self.tableroY + self.gridOffsetY
        anchoCasilla = self.anchoCasilla + self.gridAnchoExtra
        altoCasilla = self.altoCasilla + self.gridAltoExtra
        
        colores = {
            "T1": (194, 178, 128),
            "T2": (128, 128, 128),
            "T3": (255, 100, 0),
            "T4": (0, 100, 255)
        }
        
        for fila in range(self.filas):
            for columna in range(self.columnas):
                if self.matriz[fila][columna]:
                    idTorre = self.matriz[fila][columna]
                    color = colores.get(idTorre, (255, 255, 255))
                    
                    x = gridX + columna * anchoCasilla + anchoCasilla / 2
                    y = gridY + fila * altoCasilla + altoCasilla / 2
                    
                    pygame.draw.circle(self.pantalla, color, (int(x), int(y)), 25)
                    pygame.draw.circle(self.pantalla, (0, 0, 0), (int(x), int(y)), 25, 3)
    
    def ejecutar(self):
        """Loop principal de la pantalla"""
        while self.ejecutando:
            self.manejarEventos()
            self.actualizarJuego()
            self.dibujar()
            self.reloj.tick(FPS)
        
        return self.volver


# ============================================================================
# Para testing directo
# ============================================================================
if __name__ == "__main__":
    print("Este archivo debe ser importado desde otra pantalla")
    print("Para probar, usa el archivo testJuego.py")
