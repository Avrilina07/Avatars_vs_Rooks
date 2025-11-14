import math
import json
import os
from datetime import datetime

"""
ALGORITMO DEL BANQUERO - Cálculo de Puntajes
=============================================

Este módulo contiene la lógica para calcular puntajes en el juego usando
el algoritmo del banquero, que considera múltiples factores:
- Tempo de la música (desde Spotify API)
- Popularidad de la canción (desde Spotify API)
- Cantidad de avatares eliminados
- Puntos acumulados para monedas

El puntaje se calcula y se guarda automáticamente en puntajes.json
para ser utilizado por el Hall of Fame (Salón de la Fama).

FUNCIONES PRINCIPALES:
======================

1. calcularYGuardarPuntajeDesdeSpotify() - RECOMENDADA
   =========================================================
   Obtiene tempo y popularidad de Spotify API automáticamente.
   Esta es la función a usar desde el juego principal.
   
   Uso:
   from algoritmoDelBanquero import calcularYGuardarPuntajeDesdeSpotify
   
   puntaje = calcularYGuardarPuntajeDesdeSpotify(
       usuario="NombreJugador",
       avatarsMatados=15,
       puntosParaMonedas=2500,
       limiteMaximo=1000
   )


2. calcularYGuardarPuntaje() - Alternativa manual
   ==================================================
   Permite especificar manualmente tempo y popularidad.
   Útil si Spotify no está disponible o para pruebas.
   
   Uso:
   from algoritmoDelBanquero import calcularYGuardarPuntaje
   
   puntaje = calcularYGuardarPuntaje(
       usuario="NombreJugador",
       tempo=120,
       popularidad=8.5,
       avatarsMatados=15,
       puntosParaMonedas=2500,
       limiteMaximo=1000
   )


3. obtenerTempoYPopularidadSpotify()
   ====================================
   Función auxiliar que obtiene los datos de Spotify API.
   Retorna (tempo, popularidad) o valores por defecto en caso de error.
   
   Uso:
   from algoritmoDelBanquero import obtenerTempoYPopularidadSpotify
   
   tempo, popularidad = obtenerTempoYPopularidadSpotify()
"""

def obtenerRutaPuntajes():
    """
    Obtiene la ruta correcta del archivo puntajes.json
    El archivo se guarda en la misma carpeta que este script (salonDeFama/)
    
    Returns:
        str: Ruta absoluta del archivo puntajes.json
    """
    # Obtener la carpeta actual (salonDeFama/)
    carpeta_actual = os.path.dirname(os.path.abspath(__file__))
    
    # El archivo puntajes.json está en la misma carpeta
    ruta_puntajes = os.path.join(carpeta_actual, 'puntajes.json')
    
    print(f"📁 Ruta de puntajes.json: {ruta_puntajes}")
    return ruta_puntajes


def obtenerTempoYPopularidadSpotify():
    """
    Obtiene el tempo y la popularidad desde spotify_api.py
    
    Estructura:
    - Este archivo está en: sprint1/salonDeFama/algoritmoDelBanquero.py
    - spotify_api.py está en: sprint1/personalizacion/spotify_api.py
    
    Returns:
        Tupla (tempo, popularidad) o (120, 5.0) si hay error
    """
    try:
        # Obtener carpeta actual (sprint1/salonDeFama/)
        carpeta_actual = os.path.dirname(os.path.abspath(__file__))
        
        # Subir un nivel para llegar a sprint1/
        carpeta_sprint1 = os.path.dirname(carpeta_actual)
        
        # Carpeta personalizacion está en sprint1/personalizacion/
        carpeta_personalizacion = os.path.join(carpeta_sprint1, 'personalizacion')
        
        # Agregar al path si no está
        if carpeta_personalizacion not in sys.path:
            sys.path.insert(0, carpeta_personalizacion)
        
        print(f"🔍 Buscando spotify_api.py en: {carpeta_personalizacion}")
        
        # Importar las variables globales de spotify_api
        import spotify_api

        tempo = getattr(spotify_api, 'tempo', 120)
        popularidad = getattr(spotify_api, 'popularidad', 50)
        
        # Convertir popularidad a escala 0-10 si está en escala 0-100
        if popularidad > 10:
            popularidad = popularidad / 10
        
        print(f"🎵 Datos obtenidos de Spotify API: Tempo={tempo}, Popularidad={popularidad:.1f}/10")
        return tempo, popularidad
        
    except ImportError as e:
        print(f"⚠️  Advertencia: No se puede importar spotify_api.py: {e}")
        print("   Usando valores por defecto: Tempo=120, Popularidad=5.0")
        return 120, 5.0
    except Exception as e:
        print(f"⚠️  Error al obtener datos de Spotify: {e}")
        print("   Usando valores por defecto: Tempo=120, Popularidad=5.0")
        return 120, 5.0


