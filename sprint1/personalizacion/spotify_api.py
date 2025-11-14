# spotify_api.py

import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Variables globales para tracking
# Estas variables se actualizan automáticamente cuando se reproduce una canción
tempo = 120  # Valor por defecto (120 BPM)
popularidad = 50  # Valor por defecto (50/100)


class SpotifyAPI:
    """Clase para manejar la API de Spotify"""
    
    def __init__(self):
        """Inicializa la conexión con Spotify"""
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id="eeb6d740964b4faa9dcbb7e417957ac5",
            client_secret="45f1c3c863654a11a62b60f0c23f835c",
            redirect_uri="http://127.0.0.1:8888/callback",
            scope="user-modify-playback-state user-read-playback-state user-read-currently-playing"))
        
        # Variables de instancia para tracking interno
        self.ultimo_tempo = 120
        self.ultima_popularidad = 50
    
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
    
    def reproducirCancion(self, trackUri, repetir=True):
        """
        Reproduce una canción en Spotify y actualiza las variables globales
        
        Args:
            trackUri: URI de la canción a reproducir
            repetir: Si True, activa el modo repeat para que la canción se repita
            
        Returns:
            True si se reprodujo correctamente, False si hubo error
        """
        global tempo, popularidad
        
        try:
            dispositivos = self.sp.devices()
            
            if len(dispositivos["devices"]) == 0:
                print("⚠️  No hay dispositivos disponibles - Necesitas Spotify Premium")
                return False
            
            deviceId = dispositivos["devices"][0]["id"]
            self.sp.start_playback(device_id=deviceId, uris=[trackUri])
            
            # Activar modo repeat si se solicita
            if repetir:
                try:
                    self.sp.repeat(state="track")  # "track" repite la canción actual
                    print("🔁 Modo repeat activado - La canción se repetirá automáticamente")
                except Exception as e:
                    print(f"⚠️  No se pudo activar modo repeat: {e}")
            
            # Obtener información de la canción que se está reproduciendo
            # Extraer el track_id del URI
            track_id = trackUri.split(":")[-1]
            
            try:
                # Obtener info del track
                track_info = self.sp.track(track_id)
                
                # Actualizar popularidad
                if track_info and "popularity" in track_info:
                    popularidad = track_info["popularity"]
                    self.ultima_popularidad = popularidad
                    print(f"🎵 Popularidad actualizada: {popularidad}/100")
                
                # Obtener audio features para tempo
                features = self.sp.audio_features([track_id])
                if features and isinstance(features, list) and features[0]:
                    if "tempo" in features[0]:
                        tempo = features[0]["tempo"]
                        self.ultimo_tempo = tempo
                        print(f"🎵 Tempo actualizado: {tempo:.0f} BPM")
                
                print(f"✅ Variables globales actualizadas: tempo={tempo:.0f}, popularidad={popularidad}")
                
            except Exception as e:
                print(f"⚠️  Error al obtener audio features: {e}")
                print(f"   Usando valores por defecto: tempo={tempo}, popularidad={popularidad}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al reproducir canción: {e}")
            return False
    
    def obtenerInfoCancion(self, track):
        """
        Extrae información de una canción y actualiza variables globales
        
        Args:
            track: Objeto track de Spotify
            
        Returns:
            Tupla (nombre, artista, uri, tempo, popularidad)
        """
        global tempo, popularidad
        
        try:
            nombre = track.get("name")
            artista = track.get("artists", [{}])[0].get("name") if track.get("artists") else None
            uri = track.get("uri")
            
            # Obtener popularidad del track
            popularity = track.get("popularity")
            
            # Obtener audio features para extraer tempo (BPM)
            track_id = track.get("id")
            current_tempo = None
            
            if track_id:
                try:
                    features = self.sp.audio_features([track_id])
                    if features and isinstance(features, list) and features[0]:
                        current_tempo = features[0].get("tempo")
                except Exception as e:
                    print(f"⚠️  No se pudo obtener audio features: {e}")
                    current_tempo = None
            
            # Actualizar variables globales
            if current_tempo is not None:
                tempo = current_tempo
                self.ultimo_tempo = tempo
                print(f"🎵 Tempo actualizado: {tempo:.0f} BPM")
            
            if popularity is not None:
                popularidad = popularity
                self.ultima_popularidad = popularidad
                print(f"🎵 Popularidad actualizada: {popularidad}/100")
            
            return nombre, artista, uri, tempo, popularidad
            
        except Exception as e:
            print(f"❌ Error al obtener info de la canción: {e}")
            return None, None, None, None, None
    
    def obtenerCancionActual(self):
        """
        Obtiene información de la canción que se está reproduciendo actualmente
        y actualiza las variables globales
        
        Returns:
            Diccionario con info de la canción o None si hay error
        """
        global tempo, popularidad
        
        try:
            current = self.sp.current_playback()
            
            if current and current.get("item"):
                track = current["item"]
                track_id = track.get("id")
                
                # Actualizar popularidad
                if "popularity" in track:
                    popularidad = track["popularity"]
                    self.ultima_popularidad = popularidad
                
                # Obtener audio features
                if track_id:
                    try:
                        features = self.sp.audio_features([track_id])
                        if features and features[0] and "tempo" in features[0]:
                            tempo = features[0]["tempo"]
                            self.ultimo_tempo = tempo
                    except Exception:
                        pass
                
                print(f"🎵 Canción actual: {track.get('name')} - Tempo: {tempo:.0f} BPM, Pop: {popularidad}/100")
                
                return {
                    "nombre": track.get("name"),
                    "artista": track["artists"][0]["name"] if track.get("artists") else None,
                    "tempo": tempo,
                    "popularidad": popularidad
                }
            
            return None
            
        except Exception as e:
            print(f"⚠️  Error al obtener canción actual: {e}")
            return None
    
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
            print(f"🔊 Volumen ajustado a {volumen}%")
            return True
        except Exception as e:
            print(f"❌ Error al cambiar volumen: {e}")
            return False
    
    def pausarMusica(self):
        """
        Pausa la reproducción actual de Spotify
        
        Returns:
            True si se pausó correctamente, False si hubo error
        """
        try:
            self.sp.pause_playback()
            print("⏸️  Música pausada")
            return True
        except Exception as e:
            print(f"❌ Error al pausar música: {e}")
            return False
    
    def reanudarMusica(self):
        """
        Reanuda la reproducción pausada de Spotify
        
        Returns:
            True si se reanudó correctamente, False si hubo error
        """
        try:
            self.sp.start_playback()
            print("▶️  Música reanudada")
            return True
        except Exception as e:
            print(f"❌ Error al reanudar música: {e}")
            return False
    
    def activarRepeat(self, modo="track"):
        """
        Activa el modo repeat de Spotify
        
        Args:
            modo: "track" (repite canción actual), "context" (repite playlist/album), "off" (desactiva)
            
        Returns:
            True si se activó correctamente, False si hubo error
        """
        try:
            self.sp.repeat(state=modo)
            if modo == "track":
                print("🔁 Modo repeat activado: La canción se repetirá")
            elif modo == "context":
                print("🔁 Modo repeat activado: La playlist/album se repetirá")
            else:
                print("🔁 Modo repeat desactivado")
            return True
        except Exception as e:
            print(f"❌ Error al activar repeat: {e}")
            return False
    
    def desactivarRepeat(self):
        """
        Desactiva el modo repeat de Spotify
        
        Returns:
            True si se desactivó correctamente, False si hubo error
        """
        return self.activarRepeat(modo="off")
    
    def obtenerValoresActuales(self):
        """
        Obtiene los valores actuales de tempo y popularidad
        Útil para debugging
        
        Returns:
            Tupla (tempo, popularidad)
        """
        return (tempo, popularidad)


# Función auxiliar para obtener los valores actuales desde cualquier parte del código
def obtenerTempoYPopularidad():
    """
    Función auxiliar para obtener los valores actuales de tempo y popularidad
    
    Returns:
        Tupla (tempo, popularidad)
    """
    global tempo, popularidad
    return (tempo, popularidad)


# Para debugging - ejecutar este archivo directamente
if __name__ == "__main__":
    print("=" * 60)
    print("SPOTIFY API - Test de Variables Globales")
    print("=" * 60)
    print()
    
    print(f"📊 Valores iniciales:")
    print(f"   Tempo: {tempo} BPM")
    print(f"   Popularidad: {popularidad}/100")
    print()
    
    try:
        api = SpotifyAPI()
        print("✅ Conexión con Spotify establecida")
        
        # Intentar obtener canción actual
        print("\n🔍 Intentando obtener canción actual...")
        info = api.obtenerCancionActual()
        
        if info:
            print(f"✅ Canción detectada: {info['nombre']}")
        else:
            print("⚠️  No hay reproducción activa")
        
        print(f"\n📊 Valores finales:")
        print(f"   Tempo: {tempo} BPM")
        print(f"   Popularidad: {popularidad}/100")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("=" * 60)