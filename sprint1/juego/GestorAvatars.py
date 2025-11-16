import pygame
import random
from clasesAvatarsRooks import Avatars, Rooks
from Avatar import Avatar

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

