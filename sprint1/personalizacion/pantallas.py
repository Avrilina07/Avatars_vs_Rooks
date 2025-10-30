# pantallas.py

import pygame
import sys
import os
from constantes import ANCHO_VENTANA, ALTO_VENTANA, FPS, PANTALLA_COMPLETA
from componentes import Boton, DropdownTema, Slider
from temas import ConfiguracionTemas
from fondo import ColoresFondoDisponibles
from spotify_api import SpotifyAPI
from pantalla_musica import PantallaMusica
from pantalla_interfaz import PantallaPersonalizacionInterfaz
from preferencias_usuario import GestorPreferencias

carpeta_actual = os.path.dirname(os.path.abspath(__file__))  # personalizacion
carpeta_sprint1 = os.path.dirname(carpeta_actual)  # sprint1
carpeta_avatars = os.path.dirname(carpeta_sprint1)  # Avatars_vs_Rooks
carpeta_juego = os.path.join(carpeta_avatars, 'sprint1', 'juego')
sys.path.insert(0, carpeta_juego)


try:
    from pantallaDificultad import PantallaDificultad
    from pantallaJuego import PantallaJuego
    print(" Módulos del juego importados correctamente")
except ImportError as e:
    print(f"Error al importar módulos del juego: {e}")
    print(f"Asegúrate de que pantallaDificultad.py está en: {carpeta_juego}")
    sys.exit(1)


