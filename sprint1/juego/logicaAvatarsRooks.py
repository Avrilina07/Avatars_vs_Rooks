# --- MANEJO DE TODA LA LÓGICA DE FUNCIONAMIENTO DE AVATARS Y TORRES ---

import pygame
import random
from clasesAvatarsRooks import Avatars, Rooks 


class Proyectil:
    """Representa un proyectil disparado por un avatar o torre"""
    
    def __init__(self, x, y, daño, tipo, esAvatar=True, imagenes=None):
        self.x = x
        self.y = y
        self.daño = daño
        self.tipo = tipo
        self.activo = True
        self.esAvatar = esAvatar
        
        self.velocidad = -5 if esAvatar else 5
        self.radio = 5 
        
        # Configuración de imagen (solo para proyectiles de torre)
        self.imagen = None
        if not self.esAvatar and imagenes:
            # ✅ CORRECCIÓN FINAL: Se asume que la clave de la imagen es el TIPO de la torre ("T1", "T2", etc.)
            self.imagen = imagenes.get(self.tipo) 
            if self.imagen:
                self.imagen = pygame.transform.scale(self.imagen, (10, 10)) 

    def actualizar(self):
        """Mueve el proyectil y verifica límites de pantalla"""
        if self.activo:
            self.y += self.velocidad
            
            # Arreglo de límite de pantalla
            if self.y < 0 or self.y > 900: 
                self.activo = False
        
        # 🗑️ Se eliminó el bloque de código 'actualizar' duplicado que causó el error de indentación anterior.
    
    def dibujar(self, pantalla):
        """Dibuja el proyectil, usando imagen si existe, o círculo por defecto"""
        if not self.activo:
            return
        
        if self.imagen:
            # Dibujar imagen centrada
            rect = self.imagen.get_rect(center=(int(self.x), int(self.y)))
            pantalla.blit(self.imagen, rect)
        else:
            # Dibujo por defecto (proyectiles de avatars y torres sin imagen)
            if self.esAvatar:
                colores = {
                    "flechador": (255, 215, 0), "escudero": (100, 149, 237),
                    "lenador": (139, 69, 19), "canibal": (220, 20, 60)
                }
            else: # Colores por defecto para proyectiles de torre si no hay imagen
                 colores = {
                    "T1": (194, 178, 128), "T2": (128, 128, 128),  
                    "T3": (255, 100, 0), "T4": (0, 100, 255)    
                }

            color = colores.get(self.tipo, (255, 255, 255))
            pygame.draw.circle(pantalla, color, (int(self.x), int(self.y)), self.radio)
            pygame.draw.circle(pantalla, (0, 0, 0), (int(self.x), int(self.y)), self.radio, 1)
            
    def colisionaConTorre(self, torre):
        """Verifica si el proyectil colisiona con una torre (solo si es de Avatar)"""
        if self.esAvatar and torre.viva:
            distancia = ((self.x - torre.x) ** 2 + (self.y - torre.y) ** 2) ** 0.5
            return distancia < self.radio + 25 
        return False

    def colisionaConAvatar(self, avatar):
        """Verifica si el proyectil colisiona con un avatar (solo si es de Torre)"""
        if not self.esAvatar and avatar.vivo and not avatar.apareciendo:
            distancia = ((self.x - avatar.x) ** 2 + (self.y - avatar.y) ** 2) ** 0.5
            return distancia < self.radio + 20
        return False


