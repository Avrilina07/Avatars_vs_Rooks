"""Módulo para manejo centralizado de traducciones"""

import json
import os


class GestorTraducciones:
    """Gestor centralizado de traducciones multiidioma"""
    
    def __init__(self):
        self.traducciones = self._cargar_traducciones()
        self.idioma_actual = 'Español'  # idioma por defecto
    
    def _cargar_traducciones(self):
        """Carga las traducciones desde idiomas.json"""
        path = os.path.join(os.path.dirname(__file__), 'idiomas.json')
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            # Traducciones mínimas de respaldo
            return {
                'Español': {
                    'errorTitle': 'Error',
                    'successTitle': 'Éxito',
                    'login': 'Iniciar sesión',
                    'registro': 'Registrarse'
                },
                'Ingles': {
                    'errorTitle': 'Error',
                    'successTitle': 'Success',
                    'login': 'Sign in',
                    'registro': 'Register'
                }
            }
    
    def establecer_idioma(self, idioma):
        """Establece el idioma actual"""
        if idioma in self.traducciones:
            self.idioma_actual = idioma
    
    def obtener_idioma(self):
        """Obtiene el idioma actual"""
        return self.idioma_actual
    
    def t(self, clave, idioma=None):
        """Obtiene la traducción de una clave"""
        idioma_usar = idioma or self.idioma_actual
        return self.traducciones.get(idioma_usar, {}).get(clave, clave)
    
    def obtener_traducciones_idioma(self, idioma=None):
        """Obtiene todas las traducciones de un idioma"""
        idioma_usar = idioma or self.idioma_actual
        return self.traducciones.get(idioma_usar, {})
    
    def obtener_idiomas_disponibles(self):
        """Obtiene lista de idiomas disponibles"""
        return list(self.traducciones.keys())


# Instancia global para uso compartido
gestor_traducciones = GestorTraducciones()