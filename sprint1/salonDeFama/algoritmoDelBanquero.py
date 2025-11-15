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

ESTRUCTURA DEL PROYECTO:
========================
Avatars_vs_Rooks/
└── sprint1/
    ├── juego/
    ├── inicioRegistro/
    ├── salonDeFama/          <- Este archivo está aquí
    │   ├── algoritmoDelBanquero.py
    │   ├── hallOfFame.py
    │   └── puntajes.json
    └── personalizacion/
        └── spotify_api.py

FUNCIONES PRINCIPALES:
======================

1. calcularYGuardarPuntajeDesdeSpotify() - RECOMENDADA
   =========================================================
   Obtiene tempo y popularidad de Spotify API automáticamente.
   Obtiene el nombre del usuario desde session_user.json automáticamente.
   Esta es la función a usar desde el juego principal.
   
   Uso:
   from algoritmoDelBanquero import calcularYGuardarPuntajeDesdeSpotify
   
   # El usuario se obtiene automáticamente de session_user.json
   puntaje = calcularYGuardarPuntajeDesdeSpotify(
       avatarsMatados=15,
       puntosParaMonedas=2500,
       limiteMaximo=1000
   )
   
   # O especificar un usuario manualmente (opcional)
   puntaje = calcularYGuardarPuntajeDesdeSpotify(
       avatarsMatados=15,
       puntosParaMonedas=2500,
       limiteMaximo=1000,
       usuario="NombreEspecifico"
   )


2. calcularYGuardarPuntaje() - Alternativa manual
   ==================================================
   Permite especificar manualmente tempo y popularidad.
   Obtiene el nombre del usuario desde session_user.json automáticamente.
   Útil si Spotify no está disponible o para pruebas.
   
   Uso:
   from algoritmoDelBanquero import calcularYGuardarPuntaje
   
   # El usuario se obtiene automáticamente de session_user.json
   puntaje = calcularYGuardarPuntaje(
       tempo=120,
       popularidad=8.5,
       avatarsMatados=15,
       puntosParaMonedas=2500,
       limiteMaximo=1000
   )
   
   # O especificar un usuario manualmente (opcional)
   puntaje = calcularYGuardarPuntaje(
       tempo=120,
       popularidad=8.5,
       avatarsMatados=15,
       puntosParaMonedas=2500,
       limiteMaximo=1000,
       usuario="NombreEspecifico"
   )


3. obtenerUsuarioActual()
   ==========================
   Obtiene el nombre del usuario actual desde session_user.json
   Retorna "Jugador" como valor por defecto si no se encuentra el archivo.
   
   Uso:
   from algoritmoDelBanquero import obtenerUsuarioActual
   
   usuario = obtenerUsuarioActual()


4. obtenerTempoYPopularidadSpotify()
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
    
    print(f"[Ruta] Ruta de puntajes.json: {ruta_puntajes}")
    return ruta_puntajes


