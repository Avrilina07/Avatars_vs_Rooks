# spotify_api.py

import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Valores por defecto para el juego
tempo = 120  # Valor de tempo predeterminado (120 BPM es común)
popularidad = 70  # Valor de popularidad predeterminado (escala 0-100)

class SpotifyAPI:
    #Clase para manejar la API de Spotify
    
    def __init__(self):
        #Inicializa la conexión con Spotify
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id="eeb6d740964b4faa9dcbb7e417957ac5",
            client_secret="45f1c3c863654a11a62b60f0c23f835c",
            redirect_uri="http://127.0.0.1:8888/callback",
            scope="user-modify-playback-state user-read-playback-state"))
    
    def buscarCanciones(self, query, limit=5):
        """
        Busca canciones en Spotify
        
        Args:
            query: Texto de búsqueda
            limit: Número máximo de resultados (5)
            
        Returns:
            Lista de canciones encontradas
        """
        try:
            resultados = self.sp.search(q=query, type="track", limit=limit)
            return resultados["tracks"]["items"]
        except Exception as e:
            print(f"Error al buscar canciones: {e}")
            return []
    
    def reproducirCancion(self, trackUri):
        """
        Reproduce una canción en Spotify
        
        Args:
            trackUri: URI de la canción a reproducir
            
        Returns:
            True si se reprodujo correctamente, False si hubo error
        """
        try:
            dispositivos = self.sp.devices()
            
            if len(dispositivos["devices"]) == 0:
                print("No hay dispositivos disponibles - Necesitas Spotify Premium")
                return False
            
            deviceId = dispositivos["devices"][0]["id"]
            self.sp.start_playback(device_id=deviceId, uris=[trackUri])
            return True
            
        except Exception as e:
            print(f"Error al reproducir canción: {e}")
            return False
    
    def obtenerInfoCancion(self, track):
        """
        Extrae información de una canción
        
        Args:
            track: Objeto track de Spotify
            
        Returns:
            Tupla (nombre, artista, uri, tempo, popularidad)
        """
        global tempo, popularidad  # Usar las variables globales
        
        nombre = track["name"]
        artista = track["artists"][0]["name"]
        uri = track["uri"]
        
        # Actualizar las variables globales con los datos de la canción actual
        try:
            features = self.sp.audio_features([uri])[0]
            tempo = features.get("tempo", tempo)  # Usar el valor existente si no se puede obtener
        except:
            pass  # Mantener el tempo actual si hay error
            
        try:
            track_info = self.sp.track(uri)
            popularidad = track_info.get("popularity", popularidad)  # Usar el valor existente si no se puede obtener
        except:
            pass  # Mantener la popularidad actual si hay error
            
        return nombre, artista, uri, tempo, popularidad
    
    def cambiarVolumen(self, volumen):
        """
        Cambia el volumen de reproducción de Spotify
        
        Args:
            volumen: Valor entre 0 y 100
            
        Returns:
            True si se cambió correctamente, False si hubo error
        """
        try:
            self.sp.volume(volume_percent=volumen)
            return True
        except Exception as e:
            print(f"Error al cambiar volumen: {e}")
            return False