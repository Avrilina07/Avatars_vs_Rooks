# ---MANEJO DE TODA LA LÓGICA DE FUNCIONAMIENTO DE AVATARS Y TORRES---

import pygame
import random
from clasesAvatarsRooks import Avatars, Rooks


class Proyectil:
    """Representa un proyectil disparado por un avatar o torre"""
    
    def __init__(self, x, y, daño, tipo, esAvatar=True):
        self.x = x
        self.y = y
        self.daño = daño
        self.tipo = tipo
        self.activo = True
        self.esAvatar = esAvatar  # True si lo disparó un avatar, False si fue una torre
        
        # Velocidad del proyectil (dirección opuesta según quién dispara)
        self.velocidad = -5 if esAvatar else 5  # Avatars hacia arriba (-), Torres hacia abajo (+)
        
        self.radio = 5
    
    def actualizar(self):
        """Mueve el proyectil"""
        if self.activo:
            self.y += self.velocidad
            
            # Desactivar si sale de pantalla (ajustar según tu altura de pantalla)
            if self.y < 0 or self.y > 900:
                self.activo = False
    
    def dibujar(self, pantalla):
        """Dibuja el proyectil"""
        if not self.activo:
            return
        
        # Colores para avatars
        coloresAvatars = {
            "flechador": (255, 215, 0),    # Amarillo dorado
            "escudero": (100, 149, 237),   # Azul aciano
            "lenador": (139, 69, 19),      # Marrón
            "canibal": (220, 20, 60)       # Rojo carmesí
        }
        
        # Colores para torres
        coloresTorres = {
            "T1": (255, 235, 150),  # Arena - amarillo claro
            "T2": (200, 200, 200),  # Roca - gris claro
            "T3": (255, 140, 0),    # Fuego - naranja oscuro
            "T4": (0, 191, 255)     # Agua - azul cielo profundo
        }
        
        if self.esAvatar:
            color = coloresAvatars.get(self.tipo, (255, 255, 255))
        else:
            color = coloresTorres.get(self.tipo, (255, 255, 255))
        
        pygame.draw.circle(pantalla, color, (int(self.x), int(self.y)), self.radio)
        pygame.draw.circle(pantalla, (0, 0, 0), (int(self.x), int(self.y)), self.radio, 1)
    
    def colisionaConTorre(self, torre):
        """Verifica colisión con una torre (solo proyectiles de avatars)"""
        if not self.activo or not torre.viva or not self.esAvatar:
            return False
        
        radioTorre = 25
        distancia = ((self.x - torre.x)**2 + (self.y - torre.y)**2)**0.5
        return distancia < (self.radio + radioTorre)
    
    def colisionaConAvatar(self, avatar):
        """Verifica colisión con un avatar (solo proyectiles de torres)"""
        if not self.activo or not avatar.vivo or self.esAvatar:
            return False
        
        radioAvatar = 20
        distancia = ((self.x - avatar.x)**2 + (self.y - avatar.y)**2)**0.5
        return distancia < (self.radio + radioAvatar)


