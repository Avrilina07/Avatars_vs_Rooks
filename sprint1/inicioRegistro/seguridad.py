"""Módulo de seguridad compartido para encriptación y hashing"""

import os
import bcrypt
from cryptography.fernet import Fernet


class SistemaSeguridad:
    """Clase para manejar la encriptación y hashing de datos"""
    
    def __init__(self):
        # clave.key is in dataBase folder
        repo_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
        self.archivoClave = os.path.join(repo_root, 'dataBase', 'clave.key')
        self.inicializarEncriptacion()
    
    def inicializarEncriptacion(self):
        """Crea o carga la clave de encriptación"""
        if os.path.exists(self.archivoClave):
            with open(self.archivoClave, 'rb') as f:
                clave = f.read()
        else:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(self.archivoClave), exist_ok=True)
            clave = Fernet.generate_key()
            with open(self.archivoClave, 'wb') as f:
                f.write(clave)
        
        self.cipher = Fernet(clave)
    
    def hashContrasena(self, contrasena):
        """Convierte la contraseña en un hash irreversible"""
        if not contrasena:
            raise ValueError("La contraseña no puede estar vacía")
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(contrasena.encode('utf-8'), salt).decode('utf-8')
    
    def verificarContrasena(self, contrasena, hashGuardado):
        """Verifica si la contraseña coincide con el hash"""
        if not contrasena or not hashGuardado:
            return False
        try:
            return bcrypt.checkpw(contrasena.encode('utf-8'), hashGuardado.encode('utf-8'))
        except Exception:
            return False
    
    def encriptar(self, dato):
        """Encripta datos sensibles (reversible)"""
        if not dato or not dato.strip():
            return ""
        try:
            return self.cipher.encrypt(dato.encode()).decode()
        except Exception:
            return ""
    
    def desencriptar(self, datoEncriptado):
        """Desencripta datos sensibles"""
        if not datoEncriptado:
            return ""
        try:
            return self.cipher.decrypt(datoEncriptado.encode()).decode()
        except Exception:
            return ""