class PantallaPersonalizacion:
    #Pantalla principal de personalización
    
    def __init__(self):
        # Inicializar gestor de preferencias
        self.gestor_preferencias = GestorPreferencias()
        
        # Cargar preferencias del usuario
        preferencias = self.gestor_preferencias.cargar_preferencias()
        
        # Configurar pantalla
        if PANTALLA_COMPLETA:
            self.pantalla = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            info = pygame.display.Info()
            self.ancho = info.current_w
            self.alto = info.current_h
        else:
            self.pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA), pygame.RESIZABLE)
            self.ancho = ANCHO_VENTANA
            self.alto = ALTO_VENTANA
        
        pygame.display.set_caption("Personalización")
        self.reloj = pygame.time.Clock()
        self.ejecutando = True
        
        # Inicializar API de Spotify para control de volumen
        self.spotify = SpotifyAPI()
        
        # Cargar tema desde preferencias
        self.temaActual = self._obtener_tema_por_nombre(preferencias.get("tema", "Claro (Predeterminado)"))
        
        # Cargar color de fondo desde preferencias
        self.colorFondoPersonalizado = self._obtener_color_por_nombre(
            preferencias.get("color_fondo", "Vino Oscuro")
        )
        
        # Fuentes
        self.fuenteTitulo = pygame.font.SysFont('Arial', 90, bold=True)
        self.fuenteTexto = pygame.font.SysFont('Arial', 24)
        
        # Crear componentes (se actualizarán en actualizarPosiciones)
        self.botonInterfaz = None
        self.botonCancion = None
        self.dropdownTema = None
        self.botonJuego = None
        self.sliderVolumen = None
        
        self.actualizarPosiciones()
        
        # Cargar volumen desde preferencias
        volumen_guardado = preferencias.get("volumen", 50)
        if self.sliderVolumen:
            self.sliderVolumen.valor = volumen_guardado
            self.spotify.cambiarVolumen(volumen_guardado)
    
    def _obtener_tema_por_nombre(self, nombre_tema):
        """
        Obtiene un objeto Tema a partir de su nombre.
        
        Args:
            nombre_tema: Nombre del tema
            
        Returns:
            Tema: Objeto tema correspondiente o tema por defecto
        """
        todos_temas = ConfiguracionTemas.obtenerTodos()
        for tema in todos_temas:
            if tema.nombre == nombre_tema:
                return tema
        # Si no se encuentra, devolver tema por defecto
        return ConfiguracionTemas.CLARO
    
    def _obtener_color_por_nombre(self, nombre_color):
        """
        Obtiene un objeto ColorFondo a partir de su nombre.
        
        Args:
            nombre_color: Nombre del color
            
        Returns:
            ColorFondo: Objeto color correspondiente o color por defecto
        """
        todos_colores = ColoresFondoDisponibles.obtenerTodos()
        for color in todos_colores:
            if color.nombre == nombre_color:
                return color
        # Si no se encuentra, devolver color por defecto
        return ColoresFondoDisponibles.ROJO_MUY_OSCURO_3
    
    def cambiarVolumenSpotify(self, volumen):
        #Callback que se ejecuta cuando el slider cambia
        self.spotify.cambiarVolumen(volumen)
        # Guardar volumen en preferencias
        self.gestor_preferencias.actualizar_volumen(volumen)
    
    def actualizarPosiciones(self):
        #Actualiza las posiciones de los componentes según el tamaño de la ventana

        # Calcular posiciones relativas al centro
        centroX = self.ancho // 2
        centroY = self.alto // 2
        
        # Botones más grandes (310x90 en vez de 280x80)
        self.botonInterfaz = Boton(centroX - 155, centroY - 150, 310, 90, "¡PERSONALIZA TÚ INTERFAZ!", 20)
        self.botonCancion = Boton(centroX - 155, centroY - 40, 310, 90, "¡ELIGE LA CANCIÓN!", 26)
        self.dropdownTema = DropdownTema(centroX - 155, centroY + 70, 310, 55)
        
        # Botón juego a la derecha
        self.botonJuego = Boton(centroX + 180, centroY - 40, 250, 90, "¡VAMOS AL JUEGO!", 25)
        
        # Aplicar colores del fondo personalizado a todos los botones
        for boton in [self.botonInterfaz, self.botonCancion, self.botonJuego]:
            boton.colorNormal = self.colorFondoPersonalizado.obtenerColorBoton()
            boton.colorHover = self.colorFondoPersonalizado.obtenerColorHoverBoton()
            boton.colorBorde = self.colorFondoPersonalizado.obtenerColorBorde()
            boton.colorTexto = self.colorFondoPersonalizado.obtenerColorTextoBoton()
        
        # Aplicar colores al dropdown
        self.dropdownTema.colorFondo = self.colorFondoPersonalizado.obtenerColorBoton()
        self.dropdownTema.colorHover = self.colorFondoPersonalizado.obtenerColorHoverBoton()
        self.dropdownTema.colorBorde = self.colorFondoPersonalizado.obtenerColorBorde()
        self.dropdownTema.colorTexto = self.colorFondoPersonalizado.obtenerColorTextoBoton()
        
        # Slider de volumen en esquina inferior izquierda con callback
        margen = 40
        self.sliderVolumen = Slider(margen, self.alto - 80, 300, 25, 50, callback=self.cambiarVolumenSpotify)
        
        # Aplicar colores al slider según el fondo
        self.sliderVolumen.colorRelleno = self.colorFondoPersonalizado.obtenerColorBoton()
        self.sliderVolumen.colorBoton = self.colorFondoPersonalizado.obtenerColorBoton()
        self.sliderVolumen.colorBordeBoton = self.colorFondoPersonalizado.obtenerColorBorde()
    
    def manejarEventos(self):
        #Maneja todos los eventos de la pantalla
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                # No permitir cerrar si es primera vez (usuario debe completar personalización)
                # Solo permitir salir mediante el botón "Vamos al juego"
                pass
            
            # Detectar cambio de tamaño de ventana
            elif evento.type == pygame.VIDEORESIZE:
                self.ancho = evento.w
                self.alto = evento.h
                self.actualizarPosiciones()
            
            # Tecla ESC deshabilitada - el usuario debe ir al juego
            # No puede volver al login en la primera sesión
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    # No hacer nada, el usuario debe usar el botón "Vamos al juego"
                    pass
            
            # Manejar eventos de botones
            if self.botonInterfaz.manejarEvento(evento):
                self.abrirPantallaInterfaz()
            
            if self.botonCancion.manejarEvento(evento):
                self.abrirPantallaMusica()
            
            # AQUÍ ESTÁ LA NUEVA FUNCIONALIDAD DEL BOTÓN "VAMOS AL JUEGO"
            if self.botonJuego.manejarEvento(evento):
                self.abrirPantallaDificultad()
            
            # Manejar dropdown
            temaSeleccionado = self.dropdownTema.manejarEvento(evento)
            if temaSeleccionado:
                self.temaActual = temaSeleccionado
                print(f"Tema seleccionado: {temaSeleccionado.nombre}")
                # Guardar tema en preferencias
                self.gestor_preferencias.actualizar_tema(temaSeleccionado.nombre)
            
            # Manejar slider
            self.sliderVolumen.manejarEvento(evento)
    
    def abrirPantallaInterfaz(self):
        #Abre la pantalla de personalización de interfaz
        pantallaInterfaz = PantallaPersonalizacionInterfaz(
            self.pantalla, 
            self.colorFondoPersonalizado,
            self.temaActual  
        )
        nuevoColor = pantallaInterfaz.ejecutar()
    
        if nuevoColor:
            self.colorFondoPersonalizado = nuevoColor
            self.actualizarPosiciones()
            # Guardar color en preferencias
            self.gestor_preferencias.actualizar_color_fondo(nuevoColor.nombre)
            print(f"Color guardado en preferencias: {nuevoColor.nombre}")

    def abrirPantallaMusica(self):
        #Abre la pantalla de selección de música
        pantallaMusica = PantallaMusica(
            self.pantalla, 
            self.colorFondoPersonalizado,
            self.temaActual  
        )
        pantallaMusica.ejecutar()

    def _read_session_usuario(self):
        import os, json
        try:
            repo_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
            cwd = os.getcwd()
            print(f'DEBUG: cwd={cwd}')
            # Try several locations for session_user.json (now in dataBase folder)
            candidates = [
                os.path.join(repo_root, 'dataBase', 'session_user.json'),
                os.path.join(cwd, 'dataBase', 'session_user.json'),
                os.path.join(os.path.dirname(__file__), 'dataBase', 'session_user.json')
            ]
            for session_path in candidates:
                try:
                    print(f'DEBUG: buscando session_user en {session_path}')
                    if os.path.exists(session_path):
                        with open(session_path, 'r', encoding='utf-8') as f:
                            try:
                                d = json.load(f)
                                usuario = d.get('usuario')
                                print(f"DEBUG: session_user.json ({session_path}) contiene usuario={usuario}")
                                return usuario
                            except Exception as e:
                                print(f"DEBUG: error leyendo session_user.json {session_path}: {e}")
                except Exception:
                    pass
        except Exception:
            pass
        return None

    def marcarUsuarioPersonalizadoYSalir(self):
        import os, json, subprocess, sys
        usuario = self._read_session_usuario()
        if not usuario:
            # fallback: could prompt, but we'll try to find a single user or abort
            # For safety, abort if no session user
            print('No session usuario encontrado; no se marcará personalizado')
            return

        # Update usuarios.json: set personalizado = True for this usuario (case-insensitive match)
        try:
            repo_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
            # usuarios.json is now in dataBase folder
            usuarios_path = os.path.join(repo_root, 'dataBase', 'usuarios.json')
            print(f'DEBUG: intentando leer usuarios.json en {usuarios_path}')
            if os.path.exists(usuarios_path):
                with open(usuarios_path, 'r', encoding='utf-8') as f:
                    usuarios = json.load(f)
            else:
                usuarios = []

            changed = False
            for u in usuarios:
                name = (u.get('usuario') or u.get('username') or '')
                if name and name.lower() == usuario.lower():
                    u['personalizado'] = True
                    # Persistir el color de fondo seleccionado para que otras pantallas (ej. perfil Tkinter)
                    # puedan leerlo. Guardamos tanto el nombre como el RGB.
                    try:
                        u['colorFondo'] = list(self.colorFondoPersonalizado.rgb)
                        u['colorFondo_nombre'] = getattr(self.colorFondoPersonalizado, 'nombre', None)
                    except Exception:
                        pass
                    changed = True
                    break

            # If session user not found earlier (e.g., usuario was None), try a fallback:
            if not usuario:
                try:
                    # If there's exactly one user, assume it's the current
                    if len(usuarios) == 1:
                        candidate = usuarios[0]
                        name = (candidate.get('usuario') or candidate.get('username') or '')
                        if name:
                            usuario = name
                            candidate['personalizado'] = True
                            try:
                                candidate['colorFondo'] = list(self.colorFondoPersonalizado.rgb)
                                candidate['colorFondo_nombre'] = getattr(self.colorFondoPersonalizado, 'nombre', None)
                            except Exception:
                                pass
                            changed = True
                            print(f"DEBUG: sesión faltante; único usuario en usuarios.json asumido: {usuario}")
                    else:
                        # Usuario presionó ESC o SALIR en dificultad, cerrar todo
                        print("Cerrando aplicación desde pantalla de dificultad...")
                        self.ejecutando = False
                        break
                else:
                    # El juego terminó normalmente (sin ESC), cerrar aplicación
                    print("Juego finalizado, cerrando aplicación...")
                    self.ejecutando = False
                    break
        
        elif accion == 'VOLVER' or accion == 'QUIT':
            # Si intenta volver o salir desde dificultad, cerrar todo
            print("Cerrando aplicación desde pantalla de dificultad...")
            self.ejecutando = False

    def dibujar(self):
        #Dibuja todos los elementos de la pantalla

        # Fondo base con el color personalizado
        self.pantalla.fill(self.colorFondoPersonalizado.rgb)
        
        # Aplicar overlay del tema (opacidad)
        overlay = pygame.Surface((self.ancho, self.alto))
        overlay.set_alpha(self.temaActual.opacidad)
        overlay.fill((0, 0, 0))
        self.pantalla.blit(overlay, (0, 0))
        
        # Título con color según el fondo
        colorTitulo = self.colorFondoPersonalizado.obtenerColorTitulo()
        titulo = self.fuenteTitulo.render("Personalización", True, colorTitulo)
        tituloRect = titulo.get_rect(center=(self.ancho // 2, 150))
        self.pantalla.blit(titulo, tituloRect)
        
        # Dibujar componentes
        self.botonInterfaz.dibujar(self.pantalla)
        self.botonCancion.dibujar(self.pantalla)
        self.dropdownTema.dibujar(self.pantalla)
        self.botonJuego.dibujar(self.pantalla)
        
        # Texto de volumen (esquina inferior izquierda) con color según el fondo
        margen = 40
        textoVolumen = self.fuenteTexto.render("Ajustar volumen", True, colorTitulo)
        self.pantalla.blit(textoVolumen, (margen, self.alto - 110))
        
        self.sliderVolumen.dibujar(self.pantalla)
        
        # Mostrar valor del volumen
        valorTexto = self.fuenteTexto.render(f"{self.sliderVolumen.valor}%", True, colorTitulo)
        self.pantalla.blit(valorTexto, (margen + 310, self.alto - 78))
        
        pygame.display.flip()
    
    def ejecutar(self):
        #Loop principal de la pantalla
        while self.ejecutando:
            self.manejarEventos()
            self.dibujar()
            self.reloj.tick(FPS)
        
        pygame.quit()