class Avatar:
    """Representa un avatar enemigo que avanza hacia arriba"""
    
    def __init__(self, tipo, fila, columna, datosAvatar, gridConfig):

        self.tipo = tipo
        self.fila = fila
        self.columna = columna
        
        # Estadísticas del avatar
        self.vidaMax = datosAvatar["vida"]
        self.vidaActual = datosAvatar["vida"]
        self.daño = datosAvatar["daño"]
        self.duracionAparicion = datosAvatar["duracion_aparicion"]  
        
        # Cada avatar tiene su propio tiempo de ataque aleatorio
        self.duracionAtaque = random.randint(
            datosAvatar.get("duracion_ataque_min", 1),
            datosAvatar.get("duracion_ataque_max", 5)
        )
        
        print(f"🎯 {tipo} creado con duracion_ataque = {self.duracionAtaque}s")
        
        # Estado del avatar
        self.vivo = True
        self.apareciendo = True  # Estado de aparición
        self.tiempoAparicion = 0  # Contador para animación de aparición
        self.tiempoDesdeUltimoDisparo = 0  # Contador para disparar
        
        # Posición visual (calculada desde el grid)
        self.calcularPosicion(gridConfig)
        
        # velocidad fija
        self.velocidad = 0.5  # Píxeles por frame (ajustar si es muy lento/rápido)
        
        # Lista de proyectiles disparados por este avatar
        self.proyectiles = []
        
        # Guardar configuración del grid
        self.gridConfig = gridConfig
    
    def calcularPosicion(self, gridConfig):
        """Calcula la posición visual del avatar en el grid"""
        gridX = gridConfig["gridX"]
        gridY = gridConfig["gridY"]
        anchoCasilla = gridConfig["anchoCasilla"]
        altoCasilla = gridConfig["altoCasilla"]
        
        # Posición centrada en la casilla
        self.x = gridX + (self.columna * anchoCasilla) + (anchoCasilla / 2)
        self.y = gridY + (self.fila * altoCasilla) + (altoCasilla / 2)
        
        # Guardar dimensiones de casilla para movimiento
        self.anchoCasilla = anchoCasilla
        self.altoCasilla = altoCasilla
    
    def actualizar(self, fps, torres=None):
        """
        Actualiza el estado del avatar
        
        Args:
            fps: frames por segundo del juego (para calcular tiempos)
            torres: list de objetos Torre (opcional, para detectar colisiones)
        """
        if not self.vivo:
            return
        
        # Fase de aparición
        if self.apareciendo:
            self.tiempoAparicion += 1
            
            # Convertir duracion_aparicion (segundos) a frames
            if self.tiempoAparicion >= 3 * fps:
                self.apareciendo = False
                print(f"✨ {self.tipo} terminó de aparecer en columna {self.columna}")
            return  # No se mueve ni dispara durante aparición
        
        # Movimiento hacia arriba (solo si no hay colisión con torre)
        if torres:
            self.moverConColision(torres)
        else:
            self.mover()
        
        # Sistema de disparo
        self.actualizarDisparo(fps)
        
        # Actualizar proyectiles
        for proyectil in self.proyectiles[:]:
            proyectil.actualizar()
            if not proyectil.activo:
                self.proyectiles.remove(proyectil)
    
    def mover(self):
        """Mueve el avatar hacia arriba"""
        self.y -= self.velocidad  # Negativo = hacia arriba
        
        # Actualizar posición en la matriz cuando cambia de casilla
        gridY = self.gridConfig["gridY"]
        filaActual = int((self.y - gridY) / self.altoCasilla)
        
        if filaActual != self.fila and filaActual >= 0:
            self.fila = filaActual
    
    def moverConColision(self, torres):
        
        """Mueve el avatar hacia arriba, pero se detiene si colisiona con una torre"""
        
        # Guardar posición actual
        yAnterior = self.y
        
        # Intentar moverse
        self.y -= self.velocidad
        
        # Verificar colisión con torres
        for torre in torres:
            if not torre.viva:
                continue
            
            # Verificar si avatar colisiona con torre
            radioAvatar = 20
            radioTorre = 25
            distancia = ((self.x - torre.x)**2 + (self.y - torre.y)**2)**0.5
            
            if distancia < (radioAvatar + radioTorre):
                # Colisión detectada: restaurar posición anterior
                self.y = yAnterior
                print(f"🚫 {self.tipo} bloqueado por torre {torre.tipo} en ({torre.fila}, {torre.columna})")
                return  # No actualizar fila
        
        # Si no hubo colisión, actualizar posición en la matriz
        gridY = self.gridConfig["gridY"]
        filaActual = int((self.y - gridY) / self.altoCasilla)
        
        if filaActual != self.fila and filaActual >= 0:
            self.fila = filaActual
    
    def actualizarDisparo(self, fps):
        """Maneja el sistema de disparo del avatar"""
        self.tiempoDesdeUltimoDisparo += 1
        
        # Para duración de ataque del avatar
        framesPorDisparo = self.duracionAtaque * fps
        
        if self.tiempoDesdeUltimoDisparo >= framesPorDisparo:
            self.disparar()
            self.tiempoDesdeUltimoDisparo = 0
    
    def disparar(self):
        """Crea un proyectil que va hacia arriba"""
        proyectil = Proyectil(self.x, self.y, self.daño, self.tipo)
        self.proyectiles.append(proyectil)
        print(f"🏹 {self.tipo} disparó desde fila {self.fila} (cada {self.duracionAtaque}s)")
    
    def recibirDaño(self, daño):
        """Recibe daño y verifica si muere"""
        self.vidaActual -= daño
        
        if self.vidaActual <= 0:
            self.vivo = False
            print(f"💀 {self.tipo} eliminado en fila {self.fila}")
            return True  # Retorna True si murió
        
        return False
    
    def dibujar(self, pantalla):
        """Dibuja el avatar y sus proyectiles"""
        if not self.vivo:
            return
        
        # Colores de avatars
        colores = {
            "flechador": (255, 215, 0),    # Amarillo dorado
            "escudero": (100, 149, 237),   # Azul aciano
            "lenador": (139, 69, 19),      # Marrón silla de montar
            "canibal": (220, 20, 60)       # Rojo carmesí
        }
        
        # Usar get() con color por defecto blanco si no encuentra
        color = colores.get(self.tipo, (255, 255, 255))
        
        # Imprimir para debug (quitar después)
        if color == (255, 255, 255):
            print(f"⚠️ Avatar tipo '{self.tipo}' no tiene color asignado")
        
        # Tamaño del avatar
        radio = 20
        
        if self.apareciendo:
            # Efecto de pulsación durante aparición
            progreso = self.tiempoAparicion / (self.duracionAparicion * 60)  # 0.0 a 1.0
            radioAparicion = int(radio * progreso)
            
            if radioAparicion > 0:
                pygame.draw.circle(pantalla, color, (int(self.x), int(self.y)), radioAparicion)
                pygame.draw.circle(pantalla, (255, 255, 255), (int(self.x), int(self.y)), radioAparicion, 2)
        else:
            # Dibujar avatar
            pygame.draw.circle(pantalla, color, (int(self.x), int(self.y)), radio)
            pygame.draw.circle(pantalla, (255, 255, 255), (int(self.x), int(self.y)), radio, 2)
            
            # Dibujar barra de vida
            self.dibujarBarraVida(pantalla, radio)
        
        # Dibujar proyectiles
        for proyectil in self.proyectiles:
            proyectil.dibujar(pantalla)
    
    def dibujarBarraVida(self, pantalla, radio):
        """Dibuja barra de vida sobre el avatar"""
        anchoBarraMax = radio * 2
        altoBarraVida = 5
        
        # Posición de la barra (encima del avatar)
        x = self.x - radio
        y = self.y - radio - 10
        
        # Calcular porcentaje de vida
        porcentajeVida = max(0, self.vidaActual / self.vidaMax)
        anchoBarraActual = anchoBarraMax * porcentajeVida
        
        # Fondo de la barra (rojo)
        pygame.draw.rect(pantalla, (255, 0, 0), 
                        (x, y, anchoBarraMax, altoBarraVida))
        
        # Barra de vida actual (verde)
        pygame.draw.rect(pantalla, (0, 255, 0), 
                        (x, y, anchoBarraActual, altoBarraVida))
        
        # Borde
        pygame.draw.rect(pantalla, (255, 255, 255), 
                        (x, y, anchoBarraMax, altoBarraVida), 1)
    
    def llegoPantallaArriba(self):
        """Verifica si el avatar llegó a la parte superior (derrota)"""
        # Límite superior del grid
        limiteY = self.gridConfig["gridY"]
        return self.y <= limiteY


