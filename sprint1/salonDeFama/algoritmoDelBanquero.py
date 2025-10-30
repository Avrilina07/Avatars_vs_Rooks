import math
import json
import os
from datetime import datetime

def guardar_puntaje(puntaje, usuario="Jugador", tempo=0, popularidad=0, avatarsMatados=0, puntosParaMonedas=0):
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
        carpeta_actual = os.path.dirname(os.path.abspath(__file__))
        archivo_puntajes = os.path.join(carpeta_actual, 'puntajes.json')
        
        # Intentar cargar puntajes existentes
        try:
            with open(archivo_puntajes, 'r') as f:
                puntajes = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            puntajes = []
        
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
            
        print(f"Puntaje guardado exitosamente para el usuario {usuario}")
    except Exception as e:
        print(f"Error al guardar el puntaje: {str(e)}")


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


# Ejemplo de uso
if __name__ == "__main__":
    resultado = funcionDelBanquero(
        tempo=tempo,
        popularidad=popularidad,
        avatarsMatados=avatarsMatados,
        puntosParaMonedas=puntosParaMonedas,
        limiteMaximo=limiteMaximo
    )
    print(f"Puntaje ajustado: {resultado:.2f}")
    guardar_puntaje(resultado)
