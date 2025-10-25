# componentes.py
import pygame
from temas import ConfiguracionTemas

class Boton:
    #Componente de botón interactivo con efecto hover
    
    def __init__(self, x, y, ancho, alto, texto, fuenteSize=24):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.fuente = pygame.font.SysFont('Arial', fuenteSize, bold=True)
        self.colorNormal = (245, 245, 220)  # Crema claro
        self.colorHover = (232, 232, 232)  # Gris muy claro
        self.colorBorde = (0, 0, 0)  # Negro
        self.colorTexto = (0, 0, 0)  # Negro
        self.hover = False
    
    def dibujar(self, pantalla):
        #Dibuja el botón en la pantalla
        color = self.colorHover if self.hover else self.colorNormal
        pygame.draw.rect(pantalla, color, self.rect)
        pygame.draw.rect(pantalla, self.colorBorde, self.rect, 3)
        
        textoSurface = self.fuente.render(self.texto, True, self.colorTexto)
        textoRect = textoSurface.get_rect(center=self.rect.center)
        pantalla.blit(textoSurface, textoRect)
    
    def manejarEvento(self, evento):
        #Maneja eventos del mouse sobre el botón
        if evento.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(evento.pos)
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(evento.pos):
                return True
        return False

class DropdownTema:
    #Componente dropdown para seleccionar temas
    
    def __init__(self, x, y, ancho, alto):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.temas = ConfiguracionTemas.obtenerTodos()
        self.temaSeleccionado = self.temas[0]
        self.desplegado = False
        self.fuente = pygame.font.SysFont('Arial', 22, bold=True)
        self.colorFondo = (245, 245, 220)  # Crema claro
        self.colorBorde = (0, 0, 0)  # Negro
        self.colorHover = (232, 232, 232)  # Gris muy claro
        self.colorTexto = (0, 0, 0)  # Negro
        self.opcionHover = -1
    
    def dibujar(self, pantalla):
        #Dibuja el dropdown en la pantalla

        # Dibujar botón principal
        pygame.draw.rect(pantalla, self.colorFondo, self.rect)
        pygame.draw.rect(pantalla, self.colorBorde, self.rect, 3)
        
        # Texto del dropdown
        texto = self.fuente.render("¡ELIGE EL TEMA!", True, self.colorTexto)
        textoRect = texto.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        pantalla.blit(texto, textoRect)
        
        # Dibujar flecha
        flechaX = self.rect.right - 30
        flechaY = self.rect.centery
        puntosFlecha = [
            (flechaX - 5, flechaY - 5),
            (flechaX + 5, flechaY - 5),
            (flechaX, flechaY + 5)
        ]
        pygame.draw.polygon(pantalla, self.colorTexto, puntosFlecha)
        
        # Dibujar opciones si está desplegado
        if self.desplegado:
            for i, tema in enumerate(self.temas):
                opcionRect = pygame.Rect(
                    self.rect.x,
                    self.rect.bottom + i * 40,
                    self.rect.width,
                    40
                )
                
                color = self.colorHover if i == self.opcionHover else self.colorFondo
                pygame.draw.rect(pantalla, color, opcionRect)
                pygame.draw.rect(pantalla, self.colorBorde, opcionRect, 3)
                
                textoOpcion = self.fuente.render(tema.nombre, True, self.colorTexto)
                textoOpcionRect = textoOpcion.get_rect(midleft=(opcionRect.x + 10, opcionRect.centery))
                pantalla.blit(textoOpcion, textoOpcionRect)
    
    def manejarEvento(self, evento):
        #Maneja eventos del dropdown
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(evento.pos):
                self.desplegado = not self.desplegado
                return None
            
            if self.desplegado:
                for i, tema in enumerate(self.temas):
                    opcionRect = pygame.Rect(
                        self.rect.x,
                        self.rect.bottom + i * 40,
                        self.rect.width,
                        40
                    )
                    if opcionRect.collidepoint(evento.pos):
                        self.temaSeleccionado = tema
                        self.desplegado = False
                        return tema
                
                self.desplegado = False
        
        elif evento.type == pygame.MOUSEMOTION:
            if self.desplegado:
                self.opcionHover = -1
                for i, tema in enumerate(self.temas):
                    opcionRect = pygame.Rect(
                        self.rect.x,
                        self.rect.bottom + i * 40,
                        self.rect.width,
                        40
                    )
                    if opcionRect.collidepoint(evento.pos):
                        self.opcionHover = i
                        break
        
        return None