def guardarPuntaje(puntaje, usuario="Jugador", tempo=0, popularidad=0, avatarsMatados=0, puntosParaMonedas=0):
    """
    Guarda el puntaje en el archivo puntajes.json
    
    Args:
        puntaje: Puntaje a guardar
        usuario: Nombre del usuario que obtuvo el puntaje
        tempo: Tempo de la música actual
        popularidad: Popularidad de la música actual
        avatarsMatados: Cantidad de avatars eliminados
        puntosParaMonedas: Puntos acumulados para monedas
    
    Returns:
        bool: True si se guardó exitosamente, False si hubo error
    """
    try:
        # Obtener ruta del archivo puntajes.json
        carpeta_actual = os.path.dirname(os.path.abspath(__file__))
        archivo_puntajes = os.path.join(carpeta_actual, 'puntajes.json')
        
        # Intentar cargar puntajes existentes
        puntajes = []
        if os.path.exists(archivo_puntajes):
            try:
                with open(archivo_puntajes, 'r', encoding='utf-8') as f:
                    puntajes = json.load(f)
                    # Asegurar que sea una lista
                    if not isinstance(puntajes, list):
                        puntajes = []
            except json.JSONDecodeError:
                print("⚠️  Archivo puntajes.json corrupto, creando uno nuevo...")
                puntajes = []
        else:
            print("📝 Creando nuevo archivo de puntajes...")
        
        # Crear nuevo registro
        nuevo_puntaje = {
            "usuario": usuario,
            "puntaje": round(puntaje, 2),
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stats": {
                "tempo": tempo,
                "popularidad": popularidad,
                "avatarsMatados": avatarsMatados,
                "puntosParaMonedas": puntosParaMonedas
            }
        }
        
        # Agregar nuevo puntaje
        puntajes.append(nuevo_puntaje)
        
        # Guardar archivo actualizado
        with open('puntajes.json', 'w') as f:
            json.dump(puntajes, f, indent=4)
            
        print(f"✅ Puntaje guardado exitosamente para {usuario}: {puntaje:.2f}")
        print(f"   📊 Stats: {avatarsMatados} avatars | {puntosParaMonedas} puntos | Tempo: {tempo} | Pop: {popularidad:.1f}")
        return True
    except Exception as e:
        print(f"❌ Error al guardar el puntaje: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def funcionDelBanquero(tempo, popularidad, avatarsMatados, puntosParaMonedas, limiteMaximo):
    """
    Calcula un puntaje ajustado basado en múltiples factores de juego.
    
    Args:
        tempo: Valor de tempo del juego (BPM de la música)
        popularidad: Valor de popularidad (0-10 o 0-100, se normaliza automáticamente)
        avatarsMatados: Cantidad de avatares eliminados
        puntosParaMonedas: Puntos acumulados para monedas
        limiteMaximo: Límite máximo permitido para el puntaje
    
    Returns:
        float: Puntaje ajustado final
    """
    # Normalizar popularidad si está en escala 0-100
    if popularidad > 10:
        popularidad = popularidad / 10
    
    # Paso 1: Calcular la media armónica
    if tempo > 0 and popularidad > 0:
        mediaArmonica = 2 / ((1 / tempo) + (1 / popularidad))
    else:
        mediaArmonica = 0
    
    # Paso 2: Calcular el factor de intensidad
    factorIntensidad = (avatarsMatados / (tempo + 1)) * 0.05
    
    # Paso 3: Calcular el factor avatar
    factorAvatar = 1 + math.sqrt(puntosParaMonedas / 500)
    
    # Paso 4: Calcular el puntaje ajustado
    puntajeAjustado = (mediaArmonica + (factorIntensidad * 100)) * factorAvatar
    
    # Paso 5: Aplicar el límite máximo
    if puntajeAjustado > limiteMaximo:
        puntajeAjustado = limiteMaximo
    
    print(f"🎯 Cálculo del puntaje:")
    print(f"   📈 Media Armónica: {mediaArmonica:.2f}")
    print(f"   ⚡ Factor Intensidad: {factorIntensidad:.4f}")
    print(f"   👤 Factor Avatar: {factorAvatar:.2f}")
    print(f"   🏆 Puntaje Final: {puntajeAjustado:.2f}")
    
    # Paso 6: Retornar el resultado
    return puntajeAjustado


def calcularYGuardarPuntaje(usuario, tempo, popularidad, avatarsMatados, puntosParaMonedas, limiteMaximo):
    """
    Calcula el puntaje usando el algoritmo del banquero y lo guarda en puntajes.json
    
    Args:
        usuario: Nombre del usuario
        tempo: Valor de tempo del juego (BPM)
        popularidad: Valor de popularidad (0-10 o 0-100)
        avatarsMatados: Cantidad de avatares eliminados
        puntosParaMonedas: Puntos acumulados para monedas
        limiteMaximo: Límite máximo permitido para el puntaje
    
    Returns:
        float: Puntaje calculado y guardado
    """
    print(f"\n{'='*60}")
    print(f"CALCULANDO PUNTAJE PARA: {usuario}")
    print(f"{'='*60}")
    
    # Calcular puntaje usando el algoritmo del banquero
    puntaje = funcionDelBanquero(tempo, popularidad, avatarsMatados, puntosParaMonedas, limiteMaximo)
    
    # Guardar el puntaje con todos los detalles
    guardarPuntaje(
        puntaje=puntaje,
        usuario=usuario,
        tempo=tempo,
        popularidad=popularidad,
        avatarsMatados=avatarsMatados,
        puntosParaMonedas=puntosParaMonedas
    )
    
    print(f"{'='*60}\n")
    
    return puntaje


def calcularYGuardarPuntajeDesdeSpotify(usuario, avatarsMatados, puntosParaMonedas, limiteMaximo):
    """
    Calcula el puntaje usando el algoritmo del banquero, obteniendo tempo y popularidad
    directamente desde spotify_api.py. Esta es la función principal a usar desde el juego.
    
    Args:
        usuario: Nombre del usuario
        avatarsMatados: Cantidad de avatares eliminados
        puntosParaMonedas: Puntos acumulados para monedas
        limiteMaximo: Límite máximo permitido para el puntaje
    
    Returns:
        float: Puntaje calculado y guardado
    """
    # Obtener tempo y popularidad desde Spotify API
    tempo, popularidad = obtenerTempoYPopularidadSpotify()
    
    # Calcular y guardar el puntaje
    puntaje = calcularYGuardarPuntaje(
        usuario=usuario,
        tempo=tempo,
        popularidad=popularidad,
        avatarsMatados=avatarsMatados,
        puntosParaMonedas=puntosParaMonedas,
        limiteMaximo=limiteMaximo
    )
    
    return puntaje


# Ejemplo de uso
if __name__ == "__main__":
    print("=" * 60)
    print("ALGORITMO DEL BANQUERO - Ejemplo de Uso")
    print("=" * 60)
    print()
    
    # Mostrar estructura de carpetas detectada
    print("📂 Estructura detectada:")
    carpeta_actual = os.path.dirname(os.path.abspath(__file__))
    print(f"   Carpeta actual: {carpeta_actual}")
    carpeta_sprint1 = os.path.dirname(carpeta_actual)
    print(f"   Carpeta sprint1: {carpeta_sprint1}")
    carpeta_personalizacion = os.path.join(carpeta_sprint1, 'personalizacion')
    print(f"   Carpeta personalizacion: {carpeta_personalizacion}")
    print()
    
    # Opción 1: Usar datos de Spotify API (recomendado)
    print("Opción 1: Usando datos de Spotify API")
    print("-" * 60)
    try:
        puntaje_spotify = calcularYGuardarPuntajeDesdeSpotify(
            usuario="JugadorSpotify",
            avatarsMatados=20,
            puntosParaMonedas=3000,
            limiteMaximo=1000
        )
        print(f"✓ Puntaje calculado y guardado: {puntaje_spotify:.2f}\n")
    except Exception as e:
        print(f"✗ Error al calcular puntaje desde Spotify: {e}\n")
        import traceback
        traceback.print_exc()
    
    # Opción 2: Usar valores manuales (fallback)
    print("Opción 2: Usando valores manuales")
    print("-" * 60)
    resultado = calcularYGuardarPuntaje(
        usuario="JugadorManual",
        tempo=120,
        popularidad=8.5,
        avatarsMatados=15,
        puntosParaMonedas=2500,
        limiteMaximo=1000
    )
    print(f"✓ Puntaje calculado y guardado: {resultado:.2f}\n")
    
    print("=" * 60)
    print("Ejemplo completado - Revisa puntajes.json en esta carpeta")
    print("=" * 60)