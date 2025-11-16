import pygame
import random
from clasesAvatarsRooks import Avatars, Rooks 

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
        
        # Rango de ataque (solo para arquero)
        self.rangoAtaque = datosAvatar.get("rango_ataque", 0)  # 0 = melee, >0 = rango
        
        # Carga y animación de imágenes
        self.imagenes = []
        self.frameActual = 0
        self.contadorAnimacion = 0
        self.velocidadAnimacion = 8 
        
        nombre_base = self.AVATAR_IMAGEN_MAP.get(self.tipo)
        if nombre_base and avatar_imagenes:
            img1 = avatar_imagenes.get(f"Avatar_{nombre_base}_1")
            img2 = avatar_imagenes.get(f"Avatar_{nombre_base}_2")
            
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
        
        # Si es arquero, buscar torre en rango para disparar
        if self.tipo == "flechador":
            torre_en_rango = self.buscarTorreEnRango(torres)
            if torre_en_rango:
                # Disparar hacia la torre
                self.actualizarDisparo(torre_en_rango, self.gridConfig)
            # El arquero siempre avanza (no se detiene)
            self.mover(60)
            return
        
        # Lógica normal para otros avatars (melee)
        torre_bloqueando = None
        for torre in torres:
            if torre.fila == self.fila - 1 and torre.columna == self.columna and torre.viva:
                torre_bloqueando = torre
                break
        
        if torre_bloqueando:
            distancia_minima = 25 + 25
            
            if self.y - torre_bloqueando.y > distancia_minima:
                self.y -= self.velocidad
            
            self.actualizarDisparo(torre_bloqueando, self.gridConfig)
            
        else:
            self.mover(60)

    def buscarTorreEnRango(self, torres):
        """
        Busca una torre en la misma columna dentro del rango de ataque del avatar.        
        Args:
            torres: Lista de torres activas
            
        Returns:
            Torre más cercana en rango o None
        """
        torres_en_columna = [t for t in torres if t.columna == self.columna and t.viva]
        
        if not torres_en_columna:
            return None
        
        # Buscar la torre más cercana que esté DELANTE del avatar (fila menor)
        torres_delante = [t for t in torres_en_columna if t.fila < self.fila]
        
        if not torres_delante:
            return None
        
        # Ordenar por distancia y retornar la más cercana
        torres_delante.sort(key=lambda t: abs(t.fila - self.fila))
        torre_mas_cercana = torres_delante[0]
        
        # Verificar si está en rango (en casillas)
        distancia_casillas = self.fila - torre_mas_cercana.fila
        
        if distancia_casillas <= self.rangoAtaque:
            return torre_mas_cercana
        
        return None

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
        from Proyectil import Proyectil
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
        
        radio = 25
        
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
                self.dibujarBarraVida(pantalla, 25)
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