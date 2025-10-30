# preferencias_usuario.py

import json
import os


class GestorPreferencias:
    """
    Gestiona el guardado y carga de preferencias de personalización del usuario.
    Las preferencias se guardan en un archivo JSON en la carpeta dataBase.
    """
    
    def __init__(self):
        # Obtener rutas
        self.carpeta_actual = os.path.dirname(os.path.abspath(__file__))  # personalizacion
        self.carpeta_sprint1 = os.path.dirname(self.carpeta_actual)  # sprint1
        self.carpeta_database = os.path.join(self.carpeta_sprint1, 'dataBase')
        self.archivo_session = os.path.join(self.carpeta_database, 'session_user.json')
        self.archivo_preferencias = os.path.join(self.carpeta_database, 'preferencias_usuario.json')
        
        # Asegurar que la carpeta database existe
        os.makedirs(self.carpeta_database, exist_ok=True)
    
    def obtener_usuario_activo(self):
        """
        Obtiene el nombre de usuario activo desde session_user.json
        
        Returns:
            str: Nombre de usuario activo o None si no hay sesión
        """
        try:
            if os.path.exists(self.archivo_session):
                with open(self.archivo_session, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    return session_data.get('usuario', None)
        except Exception as e:
            print(f"Error al leer sesión de usuario: {e}")
        return None
    
    def cargar_preferencias(self, usuario=None):
        """
        Carga las preferencias de personalización del usuario.
        
        Args:
            usuario: Nombre de usuario (opcional, si no se proporciona usa el activo)
            
        Returns:
            dict: Diccionario con las preferencias del usuario o preferencias por defecto
        """
        if usuario is None:
            usuario = self.obtener_usuario_activo()
        
        if usuario is None:
            return self._obtener_preferencias_default()
        
        try:
            if os.path.exists(self.archivo_preferencias):
                with open(self.archivo_preferencias, 'r', encoding='utf-8') as f:
                    todas_preferencias = json.load(f)
                    
                    # Si el usuario tiene preferencias guardadas, las devuelve
                    if usuario in todas_preferencias:
                        return todas_preferencias[usuario]
        except Exception as e:
            print(f"Error al cargar preferencias: {e}")
        
        # Si no hay preferencias guardadas, devuelve las default
        return self._obtener_preferencias_default()
    
    def guardar_preferencias(self, preferencias, usuario=None):
        """
        Guarda las preferencias de personalización del usuario.
        
        Args:
            preferencias: Diccionario con las preferencias a guardar
            usuario: Nombre de usuario (opcional, si no se proporciona usa el activo)
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        if usuario is None:
            usuario = self.obtener_usuario_activo()
        
        if usuario is None:
            print("No hay usuario activo, no se pueden guardar preferencias")
            return False
        
        try:
            # Cargar preferencias existentes
            todas_preferencias = {}
            if os.path.exists(self.archivo_preferencias):
                with open(self.archivo_preferencias, 'r', encoding='utf-8') as f:
                    todas_preferencias = json.load(f)
            
            # Actualizar preferencias del usuario
            todas_preferencias[usuario] = preferencias
            
            # Guardar todas las preferencias
            with open(self.archivo_preferencias, 'w', encoding='utf-8') as f:
                json.dump(todas_preferencias, f, indent=4, ensure_ascii=False)
            
            print(f"Preferencias guardadas para el usuario: {usuario}")
            return True
            
        except Exception as e:
            print(f"Error al guardar preferencias: {e}")
            return False
    
    def _obtener_preferencias_default(self):
        """
        Retorna las preferencias por defecto.
        
        Returns:
            dict: Diccionario con preferencias por defecto
        """
        return {
            "color_fondo": "Vino Oscuro",  # Nombre del color de fondo
            "tema": "Claro (Predeterminado)",  # Nombre del tema
            "volumen": 50,  # Volumen (0-100)
            "ultima_cancion": None  # URI de la última canción reproducida
        }
    
    def actualizar_color_fondo(self, nombre_color, usuario=None):
        """
        Actualiza solo el color de fondo en las preferencias.
        
        Args:
            nombre_color: Nombre del color de fondo
            usuario: Nombre de usuario (opcional)
        """
        preferencias = self.cargar_preferencias(usuario)
        preferencias["color_fondo"] = nombre_color
        self.guardar_preferencias(preferencias, usuario)
    
    def actualizar_tema(self, nombre_tema, usuario=None):
        """
        Actualiza solo el tema en las preferencias.
        
        Args:
            nombre_tema: Nombre del tema
            usuario: Nombre de usuario (opcional)
        """
        preferencias = self.cargar_preferencias(usuario)
        preferencias["tema"] = nombre_tema
        self.guardar_preferencias(preferencias, usuario)
    
    def actualizar_volumen(self, volumen, usuario=None):
        """
        Actualiza solo el volumen en las preferencias.
        
        Args:
            volumen: Valor del volumen (0-100)
            usuario: Nombre de usuario (opcional)
        """
        preferencias = self.cargar_preferencias(usuario)
        preferencias["volumen"] = volumen
        self.guardar_preferencias(preferencias, usuario)
    
    def actualizar_cancion(self, track_uri, usuario=None):
        """
        Actualiza la última canción reproducida.
        
        Args:
            track_uri: URI de la canción de Spotify
            usuario: Nombre de usuario (opcional)
        """
        preferencias = self.cargar_preferencias(usuario)
        preferencias["ultima_cancion"] = track_uri
        self.guardar_preferencias(preferencias, usuario)