class Avatar:
    """Representa un avatar enemigo que avanza hacia arriba"""
    
    # Mapeo de tipo de avatar a nombre base de archivo de imagen
    AVATAR_IMAGEN_MAP = {
        "flechador": "Arco",
        "escudero": "escudo",
        "lenador": "hacha",
        "canibal": "bate" 
    }

    def __init__(self, tipo, fila, columna, datosAvatar, gridConfig, avatar_imagenes=None):

        self.tipo = tipo
        self.fila = fila
        self.columna = columna
        
        self.vidaMax = datosAvatar["vida"]
        self.vidaActual = datosAvatar["vida"]
        self.daño = datosAvatar["daño"]
        self.duracionAparicion = datosAvatar["duracion_aparicion"]  
        self.duracionAtaque = random.randint(
            datosAvatar.get("duracion_ataque_min", 1),
            datosAvatar.get("duracion_ataque_max", 5)
        )
        self.vivo = True
        self.apareciendo = True  
        self.tiempoAparicion = 0
        self.tiempoDesdeUltimoDisparo = 0 
        
        self.calcularPosicion(gridConfig)
        self.velocidad = 0.5 
        self.proyectiles = []
        self.gridConfig = gridConfig
        self.puntos = datosAvatar.get("puntos", 0)
        
        # Carga y animación de imágenes
        self.imagenes = []
        self.frameActual = 0
        self.contadorAnimacion = 0
        self.velocidadAnimacion = 8 
        
        nombre_base = self.AVATAR_IMAGEN_MAP.get(self.tipo)
        if nombre_base and avatar_imagenes:
            img1 = avatar_imagenes.get(f"Avatar_{nombre_base}_1")
            img2 = avatar_imagenes.get(f"Avatar_{nombre_base}_2")
            
            # MODIFICACIÓN AQUÍ: Aumentar el tamaño del avatar
            radio_visual = 70
            
            if img1:
                img1 = pygame.transform.scale(img1, (radio_visual, radio_visual))
                self.imagenes.append(img1)
            if img2:
                img2 = pygame.transform.scale(img2, (radio_visual, radio_visual))
                self.imagenes.append(img2)

    def calcularPosicion(self, gridConfig):
        """Calcula la posición visual central en la casilla"""
        gridX = gridConfig["gridX"]
        gridY = gridConfig["gridY"]
        anchoCasilla = gridConfig["anchoCasilla"]
        altoCasilla = gridConfig["altoCasilla"]
        
        self.x = gridX + self.columna * anchoCasilla + anchoCasilla / 2
        self.y = gridY + self.fila * altoCasilla + altoCasilla / 2

    def mover(self, fps):
        """Avanza una casilla si es posible"""
        self.y -= self.velocidad 
        
        gridY = self.gridConfig["gridY"]
        altoCasilla = self.gridConfig["altoCasilla"]
        centroYObjetivo = gridY + (self.fila - 1) * altoCasilla + altoCasilla / 2
        
        if self.y <= centroYObjetivo:
            self.fila -= 1
            self.y = centroYObjetivo
            self.velocidad = 0.5 
            return True 
        
        return False

    def moverConColision(self, torres):
        """Mueve el avatar y verifica si choca con alguna torre en su misma columna"""
        
        if self.fila == 0 or self.apareciendo:
            return
        
        torre_bloqueando = None
        for torre in torres:
            if torre.fila == self.fila - 1 and torre.columna == self.columna and torre.viva:
                torre_bloqueando = torre
                break
        
        if torre_bloqueando:
            distancia_minima = 25 + 25 # Radio de avatar (25) + radio de torre (25, ajustado abajo)
            
            if self.y - torre_bloqueando.y > distancia_minima:
                self.y -= self.velocidad
            
            self.actualizarDisparo(torre_bloqueando, self.gridConfig)
            
        else:
            self.mover(60) 

    def actualizar(self, torres):
        """Actualiza el estado del avatar (incluyendo animación)"""
        if not self.vivo:
            return
        
        # Lógica de animación
        if not self.apareciendo and self.imagenes:
            self.contadorAnimacion += 1
            if self.contadorAnimacion >= self.velocidadAnimacion:
                self.frameActual = (self.frameActual + 1) % len(self.imagenes)
                self.contadorAnimacion = 0
        
        # Fase de aparición
        if self.apareciendo:
            self.tiempoAparicion += 1
            if self.tiempoAparicion >= 3 * 60: 
                self.apareciendo = False
            return 
        
        # Movimiento
        self.moverConColision(torres)

        # Actualizar proyectiles
        for proyectil in self.proyectiles[:]:
            proyectil.actualizar()
            if not proyectil.activo:
                self.proyectiles.remove(proyectil)

    def actualizarDisparo(self, objetivo, gridConfig):
        """Controla el tiempo de espera entre disparos y dispara"""
        self.tiempoDesdeUltimoDisparo += 1
        
        framesPorAtaque = self.duracionAtaque * 60 
        
        if self.tiempoDesdeUltimoDisparo >= framesPorAtaque:
            self.disparar()
            self.tiempoDesdeUltimoDisparo = 0

    def disparar(self):
        """Crea un proyectil"""
        # Los proyectiles de avatar (esAvatar=True) ya se mueven hacia arriba (velocidad = -5)
        proyectil = Proyectil(self.x, self.y, self.daño, self.tipo, esAvatar=True)
        self.proyectiles.append(proyectil)
        
    def recibirDaño(self, daño):
        """Reduce la vida y verifica si muere"""
        self.vidaActual -= daño
        if self.vidaActual <= 0:
            self.vidaActual = 0
            self.vivo = False
            return self.puntos
        return 0

    def dibujarBarraVida(self, pantalla, radio):
        """Dibuja la barra de vida sobre el avatar"""
        if self.vidaActual == self.vidaMax:
            return

        anchoBarra = radio * 2
        altoBarra = 5
        
        # Fondo rojo
        barraFondo = pygame.Rect(self.x - anchoBarra / 2, self.y - radio - 10, anchoBarra, altoBarra)
        pygame.draw.rect(pantalla, (255, 0, 0), barraFondo)

        # Vida verde
        anchoVida = (self.vidaActual / self.vidaMax) * anchoBarra
        barraVida = pygame.Rect(self.x - anchoBarra / 2, self.y - radio - 10, anchoVida, altoBarra)
        pygame.draw.rect(pantalla, (0, 255, 0), barraVida)

    def dibujar(self, pantalla):
        """Dibuja el avatar y sus proyectiles, usando imagen si existe"""
        if not self.vivo:
            return
        
        radio = 25 # Este es el radio para el dibujo de los círculos (si no hay imagen), no para la imagen.
        
        if self.imagenes:
            imagen_a_dibujar = self.imagenes[self.frameActual % len(self.imagenes)]
            rect = imagen_a_dibujar.get_rect(center=(int(self.x), int(self.y)))
            
            if self.apareciendo:
                progreso = self.tiempoAparicion / (3 * 60) 
                progreso = min(1.0, progreso)
                alpha = int(255 * progreso)
                imagen_a_dibujar.set_alpha(alpha)
                pantalla.blit(imagen_a_dibujar, rect)
            else:
                imagen_a_dibujar.set_alpha(255) 
                pantalla.blit(imagen_a_dibujar, rect)
            
            if not self.apareciendo:
                # Pasar el radio visual que se usó para escalar la imagen
                self.dibujarBarraVida(pantalla, 25) # Asumiendo que 25 es el radio efectivo para la barra de vida
        else:
            colores = {
                "flechador": (255, 215, 0), "escudero": (100, 149, 237),
                "lenador": (139, 69, 19), "canibal": (220, 20, 60)
            }
            color = colores.get(self.tipo, (255, 255, 255))
            
            if self.apareciendo:
                 pass
            else:
                pygame.draw.circle(pantalla, color, (int(self.x), int(self.y)), radio)
                pygame.draw.circle(pantalla, (255, 255, 255), (int(self.x), int(self.y)), radio, 2)
                self.dibujarBarraVida(pantalla, radio)
        
        # Dibujar proyectiles
        for proyectil in self.proyectiles:
            proyectil.dibujar(pantalla)

    def llegoPantallaArriba(self):
        """Verifica si el avatar llegó a la fila superior (fila 0)"""
        return self.fila == 0


