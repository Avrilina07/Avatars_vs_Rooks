import math
import json
import os
import sys
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
    
    Returns:
        str: Ruta absoluta del archivo puntajes.json
    """
    carpeta_actual = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(carpeta_actual, 'puntajes.json')


def obtenerTempoYPopularidadSpotify():
    """
    Obtiene el tempo y la popularidad desde spotify_api.py
    
    Returns:
        Tupla (tempo, popularidad) o (None, None) si hay error
    """
    try:
        # Agregar la carpeta personalizacion al path para importar spotify_api
        carpeta_personalizacion = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'personalizacion'
        )
        
        if carpeta_personalizacion not in sys.path:
            sys.path.insert(0, carpeta_personalizacion)
        
        # Importar las variables globales de spotify_api
        import spotify_api

        tempo = getattr(spotify_api, 'tempo', 120)
        popularidad = getattr(spotify_api, 'popularidad', 50)
        
        # Convertir popularidad a escala 0-10 si está en escala 0-100
        if popularidad > 10:
            popularidad = popularidad / 10
        
        print(f"Datos obtenidos de Spotify API: Tempo={tempo}, Popularidad={popularidad:.1f}/10")
        return tempo, popularidad
        
    except ImportError:
        print("Advertencia: No se puede acceder a spotify_api.py. Usando valores por defecto.")
        return 120, 5.0
    except Exception as e:
        print(f"Error al obtener datos de Spotify: {e}. Usando valores por defecto.")
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
    """
    try:
        # Obtener ruta del archivo puntajes.json
        archivo_puntajes = obtenerRutaPuntajes()
        
        # Intentar cargar puntajes existentes
        try:
            with open(archivo_puntajes, 'r', encoding='utf-8') as f:
                puntajes = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            puntajes = []
        
        # Crear nuevo registro
        nuevoPuntaje = {
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
        puntajes.append(nuevoPuntaje)
        
        # Guardar archivo actualizado
        with open(archivo_puntajes, 'w', encoding='utf-8') as f:
            json.dump(puntajes, f, indent=4, ensure_ascii=False)
            
        print(f"Puntaje guardado exitosamente para el usuario {usuario}: {puntaje:.2f}")
        return True
    except Exception as e:
        print(f"Error al guardar el puntaje: {str(e)}")
        return False


def funcionDelBanquero(tempo, popularidad, avatarsMatados, puntosParaMonedas, limiteMaximo):
    """
    Calcula un puntaje ajustado basado en múltiples factores de juego.
    
    Args:
        tempo: Valor de tempo del juego
        popularidad: Valor de popularidad
        avatars_matados: Cantidad de avatares eliminados
        puntos_avatar: Puntos acumulados del avatar
        limite_maximo: Límite máximo permitido para el puntaje
    
    Returns:
        float: Puntaje ajustado final
    """
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
    
    # Paso 6: Retornar el resultado
    return puntajeAjustado


def calcularYGuardarPuntaje(usuario, tempo, popularidad, avatarsMatados, puntosParaMonedas, limiteMaximo):
    """
    Calcula el puntaje usando el algoritmo del banquero y lo guarda en puntajes.json
    
    Args:
        usuario: Nombre del usuario
        tempo: Valor de tempo del juego
        popularidad: Valor de popularidad
        avatarsMatados: Cantidad de avatares eliminados
        puntosParaMonedas: Puntos acumulados del avatar
        limiteMaximo: Límite máximo permitido para el puntaje
    
    Returns:
        float: Puntaje calculado y guardado
    """
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
    
    return puntaje


def calcularYGuardarPuntajeDesdeSpotify(usuario, avatarsMatados, puntosParaMonedas, limiteMaximo):
    """
    Calcula el puntaje usando el algoritmo del banquero, obteniendo tempo y popularidad
    directamente desde spotify_api.py. Esta es la función principal a usar desde el juego.
    
    Args:
        usuario: Nombre del usuario
        avatarsMatados: Cantidad de avatares eliminados
        puntosParaMonedas: Puntos acumulados del avatar
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
    print("Ejemplo completado")
    print("=" * 60)