class Torre:
    """Representa una torre colocada en el tablero"""
    
    def __init__(self, tipo, fila, columna, datosTorre, gridConfig):

        self.tipo = tipo
        self.fila = fila
        self.columna = columna
        
        # Estadísticas de la torre
        self.vidaMax = datosTorre["vida"]
        self.vidaActual = datosTorre["vida"]
        self.daño = datosTorre["daño"]
        self.valor = datosTorre["valor"]
        
        # Valor random para cada torre
        self.duracionAtaque = random.randint(
            datosTorre.get("duracion_ataque_min", 1),
            datosTorre.get("duracion_ataque_max", 5)
        )
        
        # Estado
        self.viva = True
        self.tiempoAtaque = 0
        
        # ⬅️ NUEVO: Lista de proyectiles
        self.proyectiles = []
        
        # Calcular posición visual
        self.calcularPosicion(gridConfig)
        
        print(f"🏰 Torre {tipo} creada en ({fila}, {columna}) - Ataque cada {self.duracionAtaque}s")
    
    def calcularPosicion(self, gridConfig):
        
        """Calcula posición visual en el grid"""
        
        gridX = gridConfig["gridX"]
        gridY = gridConfig["gridY"]
        anchoCasilla = gridConfig["anchoCasilla"]
        altoCasilla = gridConfig["altoCasilla"]
        
        self.x = gridX + (self.columna * anchoCasilla) + (anchoCasilla / 2)
        self.y = gridY + (self.fila * altoCasilla) + (altoCasilla / 2)
    
    def actualizar(self, avatars, fps):
        """Actualiza la torre (dispara proyectiles a avatars en rango)"""
        if not self.viva:
            return
        
        # Actualizar proyectiles existentes
        for proyectil in self.proyectiles[:]:
            proyectil.actualizar()
            if not proyectil.activo:
                self.proyectiles.remove(proyectil)
        
        # Buscar avatars en rango
        avatarsEnRango = []
        for avatar in avatars:
            if not avatar.vivo or avatar.apareciendo:
                continue
            
            if self.dentroRango(avatar):
                avatarsEnRango.append(avatar)
        
        # Si hay avatars, disparar al más cercano
        if avatarsEnRango:
            avatarsEnRango.sort(key=lambda a: abs(a.fila - self.fila))
            self.atacar(avatarsEnRango[0], fps)
    
    def atacar(self, avatar, fps):
        """Dispara un proyectil hacia el avatar"""
        self.tiempoAtaque += 1
        
        framesPorAtaque = self.duracionAtaque * fps
        
        if self.tiempoAtaque >= framesPorAtaque:
            # Crear proyectil
            proyectil = Proyectil(self.x, self.y, self.daño, self.tipo, esAvatar=False)
            self.proyectiles.append(proyectil)
            
            self.tiempoAtaque = 0
            print(f"🏹 Torre {self.tipo} ({self.fila}, {self.columna}) disparó a {avatar.tipo}")
    
    def dentroRango(self, avatar):
        """Verifica si un avatar está en la misma columna que la torre"""
        # Las torres solo atacan avatars de su columna
        return self.columna == avatar.columna
    
    def recibirDaño(self, daño):
        """Recibe daño de proyectiles"""
        self.vidaActual -= daño
        
        if self.vidaActual <= 0:
            self.viva = False
            print(f"💥 Torre {self.tipo} destruida en ({self.fila}, {self.columna})")
            return True
        
        return False
    
    def dibujar(self, pantalla):
        """Dibuja la torre y sus proyectiles.
        Los siguientes datos se pueden modificar para añadir las imágenes finales para el juego"""
        if not self.viva:
            return
        
        # Colores por tipo de torre
        colores = {
            "T1": (194, 178, 128),  # Arena (beige)
            "T2": (128, 128, 128),  # Roca (gris)
            "T3": (255, 100, 0),    # Fuego (naranja)
            "T4": (0, 100, 255)     # Agua (azul)
        }
        
        color = colores.get(self.tipo, (255, 255, 255))
        
        # Tamaño de la torre
        radio = 25
        
        # Dibujar torre
        pygame.draw.circle(pantalla, color, (int(self.x), int(self.y)), radio)
        pygame.draw.circle(pantalla, (0, 0, 0), (int(self.x), int(self.y)), radio, 3)
        
        # Dibujar barra de vida
        self.dibujarBarraVida(pantalla, radio)
        
        # Dibujar rango de ataque (opcional para debug) (quitar el # al siguiente comentario si se quiere aplicar)
        # self.dibujarRangoAtaque(pantalla)
        
        # Dibujar proyectiles
        for proyectil in self.proyectiles:
            proyectil.dibujar(pantalla)
    
    def dibujarBarraVida(self, pantalla, radio):
        """Dibuja barra de vida sobre la torre"""
        anchoBarraMax = radio * 2
        altoBarraVida = 6
        
        x = self.x - radio
        y = self.y - radio - 15
        
        porcentajeVida = max(0, self.vidaActual / self.vidaMax)
        anchoBarraActual = anchoBarraMax * porcentajeVida
        
        # Fondo (rojo)
        pygame.draw.rect(pantalla, (255, 0, 0), (x, y, anchoBarraMax, altoBarraVida))
        
        # Vida actual (verde)
        pygame.draw.rect(pantalla, (0, 255, 0), (x, y, anchoBarraActual, altoBarraVida))
        
        # Borde
        pygame.draw.rect(pantalla, (255, 255, 255), (x, y, anchoBarraMax, altoBarraVida), 2)
    
    def dibujarRangoAtaque(self, pantalla):
        """Dibuja el rango de ataque (para debug)"""
        # Calcular el área del rango
        gridX = self.gridConfig.get("gridX", 0)
        gridY = self.gridConfig.get("gridY", 0)
        anchoCasilla = self.gridConfig.get("anchoCasilla", 100)
        altoCasilla = self.gridConfig.get("altoCasilla", 100)
        
        # Dibujar rectángulo del rango
        x1 = gridX + (self.columna - self.rangoAtaque) * anchoCasilla
        y1 = gridY + (self.fila - self.rangoAtaque) * altoCasilla
        ancho = (2 * self.rangoAtaque + 1) * anchoCasilla
        alto = (2 * self.rangoAtaque + 1) * altoCasilla
        
        pygame.draw.rect(pantalla, (255, 255, 0), (x1, y1, ancho, alto), 2)