class Torre:
    """Representa una torre colocada en el tablero"""
    
    # Mapeo de 'tipo' a nombre de archivo (usado para cargar la imagen de la torre)
    TORRE_IMAGEN_MAP = {
        "T1": "Torre_arena",
        "T2": "Torre_roca",
        "T3": "Torre_fuego",
        "T4": "Torre_agua"
    }
    
    def __init__(self, tipo, fila, columna, datosTorre, gridConfig, torre_imagenes=None):

        self.tipo = tipo
        self.fila = fila
        self.columna = columna
        
        self.vidaMax = datosTorre["vida"]
        self.vidaActual = datosTorre["vida"]
        self.daño = datosTorre["daño"]
        self.valor = datosTorre["valor"]
        self.duracionAtaque = random.randint(
            datosTorre.get("duracion_ataque_min", 1),
            datosTorre.get("duracion_ataque_max", 5)
        )
        
        self.viva = True
        self.tiempoAtaque = 0
        self.proyectiles = []
        self.rangoAtaque = 1 

        # Cargar imagen de la torre
        self.imagen = None
        nombre_base = self.TORRE_IMAGEN_MAP.get(self.tipo)
        if nombre_base and torre_imagenes:
            self.imagen = torre_imagenes.get(nombre_base)
            if self.imagen:
                # MODIFICACIÓN AQUÍ: Aumentar el tamaño de la torre
                radio_visual = 90
                self.imagen = pygame.transform.scale(self.imagen, (radio_visual, radio_visual))

        self.calcularPosicion(gridConfig)

    def calcularPosicion(self, gridConfig):
        """Calcula la posición visual central en la casilla"""
        gridX = gridConfig["gridX"]
        gridY = gridConfig["gridY"]
        anchoCasilla = gridConfig["anchoCasilla"]
        altoCasilla = gridConfig["altoCasilla"]
        
        self.x = gridX + self.columna * anchoCasilla + anchoCasilla / 2
        self.y = gridY + self.fila * altoCasilla + altoCasilla / 2

    def dentroRango(self, avatar):
        """Verifica si un avatar está dentro del rango de ataque (cualquier casilla inferior en la misma columna)"""
        # El avatar debe estar en la misma columna Y en una fila MAYOR (más abajo) que la torre.
        return avatar.columna == self.columna and avatar.fila > self.fila
            
    def recibirDaño(self, daño):
        """Reduce la vida y verifica si muere"""
        self.vidaActual -= daño
        if self.vidaActual <= 0:
            self.vidaActual = 0
            self.viva = False

    def dibujarBarraVida(self, pantalla, radio):
        """Dibuja la barra de vida sobre la torre"""
        if self.vidaActual == self.vidaMax:
            return

        anchoBarra = radio * 2
        altoBarra = 5
        
        # Fondo rojo
        barraFondo = pygame.Rect(self.x - anchoBarra / 2, self.y - radio - 10, anchoBarra, altoBarra)
        pygame.draw.rect(pantalla, (255, 0, 0), barraFondo)

        # Vida verde
        anchoVida = (self.vidaActual / self.vidaMax) * anchoBarra
        barraVida = pygame.Rect(self.x - anchoBarra / 2, self.y - radio - 10, anchoVida, altoBarra)
        pygame.draw.rect(pantalla, (0, 255, 0), barraVida)

    def dibujar(self, pantalla):
        """Dibuja la torre y sus proyectiles, usando imagen si existe"""
        if not self.viva:
            return
        
        radio = 30 # Este es el radio para el dibujo de los círculos (si no hay imagen), no para la imagen.
        
        if self.imagen:
            rect = self.imagen.get_rect(center=(int(self.x), int(self.y)))
            pantalla.blit(self.imagen, rect)
            
            # Pasar el radio visual que se usó para escalar la imagen
            self.dibujarBarraVida(pantalla, 30) # Asumiendo que 30 es el radio efectivo para la barra de vida
        else:
            # Dibujar el círculo por defecto
            colores = {
                "T1": (194, 178, 128), "T2": (128, 128, 128),  
                "T3": (255, 100, 0), "T4": (0, 100, 255)    
            }
            color = colores.get(self.tipo, (255, 255, 255))
            pygame.draw.circle(pantalla, color, (int(self.x), int(self.y)), radio)
            pygame.draw.circle(pantalla, (0, 0, 0), (int(self.x), int(self.y)), radio, 3)
            self.dibujarBarraVida(pantalla, radio)
        
        # Dibujar proyectiles
        for proyectil in self.proyectiles:
            proyectil.dibujar(pantalla)


