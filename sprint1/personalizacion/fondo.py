#fondo.py
class ColorFondo:
    #Representa un color de fondo con su configuración de UI
    
    def __init__(self, nombre, rgb, esClaro):
        self.nombre = nombre
        self.rgb = rgb
        self.esClaro = esClaro  # True si el fondo es claro, False si es oscuro
    
    def obtenerColorBoton(self):
        #Retorna el color de botón apropiado según si el fondo es claro u oscuro
        if self.esClaro:
            return (96, 96, 96)  # Gris oscuro #606060
        else:
            return (245, 245, 220)  # Crema claro #F5F5DC
    
    def obtenerColorHoverBoton(self):
        #Retorna el color hover del botón
        if self.esClaro:
            return (112, 112, 112)  # Gris un poco más claro
        else:
            return (232, 232, 232)  # Gris muy claro #E8E8E8
    
    def obtenerColorBorde(self):
        #Retorna el color del borde del botón

        return (0, 0, 0)  # Negro para todos los fondos
    
    def obtenerColorTextoBoton(self):
        #Retorna el color del texto en botones
        if self.esClaro:
            return (255, 255, 255)  # Blanco
        else:
            return (0, 0, 0)  # Negro
    
    def obtenerColorTitulo(self):
        #Retorna el color del título
        if self.esClaro:
            return (0, 0, 0)  # Negro
        else:
            return (245, 245, 220)  # Crema claro


