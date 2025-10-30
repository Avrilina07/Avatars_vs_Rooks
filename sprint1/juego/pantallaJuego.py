import pygame
import sys
import os
import subprocess
import runpy

# Configuración para que el módulo encuentre las carpetas necesarias
carpeta_actual = os.path.dirname(os.path.abspath(__file__))
carpeta_padre = os.path.dirname(carpeta_actual)

# Agregar carpeta de personalización al path
carpeta_personalizacion = os.path.join(carpeta_padre, 'personalizacion')
sys.path.insert(0, carpeta_personalizacion)

# Agregar carpeta de salón de la fama al path
carpeta_salon_fama = os.path.join(carpeta_padre, 'salonDeFama')
sys.path.insert(0, carpeta_salon_fama)

# Importaciones necesarias
from constantes import FPS
from componentes import Boton
from clasesAvatarsRooks import Avatars, Rooks
from logicaAvatarsRooks import GestorAvatars, GestorTorres
from coins import generarMonedas
from algoritmoDelBanquero import funcionDelBanquero, guardar_puntaje
from spotify_api import tempo, popularidad

class PantallaJuego:
    """Pantalla de colocación de torres en el tablero 9x5"""

    def __init__(self, pantalla, colorFondo, temaActual, dificultad, spotify=None):
        """
        Inicializa la pantalla de juego
        
        Args:
            spotify: Objeto SpotifyAPI para controlar la música (opcional)
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
        
        # Control de música
        self.spotify = spotify

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
        
        self.gridOffsetX = 130
        self.gridOffsetY = 200
        self.gridAnchoExtra = -50
        self.gridAltoExtra = -25
        
        self.imagenTablero = self.cargarImagenTablero()
        self.matriz = [[None for _ in range(self.columnas)] for _ in range(self.filas)]
        self.torreSeleccionada = None

        # === CARGA DE IMÁGENES DEL JUEGO ===
        self.imagenes_torres = {}
        self.imagenes_avatars = {}
        self.imagenes_proyectiles = {}
        self.cargarImagenesJuego()

        # === FUENTES ===
        self.fuenteTitulo = pygame.font.SysFont('Arial', 65, bold=True)
        self.fuenteTorre = pygame.font.SysFont('Arial', 32, bold=True)
        self.fuenteInfo = pygame.font.SysFont('Arial', 28) 

        # === LÓGICA DE JUEGO ===
        self.rooks = Rooks()
        self.avatars = Avatars()
        self.datosTorres = { 
            "T1": self.rooks.torreArena, "T2": self.rooks.torreRoca,
            "T3": self.rooks.torreFuego, "T4": self.rooks.torreAgua
        }
        self.dinero = 350
        self.monedas = []
        self.puntosParaMonedas = 0  
        self.umbralMonedas = 100     
        self.gestorAvatars = None
        self.gestorTorres = None
        self.juegoIniciado = False
        
        # === ESTADOS Y BOTONES DE DERROTA ===
        self.estadoJuego = "CONFIGURACION" 
        self.botonReiniciar = self.crearBotonReiniciar()
        
        # === BOTONES RECTANGULARES ===
        self.botonesTorres = self.crearBotonesTorres()
        self.botonIniciar = self.crearBotonIniciar()

        # === BOTÓN "USUARIO" ===
        margen = 60
        self.usuarioRadio = 35
        self.usuarioCentroX = self.ancho - margen
        self.usuarioCentroY = margen
        self.usuarioTexto = "USER"
        self.usuarioHover = False
        
        self.colorUsuarioNormal = self.colorFondo.obtenerColorBoton()
        self.colorUsuarioHover = self.colorFondo.obtenerColorHoverBoton()
        self.colorUsuarioBorde = self.colorFondo.obtenerColorBorde()
        self.colorUsuarioTexto = self.colorFondo.obtenerColorTextoBoton()
        self.fuenteUsuario = pygame.font.SysFont('Arial', 18, bold=True)


    # === MÉTODOS DE UTILIDAD ===
    def cargarImagenTablero(self):
        """Carga y escala la imagen del tablero"""
        try:
            rutaImagen = os.path.join(carpeta_actual, 'imagenes', 'Tablero.png')
            imagen = pygame.image.load(rutaImagen)
            imagen = pygame.transform.scale(imagen, (self.anchoTablero, self.altoTablero))
            return imagen
        except Exception as e:
            print(f"Error cargando imagen del tablero: {e}")
            return None

    def cargarImagenesJuego(self):
        """Carga todas las imágenes de avatars, torres y proyectiles"""
        try:
            ruta_base = os.path.join(carpeta_actual, 'imagenes')

            # --- AVATARS ---
            nombres_avatars = ["Arco_1", "Arco_2", "hacha_1", "hacha_2", 
                               "bate_1", "bate_2", "escudo_1", "escudo_2"]
            for nombre in nombres_avatars:
                clave = f"Avatar_{nombre}"
                ruta = os.path.join(ruta_base, f"{clave}.png")
                self.imagenes_avatars[clave] = pygame.image.load(ruta).convert_alpha()

            # --- TORRES ---
            nombres_torres = ["Torre_arena", "Torre_roca", "Torre_fuego", "Torre_agua"]
            for nombre in nombres_torres:
                ruta = os.path.join(ruta_base, f"{nombre}.png")
                self.imagenes_torres[nombre] = pygame.image.load(ruta).convert_alpha()

            # --- PROYECTILES ---
            # Se asume que los nombres de los archivos de proyectiles son T1.png, T2.png, etc.
            # Sin embargo, el código original usa nombres largos, los mantendré aquí:
            mapa_proyectiles = {
                "T1": "Ataque_arena", "T2": "Ataque_roca",
                "T3": "Ataque_fuego", "T4": "Ataque_agua"
            }
            # *** NOTA IMPORTANTE: Si los proyectiles se llaman T1.png, T2.png, etc.
            # *** Debes cambiar el mapeo arriba a:
            # *** mapa_proyectiles = {"T1": "T1", "T2": "T2", ...} 
            
            for tipo_torre, nombre_archivo in mapa_proyectiles.items():
                # El archivo de imagen se llama Ataque_arena.png, Ataque_roca.png, etc.
                ruta = os.path.join(ruta_base, f"{nombre_archivo}.png")
                self.imagenes_proyectiles[tipo_torre] = pygame.image.load(ruta).convert_alpha()

            print("🖼️ Todas las imágenes de juego cargadas correctamente.")
            
        except Exception as e:
            print(f"❌ Error crítico cargando una imagen: {e}. Asegúrate de que todas están en la carpeta 'imagenes'.")


    # === MÉTODOS DE CREACIÓN DE BOTONES ===
    
    def crearBotonReiniciar(self):
        """Crea el botón REINICIAR JUEGO, centrado en la pantalla para la derrota."""
        boton = Boton(
            self.ancho // 2, 
            self.alto // 2 + 100, 
            350,  
            80,   
            "REINICIAR",
            36
        )

        boton.colorNormal = (0, 150, 0)
        boton.colorHover = (0, 200, 0)
        boton.colorBorde = self.colorFondo.obtenerColorBorde()
        boton.colorTexto = (255, 255, 255)

        return boton

    def crearBotonesTorres(self):
        """Crea los botones de las 4 torres con el layout 2x2"""
        botones = []

        baseX = 850    
        baseY = 250    
        espacioX = 240  
        espacioY = 120  

        infoBotones = [
            ("T1", "Arena", self.rooks.torreArena),
            ("T2", "Roca", self.rooks.torreRoca),
            ("T3", "Fuego", self.rooks.torreFuego),
            ("T4", "Agua", self.rooks.torreAgua)
        ]

        for i, (id_torre, nombre, datos) in enumerate(infoBotones):
            columna = i % 2
            fila = i // 2
            
            texto_boton = f"{nombre}\n₡{datos['valor']}"

            boton = Boton(
                baseX + columna * espacioX,
                baseY + fila * espacioY,
                220, 90, texto_boton, 28
            )

            boton.colorNormal = self.colorFondo.obtenerColorBoton()
            boton.colorHover = self.colorFondo.obtenerColorHoverBoton()
            boton.colorBorde = self.colorFondo.obtenerColorBorde()
            boton.colorTexto = self.colorFondo.obtenerColorTextoBoton()

            boton.id_torre = id_torre
            botones.append(boton)

        return botones

    def crearBotonIniciar(self):
        """Crea el botón INICIAR JUEGO"""
        boton = Boton(
            925, 480, 300, 80, "INICIAR JUEGO", 32
        )

        boton.colorNormal = self.colorFondo.obtenerColorBoton()
        boton.colorHover = self.colorFondo.obtenerColorHoverBoton()
        boton.colorBorde = self.colorFondo.obtenerColorBorde()
        boton.colorTexto = self.colorFondo.obtenerColorTextoBoton()

        return boton

    # === MÉTODOS DE LÓGICA DE JUEGO ===
    
    def reiniciarJuego(self):
        """Reinicia el juego volviendo al estado de CONFIGURACION."""
        
        # 1. Resetear variables de juego
        self.matriz = [[None for _ in range(self.columnas)] for _ in range(self.filas)]
        self.torreSeleccionada = None
        self.dinero = 350
        self.gestorAvatars = None
        self.gestorTorres = None
        self.juegoIniciado = False
        
        # Resetear sistema de monedas
        self.monedas = []
        self.puntosParaMonedas = 0
        
        # 2. Resetear estados
        self.estadoJuego = "CONFIGURACION"
        print("🔄 Juego reiniciado. Volviendo a la fase de configuración.")

    def iniciarJuego(self):
        """Inicia el juego (crea gestores y comienza spawneo)"""
        gridConfig = {
            "gridX": self.tableroX + self.gridOffsetX,
            "gridY": self.tableroY + self.gridOffsetY,
            "anchoCasilla": self.anchoCasilla + self.gridAnchoExtra,
            "altoCasilla": self.altoCasilla + self.gridAltoExtra
        }
        
        # PASAR IMÁGENES AL GESTOR DE TORRES
        self.gestorTorres = GestorTorres(
            self.matriz, self.datosTorres, gridConfig, 
            torre_imagenes=self.imagenes_torres,
            proyectil_imagenes=self.imagenes_proyectiles
        )
        
        # PASAR IMÁGENES AL GESTOR DE AVATARS
        self.gestorAvatars = GestorAvatars(
            gridConfig, self.dificultad, FPS, 
            avatar_imagenes=self.imagenes_avatars,
            proyectil_imagenes=self.imagenes_proyectiles 
        )
        
        self.gestorAvatars.iniciar()
        
        self.juegoIniciado = True
        self.estadoJuego = "JUGANDO"
        print(f"🎮 Juego iniciado en dificultad {self.dificultad}!")
    
    def actualizarJuego(self):
        """Actualiza la lógica del juego cada frame"""
        if self.estadoJuego != "JUGANDO":
            return
        
        self.gestorAvatars.actualizar(self.gestorTorres.torres)
        self.gestorTorres.actualizar(self.gestorAvatars.avatarsActivos, FPS)
        
        # Obtener puntos ganados este frame
        puntosFrame = self.gestorAvatars.obtenerYResetearPuntos()
        self.puntosParaMonedas += puntosFrame
        
        # Generar monedas cuando se alcance el umbral
        if self.puntosParaMonedas >= self.umbralMonedas:
            self.puntosParaMonedas -= self.umbralMonedas
            self.monedas.extend(generarMonedas())
            print(f"💰 ¡Monedas generadas! ({len(self.monedas)} monedas nuevas)")
        
        stats = self.gestorAvatars.obtenerEstadisticas()
        
        if stats["perdio"] or stats["gano"]:
            # Calcular puntaje usando el algoritmo del banquero
            puntaje = funcionDelBanquero(
                tempo=tempo,
                popularidad=popularidad,
                avatarsMatados=self.gestorAvatars.avatarsMatados,
                puntosParaMonedas=self.puntosParaMonedas,
                limiteMaximo=1000  # Ajustar según necesidad
            )
            
            # Guardar puntaje en el Hall of Fame
            nombreUsuario = self.usuarioTexto  # O implementar forma de obtener nombre real
            guardar_puntaje(
                puntaje=puntaje,
                usuario=nombreUsuario,
                tempo=tempo,
                popularidad=popularidad,
                avatarsMatados=self.gestorAvatars.avatarsMatados,
                puntosParaMonedas=self.puntosParaMonedas
            )
            
            # Actualizar estado según victoria/derrota
            if stats["perdio"]:
                print(f"💀 ¡PERDISTE! {stats['resultado']}")
                print(f"Puntaje final: {puntaje:.2f}")
                self.estadoJuego = "PERDIDO"
            else:
                print(f"🎉 ¡GANASTE! {stats['resultado']}")
                print(f"Puntaje final: {puntaje:.2f}")
                self.ejecutando = False
            
    def obtenerCasillaClick(self, mouseX, mouseY):
        """Convierte coordenadas de mouse a fila/columna"""
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
        """Coloca una torre en la casilla si es posible"""
        # Verificar estado actualizado de la matriz
        if self.matriz[fila][columna] is not None:
            print(f"Ya hay una torre ({self.matriz[fila][columna]}) en ({fila}, {columna})")
            return
        
        if self.torreSeleccionada is None:
            print("Selecciona una torre primero")
            return
        
        costo = self.datosTorres[self.torreSeleccionada]["valor"]
        
        if self.dinero >= costo:
            self.matriz[fila][columna] = self.torreSeleccionada
            self.dinero -= costo
            print(f"Torre {self.torreSeleccionada} colocada en ({fila}, {columna})")
            
            if self.juegoIniciado and self.gestorTorres:
                self.gestorTorres.agregarTorre(self.torreSeleccionada, fila, columna)
        else:
            print(f"Dinero insuficiente (tienes ₡{self.dinero}, necesitas ${costo})")
    
    def quitarTorre(self, fila, columna):
        """Quita una torre y devuelve el dinero"""
        if self.matriz[fila][columna] is not None:
            idTorre = self.matriz[fila][columna]
            valorDevolver = self.datosTorres[idTorre]["valor"]
            self.dinero += valorDevolver
            self.matriz[fila][columna] = None
            print(f"Torre {idTorre} removida, +${valorDevolver}")
            
            if self.juegoIniciado and self.gestorTorres:
                self.gestorTorres.eliminarTorre(fila, columna)

    # === MANEJO DE EVENTOS ===
    def manejarEventos(self):
        """Procesa todos los eventos de entrada"""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.ejecutando = False
                self.volver = False
                # Pausar música antes de cerrar
                if self.spotify:
                    try:
                        print("DEBUG: Pausando música al cerrar el juego (QUIT)")
                        self.spotify.pausarMusica()
                    except Exception as e:
                        print(f"Error al pausar música: {e}")
                pygame.quit()
                sys.exit()
            
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.ejecutando = False
                    self.volver = True
                    # Pausar música al presionar ESC
                    if self.spotify:
                        try:
                            print("DEBUG: Pausando música al salir con ESC")
                            self.spotify.pausarMusica()
                        except Exception as e:
                            print(f"Error al pausar música: {e}")

            mouseX, mouseY = pygame.mouse.get_pos()
            distancia = ((mouseX - self.usuarioCentroX) ** 2 + 
                         (mouseY - self.usuarioCentroY) ** 2) ** 0.5
            esta_sobre_usuario = distancia <= self.usuarioRadio

            if evento.type == pygame.MOUSEMOTION:
                self.usuarioHover = esta_sobre_usuario
                
                # Manejo de hover de botones de torres e iniciar (si aplica)
                if self.estadoJuego in ("CONFIGURACION", "JUGANDO"):
                    for boton in self.botonesTorres:
                        boton.manejarEvento(evento)
                    
                    if self.estadoJuego == "CONFIGURACION":
                        self.botonIniciar.manejarEvento(evento)
                
                if self.estadoJuego == "PERDIDO":
                    self.botonReiniciar.manejarEvento(evento)

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                
                # Click en botón de Usuario
                if esta_sobre_usuario:
                    print("Abriendo perfil de usuario...")
                    try:
                        # Pausar música antes de abrir userPage
                        if self.spotify:
                            try:
                                print("DEBUG: Pausando música al abrir perfil de usuario")
                                self.spotify.pausarMusica()
                            except Exception as e:
                                print(f"Error al pausar música: {e}")
                        
                        # Guardar el estado actual del juego si es necesario
                        pygame.quit()
                        
                        # Abrir userPage
                        userpage_path = os.path.join(carpeta_personalizacion, 'userPage.py')
                        runpy.run_path(userpage_path, run_name='__main__')
                        
                        # Cerrar el juego completamente
                        self.ejecutando = False
                        self.volver = False
                        sys.exit(0)
                        
                    except Exception as e:
                        print(f"Error al abrir perfil: {e}")
                        # Intentar reiniciar Pygame si falla
                        try:
                            pygame.init()
                            self.pantalla = pygame.display.set_mode((self.ancho, self.alto))
                        except:
                            self.ejecutando = False
                            self.volver = False
                    continue  # Importante: evitar que se procesen otros eventos

                # Lógica del estado PERDIDO (prioridad alta)
                if self.estadoJuego == "PERDIDO":
                    if self.botonReiniciar.manejarEvento(evento):
                        self.reiniciarJuego()
                        
                        continue

                # Lógica de SELECCIÓN de torres (en CONFIGURACION y JUGANDO)
                if self.estadoJuego in ("CONFIGURACION", "JUGANDO"):
                    for boton in self.botonesTorres:
                        if boton.manejarEvento(evento):
                            self.torreSeleccionada = boton.id_torre
                            print(f"Torre seleccionada: {self.torreSeleccionada}")
                            continue

                # Lógica de INICIAR JUEGO (solo en CONFIGURACION)
                if self.estadoJuego == "CONFIGURACION":
                    if self.botonIniciar.manejarEvento(evento):
                        self.iniciarJuego()
                        continue

                # Lógica de click en el tablero (Colocar/Quitar)
                if self.estadoJuego in ("CONFIGURACION", "JUGANDO"):
                    casilla = self.obtenerCasillaClick(mouseX, mouseY)
                    if casilla:
                        fila, columna = casilla
                        
                        if evento.button == 1:  # Click izquierdo: Colocar
                            self.colocarTorre(fila, columna)
                        elif evento.button == 3:  # Click derecho: Quitar
                            self.quitarTorre(fila, columna)
                
                # Detectar clicks en monedas (solo cuando está JUGANDO)
                if self.estadoJuego == "JUGANDO" and evento.button == 1:
                    puntosGanados = 0
                    tamañoCelda = self.anchoCasilla + self.gridAnchoExtra
                    offsetX = self.tableroX + self.gridOffsetX
                    offsetY = self.tableroY + self.gridOffsetY
                    
                    for moneda in self.monedas[:]:  
                        if moneda.verificarClick((mouseX, mouseY), tamañoCelda, offsetX, offsetY):
                            puntosGanados += moneda.valor
                            print(f"💰 ¡Moneda de {moneda.valor} recogida!")
                    
                    if puntosGanados > 0:
                        self.dinero += puntosGanados
                        # Eliminar monedas clickeadas
                        self.monedas = [m for m in self.monedas if not m.clickeada]

    # === MÉTODOS DE DIBUJO ===
    
    def dibujarPantallaDerrota(self):
        """Dibuja el overlay oscuro, el mensaje de derrota y el botón de Reiniciar."""
        
        # 1. Overlay oscuro
        overlay = pygame.Surface((self.ancho, self.alto))
        overlay.set_alpha(200) 
        overlay.fill((0, 0, 0))
        self.pantalla.blit(overlay, (0, 0))
        
        # 2. Mensaje "¡HAS PERDIDO!"
        fuenteMensaje = pygame.font.SysFont('Arial', 100, bold=True)
        mensaje = fuenteMensaje.render("¡HAS PERDIDO!", True, (255, 0, 0)) 
        
        mensajeRect = mensaje.get_rect(center=(self.ancho // 2, self.alto // 2 - 50))
        self.pantalla.blit(mensaje, mensajeRect)
        
        # 3. Botón Reiniciar
        self.botonReiniciar.dibujar(self.pantalla)

    def dibujarDinero(self):
        """Muestra el dinero actual del jugador debajo del botón Iniciar Juego"""
        texto = f"Dinero: ₡{self.dinero}"
        color = self.colorFondo.obtenerColorTitulo()
        fuenteDinero = pygame.font.SysFont('Arial', 36, bold=True)
        render = fuenteDinero.render(texto, True, color)

        # La posición es relativa al botón iniciar, aunque este no se dibuje en JUGANDO
        x = self.botonIniciar.rect.centerx
        y = self.botonIniciar.rect.bottom + 40  
        rect = render.get_rect(center=(x, y))
        self.pantalla.blit(render, rect)

    def dibujarEstadisticas(self):
        """Dibuja información del juego en curso debajo del Dinero"""
        if self.estadoJuego != "JUGANDO":
            return
        
        stats = self.gestorAvatars.obtenerEstadisticas()
        
        y = self.botonIniciar.rect.bottom + 40 + 50 
        
        color = self.colorFondo.obtenerColorTitulo()
        fuenteStats = self.fuenteInfo 
        x_base = self.botonIniciar.rect.centerx - 100 
        
        # Dificultad
        textoDif = f"Dificultad: {stats['dificultad']}"
        renderDif = fuenteStats.render(textoDif, True, color)
        self.pantalla.blit(renderDif, (x_base, y))
        y += 35
        
        # Tiempo restante
        textoTiempo = f"Tiempo: {stats['tiempoRestanteStr']}"
        colorTiempo = (255, 0, 0) if stats['tiempoRestante'] < 10 else color
        renderTiempo = fuenteStats.render(textoTiempo, True, colorTiempo)
        self.pantalla.blit(renderTiempo, (x_base, y))
        y += 35
        
        # Enemigos vivos
        textoEnemigos = f"Enemigos: {stats['avatarsVivos']}"
        renderEnemigos = fuenteStats.render(textoEnemigos, True, color)
        self.pantalla.blit(renderEnemigos, (x_base, y))
        y += 35
        
        # Torres restantes
        textoTorres = f"Torres: {len(self.gestorTorres.torres)}"
        renderTorres = fuenteStats.render(textoTorres, True, color)
        self.pantalla.blit(renderTorres, (x_base, y))

    def dibujarBotonUsuario(self):
        """Dibuja el botón redondo de usuario"""
        color = self.colorUsuarioHover if self.usuarioHover else self.colorUsuarioNormal
        
        pygame.draw.circle(self.pantalla, color, (self.usuarioCentroX, self.usuarioCentroY), self.usuarioRadio)
        pygame.draw.circle(self.pantalla, self.colorUsuarioBorde, 
                           (self.usuarioCentroX, self.usuarioCentroY), self.usuarioRadio, 3)
        
        textoSurface = self.fuenteUsuario.render(self.usuarioTexto, True, self.colorUsuarioTexto)
        textoRect = textoSurface.get_rect(center=(self.usuarioCentroX, self.usuarioCentroY))
        self.pantalla.blit(textoSurface, textoRect)
    
    def dibujarTorresMatriz(self):
        """Dibuja las torres colocadas antes de iniciar usando imágenes."""
        gridX = self.tableroX + self.gridOffsetX
        gridY = self.tableroY + self.gridOffsetY
        anchoCasilla = self.anchoCasilla + self.gridAnchoExtra
        altoCasilla = self.altoCasilla + self.gridAltoExtra
        
        mapa_torres = {
            "T1": "Torre_arena", "T2": "Torre_roca", 
            "T3": "Torre_fuego", "T4": "Torre_agua"
        }
        
        for fila in range(self.filas):
            for columna in range(self.columnas):
                idTorre = self.matriz[fila][columna]
                
                if idTorre:
                    nombre_imagen = mapa_torres.get(idTorre)
                    
                    if nombre_imagen and nombre_imagen in self.imagenes_torres:
                        imagen = self.imagenes_torres[nombre_imagen]
                        # Redimensionar para previsualización 
                        radio_visual = 50 
                        imagen_escalada = pygame.transform.scale(imagen, (radio_visual, radio_visual))

                        x = gridX + columna * anchoCasilla + anchoCasilla / 2
                        y = gridY + fila * altoCasilla + altoCasilla / 2
                        
                        rect = imagen_escalada.get_rect(center=(int(x), int(y)))
                        self.pantalla.blit(imagen_escalada, rect)
                    else:
                        # Fallback: Dibuja un círculo si la imagen falla
                        color = (255, 0, 0) 
                        x = gridX + columna * anchoCasilla + anchoCasilla / 2
                        y = gridY + fila * altoCasilla + altoCasilla / 2
                        pygame.draw.circle(self.pantalla, color, (int(x), int(y)), 25)
        
    def dibujar(self):
        """Dibuja todos los elementos en pantalla (Un solo frame)"""
        
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

        # 2. Tablero, grid
        if self.imagenTablero:
            self.pantalla.blit(self.imagenTablero, (self.tableroX, self.tableroY))
        
        # 3. Dibujo de Torres/Avatars
        if self.estadoJuego == "CONFIGURACION":
            self.dibujarTorresMatriz() 
        elif self.estadoJuego in ("JUGANDO", "PERDIDO"):
            if self.gestorTorres:
                self.gestorTorres.dibujar(self.pantalla)
            if self.gestorAvatars:
                self.gestorAvatars.dibujar(self.pantalla)
            
            # Dibujar monedas (solo en estado JUGANDO)
            if self.estadoJuego == "JUGANDO":
                tamañoCelda = self.anchoCasilla + self.gridAnchoExtra
                offsetX = self.tableroX + self.gridOffsetX
                offsetY = self.tableroY + self.gridOffsetY
                for moneda in self.monedas:
                    moneda.dibujar(self.pantalla, tamañoCelda, offsetX, offsetY)


        # 4. Botones rectangulares (Se dibujan en CONFIGURACION Y JUGANDO)
        if self.estadoJuego in ("CONFIGURACION", "JUGANDO"):
            for boton in self.botonesTorres:
                boton.dibujar(self.pantalla)
                if hasattr(boton, 'id_torre') and boton.id_torre == self.torreSeleccionada:
                    pygame.draw.rect(self.pantalla, (255, 215, 0), boton.rect, 5) 
            
        # Botón INICIAR solo en CONFIGURACION
        if self.estadoJuego == "CONFIGURACION":
            self.botonIniciar.dibujar(self.pantalla) 
        
        # 5. Dinero y Estadísticas 
        if self.estadoJuego != "PERDIDO":
            self.dibujarDinero()
            if self.estadoJuego == "JUGANDO":
                self.dibujarEstadisticas()
        
        # 6. DIBUJO DEL BOTÓN "USUARIO"
        self.dibujarBotonUsuario()

        # 7. PANTALLA DE DERROTA
        if self.estadoJuego == "PERDIDO":
            self.dibujarPantallaDerrota()
        
        # Actualizar pantalla
        pygame.display.flip()

    # === LOOP PRINCIPAL ===
    def ejecutar(self):
        """
        Loop principal de la pantalla
        """
        while self.ejecutando:
            self.manejarEventos()
            self.actualizarJuego()
            self.dibujar()
            self.reloj.tick(FPS)
        
        return self.volver