class GestorAvatars:
    """Gestiona la aparición, movimiento y ataques de todos los avatars"""
    
    def __init__(self, gridConfig, dificultad="Facil", fps=60):

        self.gridConfig = gridConfig
        self.fps = fps
        self.avatarsActivos = []
        
        # Config por dificultad
        self.dificultad = dificultad
        self.configurarDificultad()
        
        # Estado del juego
        self.juegoActivo = False
        self.jugadorPerdio = False
        self.jugadorGano = False
        self.causaResultado = ""
        
        # Temporizador de partida
        self.tiempoTranscurrido = 0  # En frames
        self.tiempoLimiteFrames = self.tiempoLimite * fps  # Convertir a frames
        
        # Control de spawn
        self.tiempoSpawn = 0
        
        # Instanciar clase Avatars para obtener datos
        self.datosAvatars = Avatars()
        
        # Probabilidades de aparición (puede modificarse o eliminarse según preferencia del cliente)
        self.probabilidades = {
            "flechador": 40,
            "escudero": 30,
            "lenador": 20,
            "canibal": 10
        }
    
    def configurarDificultad(self):
        """Configura parámetros según la dificultad"""
        configuraciones = {
            
            # Intervalos de spawn ya calculados para no calcularlos cada vez que se necesite
            # Sujeto a cambios según gusto del cliente
            
            "Facil": {
                "tiempoLimite": 90,      # 1:30 minutos
                "intervaloSpawn": 3.0    # 3 segundos base
            },
            "Intermedio": {
                "tiempoLimite": 120,     # 2:00 minutos
                "intervaloSpawn": 2.4    # 3 * 0.80 = 2.4 segundos (spawn 25% más rápido)
            },
            "Dificil": {
                "tiempoLimite": 150,     # 2:30 minutos
                "intervaloSpawn": 1.92   # 2.4 * 0.80 = 1.92 segundos (spawn 50% más rápido que Fácil)
            }
        }
        
        config = configuraciones.get(self.dificultad, configuraciones["Facil"])
        
        self.tiempoLimite = config["tiempoLimite"]
        self.intervaloSpawn = int(config["intervaloSpawn"] * self.fps)  # Convertir a frames
        
        print(f"⚙️ Dificultad: {self.dificultad}")
        print(f"⏱️ Tiempo límite: {self.tiempoLimite}s ({self.tiempoLimite//60}:{self.tiempoLimite%60:02d})")
        print(f"👥 Intervalo spawn: {config['intervaloSpawn']:.2f}s")
    
    def iniciar(self):
        """Inicia el sistema de spawneo"""
        self.juegoActivo = True
        self.tiempoTranscurrido = 0
        print(f"🎮 Juego iniciado - {self.dificultad}")
    
    def actualizar(self, torres):
        
        """Actualiza todos los avatars y sus proyectiles"""
        
        if not self.juegoActivo:
            return
        
        # Actualiza temporizador
        self.tiempoTranscurrido += 1
        
        # Verifica victoria
        if self.tiempoTranscurrido >= self.tiempoLimiteFrames:
            self.jugadorGano = True
            self.causaResultado = f"¡Sobreviviste {self.tiempoLimite}s!"
            self.juegoActivo = False
            print(f"🎉 ¡VICTORIA! {self.causaResultado}")
            return
        
        # Spawn de nuevos avatars
        self.actualizarSpawn()
        
        # Actualizar cada avatar
        for avatar in self.avatarsActivos[:]:
            if not avatar.vivo:
                self.avatarsActivos.remove(avatar)
                continue
            
            # Actualizar avatar pasando las torres para detección de colisiones
            avatar.actualizar(self.fps, torres)
            
            # Condición de derrota
            if avatar.llegoPantallaArriba():
                self.jugadorPerdio = True
                self.causaResultado = f"Un {avatar.tipo} llegó a la base"
                self.juegoActivo = False
                print(f"💀 ¡DERROTA! {self.causaResultado}")
                return
        
        # Verificar colisiones de proyectiles de avatars con torres
        for avatar in self.avatarsActivos:
            for proyectil in avatar.proyectiles:
                for torre in torres:
                    if proyectil.colisionaConTorre(torre):
                        torre.recibirDaño(proyectil.daño)
                        proyectil.activo = False
                        print(f"💥 Proyectil de {avatar.tipo} impactó torre {torre.tipo}")
                        break
        
        # Verificar colisiones de proyectiles de torres con avatars
        for torre in torres:
            for proyectil in torre.proyectiles:
                for avatar in self.avatarsActivos:
                    if proyectil.colisionaConAvatar(avatar):
                        avatar.recibirDaño(proyectil.daño)
                        proyectil.activo = False
                        print(f"💥 Proyectil de torre {torre.tipo} impactó {avatar.tipo}")
                        break
    
    def actualizarSpawn(self):
        """Controla el spawn continuo de avatars"""
        # Incrementar contador de spawn
        self.tiempoSpawn += 1
        
        # Spawnear nuevo avatar cada X frames
        if self.tiempoSpawn >= self.intervaloSpawn:
            self.spawnearAvatar()
            self.tiempoSpawn = 0
    
    def spawnearAvatar(self):
        """Crea un nuevo avatar en la fila inferior"""
        # 0-4 para tablero 5 columnas
        columna = random.randint(0, 4)
        
        # última fila para tablero 9 filas
        fila = 8
        
        # Seleccionar tipo según probabilidades
        tipo = self.seleccionarTipoAvatar()
        
        # Obtener datos del avatar
        datosAvatar = getattr(self.datosAvatars, tipo)
        
        # Crear avatar
        avatar = Avatar(tipo, fila, columna, datosAvatar, self.gridConfig)
        self.avatarsActivos.append(avatar)
        
        tiempoRestante = (self.tiempoLimiteFrames - self.tiempoTranscurrido) / self.fps
        print(f"👤 {tipo} spawneado en columna {columna} (Tiempo restante: {int(tiempoRestante)}s)")
    
    def seleccionarTipoAvatar(self):
        """Selecciona tipo de avatar según probabilidades"""
        # Crear lista ponderada
        tipos = []
        for tipo, prob in self.probabilidades.items():
            tipos.extend([tipo] * prob)
        
        return random.choice(tipos)
    
    def dibujar(self, pantalla):
        """Dibuja todos los avatars y sus proyectiles"""
        for avatar in self.avatarsActivos:
            avatar.dibujar(pantalla)
    
    def obtenerTiempoRestante(self):
        """Retorna el tiempo restante en segundos"""
        if not self.juegoActivo:
            return 0
        
        framesRestantes = self.tiempoLimiteFrames - self.tiempoTranscurrido
        return max(0, framesRestantes / self.fps)
    
    def obtenerEstadisticas(self):
        """Retorna estadísticas actuales del juego"""
        tiempoRestante = self.obtenerTiempoRestante()
        minutos = int(tiempoRestante // 60)
        segundos = int(tiempoRestante % 60)
        
        return {
            "dificultad": self.dificultad,
            "tiempoRestante": tiempoRestante,
            "tiempoRestanteStr": f"{minutos}:{segundos:02d}",
            "avatarsVivos": len(self.avatarsActivos),
            "juegoActivo": self.juegoActivo,
            "perdio": self.jugadorPerdio,
            "gano": self.jugadorGano,
            "resultado": self.causaResultado
        }


class GestorTorres:
    """Gestiona todas las torres del tablero"""
    
    def __init__(self, matriz, datosTorres, gridConfig):
        
        self.torres = []
        self.gridConfig = gridConfig
        self.datosTorres = datosTorres
        self.matriz = matriz  # Guardar referencia a la matriz
        self.crearTorresDesdeMatriz(matriz, datosTorres)
    
    def crearTorresDesdeMatriz(self, matriz, datosTorres):
        """Convierte la matriz de pantallaJuego en objetos Torre"""
        for fila in range(len(matriz)):
            for columna in range(len(matriz[0])):
                idTorre = matriz[fila][columna]
                
                if idTorre:  # Si hay una torre
                    datos = datosTorres[idTorre]
                    torre = Torre(idTorre, fila, columna, datos, self.gridConfig)
                    self.torres.append(torre)
        
        print(f"🏰 {len(self.torres)} torres creadas")
    
    def agregarTorre(self, idTorre, fila, columna):
        """
        Agrega una nueva torre durante la partida
        
        Args:
            idTorre: str - "T1", "T2", "T3", "T4"
            fila: int - fila en la matriz
            columna: int - columna en la matriz
        
        Returns:
            Torre: objeto torre creado, o None si falla
        """
        try:
            datos = self.datosTorres[idTorre]
            torre = Torre(idTorre, fila, columna, datos, self.gridConfig)
            self.torres.append(torre)
            print(f"🏰 Torre {idTorre} agregada en ({fila}, {columna}) durante partida")
            return torre
        except Exception as e:
            print(f"❌ Error agregando torre: {e}")
            return None
    
    def eliminarTorre(self, fila, columna):
        
        """Elimina una torre en una posición específica"""
        
        for torre in self.torres[:]:
            if torre.fila == fila and torre.columna == columna:
                self.torres.remove(torre)
                print(f"🗑️ Torre {torre.tipo} eliminada de ({fila}, {columna})")
                return True
        return False
    
    def actualizar(self, avatars, fps):
        
        """Actualiza todas las torres (las hace atacar)"""
        
        for torre in self.torres:
            if torre.viva:
                torre.actualizar(avatars, fps)
        
        # Limpieza de matriz
        torres_destruidas = [t for t in self.torres if not t.viva]
        for torre in torres_destruidas:
            # Limpiar la casilla en la matriz
            if self.matriz[torre.fila][torre.columna] == torre.tipo:
                self.matriz[torre.fila][torre.columna] = None
                print(f"🧹 Casilla ({torre.fila}, {torre.columna}) limpiada en la matriz")
        
        # Eliminar torres destruidas
        self.torres = [t for t in self.torres if t.viva]
    
    def dibujar(self, pantalla):
        """Dibuja todas las torres"""
        for torre in self.torres:
            torre.dibujar(pantalla)
    
    def verificarTodasDestruidas(self):
        """Verifica si todas las torres fueron destruidas"""
        return len(self.torres) == 0