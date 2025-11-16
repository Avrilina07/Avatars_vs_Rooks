import pygame
import random
from clasesAvatarsRooks import Avatars, Rooks
from Torre import Torre
from Proyectil import Proyectil
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