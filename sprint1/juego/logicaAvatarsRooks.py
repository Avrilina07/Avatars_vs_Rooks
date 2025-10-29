# ---MANEJO DE TODA LA LÓGICA DE FUNCIONAMIENTO DE AVATARS Y TORRES---

import pygame
import random
from clasesAvatarsRooks import Avatars, Rooks


class Proyectil:
    """Representa un proyectil disparado por un avatar"""
    
    def __init__(self, x, y, daño, tipo):
        
        self.x = x
        self.y = y
        self.daño = daño
        self.tipo = tipo # tipo de avatar que lo disparó (para color)
        self.activo = True
        
        # Velocidad del proyectil (píxeles por frame)
        self.velocidad = -5  # Negativo = hacia arriba
        
        # Tamaño del proyectil
        self.radio = 5
    
    def actualizar(self):
        """Mueve el proyectil hacia arriba"""
        if self.activo:
            self.y += self.velocidad
            
            if self.y < 0:
                self.activo = False
    
    def dibujar(self, pantalla):
        """Dibuja el proyectil"""
        if not self.activo:
            return
        
        # Color del proyectil según tipo de avatar (se puede cambiar si se utilizan imágenes)
        colores = {
            "flechador": (255, 215, 0),    # Dorado
            "escudero": (135, 206, 250),   # Azul claro
            "lenador": (210, 105, 30),     # Chocolate
            "canibal": (255, 69, 0)        # Rojo naranja
        }
        
        color = colores.get(self.tipo, (255, 255, 255))
        
        # Dibujar proyectil circular
        pygame.draw.circle(pantalla, color, (int(self.x), int(self.y)), self.radio)
        pygame.draw.circle(pantalla, (255, 255, 255), (int(self.x), int(self.y)), self.radio, 1)
    
    def colisionaConTorre(self, torre):
        """
        Verifica colisión con una torre
        
        Args:
            torre: objeto Torre
            
        Returns:
            bool: True si hay colisión
        """
        if not self.activo or not torre.viva:
            return False
        
        # Radio de colisión de torre
        radioTorre = 25
        
        # Distancia entre proyectil y torre
        distancia = ((self.x - torre.x)**2 + (self.y - torre.y)**2)**0.5
        
        return distancia < (self.radio + radioTorre)


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
        self.velocidad = 1.0  # Píxeles por frame (ajustar si es muy lento/rápido)
        
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
            
            # ⚙️ AJUSTAR: Convertir duracion_aparicion (segundos) a frames
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
        
        # ⚙️ AJUSTAR: Colores por tipo de avatar
        colores = {
            "flechador": (255, 200, 0),    # Amarillo
            "escudero": (100, 100, 255),   # Azul
            "leñador": (139, 69, 19),      # Marrón
            "caníbal": (255, 0, 0)         # Rojo
        }
        
        color = colores.get(self.tipo, (255, 255, 255))
        
        # ⚙️ AJUSTAR: Tamaño del avatar
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
        return len(self.torres) == 0