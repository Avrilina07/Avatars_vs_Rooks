# pantallaDificultad.py
# Pantalla de selección de dificultad para Avatars VS Rooks

import pygame
import sys
import os

# Importar desde personalizacion 
carpeta_actual = os.path.dirname(os.path.abspath(__file__))  # juego
carpeta_sprint1 = os.path.dirname(carpeta_actual)  # sprint1
carpeta_personalizacion = os.path.join(carpeta_sprint1, 'personalizacion')
sys.path.insert(0, carpeta_personalizacion)

from constantes import FPS, PANTALLA_COMPLETA
from componentes import Boton, BotonVolver

# Importar pantallaJuego desde la misma carpeta
from pantallaJuego import PantallaJuego


class PantallaDificultad:
    """Pantalla de selección de dificultad con 4 opciones"""
    
    def __init__(self, pantalla, colorFondo, temaActual):
        """
        Inicializa la pantalla de dificultad
        
        Args:
            pantalla: Surface de pygame
            colorFondo: Objeto ColorFondo con configuración de colores
            temaActual: Objeto Tema con opacidad
        """
        self.pantalla = pantalla
        self.reloj = pygame.time.Clock()
        self.ejecutando = True
        self.volver = False
        self.iniciarJuego = False
        
        # Configuración de colores y tema
        self.colorFondo = colorFondo
        self.temaActual = temaActual
        
        # Dimensiones de pantalla
        self.ancho, self.alto = self.pantalla.get_size()
        
        # Dificultad seleccionada
        self.dificultadSeleccionada = None
        
        # Fuentes
        self.fuenteTitulo = pygame.font.SysFont('Arial', 60, bold=True)
        self.fuenteSubtitulo = pygame.font.SysFont('Arial', 28)
        self.fuenteDescripcion = pygame.font.SysFont('Arial', 18)
        
        # Crear botones
        self.crearBotones()
        
        # Botón volver
        self.botonVolver = BotonVolver(40, 40)
        self.actualizarColoresBotonVolver()
    
    def crearBotones(self):
        """Crea los botones de dificultad"""
        # Configuración de botones
        anchoBoton = 250
        altoBoton = 70
        espacioVertical = 20
        
        # Calcular posición inicial centrada
        totalAltura = 4 * altoBoton + 3 * espacioVertical
        inicioY = (self.alto - totalAltura) // 2
        centroX = (self.ancho - anchoBoton) // 2
        
        # Datos de las dificultades
        dificultades = [
            {
                'nombre': 'FÁCIL',
                'descripcion': 'Para principiantes',
                'color_texto': (0, 150, 0)  # Verde
            },
            {
                'nombre': 'MEDIO',
                'descripcion': 'Desafío balanceado',
                'color_texto': (255, 165, 0)  # Naranja
            },
            {
                'nombre': 'DIFÍCIL',
                'descripcion': 'Para expertos',
                'color_texto': (255, 0, 0)  # Rojo
            },
            {
                'nombre': 'SALIR',
                'descripcion': 'Volver al menú',
                'color_texto': None  # Usará el color por defecto
            }
        ]
        
        self.botones = []
        for i, dif in enumerate(dificultades):
            y = inicioY + i * (altoBoton + espacioVertical)
            boton = Boton(centroX, y, anchoBoton, altoBoton, dif['nombre'], 32)
            
            # Aplicar colores según el fondo personalizado
            boton.colorNormal = self.colorFondo.obtenerColorBoton()
            boton.colorHover = self.colorFondo.obtenerColorHoverBoton()
            boton.colorBorde = self.colorFondo.obtenerColorBorde()
            
            # Color de texto especial para cada dificultad (excepto SALIR)
            if dif['color_texto']:
                boton.colorTexto = dif['color_texto']
            else:
                boton.colorTexto = self.colorFondo.obtenerColorTextoBoton()
            
            # Guardar información adicional
            boton.descripcion = dif['descripcion']
            boton.nombre = dif['nombre']
            
            self.botones.append(boton)
    
    def actualizarColoresBotonVolver(self):
        """Actualiza los colores del botón volver según el tema"""
        self.botonVolver.colorFondo = self.colorFondo.obtenerColorBoton()
        self.botonVolver.colorHover = self.colorFondo.obtenerColorHoverBoton()
        self.botonVolver.colorBorde = self.colorFondo.obtenerColorBorde()
        self.botonVolver.colorTexto = self.colorFondo.obtenerColorTextoBoton()
    
    def manejarEventos(self):
        """Procesa los eventos de entrada"""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.ejecutando = False
                self.volver = False
                return 'QUIT'
            
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.ejecutando = False
                    self.volver = True
                    return 'VOLVER'
            
            # Manejar botón volver
            if self.botonVolver.manejarEvento(evento):
                self.ejecutando = False
                self.volver = True
                return 'VOLVER'
            
            # Manejar botones de dificultad
            for boton in self.botones:
                if boton.manejarEvento(evento):
                    if boton.nombre == 'SALIR':
                        self.ejecutando = False
                        self.volver = True
                        return 'VOLVER'
                    else:
                        # Seleccionar dificultad e iniciar juego
                        self.dificultadSeleccionada = boton.nombre
                        self.iniciarJuego = True
                        self.ejecutando = False
                        print(f"Dificultad seleccionada: {self.dificultadSeleccionada}")
                        return 'JUGAR'
        
        return None
    
    def dibujar(self):
        """Dibuja todos los elementos en pantalla"""
        # 1. Fondo con color personalizado
        self.pantalla.fill(self.colorFondo.rgb)
        
        # 2. Overlay de tema (opacidad)
        overlay = pygame.Surface((self.ancho, self.alto))
        overlay.set_alpha(self.temaActual.opacidad)
        overlay.fill((0, 0, 0))
        self.pantalla.blit(overlay, (0, 0))
        
        # 3. Título
        colorTexto = self.colorFondo.obtenerColorTitulo()
        titulo = self.fuenteTitulo.render("Seleccionar Dificultad", True, colorTexto)
        tituloRect = titulo.get_rect(center=(self.ancho // 2, 100))
        self.pantalla.blit(titulo, tituloRect)
        
        # 4. Subtítulo
        subtitulo = self.fuenteSubtitulo.render("Elige tu nivel de desafío", True, colorTexto)
        subtituloRect = subtitulo.get_rect(center=(self.ancho // 2, 150))
        self.pantalla.blit(subtitulo, subtituloRect)
        
        # 5. Botón volver
        self.botonVolver.dibujar(self.pantalla)
        
        # 6. Botones de dificultad con descripciones
        for boton in self.botones:
            boton.dibujar(self.pantalla)
            
            # Dibujar descripción debajo de cada botón (excepto para los botones hover)
            if not boton.hover:
                desc = self.fuenteDescripcion.render(boton.descripcion, True, colorTexto)
                descRect = desc.get_rect(center=(boton.rect.centerx, boton.rect.bottom + 10))
                self.pantalla.blit(desc, descRect)
        
        # 7. Información adicional en la parte inferior
        info = self.fuenteDescripcion.render("Presiona ESC o el botón Volver para regresar", True, colorTexto)
        infoRect = info.get_rect(center=(self.ancho // 2, self.alto - 30))
        self.pantalla.blit(info, infoRect)
        
        pygame.display.flip()
    
    def ejecutar(self):
        """
        Loop principal de la pantalla
        
        Returns:
            tuple: (accion, dificultad) donde accion puede ser 'JUGAR', 'VOLVER' o 'QUIT'
        """
        while self.ejecutando:
            accion = self.manejarEventos()
            self.dibujar()
            self.reloj.tick(FPS)
        
        if self.iniciarJuego:
            return ('JUGAR', self.dificultadSeleccionada)
        elif self.volver:
            return ('VOLVER', None)
        else:
            return ('QUIT', None)