def obtenerUsuarioActual():
    """
    Obtiene el nombre del usuario actual desde session_user.json
    
    Returns:
        str: Nombre del usuario actual o "Jugador" si no se encuentra
    """
    try:
        # Obtener carpeta actual (salonDeFama/)
        carpeta_actual = os.path.dirname(os.path.abspath(__file__))
        
        # Subir un nivel para llegar a sprint1/
        carpeta_sprint1 = os.path.dirname(carpeta_actual)
        
        # Obtener ruta de session_user.json en sprint1/dataBase/
        ruta_session = os.path.join(carpeta_sprint1, 'dataBase', 'session_user.json')
        
        if os.path.exists(ruta_session):
            with open(ruta_session, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
                usuario = session_data.get('usuario', 'Jugador')
                print(f"[Usuario] Usuario obtenido de session_user.json: {usuario}")
                return usuario
        else:
            print(f"[Advertencia] Archivo session_user.json no encontrado en: {ruta_session}")
            print("   Usando nombre por defecto: Jugador")
            return "Jugador"
    except Exception as e:
        print(f"[Advertencia] Error al leer session_user.json: {e}")
        print("   Usando nombre por defecto: Jugador")
        return "Jugador"


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
        
        print(f"[Spotify] Buscando spotify_api.py en: {carpeta_personalizacion}")
        
        # Importar las variables globales de spotify_api
        import spotify_api

        tempo = getattr(spotify_api, 'tempo', 120)
        popularidad = getattr(spotify_api, 'popularidad', 50)
        
        # Convertir popularidad a escala 0-10 si está en escala 0-100
        if popularidad > 10:
            popularidad = popularidad / 10
        
        print(f"[Spotify] Datos obtenidos de Spotify API: Tempo={tempo}, Popularidad={popularidad:.1f}/10")
        return tempo, popularidad
        
    except ImportError as e:
        print(f"[Advertencia] No se puede importar spotify_api.py: {e}")
        print("   Usando valores por defecto: Tempo=120, Popularidad=5.0")
        return 120, 5.0
    except Exception as e:
        print(f"[Advertencia] Error al obtener datos de Spotify: {e}")
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
        archivo_puntajes = obtenerRutaPuntajes()
        
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
                print("[Advertencia] Archivo puntajes.json corrupto, creando uno nuevo...")
                puntajes = []
        else:
            print("[Info] Creando nuevo archivo de puntajes...")
        
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
            
        print(f"[Exito] Puntaje guardado exitosamente para {usuario}: {puntaje:.2f}")
        print(f"   Stats: {avatarsMatados} avatars | {puntosParaMonedas} puntos | Tempo: {tempo} | Pop: {popularidad:.1f}")
        return True
    except Exception as e:
        print(f"[Error] Error al guardar el puntaje: {str(e)}")
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
    
    print(f"[Calculo] Calculo del puntaje:")
    print(f"   Media Armonica: {mediaArmonica:.2f}")
    print(f"   Factor Intensidad: {factorIntensidad:.4f}")
    print(f"   Factor Avatar: {factorAvatar:.2f}")
    print(f"   Puntaje Final: {puntajeAjustado:.2f}")
    
    # Paso 6: Retornar el resultado
    return puntajeAjustado


def calcularYGuardarPuntaje(tempo, popularidad, avatarsMatados, puntosParaMonedas, limiteMaximo, usuario=None):
    """
    Calcula el puntaje usando el algoritmo del banquero y lo guarda en puntajes.json
    
    Args:
        tempo: Valor de tempo del juego (BPM)
        popularidad: Valor de popularidad (0-10 o 0-100)
        avatarsMatados: Cantidad de avatares eliminados
        puntosParaMonedas: Puntos acumulados para monedas
        limiteMaximo: Límite máximo permitido para el puntaje
        usuario: Nombre del usuario (opcional, se obtiene de session_user.json si no se especifica)
    
    Returns:
        float: Puntaje calculado y guardado
    """
    # Si no se proporciona usuario, obtenerlo de session_user.json
    if usuario is None:
        usuario = obtenerUsuarioActual()
    
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


def calcularYGuardarPuntajeDesdeSpotify(avatarsMatados, puntosParaMonedas, limiteMaximo, usuario=None):
    """
    Calcula el puntaje usando el algoritmo del banquero, obteniendo tempo y popularidad
    directamente desde spotify_api.py. Esta es la función principal a usar desde el juego.
    
    Args:
        avatarsMatados: Cantidad de avatares eliminados
        puntosParaMonedas: Puntos acumulados para monedas
        limiteMaximo: Límite máximo permitido para el puntaje
        usuario: Nombre del usuario (opcional, se obtiene de session_user.json si no se especifica)
    
    Returns:
        float: Puntaje calculado y guardado
    """
    # Si no se proporciona usuario, obtenerlo de session_user.json
    if usuario is None:
        usuario = obtenerUsuarioActual()
    
    # Obtener tempo y popularidad desde Spotify API
    tempo, popularidad = obtenerTempoYPopularidadSpotify()
    
    # Calcular y guardar el puntaje
    puntaje = calcularYGuardarPuntaje(
        tempo=tempo,
        popularidad=popularidad,
        avatarsMatados=avatarsMatados,
        puntosParaMonedas=puntosParaMonedas,
        limiteMaximo=limiteMaximo,
        usuario=usuario
    )
    
    return puntaje


# Ejemplo de uso
if __name__ == "__main__":
    print("=" * 60)
    print("ALGORITMO DEL BANQUERO - Ejemplo de Uso")
    print("=" * 60)
    print()
    
    # Mostrar estructura de carpetas detectada
    print("Estructura detectada:")
    carpeta_actual = os.path.dirname(os.path.abspath(__file__))
    print(f"   Carpeta actual: {carpeta_actual}")
    carpeta_sprint1 = os.path.dirname(carpeta_actual)
    print(f"   Carpeta sprint1: {carpeta_sprint1}")
    carpeta_personalizacion = os.path.join(carpeta_sprint1, 'personalizacion')
    print(f"   Carpeta personalizacion: {carpeta_personalizacion}")
    print()
    
    # Opción 1: Usar datos de Spotify API con usuario de session_user.json (recomendado)
    print("Opcion 1: Usando datos de Spotify API y usuario de session_user.json")
    print("-" * 60)
    try:
        puntaje_spotify = calcularYGuardarPuntajeDesdeSpotify(
            avatarsMatados=20,
            puntosParaMonedas=3000,
            limiteMaximo=1000
        )
        print(f"[OK] Puntaje calculado y guardado: {puntaje_spotify:.2f}\n")
    except Exception as e:
        print(f"[Error] Error al calcular puntaje desde Spotify: {e}\n")
        import traceback
        traceback.print_exc()
    
    # Opción 2: Usar valores manuales con usuario de session_user.json (fallback)
    print("Opcion 2: Usando valores manuales y usuario de session_user.json")
    print("-" * 60)
    resultado = calcularYGuardarPuntaje(
        tempo=120,
        popularidad=8.5,
        avatarsMatados=15,
        puntosParaMonedas=2500,
        limiteMaximo=1000
    )
    print(f"[OK] Puntaje calculado y guardado: {resultado:.2f}\n")
    
    print("=" * 60)
    print("Ejemplo completado - Revisa puntajes.json en esta carpeta")
    print("=" * 60)