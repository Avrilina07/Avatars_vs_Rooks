# temas.py

class Tema:
    #Clase que representa un tema visual con su nivel de opacidad
    
    def __init__(self, nombre, opacidad):
        self.nombre = nombre
        self.opacidad = opacidad  # 0-255, donde 0 es transparente y 255 opaco


class ConfiguracionTemas:
    #Clase que contiene todos los temas disponibles
    
    CLARO = Tema("Claro (Predeterminado)", 50)
    INTERMEDIO = Tema("Intermedio", 120)
    OSCURO = Tema("Oscuro", 200)
    
    @staticmethod
    def obtenerTodos():
        """
        Retorna una lista con todos los temas disponibles
        
        @staticmethod: Decorador que permite llamar este método sin crear 
        una instancia de la clase. Se usa porque el método no necesita 
        acceder a datos de instancia (self) ni de la clase (cls), solo 
        retorna una lista de constantes ya definidas.
        """
        return [
            ConfiguracionTemas.CLARO,
            ConfiguracionTemas.INTERMEDIO,
            ConfiguracionTemas.OSCURO
        ]