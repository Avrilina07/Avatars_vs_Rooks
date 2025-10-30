import math
import json
import os
import sys
from datetime import datetime

# Configurar rutas para importaciones
carpeta_actual = os.path.dirname(os.path.abspath(__file__))
carpeta_sprint1 = os.path.dirname(carpeta_actual)
carpeta_personalizacion = os.path.join(carpeta_sprint1, 'personalizacion')

# Añadir carpeta de personalización al path si no está
if carpeta_personalizacion not in sys.path:
    sys.path.insert(0, carpeta_personalizacion)

from spotify_api import tempo, popularidad

# Ruta absoluta al archivo de puntajes
RUTA_PUNTAJES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'puntajes.json')
LIMITE_MAXIMO_DEFAULT = 1000

def guardar_puntaje(puntaje, usuario="Jugador", stats=None):
    """
    Guarda el puntaje en el archivo puntajes.json
    
    Args:
        puntaje: Puntaje a guardar
        usuario: Nombre del usuario que obtuvo el puntaje
        stats: Diccionario con estadísticas adicionales del juego
    """
    try:
        # Intentar cargar puntajes existentes
        try:
            with open(RUTA_PUNTAJES, 'r') as f:
                puntajes = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            puntajes = []
        
        # Si no se proporcionan stats, usar valores por defecto
        if stats is None:
            stats = {
                "tempo": tempo,
                "popularidad": popularidad,
                "avatarsMatados": 0,
                "puntosParaMonedas": 0
            }
        
        # Crear nuevo registro
        nuevo_puntaje = {
            "usuario": usuario,
            "puntaje": round(puntaje, 2),
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stats": stats
        }
        
        # Agregar nuevo puntaje
        puntajes.append(nuevo_puntaje)
        
        # Guardar archivo actualizado
        with open(RUTA_PUNTAJES, 'w') as f:
            json.dump(puntajes, f, indent=4)
            
        print(f"Puntaje guardado exitosamente para el usuario {usuario}")
    except Exception as e:
        print(f"Error al guardar el puntaje: {str(e)}")


def funcionDelBanquero(stats):
    """
    Calcula un puntaje ajustado basado en múltiples factores de juego.
    
    Args:
        stats: Diccionario con las estadísticas del juego que debe incluir:
            - tempo: Valor de tempo del juego
            - popularidad: Valor de popularidad
            - avatarsMatados: Cantidad de avatares eliminados
            - puntosParaMonedas: Puntos acumulados del avatar
            - limiteMaximo: (opcional) Límite máximo permitido para el puntaje
    
    Returns:
        float: Puntaje ajustado final
    """
    tempo = stats.get("tempo", 0)
    popularidad = stats.get("popularidad", 0)
    avatarsMatados = stats.get("avatarsMatados", 0)
    puntosParaMonedas = stats.get("puntosParaMonedas", 0)
    limiteMaximo = stats.get("limiteMaximo", LIMITE_MAXIMO_DEFAULT)
    
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


# Ejemplo de uso
if __name__ == "__main__":
    stats_ejemplo = {
        "tempo": tempo,
        "popularidad": popularidad,
        "avatarsMatados": 10,
        "puntosParaMonedas": 100,
        "limiteMaximo": LIMITE_MAXIMO_DEFAULT
    }
    
    resultado = funcionDelBanquero(stats_ejemplo)
    print(f"Puntaje ajustado: {resultado:.2f}")
    guardar_puntaje(resultado, stats=stats_ejemplo)