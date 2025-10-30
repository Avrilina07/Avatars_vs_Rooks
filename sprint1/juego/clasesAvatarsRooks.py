# ---CLASES CON PARÁMETROS BÁSICOS DE LOS AVATARS Y LAS TORRES---

import random

class Avatars:
    def __init__(self):
        # Definición de los 4 avatars
        self.flechador = {
            "vida": 5,
            "daño": 1,
            "duracion_aparicion": 17,
            "duracion_ataque_min": 1,  
            "duracion_ataque_max": 5  
            ,
            "puntos": 10  # ← AGREGADO: puntos concedidos al morir
        } 
        self.escudero = {
            "vida": 10,
            "daño": 2,
            "duracion_aparicion": 17,
            "duracion_ataque_min": 1,
            "duracion_ataque_max": 5
            ,
            "puntos": 15  # ← AGREGADO
        }
        self.lenador = {
            "vida": 25,
            "daño": 3,
            "duracion_aparicion": 20,
            "duracion_ataque_min": 1,
            "duracion_ataque_max": 5
            ,
            "puntos": 25  # ← AGREGADO
        }
        self.canibal = {
            "vida": 25,
            "daño": 4,
            "duracion_aparicion": 20,
            "duracion_ataque_min": 1,
            "duracion_ataque_max": 5
            ,
            "puntos": 30  # ← AGREGADO
        }

class Rooks:
    def __init__(self):
        # Definición de los 4 tipos de torres
        self.torreArena = {
            "vida": 2,
            "daño": 2,
            "valor": 50,
            "duracion_ataque_min": 1, 
            "duracion_ataque_max": 5  
        } 
        self.torreRoca = {
            "vida": 4,
            "daño": 3,
            "valor": 100,
            "duracion_ataque_min": 1,
            "duracion_ataque_max": 5
        }
        self.torreFuego = {
            "vida": 8,
            "daño": 4,
            "valor": 150,
            "duracion_ataque_min": 1,
            "duracion_ataque_max": 5
        }
        self.torreAgua = {
            "vida": 8,
            "daño": 5,
            "valor": 150,
            "duracion_ataque_min": 1,
            "duracion_ataque_max": 5
        }