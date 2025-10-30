# spotify_Api.py

import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Variables globales para tracking
tempo = 120  # Valor por defecto (120 BPM)
popularidad = 50  # Valor por defecto (50/100)


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
            Tupla (nombre, artista, uri)
        """
        try:
            nombre = track.get("name")
            artista = track.get("artists", [{}])[0].get("name") if track.get("artists") else None
            uri = track.get("uri")
            # Popularity suele venir en el objeto track
            popularity = track.get("popularity")

            # Obtener audio features para extraer tempo (BPM)
            global tempo, popularidad
            
            track_id = track.get("id")
            current_tempo = None
            if track_id:
                try:
                    features = self.sp.audio_features([track_id])
                    if features and isinstance(features, list) and features[0]:
                        current_tempo = features[0].get("tempo")
                except Exception:
                    # No fallar por audio features; dejar tempo como None
                    current_tempo = None
            
            # Actualizar variables globales
            if current_tempo is not None:
                tempo = current_tempo
            if popularity is not None:
                popularidad = popularity

            return nombre, artista, uri, tempo, popularity
        except Exception as e:
            print(f"Error al obtener info de la canción: {e}")
            return None, None, None, None, None
    
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
    
    def pausarMusica(self):
        """
        Pausa la reproducción actual de Spotify
        
        Returns:
            True si se pausó correctamente, False si hubo error
        """
        try:
            self.sp.pause_playback()
            print("Música pausada")
            return True
        except Exception as e:
            print(f"Error al pausar música: {e}")
            return False
    
    def reanudarMusica(self):
        """
        Reanuda la reproducción pausada de Spotify
        
        Returns:
            True si se reanudó correctamente, False si hubo error
        """
        try:
            self.sp.start_playback()
            print("Música reanudada")
            return True
        except Exception as e:
            print(f"Error al reanudar música: {e}")
            return False