class Slider:
    #Componente slider para controlar valores numéricos
    
    def __init__(self, x, y, ancho, alto, valorInicial=50, callback=None):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.valor = valorInicial  # 0-100
        self.valorAnterior = valorInicial
        self.arrastrando = False
        # Colores por defecto (pueden ser cambiados desde fuera)
        self.colorBarra = (211, 211, 211)  # Gris claro
        self.colorRelleno = (245, 245, 220)  # Crema Claro
        self.colorBoton = (245, 245, 220)  # Crema Claro
        self.colorBordeBoton = (0, 0, 0)  # Negro
        self.fuente = pygame.font.Font(None, 20)
        self.callback = callback  # Función a llamar cuando cambia el valor
    
    def dibujar(self, pantalla):
        #Dibuja el slider en la pantalla

        # Dibujar barra de fondo con bordes redondeados
        pygame.draw.rect(pantalla, self.colorBarra, self.rect, border_radius=10)
        
        # Dibujar relleno según el valor
        anchoRelleno = int(self.rect.width * (self.valor / 100))
        if anchoRelleno > 0:
            rectRelleno = pygame.Rect(self.rect.x, self.rect.y, anchoRelleno, self.rect.height)
            pygame.draw.rect(pantalla, self.colorRelleno, rectRelleno, border_radius=10)
        
        # Dibujar botón deslizante (círculo)
        botonX = self.rect.x + anchoRelleno
        botonY = self.rect.centery
        radio = 15
        pygame.draw.circle(pantalla, self.colorBoton, (botonX, botonY), radio)
        pygame.draw.circle(pantalla, self.colorBordeBoton, (botonX, botonY), radio, 3)
    
    def manejarEvento(self, evento):
        #Maneja eventos del slider
        if evento.type == pygame.MOUSEBUTTONDOWN:
            botonX = self.rect.x + int(self.rect.width * (self.valor / 100))
            botonY = self.rect.centery
            # Verificar si el clic está en el círculo o en la barra
            distancia = ((evento.pos[0] - botonX) ** 2 + (evento.pos[1] - botonY) ** 2) ** 0.5
            if distancia <= 15 or self.rect.collidepoint(evento.pos):
                self.arrastrando = True
                self.actualizarValor(evento.pos[0])
        
        elif evento.type == pygame.MOUSEBUTTONUP:
            self.arrastrando = False
        
        elif evento.type == pygame.MOUSEMOTION:
            if self.arrastrando:
                self.actualizarValor(evento.pos[0])
    
    def actualizarValor(self, mouseX):
        #Actualiza el valor del slider según la posición del mouse
        posicionRelativa = mouseX - self.rect.x
        self.valor = max(0, min(100, int((posicionRelativa / self.rect.width) * 100)))
        
        # Llamar al callback si el valor cambió y hay callback definido
        if self.callback and self.valor != self.valorAnterior:
            self.callback(self.valor)
            self.valorAnterior = self.valor

class SelectorColor:
    #Selector visual de color que muestra una cuadrícula de colores
    def __init__(self, x, y, coloresDisponibles, columnas=5):
        self.x = x
        self.y = y
        self.colores = coloresDisponibles
        self.columnas = columnas
        self.tamanoCelda = 60
        self.espacio = 10
        self.colorSeleccionado = None
        self.fuente = pygame.font.SysFont('Arial', 16)
    
    def dibujar(self, pantalla):
        #Dibuja la cuadrícula de colores
        for i, color in enumerate(self.colores):
            fila = i // self.columnas
            col = i % self.columnas
            
            x = self.x + col * (self.tamanoCelda + self.espacio)
            y = self.y + fila * (self.tamanoCelda + self.espacio)
            
            rect = pygame.Rect(x, y, self.tamanoCelda, self.tamanoCelda)
            
            # Dibujar cuadrado de color
            pygame.draw.rect(pantalla, color.rgb, rect)
            pygame.draw.rect(pantalla, (0, 0, 0), rect, 2)
    
    def manejarEvento(self, evento):
        #Detecta clic en un color
        if evento.type == pygame.MOUSEBUTTONDOWN:
            for i, color in enumerate(self.colores):
                fila = i // self.columnas
                col = i % self.columnas
                
                x = self.x + col * (self.tamanoCelda + self.espacio)
                y = self.y + fila * (self.tamanoCelda + self.espacio)
                
                rect = pygame.Rect(x, y, self.tamanoCelda, self.tamanoCelda)
                
                if rect.collidepoint(evento.pos):
                    self.colorSeleccionado = color
                    return color
        
        return None

class BotonVolver:
    #Botón especial para volver a la pantalla anterior
    
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 120, 40)
        self.fuente = pygame.font.SysFont('Arial', 20, bold=True)
        # Colores por defecto (pueden ser cambiados desde fuera)
        self.colorFondo = (245, 245, 220)
        self.colorHover = (232, 232, 232)
        self.colorBorde = (0, 0, 0)
        self.colorTexto = (0, 0, 0)
        self.hover = False
    
    def dibujar(self, pantalla):
        #Dibuja el botón volver
        color = self.colorHover if self.hover else self.colorFondo
        pygame.draw.rect(pantalla, color, self.rect)
        pygame.draw.rect(pantalla, self.colorBorde, self.rect, 2)
        
        # Flecha y texto
        texto = self.fuente.render("← Volver", True, self.colorTexto)
        textoRect = texto.get_rect(center=self.rect.center)
        pantalla.blit(texto, textoRect)
    
    def manejarEvento(self, evento):
        #Maneja eventos del botón
        if evento.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(evento.pos)
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(evento.pos):
                return True
        return False