class GestorAvatars:
    """Gestiona la aparición, movimiento y ataques de todos los avatars"""
    
    def __init__(self, gridConfig, dificultad="Facil", fps=60, avatar_imagenes=None, proyectil_imagenes=None):
        
        self.gridConfig = gridConfig
        self.fps = fps
        self.avatarsActivos = []
        
        self.dificultad = dificultad
        self.configurarDificultad()
        self.juegoActivo = False
        self.jugadorPerdio = False
        self.jugadorGano = False
        self.causaResultado = ""
        self.tiempoTranscurrido = 0
        self.tiempoLimiteFrames = self.tiempoLimite * fps
        self.tiempoSpawn = 0
        self.puntosGanados = 0
        self.avatarsMatados = 0
        
        self.datosAvatars = Avatars()
        
        # Guardar referencias a las imágenes
        self.avatar_imagenes = avatar_imagenes
        self.proyectil_imagenes = proyectil_imagenes
        
        self.probabilidades = { 
            "flechador": 0.4, "escudero": 0.3, 
            "lenador": 0.2, "canibal": 0.1
        }
        
    def configurarDificultad(self):
        """Configura los parámetros de tiempo y spawn según la dificultad."""
        
        # Tiempo de la partida en segundos
        tiempo_base = 60 # 60 segundos para la partida

        if self.dificultad == "FÁCIL":
            self.tiempoLimite = tiempo_base * 1.5 
            self.spawnMin = 4
            self.spawnMax = 7
        elif self.dificultad == "MEDIO":
            self.tiempoLimite = tiempo_base
            self.spawnMin = 3
            self.spawnMax = 5
        elif self.dificultad == "DIFÍCIL":
            self.tiempoLimite = tiempo_base * 0.8 
            self.spawnMin = 2
            self.spawnMax = 4
        else:
            self.tiempoLimite = tiempo_base
            self.spawnMin = 3
            self.spawnMax = 5
            
        print(f"📊 Dificultad '{self.dificultad}' configurada. Tiempo límite: {self.tiempoLimite}s")
        print(f"Intervalo de spawn: {self.spawnMin}-{self.spawnMax} segundos.")
    
    def iniciar(self):
        self.juegoActivo = True
        self.tiempoTranscurrido = 0
        self.tiempoLimiteFrames = self.tiempoLimite * self.fps
        self.tiempoSpawn = 0
        
    def obtenerEstadisticas(self):
        tiempoRestante = max(0, self.tiempoLimiteFrames - self.tiempoTranscurrido) // self.fps
        minutos = tiempoRestante // 60
        segundos = tiempoRestante % 60
        
        return {
            "dificultad": self.dificultad,
            "tiempoRestante": tiempoRestante,
            "tiempoRestanteStr": f"{minutos:02}:{segundos:02}",
            "avatarsVivos": len(self.avatarsActivos),
            "perdio": self.jugadorPerdio,
            "gano": self.jugadorGano,
            "resultado": self.causaResultado
        }

    def obtenerYResetearPuntos(self):
        puntos = self.puntosGanados
        self.puntosGanados = 0
        return puntos

    def actualizar(self, torres):
        """Actualiza la lógica de los avatars, movimiento, y colisiones con proyectiles de torre"""
        if not self.juegoActivo:
            return

        self.actualizarSpawn()
        
        # 1. Actualizar Avatars (movimiento y ataque a torres)
        for avatar in self.avatarsActivos[:]:
            avatar.actualizar(torres) 
            
            # Verificar si el avatar llegó al final
            if avatar.llegoPantallaArriba():
                self.juegoActivo = False
                self.jugadorPerdio = True
                self.causaResultado = f"Un {avatar.tipo} llegó al final."
                print(f"💀 ¡PERDISTE! {self.causaResultado}")
                return
        
        # 2. Actualizar Colisiones (Avatars vs Proyectiles de Torre)
        for torre in torres:
            for proyectil in torre.proyectiles[:]:
                for avatar in self.avatarsActivos[:]:
                    if proyectil.colisionaConAvatar(avatar):
                        puntos = avatar.recibirDaño(proyectil.daño)
                        self.puntosGanados += puntos
                        proyectil.activo = False
                        
                        if not avatar.vivo:
                            self.avatarsActivos.remove(avatar)
                            self.avatarsMatados += 1
                            print(f"🎯 {avatar.tipo} eliminado. Puntos: +{puntos}")
                        
                        break # Un proyectil solo golpea a un avatar
        
        # 3. Actualizar Colisiones (Torres vs Proyectiles de Avatar)
        for avatar in self.avatarsActivos:
            for proyectil in avatar.proyectiles[:]:
                # 🛡️ Usamos una copia de 'torres' para evitar problemas si se elimina una torre
                for torre in torres[:]:
                    if proyectil.colisionaConTorre(torre):
                        torre.recibirDaño(proyectil.daño)
                        proyectil.activo = False
                        
                        if not torre.viva:
                            # Se elimina de la lista 'torres' (que debe ser una referencia compartida)
                            try:
                                torres.remove(torre)
                                print(f"💥 Torre {torre.tipo} eliminada.")
                            except ValueError:
                                pass # Ya fue eliminada o no estaba en la lista

                        break
        
        # 4. Control de tiempo/victoria
        self.tiempoTranscurrido += 1
        if self.tiempoTranscurrido >= self.tiempoLimiteFrames:
            self.juegoActivo = False
            self.jugadorGano = True
            self.causaResultado = "Tiempo agotado. ¡Sobreviviste!"
            print(f"🎉 ¡GANASTE! {self.causaResultado}")

    def actualizarSpawn(self):
        """Controla el tiempo de espera entre spawns y llama a spawnearAvatar"""
        self.tiempoSpawn += 1
        
        if self.juegoActivo and self.tiempoTranscurrido % self.fps == 0: # Cada segundo
            # Si el tiempo actual es mayor que el tiempo máximo configurado para el intervalo
            if (self.tiempoSpawn / self.fps) >= random.randint(self.spawnMin, self.spawnMax): 
                self.spawnearAvatar()
                self.tiempoSpawn = 0
            
    def seleccionarTipoAvatar(self):
        """Selecciona el tipo de avatar basado en probabilidades"""
        pesoTotal = sum(self.probabilidades.values())
        valorAleatorio = random.uniform(0, pesoTotal)
        acumulado = 0
        for tipo, peso in self.probabilidades.items():
            acumulado += peso
            if valorAleatorio <= acumulado:
                return tipo
        return random.choice(list(self.probabilidades.keys())) 

    def spawnearAvatar(self):
        """Crea un nuevo avatar en la fila inferior"""
        columna = random.randint(0, 4)
        fila = 8
        tipo = self.seleccionarTipoAvatar()
        datosAvatar = getattr(self.datosAvatars, tipo)
        
        avatar = Avatar(tipo, fila, columna, datosAvatar, self.gridConfig, 
                        avatar_imagenes=self.avatar_imagenes)
        self.avatarsActivos.append(avatar)
        
        tiempoRestante = (self.tiempoLimiteFrames - self.tiempoTranscurrido) / self.fps
        print(f"👤 {tipo} spawneado en columna {columna} (Tiempo restante: {int(tiempoRestante)}s)")
    
    def dibujar(self, pantalla):
        """Dibuja todos los avatars y sus proyectiles"""
        for avatar in self.avatarsActivos:
            avatar.dibujar(pantalla)


