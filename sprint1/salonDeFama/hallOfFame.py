"""
Hall of Fame - Salón de la Fama
Muestra y gestiona los 10 mejores puntajes del juego
"""

import pygame
import json
import os
import sys


class HallOfFame:
    def __init__(self, ancho=900, alto=700, archivoPuntajes="puntajes.json"):
        """
        Inicializa el Salón de la Fama
        
        Args:
            ancho: Ancho de la ventana
            alto: Alto de la ventana
            archivoPuntajes: Nombre del archivo JSON con los puntajes
        """
        pygame.init()
        
        # Obtener dimensiones de pantalla completa
        info = pygame.display.Info()
        self.ancho = info.current_w
        self.alto = info.current_h
        
        # Obtener la ruta correcta del archivo puntajes.json
        carpeta_actual = os.path.dirname(os.path.abspath(__file__))
        self.archivoPuntajes = os.path.join(carpeta_actual, archivoPuntajes)
        
        # Crear pantalla en modo pantalla completa
        self.pantalla = pygame.display.set_mode((self.ancho, self.alto), pygame.FULLSCREEN)
        pygame.display.set_caption("Hall of Fame - Salón de la Fama")
        
        # Colores
        self.colorFondo = (10, 15, 30)
        self.colorFondoTabla = (20, 25, 45)
        self.colorTitulo = (255, 215, 0)
        self.colorTexto = (255, 255, 255)
        self.colorTextoSecundario = (180, 180, 200)
        self.colorBoton = (50, 120, 200)
        self.colorBotonHover = (70, 150, 230)
        self.colorBorde = (100, 120, 180)
        self.colorOro = (255, 215, 0)
        self.colorPlata = (192, 192, 192)
        self.colorBronce = (205, 127, 50)
        
        # Fuentes
        try:
            self.fuenteTitulo = pygame.font.Font(None, 72)
            self.fuenteSubtitulo = pygame.font.Font(None, 40)
            self.fuenteTexto = pygame.font.Font(None, 30)
            self.fuenteBoton = pygame.font.Font(None, 36)
            self.fuentePequena = pygame.font.Font(None, 24)
        except:
            self.fuenteTitulo = pygame.font.SysFont('arial', 72, bold=True)
            self.fuenteSubtitulo = pygame.font.SysFont('arial', 40)
            self.fuenteTexto = pygame.font.SysFont('arial', 30)
            self.fuenteBoton = pygame.font.SysFont('arial', 36)
            self.fuentePequena = pygame.font.SysFont('arial', 24)
        
        # Datos
        self.puntajes = []
        self.cargarPuntajes()
        
        # Botón de volver - Posicionado dinámicamente debajo del cuadro
        margen = 60
        altoTabla = self.alto - 300
        yTabla = 150
        yBoton = yTabla + altoTabla + 40  # 40 píxeles debajo del cuadro
        self.botonVolver = pygame.Rect(self.ancho // 2 - 120, yBoton, 240, 55)
        
        self.reloj = pygame.time.Clock()
        self.ejecutando = True
        self.volverAlJuego = False
    
    
    def cargarPuntajes(self):
        """
        Carga los puntajes desde el archivo JSON
        """
        try:
            if os.path.exists(self.archivoPuntajes):
                with open(self.archivoPuntajes, 'r', encoding='utf-8') as archivo:
                    datos = json.load(archivo)
                    self.puntajes = datos if isinstance(datos, list) else []
                    self.organizarPuntajes()
                    print(f"{len(self.puntajes)} puntajes cargados desde {self.archivoPuntajes}")
            else:
                self.puntajes = []
                print(f"Archivo {self.archivoPuntajes} no encontrado, iniciando vacío")
        except Exception as e:
            print(f"Error al cargar puntajes: {e}")
            self.puntajes = []
    
    
    def organizarPuntajes(self):
        """
        Organiza los puntajes de mayor a menor y mantiene solo los mejores 10
        Elimina automáticamente los puntajes que no entran en el top 10
        """
        # Ordenar por puntaje descendente
        self.puntajes.sort(key=lambda x: x.get("puntaje", 0), reverse=True)
        
        # Verificar si hay puntajes que se eliminarán
        puntajesEliminados = len(self.puntajes) - 10
        
        # Mantener solo los mejores 10
        self.puntajes = self.puntajes[:10]
        
        if puntajesEliminados > 0:
            print(f"{puntajesEliminados} puntaje(s) eliminado(s) por no entrar en el top 10")
        
        # Guardar los cambios
        saved = self.guardarPuntajes()

        # Publicar Top10 en Twitter si se guardó correctamente
        if saved and self.puntajes:
            try:
                # import dinámico para evitar dependencia global
                try:
                    import importlib
                    twtitterAPI = importlib.import_module('salonDeFama.twtitterAPI')
                except Exception:
                    # Fallback a import relativo
                    from . import twtitterAPI

                # Preparar lista de tuplas (pos, usuario, puntaje)
                top_list = []
                for idx, registro in enumerate(self.puntajes):
                    nombre, pts = self.leerUsuarioYPuntaje(registro)
                    top_list.append((idx + 1, nombre, pts))

                # Publicar (dry_run=False para publicar realmente)
                try:
                    twtitterAPI.post_top10(top_list, dry_run=False)
                except Exception as e:
                    print(f"Error al publicar Top10 en Twitter: {e}")
            except Exception:
                # Si no existe el módulo de Twitter, no interrumpir el flujo
                pass
    
    
    def guardarPuntajes(self):
        """
        Guarda los puntajes organizados en el archivo JSON
        """
        try:
            with open(self.archivoPuntajes, 'w', encoding='utf-8') as archivo:
                json.dump(self.puntajes, archivo, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar puntajes: {e}")
            return False
    
    
    def leerUsuarioYPuntaje(self, registro):
        """
        Lee el nombre de usuario y puntaje de un registro
        
        Args:
            registro: Diccionario con los datos del registro
            
        Returns:
            tuple: (nombreUsuario, puntaje)
        """
        nombreUsuario = registro.get("usuario", "Desconocido")
        puntaje = registro.get("puntaje", 0)
        return nombreUsuario, puntaje
    
    
    def obtenerTop10(self):
        """
        Obtiene los 10 mejores puntajes
        
        Returns:
            Lista con los mejores 10 puntajes
        """
        return self.puntajes[:10]
    
    
    def dibujarFondo(self):
        """
        Dibuja el fondo decorativo
        """
        self.pantalla.fill(self.colorFondo)
        
        # Estrellas decorativas
        import random
        random.seed(42)  # Semilla fija para que las estrellas no se muevan
        for _ in range(100):
            x = random.randint(0, self.ancho)
            y = random.randint(0, self.alto)
            tamano = random.randint(1, 3)
            brillo = random.randint(150, 255)
            pygame.draw.circle(self.pantalla, (brillo, brillo, brillo), (x, y), tamano)
    
    
    def dibujarTitulo(self):
        """
        Dibuja el título del Hall of Fame
        """
        # Título principal
        titulo = self.fuenteTitulo.render("Salon de la Fama", True, self.colorTitulo)
        rectTitulo = titulo.get_rect(center=(self.ancho // 2, 60))
        
        # Sombra del título
        tituloSombra = self.fuenteTitulo.render("Salon de la Fama", True, (50, 50, 50))
        rectSombra = tituloSombra.get_rect(center=(self.ancho // 2 + 3, 63))
        
        self.pantalla.blit(tituloSombra, rectSombra)
        self.pantalla.blit(titulo, rectTitulo)
        
        # Subtítulo
        subtitulo = self.fuentePequena.render("Los 10 Mejores Puntajes", True, self.colorTextoSecundario)
        rectSubtitulo = subtitulo.get_rect(center=(self.ancho // 2, 110))
        self.pantalla.blit(subtitulo, rectSubtitulo)
        
        # Línea decorativa
        pygame.draw.line(
            self.pantalla,
            self.colorTitulo,
            (self.ancho // 2 - 350, 130),
            (self.ancho // 2 + 350, 130),
            3
        )
    
    
    def dibujarFondoTabla(self):
        """
        Dibuja el fondo de la tabla de puntajes
        """
        margen = 60
        anchoTabla = self.ancho - (margen * 2)
        altoTabla = self.alto - 300  # Agrandado para acomodar todos los usuarios
        yTabla = 150
        
        # Fondo de la tabla con efecto de brillo
        rectTabla = pygame.Rect(margen, yTabla, anchoTabla, altoTabla)
        pygame.draw.rect(self.pantalla, self.colorFondoTabla, rectTabla, border_radius=20)
        pygame.draw.rect(self.pantalla, self.colorBorde, rectTabla, 3, border_radius=20)
    
    
    def dibujarEncabezados(self):
        """
        Dibuja los encabezados de la tabla
        """
        yEncabezado = 170
        
        encabezados = [
            ("POSICIÓN", 140),
            ("JUGADOR", 360),
            ("PUNTAJE", 650)
        ]
        
        for texto, x in encabezados:
            superficie = self.fuenteSubtitulo.render(texto, True, self.colorTitulo)
            self.pantalla.blit(superficie, (x, yEncabezado))
        
        # Línea separadora - Agrandada para nueva altura de tabla
        margen = 60
        pygame.draw.line(
            self.pantalla,
            self.colorBorde,
            (margen, 220),
            (self.ancho - margen, 220),
            2
        )
    
    
    def obtenerColorPosicion(self, posicion):
        """
        Obtiene el color según la posición en el ranking
        
        Args:
            posicion: Posición en el ranking (1-10)
            
        Returns:
            Color correspondiente
        """
        if posicion == 1:
            return self.colorOro
        elif posicion == 2:
            return self.colorPlata
        elif posicion == 3:
            return self.colorBronce
        else:
            return self.colorTexto
    
    
    def obtenerMedallaEmoji(self, posicion):
        """
        Obtiene el texto de la posición
        
        Args:
            posicion: Posición en el ranking (1-10)
            
        Returns:
            String con la posición formateada
        """
        return f"{posicion}°"
    
    
    def dibujarPuntajes(self):
        """
        Dibuja la lista de los 10 mejores puntajes
        """
        top10 = self.obtenerTop10()
        
        yInicial = 245
        espaciado = 40
        
        # Si no hay puntajes
        if not top10:
            textoVacio = self.fuenteTexto.render(
                "No hay puntajes registrados",
                True,
                self.colorTextoSecundario
            )
            rectVacio = textoVacio.get_rect(center=(self.ancho // 2, 380))
            self.pantalla.blit(textoVacio, rectVacio)
            
            textoInfo = self.fuentePequena.render(
                "¡Sé el primero en aparecer en el Salon de la fama!",
                True,
                self.colorTextoSecundario
            )
            rectInfo = textoInfo.get_rect(center=(self.ancho // 2, 420))
            self.pantalla.blit(textoInfo, rectInfo)
            return
        
        # Dibujar cada puntaje
        for i, registro in enumerate(top10):
            posicion = i + 1
            yPos = yInicial + i * espaciado
            
            # Leer usuario y puntaje
            nombreUsuario, puntaje = self.leerUsuarioYPuntaje(registro)
            
            # Color según posición
            color = self.obtenerColorPosicion(posicion)
            
            # Resaltar el podio (top 3)
            if posicion <= 3:
                # Fondo resaltado para el podio
                pygame.draw.rect(
                    self.pantalla,
                    (30, 35, 55),
                    (70, yPos - 6, self.ancho - 140, espaciado - 4),
                    border_radius=8
                )
                pygame.draw.rect(
                    self.pantalla,
                    color,
                    (70, yPos - 6, self.ancho - 140, espaciado - 4),
                    2,
                    border_radius=8
                )
            
            # Nombre de usuario (truncar si es muy largo)
            nombreMostrar = nombreUsuario[:22] + "..." if len(nombreUsuario) > 22 else nombreUsuario
            textoNombre = self.fuenteTexto.render(nombreMostrar, True, color)
            self.pantalla.blit(textoNombre, (240, yPos))
            
            # Puntaje
            textoPuntaje = self.fuenteTexto.render(f"{puntaje:.2f}", True, color)
            self.pantalla.blit(textoPuntaje, (650, yPos))
            
            # Pequeña barra decorativa para el puntaje
            anchoBarra = min(200, int(puntaje / 2.5))  # Escala visual del puntaje
            pygame.draw.rect(
                self.pantalla,
                color,
                (650, yPos + 32, anchoBarra, 3),
                border_radius=2
            )
    
    
    def dibujarBotonVolver(self, posicionMouse):
        """
        Dibuja el botón para volver al juego
        
        Args:
            posicionMouse: Posición actual del mouse
        """
        # Cambiar color si el mouse está sobre el botón
        if self.botonVolver.collidepoint(posicionMouse):
            color = self.colorBotonHover
        else:
            color = self.colorBoton
        
        # Sombra del botón
        pygame.draw.rect(
            self.pantalla,
            (5, 5, 10),
            (self.botonVolver.x + 4, self.botonVolver.y + 4,
             self.botonVolver.width, self.botonVolver.height),
            border_radius=15
        )
        
        # Botón
        pygame.draw.rect(self.pantalla, color, self.botonVolver, border_radius=15)
        pygame.draw.rect(self.pantalla, self.colorTexto, self.botonVolver, 3, border_radius=15)
        
        # Texto del botón
        textoBoton = self.fuenteBoton.render("VOLVER", True, self.colorTexto)
        rectTexto = textoBoton.get_rect(center=self.botonVolver.center)
        self.pantalla.blit(textoBoton, rectTexto)
    
    
    def manejarEventos(self):
        """
        Maneja los eventos de Pygame
        
        Returns:
            Posición del mouse
        """
        posicionMouse = pygame.mouse.get_pos()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.ejecutando = False
            
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if self.botonVolver.collidepoint(posicionMouse):
                    self.volverAlJuego = True
                    self.ejecutando = False
            
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.volverAlJuego = True
                    self.ejecutando = False
                elif evento.key == pygame.K_r:
                    # Recargar puntajes (útil para debugging)
                    self.cargarPuntajes()
        
        return posicionMouse
    
    
    def ejecutar(self):
        """
        Ejecuta el bucle principal del Hall of Fame
        
        Returns:
            True si se debe volver al juego, False si se debe cerrar
        """
        while self.ejecutando:
            posicionMouse = self.manejarEventos()
            
            # Dibujar todo
            self.dibujarFondo()
            self.dibujarFondoTabla()
            self.dibujarTitulo()
            self.dibujarEncabezados()
            self.dibujarPuntajes()
            self.dibujarBotonVolver(posicionMouse)
            
            pygame.display.flip()
            self.reloj.tick(60)
        
        return self.volverAlJuego
    
    
    def cerrar(self):
        """
        Cierra el Hall of Fame
        """
        pygame.quit()


def mostrarHallOfFame(archivoPuntajes="puntajes.json"):
    """
    Función auxiliar para mostrar el Hall of Fame
    
    Args:
        archivoPuntajes: Nombre del archivo JSON con los puntajes
        
    Returns:
        True si se debe volver al juego, False en caso contrario
    """
    hallOfFame = HallOfFame(archivoPuntajes=archivoPuntajes)
    resultado = hallOfFame.ejecutar()
    hallOfFame.cerrar()
    return resultado


# Ejemplo de uso independiente
if __name__ == "__main__":
    print("\n" + "="*50)
    print("HALL OF FAME - SALÓN DE LA FAMA")
    print("="*50)
    print("\nCargando los 10 mejores puntajes...")
    print("Presiona ESC o click en VOLVER para salir\n")
    
    mostrarHallOfFame()
    
    print("\n¡Hasta pronto!\n")