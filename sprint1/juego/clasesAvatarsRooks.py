import random

class Avatars:
    def __init__(self):
        # Definición de los 4 avatares
        self.flechador = {
            "vida": 5,
            "daño": 1,
            "duracion_aparicion": 17,
            "duracion_ataque": random.randint(1, 5) 
        } 
        self.escudero = {
            "vida": 10,
            "daño": 2,
            "duracion_aparicion": 17,
            "duracion_ataque": random.randint(1, 5)
        }
        self.lenador = {
            "vida": 25,
            "daño": 3,
            "duracion_aparicion": 20,
            "duracion_ataque": random.randint(1, 5)
        }
        self.canibal = {
            "vida": 25,
            "daño": 4,
            "duracion_aparicion": 20,
            "duracion_ataque": random.randint(1, 5)
        }