class GestorTorres:
    """Gestiona todas las torres del tablero"""
    
    def __init__(self, matriz, datosTorres, gridConfig, torre_imagenes=None, proyectil_imagenes=None):

        self.torres = []
        self.gridConfig = gridConfig
        self.datosTorres = datosTorres
        self.matriz = matriz 
        
        # Guardar referencias a las imágenes
        self.torre_imagenes = torre_imagenes
        self.proyectil_imagenes = proyectil_imagenes 
        
        self.crearTorresDesdeMatriz(matriz, datosTorres)
    
    def crearTorresDesdeMatriz(self, matriz, datosTorres):
        """Convierte la matriz de pantallaJuego en objetos Torre, pasándoles las imágenes"""
        for fila in range(len(matriz)):
            for columna in range(len(matriz[0])):
                idTorre = matriz[fila][columna]
                
                if idTorre:
                    datos = datosTorres[idTorre]
                    torre = Torre(idTorre, fila, columna, datos, self.gridConfig, 
                                  torre_imagenes=self.torre_imagenes)
                    self.torres.append(torre)
        
        print(f"🏰 {len(self.torres)} torres creadas")
    
    def agregarTorre(self, idTorre, fila, columna):
        """Agrega una nueva torre durante la partida, pasándole las imágenes"""
        try:
            datos = self.datosTorres[idTorre]
            torre = Torre(idTorre, fila, columna, datos, self.gridConfig, 
                          torre_imagenes=self.torre_imagenes)
            self.torres.append(torre)
            print(f"🏰 Torre {idTorre} agregada en ({fila}, {columna}) durante partida")
            return torre
        except Exception as e:
            print(f"❌ Error agregando torre: {e}")
            return None

    def eliminarTorre(self, fila, columna):
        """Elimina una torre por posición (llamado desde PantallaJuego al hacer click derecho)"""
        for torre in self.torres[:]:
            if torre.fila == fila and torre.columna == columna:
                self.torres.remove(torre)
                print(f"Torre {torre.tipo} eliminada de la lista activa.")
                return True
        return False
    
    def actualizar(self, avatars, fps):
        """Actualiza la lógica de las torres (ataque)"""
        for torre in self.torres:
            if not torre.viva:
                continue

            # 1. Buscar objetivo
            objetivo = None
            for avatar in avatars:
                # Usa la nueva lógica de rango que permite el ataque a distancia
                if torre.dentroRango(avatar) and avatar.vivo and not avatar.apareciendo:
                    objetivo = avatar
                    break # La torre ataca al avatar más cercano (el primero que encuentra)
            
            # 2. Controlar el tiempo de ataque y disparar
            torre.tiempoAtaque += 1
            framesPorAtaque = torre.duracionAtaque * fps
            
            if objetivo and torre.tiempoAtaque >= framesPorAtaque:
                # CREACIÓN DEL PROYECTIL: Le pasa el diccionario de imágenes
                proyectil = Proyectil(
                    torre.x, torre.y, torre.daño, torre.tipo, 
                    esAvatar=False, 
                    imagenes=self.proyectil_imagenes 
                )
                torre.proyectiles.append(proyectil)
                torre.tiempoAtaque = 0
            
            # 3. Mover y limpiar proyectiles
            for proyectil in torre.proyectiles[:]:
                proyectil.actualizar()
                if not proyectil.activo:
                    torre.proyectiles.remove(proyectil)

    def dibujar(self, pantalla):
        """Dibuja todas las torres y sus proyectiles"""
        for torre in self.torres:
            torre.dibujar(pantalla)