class ColoresFondoDisponibles:
    #Clase que contiene todos los colores de fondo disponibles
    
    # Verdes claros
    VERDE_LIMA_1 = ColorFondo("Verde Lima Brillante", (130, 251, 6), True)
    VERDE_LIMA_2 = ColorFondo("Verde Lima", (104, 232, 5), True)
    VERDE_LIMA_3 = ColorFondo("Verde Lima Oscuro", (79, 213, 3), True)
    VERDE_CLARO_1 = ColorFondo("Verde Claro", (53, 193, 2), False)
    VERDE_CLARO_2 = ColorFondo("Verde", (27, 174, 0), False)
    
    # Beiges/Cremas
    BEIGE_1 = ColorFondo("Beige Claro", (229, 206, 183), True)
    BEIGE_2 = ColorFondo("Beige", (210, 188, 165), True)
    BEIGE_3 = ColorFondo("Beige Medio", (192, 170, 148), True)
    BEIGE_4 = ColorFondo("Beige Oscuro", (173, 152, 130), True)
    BEIGE_5 = ColorFondo("Marrón Claro", (154, 134, 112), True)
    
    # Morados claros
    MORADO_CLARO_1 = ColorFondo("Morado Claro", (151, 138, 225), True)
    MORADO_CLARO_2 = ColorFondo("Morado", (177, 163, 233), True)
    MORADO_CLARO_3 = ColorFondo("Morado Pastel", (203, 187, 240), True)
    MORADO_CLARO_4 = ColorFondo("Morado Muy Claro", (228, 212, 248), True)
    MORADO_CLARO_5 = ColorFondo("Lila", (254, 236, 255), True)
    
    # Amarillos/Dorados
    AMARILLO_1 = ColorFondo("Amarillo Dorado", (187, 158, 78), True)
    AMARILLO_2 = ColorFondo("Amarillo Mostaza", (204, 182, 102), True)
    AMARILLO_3 = ColorFondo("Amarillo Claro", (221, 207, 126), True)
    AMARILLO_4 = ColorFondo("Amarillo Pastel", (238, 231, 149), True)
    AMARILLO_5 = ColorFondo("Amarillo Muy Claro", (255, 255, 173), True)
    
    CREMA_1 = ColorFondo("Crema Verde", (192, 187, 126), True)
    CREMA_2 = ColorFondo("Crema", (208, 204, 151), True)
    CREMA_3 = ColorFondo("Crema Claro", (224, 221, 175), True)
    CREMA_4 = ColorFondo("Crema Muy Claro", (239, 238, 200), True)
    CREMA_5 = ColorFondo("Casi Blanco", (255, 254, 240), True)
    
    # Marrones oscuros
    MARRON_1 = ColorFondo("Marrón Rojizo", (143, 74, 55), False)
    MARRON_2 = ColorFondo("Marrón", (125, 58, 41), False)
    MARRON_3 = ColorFondo("Marrón Oscuro", (107, 42, 28), False)
    MARRON_4 = ColorFondo("Marrón Muy Oscuro", (88, 26, 14), False)
    MARRON_5 = ColorFondo("Marrón Negro", (70, 10, 0), False)
    
    # Naranjas
    NARANJA_1 = ColorFondo("Naranja Oscuro", (202, 95, 33), False)
    NARANJA_2 = ColorFondo("Naranja", (215, 119, 56), False)
    NARANJA_3 = ColorFondo("Naranja Claro", (229, 143, 79), True)
    NARANJA_4 = ColorFondo("Naranja Pastel", (242, 167, 102), True)
    NARANJA_5 = ColorFondo("Naranja Muy Claro", (255, 191, 125), True)
    
    # Rosas
    ROSA_OSCURO_1 = ColorFondo("Rosa Oscuro", (167, 57, 68), False)
    ROSA_OSCURO_2 = ColorFondo("Rosa", (189, 81, 90), False)
    ROSA_MEDIO = ColorFondo("Rosa Medio", (211, 105, 113), False)
    ROSA_CLARO_1 = ColorFondo("Rosa Claro", (233, 129, 135), True)
    ROSA_CLARO_2 = ColorFondo("Rosa Muy Claro", (255, 153, 157), True)
    
    # Rojos brillantes
    ROJO_1 = ColorFondo("Rojo Brillante", (251, 5, 36), False)
    ROJO_2 = ColorFondo("Rojo", (252, 41, 58), False)
    ROJO_3 = ColorFondo("Rojo Claro", (253, 76, 80), False)
    ROJO_4 = ColorFondo("Rojo Pastel", (254, 112, 102), True)
    ROJO_5 = ColorFondo("Rojo Muy Claro", (255, 147, 124), True)
    
    # Rojos oscuros
    ROJO_OSCURO_1 = ColorFondo("Rojo Ladrillo", (245, 87, 82), False)
    ROJO_OSCURO_2 = ColorFondo("Rojo Granate", (224, 65, 67), False)
    ROJO_OSCURO_3 = ColorFondo("Granate", (203, 44, 52), False)
    ROJO_OSCURO_4 = ColorFondo("Granate Oscuro", (181, 22, 37), False)
    ROJO_OSCURO_5 = ColorFondo("Borgoña", (160, 0, 22), False)
    
    # Rojos muy oscuros
    ROJO_MUY_OSCURO_1 = ColorFondo("Rojo Vino", (223, 35, 40), False)
    ROJO_MUY_OSCURO_2 = ColorFondo("Vino", (202, 26, 30), False)
    ROJO_MUY_OSCURO_3 = ColorFondo("Vino Oscuro", (180, 18, 20), False)
    ROJO_MUY_OSCURO_4 = ColorFondo("Rojo Sangre", (159, 9, 10), False)
    ROJO_MUY_OSCURO_5 = ColorFondo("Rojo Negro", (137, 0, 0), False)
    
    # Morados oscuros
    MORADO_OSCURO_1 = ColorFondo("Azul Marino Oscuro", (17, 22, 37), False)
    MORADO_OSCURO_2 = ColorFondo("Morado Oscuro", (52, 25, 49), False)
    MORADO_OSCURO_3 = ColorFondo("Morado Medio", (87, 27, 60), False)
    MORADO_OSCURO_4 = ColorFondo("Morado Rojizo", (122, 30, 72), False)
    MORADO_OSCURO_5 = ColorFondo("Magenta Oscuro", (157, 32, 83), False)
    
    # Rosas oscuros
    ROSA_GRISACEO_1 = ColorFondo("Rosa Grisáceo", (126, 88, 93), False)
    ROSA_GRISACEO_2 = ColorFondo("Rosa Gris", (151, 111, 116), False)
    ROSA_GRISACEO_3 = ColorFondo("Rosa Gris Claro", (175, 135, 140), True)
    ROSA_GRISACEO_4 = ColorFondo("Rosa Pálido", (200, 158, 163), True)
    ROSA_GRISACEO_5 = ColorFondo("Rosa Muy Pálido", (224, 181, 186), True)
    
    # Verdes azulados (Teal/Cyan)
    TEAL_1 = ColorFondo("Verde Azulado Oscuro", (22, 133, 114), False)
    TEAL_2 = ColorFondo("Teal", (50, 158, 138), False)
    TEAL_3 = ColorFondo("Teal Claro", (78, 183, 162), False)
    TEAL_4 = ColorFondo("Cyan", (106, 207, 186), True)
    TEAL_5 = ColorFondo("Cyan Claro", (134, 232, 210), True)
    
    # Cyans claros
    CYAN_1 = ColorFondo("Cyan Azulado", (22, 147, 165), False)
    CYAN_2 = ColorFondo("Azul Cyan", (69, 181, 196), False)
    CYAN_3 = ColorFondo("Cyan Pastel", (126, 206, 202), True)
    CYAN_4 = ColorFondo("Cyan Muy Claro", (160, 222, 214), True)
    CYAN_5 = ColorFondo("Cyan Casi Blanco", (199, 237, 232), True)
    
    # Morados medios
    MORADO_MEDIO_1 = ColorFondo("Morado Profundo", (76, 52, 90), False)
    MORADO_MEDIO_2 = ColorFondo("Morado Violeta", (62, 39, 75), False)
    MORADO_MEDIO_3 = ColorFondo("Violeta", (48, 26, 60), False)
    MORADO_MEDIO_4 = ColorFondo("Violeta Oscuro", (34, 13, 45), False)
    MORADO_MEDIO_5 = ColorFondo("Morado Negro", (20, 0, 30), False)
    
    # Azules oscuros
    AZUL_1 = ColorFondo("Azul Medio", (37, 57, 120), False)
    AZUL_2 = ColorFondo("Azul", (28, 43, 104), False)
    AZUL_3 = ColorFondo("Azul Oscuro", (19, 29, 88), False)
    AZUL_4 = ColorFondo("Azul Muy Oscuro", (9, 14, 71), False)
    AZUL_5 = ColorFondo("Azul Noche", (0, 0, 55), False)
    
    # Verdes oscuros
    VERDE_OSCURO_1 = ColorFondo("Verde Bosque", (6, 103, 86), False)
    VERDE_OSCURO_2 = ColorFondo("Verde Oscuro", (5, 87, 71), False)
    VERDE_OSCURO_3 = ColorFondo("Verde Profundo", (3, 72, 57), False)
    VERDE_OSCURO_4 = ColorFondo("Verde Muy Oscuro", (2, 56, 42), False)
    VERDE_OSCURO_5 = ColorFondo("Verde Negro", (0, 40, 27), False)
    
    @staticmethod
    def obtenerTodos():
        #Método estático que retorna todos los colores disponibles        
        return [
            # Verdes
            ColoresFondoDisponibles.VERDE_LIMA_1,
            ColoresFondoDisponibles.VERDE_LIMA_2,
            ColoresFondoDisponibles.VERDE_LIMA_3,
            ColoresFondoDisponibles.VERDE_CLARO_1,
            ColoresFondoDisponibles.VERDE_CLARO_2,
            
            # Beiges
            ColoresFondoDisponibles.BEIGE_1,
            ColoresFondoDisponibles.BEIGE_2,
            ColoresFondoDisponibles.BEIGE_3,
            ColoresFondoDisponibles.BEIGE_4,
            ColoresFondoDisponibles.BEIGE_5,
            
            # Morados claros
            ColoresFondoDisponibles.MORADO_CLARO_1,
            ColoresFondoDisponibles.MORADO_CLARO_2,
            ColoresFondoDisponibles.MORADO_CLARO_3,
            ColoresFondoDisponibles.MORADO_CLARO_4,
            ColoresFondoDisponibles.MORADO_CLARO_5,
            
            # Amarillos
            ColoresFondoDisponibles.AMARILLO_1,
            ColoresFondoDisponibles.AMARILLO_2,
            ColoresFondoDisponibles.AMARILLO_3,
            ColoresFondoDisponibles.AMARILLO_4,
            ColoresFondoDisponibles.AMARILLO_5,
            
            # Cremas
            ColoresFondoDisponibles.CREMA_1,
            ColoresFondoDisponibles.CREMA_2,
            ColoresFondoDisponibles.CREMA_3,
            ColoresFondoDisponibles.CREMA_4,
            ColoresFondoDisponibles.CREMA_5,
            
            # Marrones
            ColoresFondoDisponibles.MARRON_1,
            ColoresFondoDisponibles.MARRON_2,
            ColoresFondoDisponibles.MARRON_3,
            ColoresFondoDisponibles.MARRON_4,
            ColoresFondoDisponibles.MARRON_5,
            
            # Naranjas
            ColoresFondoDisponibles.NARANJA_1,
            ColoresFondoDisponibles.NARANJA_2,
            ColoresFondoDisponibles.NARANJA_3,
            ColoresFondoDisponibles.NARANJA_4,
            ColoresFondoDisponibles.NARANJA_5,
            
            # Rosas
            ColoresFondoDisponibles.ROSA_OSCURO_1,
            ColoresFondoDisponibles.ROSA_OSCURO_2,
            ColoresFondoDisponibles.ROSA_MEDIO,
            ColoresFondoDisponibles.ROSA_CLARO_1,
            ColoresFondoDisponibles.ROSA_CLARO_2,
            
            # Rojos brillantes
            ColoresFondoDisponibles.ROJO_1,
            ColoresFondoDisponibles.ROJO_2,
            ColoresFondoDisponibles.ROJO_3,
            ColoresFondoDisponibles.ROJO_4,
            ColoresFondoDisponibles.ROJO_5,
            
            # Rojos oscuros
            ColoresFondoDisponibles.ROJO_OSCURO_1,
            ColoresFondoDisponibles.ROJO_OSCURO_2,
            ColoresFondoDisponibles.ROJO_OSCURO_3,
            ColoresFondoDisponibles.ROJO_OSCURO_4,
            ColoresFondoDisponibles.ROJO_OSCURO_5,
            
            # Rojos muy oscuros
            ColoresFondoDisponibles.ROJO_MUY_OSCURO_1,
            ColoresFondoDisponibles.ROJO_MUY_OSCURO_2,
            ColoresFondoDisponibles.ROJO_MUY_OSCURO_3,
            ColoresFondoDisponibles.ROJO_MUY_OSCURO_4,
            ColoresFondoDisponibles.ROJO_MUY_OSCURO_5,
            
            # Morados oscuros
            ColoresFondoDisponibles.MORADO_OSCURO_1,
            ColoresFondoDisponibles.MORADO_OSCURO_2,
            ColoresFondoDisponibles.MORADO_OSCURO_3,
            ColoresFondoDisponibles.MORADO_OSCURO_4,
            ColoresFondoDisponibles.MORADO_OSCURO_5,
            
            # Rosas grisáceos
            ColoresFondoDisponibles.ROSA_GRISACEO_1,
            ColoresFondoDisponibles.ROSA_GRISACEO_2,
            ColoresFondoDisponibles.ROSA_GRISACEO_3,
            ColoresFondoDisponibles.ROSA_GRISACEO_4,
            ColoresFondoDisponibles.ROSA_GRISACEO_5,
            
            # Teals/Cyans
            ColoresFondoDisponibles.TEAL_1,
            ColoresFondoDisponibles.TEAL_2,
            ColoresFondoDisponibles.TEAL_3,
            ColoresFondoDisponibles.TEAL_4,
            ColoresFondoDisponibles.TEAL_5,
            
            # Cyans claros
            ColoresFondoDisponibles.CYAN_1,
            ColoresFondoDisponibles.CYAN_2,
            ColoresFondoDisponibles.CYAN_3,
            ColoresFondoDisponibles.CYAN_4,
            ColoresFondoDisponibles.CYAN_5,
            
            # Morados medios
            ColoresFondoDisponibles.MORADO_MEDIO_1,
            ColoresFondoDisponibles.MORADO_MEDIO_2,
            ColoresFondoDisponibles.MORADO_MEDIO_3,
            ColoresFondoDisponibles.MORADO_MEDIO_4,
            ColoresFondoDisponibles.MORADO_MEDIO_5,
            
            # Azules
            ColoresFondoDisponibles.AZUL_1,
            ColoresFondoDisponibles.AZUL_2,
            ColoresFondoDisponibles.AZUL_3,
            ColoresFondoDisponibles.AZUL_4,
            ColoresFondoDisponibles.AZUL_5,
            
            # Verdes oscuros
            ColoresFondoDisponibles.VERDE_OSCURO_1,
            ColoresFondoDisponibles.VERDE_OSCURO_2,
            ColoresFondoDisponibles.VERDE_OSCURO_3,
            ColoresFondoDisponibles.VERDE_OSCURO_4,
            ColoresFondoDisponibles.VERDE_OSCURO_5,
        ]