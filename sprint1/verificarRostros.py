
# Código para verificar qué usuarios tienen datos de reconocimiento facial guardados (hecha gracias a mi amiga claude)
# Esto nos ayuda a monitorear si hay errores en el proceso del registro facial

import json
import os

def verificar_usuarios_con_rostro():
    """Verifica qué usuarios en usuarios.json tienen datos faciales"""
    
    # usuarios.json is now in dataBase folder
    usuarios_path = os.path.join(os.path.dirname(__file__), '..', 'dataBase', 'usuarios.json')
    
    if not os.path.exists(usuarios_path):
        print("❌ ERROR: No se encontró el archivo usuarios.json")
        print(f"   Ruta buscada: {usuarios_path}")
        return
    
    with open(usuarios_path, 'r', encoding='utf-8') as f:
        usuarios = json.load(f)
    
    print("=" * 70)
    print("📊 VERIFICACIÓN DE DATOS DE RECONOCIMIENTO FACIAL")
    print("=" * 70)
    print()
    
    if not usuarios:
        print("⚠️  El archivo usuarios.json está vacío")
        return
    
    print(f"Total de usuarios registrados: {len(usuarios)}\n")
    
    con_rostro = []
    sin_rostro = []
    
    for usuario in usuarios:
        nombre_usuario = usuario.get('usuario') or usuario.get('username') or 'Desconocido'
        tiene_rostro = 'face_enc' in usuario and usuario['face_enc']
        
        if tiene_rostro:
            con_rostro.append(nombre_usuario)
            print(f"✅ {nombre_usuario}")
            print(f"   - Nombre: {usuario.get('nombre', 'N/A')}")
            print(f"   - Rostro registrado: Sí")
            print(f"   - Longitud de datos: {len(usuario['face_enc'])} caracteres")
            print()
        else:
            sin_rostro.append(nombre_usuario)
    
    if sin_rostro:
        print("\n" + "=" * 70)
        print("⚠️  USUARIOS SIN DATOS DE RECONOCIMIENTO FACIAL:")
        print("=" * 70)
        for usuario in usuarios:
            nombre_usuario = usuario.get('usuario') or usuario.get('username') or 'Desconocido'
            if nombre_usuario in sin_rostro:
                print(f"❌ {nombre_usuario}")
                print(f"   - Nombre: {usuario.get('nombre', 'N/A')}")
                print(f"   - Rostro registrado: No")
                print(f"   - ⚠️  Este usuario NO puede usar login facial")
                print()
    
    print("\n" + "=" * 70)
    print("📈 RESUMEN:")
    print("=" * 70)
    print(f"✅ Usuarios con rostro registrado: {len(con_rostro)}")
    print(f"❌ Usuarios sin rostro registrado: {len(sin_rostro)}")
    print()
    
    if sin_rostro:
        print("🔧 ACCIÓN REQUERIDA:")
        print("Los siguientes usuarios necesitan registrar su rostro:")
        for nombre in sin_rostro:
            print(f"   - {nombre}")
        print()
        print("Para registrar rostros:")
        print("1. Ejecuta: python inicioRegistro/registro.py")
        print("2. Ingresa el nombre de usuario existente")
        print("3. Haz clic en 'Registrar rostro'")
        print("4. Completa el registro")
    else:
        print("🎉 ¡Todos los usuarios tienen rostro registrado!")
    
    print("=" * 70)

if __name__ == "__main__":
    verificar_usuarios_con_rostro()
    input("\nPresiona Enter para salir...")
