import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from PIL import Image, ImageTk, ImageDraw
import json
import os
import base64
import io
import numpy as np
try:
    from cryptography.fernet import Fernet
except Exception:
    Fernet = None

class userProfilePage:
    def __init__(self, root):
        self.root = root
        self.root.title("Perfil de Usuario")
        # Abrir en pantalla completa
        try:
            # En Windows esto quita borde y ocupa toda la pantalla
            self.root.attributes("-fullscreen", True)
        except Exception:
            # Fallback a ventana maximizada
            try:
                self.root.state('zoomed')
            except Exception:
                self.root.geometry("450x650")
        # Cargar datos del usuario actual y determinar color de fondo
        self.userData = self.load_current_user()

        # Determinar color de fondo: puede venir como lista/tupla RGB o como string hex
        self.bg_color = "white"
        try:
            cf = None
            if isinstance(self.userData, dict):
                cf = self.userData.get('colorFondo') or self.userData.get('color_fondo') or self.userData.get('color')

            if cf:
                if isinstance(cf, (list, tuple)) and len(cf) >= 3:
                    # rgb -> hex
                    r, g, b = int(cf[0]), int(cf[1]), int(cf[2])
                    self.bg_color = '#%02x%02x%02x' % (r, g, b)
                elif isinstance(cf, str):
                    self.bg_color = cf
        except Exception:
            self.bg_color = "white"

        self.root.configure(bg=self.bg_color)
        # Permitir salir del modo fullscreen con Escape (útil para desarrollo)
        try:
            self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        except Exception:
            pass
        
        self.profileImage = None
        
        self.createWidgets()

    def load_current_user(self):
        """Carga los datos del usuario actual desde la base de datos"""
        try:
            # Leer session_user.json (soportamos claves 'usuario' o 'username')
            session_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataBase', 'session_user.json')
            session = {}
            if os.path.exists(session_file):
                with open(session_file, 'r', encoding='utf-8') as f:
                    try:
                        session = json.load(f)
                    except Exception:
                        session = {}

            session_name = session.get('usuario') or session.get('username') or session.get('user')

            # Leer usuarios
            users_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataBase', 'usuarios.json')
            users = []
            if os.path.exists(users_file):
                with open(users_file, 'r', encoding='utf-8') as f:
                    try:
                        users = json.load(f)
                    except Exception:
                        users = []

            # Encontrar usuario por 'usuario' o 'username'
            for u in users:
                name = u.get('usuario') or u.get('username') or u.get('user')
                if name and session_name and name.lower() == session_name.lower():
                    # Normalizar campos para la UI (mapear email->correo, usuario->username, etc.)
                    # Intentar desencriptar email si está cifrado con Fernet (clave.key)
                    correo_raw = u.get('correo') or u.get('email') or u.get('mail') or ''
                    correo = correo_raw
                    try:
                        if isinstance(correo_raw, str) and Fernet is not None:
                            # localizar clave.key
                            clave_paths = [
                                os.path.join(os.path.dirname(__file__), '..', 'dataBase', 'clave.key'),
                                os.path.join(os.getcwd(), 'dataBase', 'clave.key'),
                                os.path.join(os.path.dirname(__file__), 'dataBase', 'clave.key'),
                            ]
                            key_bytes = None
                            for kp in clave_paths:
                                kp = os.path.normpath(kp)
                                if os.path.exists(kp):
                                    with open(kp, 'rb') as fk:
                                        key_bytes = fk.read()
                                    break
                            if key_bytes:
                                f = Fernet(key_bytes)
                                try:
                                    # many fields were encrypted directly as f.encrypt(text)
                                    correo = f.decrypt(correo_raw.encode()).decode('utf-8')
                                except Exception:
                                    # fallback: leave original
                                    correo = correo_raw
                    except Exception:
                        correo = correo_raw

                    normalized = {
                        'nombre': u.get('nombre', ''),
                        'apellidos': u.get('apellidos', ''),
                        'username': name,
                        'correo': correo,
                        'fechaNacimiento': u.get('fechaNacimiento') or u.get('fecha_nacimiento') or '',
                        'tarjetaCredito': u.get('tarjetaCredito') or u.get('tarjeta') or u.get('tarjeta_credito') or '',
                        'cvv': u.get('cvv') or '',
                        'fechaCaducidad': u.get('fechaCaducidad') or u.get('fecha_caducidad') or '',
                        'contrasena': u.get('contrasena') or u.get('contrasenaHash') or '',
                        'tieneFotoRegistrada': u.get('tieneFotoRegistrada') or u.get('fotoRegistrada') or False,
                        # posibles keys creadas al guardar desde la personalizacion
                        'colorFondo': u.get('colorFondo') or u.get('color_fondo') or u.get('colorFondo_nombre') or None
                    }
                    return normalized

            # Si no encontramos por session_name, intentar heurística: si solo hay un usuario, asumir ese
            if len(users) == 1:
                u = users[0]
                name = u.get('usuario') or u.get('username') or u.get('user') or ''
                normalized = {
                    'nombre': u.get('nombre', ''),
                    'apellidos': u.get('apellidos', ''),
                    'username': name,
                    'correo': u.get('correo') or u.get('email') or '',
                    'fechaNacimiento': u.get('fechaNacimiento') or '',
                    'tarjetaCredito': u.get('tarjetaCredito') or '',
                    'cvv': u.get('cvv') or '',
                    'fechaCaducidad': u.get('fechaCaducidad') or '',
                    'contrasena': u.get('contrasena') or u.get('contrasenaHash') or '',
                    'tieneFotoRegistrada': u.get('tieneFotoRegistrada') or u.get('fotoRegistrada') or False,
                    'colorFondo': u.get('colorFondo') or u.get('color_fondo') or None
                }
                return normalized

        except Exception as e:
            print(f"Error cargando datos de usuario: {e}")

        # Fallback genérico
        return {
            'nombre': '',
            'apellidos': '',
            'username': '',
            'correo': '',
            'fechaNacimiento': '',
            'tarjetaCredito': '',
            'cvv': '',
            'fechaCaducidad': '',
            'contrasena': '',
            'tieneFotoRegistrada': False,
            'colorFondo': None
        }
    def save_user_data(self):
        """Guarda los cambios del usuario en la base de datos"""
        try:
            users_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataBase', 'usuarios.json')

            # Leer usuarios existentes
            users = []
            if os.path.exists(users_file):
                with open(users_file, 'r', encoding='utf-8') as f:
                    try:
                        users = json.load(f)
                    except Exception:
                        users = []

            # Buscar y actualizar por 'usuario' o 'username'
            updated = False
            for user in users:
                name = user.get('usuario') or user.get('username') or user.get('user')
                if name and name == self.userData.get('username'):
                    # Mantener claves existentes y actualizar los valores relevantes
                    user['nombre'] = self.userData.get('nombre', user.get('nombre', ''))
                    user['apellidos'] = self.userData.get('apellidos', user.get('apellidos', ''))
                    # email/email key
                    if 'email' in user:
                        user['email'] = self.userData.get('correo', user.get('email', ''))
                    else:
                        user['correo'] = self.userData.get('correo', user.get('correo', ''))

                    user['tarjetaCredito'] = self.userData.get('tarjetaCredito', user.get('tarjetaCredito', user.get('tarjeta', '')))
                    user['cvv'] = self.userData.get('cvv', user.get('cvv', ''))
                    user['fechaCaducidad'] = self.userData.get('fechaCaducidad', user.get('fechaCaducidad', ''))
                    user['tieneFotoRegistrada'] = self.userData.get('tieneFotoRegistrada', user.get('tieneFotoRegistrada', user.get('fotoRegistrada', False)))

                    # Persistir rutaFoto/foto si existe
                    if self.userData.get('rutaFoto'):
                        user['rutaFoto'] = self.userData.get('rutaFoto')
                        user['foto'] = self.userData.get('rutaFoto')
                    if self.userData.get('foto'):
                        user['foto'] = self.userData.get('foto')

                    # Persistir face_enc si existe
                    if self.userData.get('face_enc'):
                        user['face_enc'] = self.userData.get('face_enc')

                    # color
                    if self.userData.get('colorFondo') is not None:
                        user['colorFondo'] = self.userData.get('colorFondo')

                    updated = True
                    break

            if not updated:
                # crear registro mínimo
                new_user = {
                    'usuario': self.userData.get('username', ''),
                    'nombre': self.userData.get('nombre', ''),
                    'apellidos': self.userData.get('apellidos', ''),
                    'email': self.userData.get('correo', ''),
                    'tarjetaCredito': self.userData.get('tarjetaCredito', ''),
                    'cvv': self.userData.get('cvv', ''),
                    'fechaCaducidad': self.userData.get('fechaCaducidad', ''),
                    'tieneFotoRegistrada': self.userData.get('tieneFotoRegistrada', False)
                }
                if self.userData.get('colorFondo') is not None:
                    new_user['colorFondo'] = self.userData.get('colorFondo')
                if self.userData.get('rutaFoto'):
                    new_user['rutaFoto'] = self.userData.get('rutaFoto')
                    new_user['foto'] = self.userData.get('rutaFoto')
                if self.userData.get('foto'):
                    new_user['foto'] = self.userData.get('foto')
                if self.userData.get('face_enc'):
                    new_user['face_enc'] = self.userData.get('face_enc')
                users.append(new_user)

            # Guardar cambios
            with open(users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Éxito", "Los cambios han sido guardados")

        except Exception as e:
            print(f"Error guardando datos: {e}")
            messagebox.showerror("Error", "No se pudieron guardar los cambios")
        
    def createCircularImage(self, size=100):
        """Crea una imagen circular placeholder para el perfil"""
        img = Image.new('RGB', (size, size), color='#E0E0E0')
        draw = ImageDraw.Draw(img)
        draw.ellipse([0, 0, size, size], fill='#E0E0E0', outline='#BDBDBD', width=2)
        
        # Dibujar icono de usuario
        draw.ellipse([35, 25, 65, 55], fill='#9E9E9E')
        draw.ellipse([25, 60, 75, 110], fill='#9E9E9E')
        
        return img
    
    def createWidgets(self):
        # Frame principal centrado
        mainFrame = tk.Frame(self.root, bg=self.bg_color)
        mainFrame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Imagen de perfil
        profileFrame = tk.Frame(mainFrame, bg=self.bg_color)
        profileFrame.pack(pady=(0, 10))
        
        # Crear imagen circular: intentar cargar imagen guardada y componer sobre el color de fondo
        final_img = None
        try:
            ruta = self.userData.get('rutaFoto') or self.userData.get('foto')
            repo_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
            # Si no hay ruta en datos, comprobar por convención dataBase/imagenes/<username>.png
            if not ruta:
                username = self.userData.get('username') or self.userData.get('usuario')
                if username:
                    candidate = os.path.join('dataBase', 'imagenes', f"{username}.png")
                    abs_candidate = os.path.normpath(os.path.join(repo_root, candidate))
                    if os.path.exists(abs_candidate):
                        ruta = candidate

            if ruta:
                abs_path = ruta if os.path.isabs(ruta) else os.path.normpath(os.path.join(repo_root, ruta))
                if os.path.exists(abs_path):
                    img = Image.open(abs_path).convert('RGBA')
                    # Crop center square
                    w, h = img.size
                    if w != h:
                        if w > h:
                            left = (w - h) // 2
                            img = img.crop((left, 0, left + h, h))
                        else:
                            top = (h - w) // 2
                            img = img.crop((0, top, w, top + w))
                    img = img.resize((100, 100), Image.Resampling.LANCZOS)

                    # Crear máscara circular
                    mask = Image.new('L', (100, 100), 0)
                    mdraw = ImageDraw.Draw(mask)
                    mdraw.ellipse([0, 0, 100, 100], fill=255)

                    # Determinar color de fondo (bg_color puede ser nombre o hex)
                    try:
                        from PIL import ImageColor
                        bg_rgb = ImageColor.getrgb(self.bg_color) if hasattr(self, 'bg_color') and self.bg_color else (255, 255, 255)
                    except Exception:
                        bg_rgb = (255, 255, 255)

                    # Componer imagen sobre fondo del color de la página
                    canvas = Image.new('RGB', (100, 100), bg_rgb)
                    canvas.paste(img, (0, 0), mask)

                    final_img = canvas

        except Exception:
            final_img = None

        if final_img is None:
            # usar placeholder circular (ya RGB)
            final_img = self.createCircularImage(100)

        # Dibujar un borde fino del mismo color del fondo (opcional, aquí queda sutil)
        try:
            draw = ImageDraw.Draw(final_img)
            w, h = final_img.size
            outline_width = max(1, int(min(w, h) * 0.03))
            # usar bg_color para el contorno (esto hará que se vea integrado)
            try:
                from PIL import ImageColor
                outline_rgb = ImageColor.getrgb(self.bg_color) if hasattr(self, 'bg_color') and self.bg_color else (255, 255, 255)
            except Exception:
                outline_rgb = (255, 255, 255)
            draw.ellipse([outline_width//2, outline_width//2, w - (outline_width//2) - 1, h - (outline_width//2) - 1], outline=outline_rgb, width=outline_width)
        except Exception:
            pass

        self.profileImage = ImageTk.PhotoImage(final_img)
        
        self.profileLabel = tk.Label(profileFrame, image=self.profileImage, bg=self.bg_color, cursor="hand2")
        self.profileLabel.pack()
        self.profileLabel.bind("<Button-1>", lambda e: self.changeProfilePhoto())
        
        # Username (título)
        usernameLabel = tk.Label(mainFrame, text=self.userData.get("username", ""),
                 font=("Arial", 14), bg=self.bg_color, fg="#424242")
        usernameLabel.pack(pady=(5, 30))
        
        # Campos de información
        fieldsFrame = tk.Frame(mainFrame, bg=self.bg_color)
        fieldsFrame.pack()
        
        # Nombre y Apellidos en una fila
        nameFrame = tk.Frame(fieldsFrame, bg=self.bg_color)
        nameFrame.pack(pady=(0, 20))
        
        # Nombre
        nombreBox = tk.Frame(nameFrame, bg=self.bg_color)
        nombreBox.grid(row=0, column=0, padx=(0, 40))
        tk.Label(nombreBox, text="Nombre", font=("Arial", 11), 
            bg=self.bg_color, fg="#757575").pack()
        tk.Label(nombreBox, text=self.userData.get("nombre", ""), font=("Arial", 11, "bold"), 
            bg=self.bg_color, fg="#212121").pack(pady=(3, 0))
        
        # Apellidos
        apellidosBox = tk.Frame(nameFrame, bg=self.bg_color)
        apellidosBox.grid(row=0, column=1)
        tk.Label(apellidosBox, text="Apellidos", font=("Arial", 11), 
            bg=self.bg_color, fg="#757575").pack()
        tk.Label(apellidosBox, text=self.userData.get("apellidos", ""), font=("Arial", 11, "bold"), 
            bg=self.bg_color, fg="#212121").pack(pady=(3, 0))
        
        # Correo (centrado)
        correoFrame = tk.Frame(fieldsFrame, bg=self.bg_color)
        correoFrame.pack(pady=(0, 20))
        tk.Label(correoFrame, text="Correo", font=("Arial", 11),
            bg=self.bg_color, fg="#757575").pack()
        tk.Label(correoFrame, text=self.userData.get("correo", ""), font=("Arial", 11, "bold"),
            bg=self.bg_color, fg="#212121").pack(pady=(3, 0))
        
        # Fecha de nacimiento (centrado)
        fechaFrame = tk.Frame(fieldsFrame, bg=self.bg_color)
        fechaFrame.pack(pady=(0, 20))
        tk.Label(fechaFrame, text="Fecha de nacimiento", font=("Arial", 11),
            bg=self.bg_color, fg="#757575").pack()
        tk.Label(fechaFrame, text=self.userData.get("fechaNacimiento", ""), font=("Arial", 11, "bold"),
            bg=self.bg_color, fg="#212121").pack(pady=(3, 0))
        
        # Tarjeta de crédito con botón Editar (alineados)
        cardMainFrame = tk.Frame(fieldsFrame, bg=self.bg_color)
        cardMainFrame.pack(pady=(0, 20))
        
        cardContentFrame = tk.Frame(cardMainFrame, bg=self.bg_color)
        cardContentFrame.pack()
        
        # Label y valor de tarjeta
        cardLabelFrame = tk.Frame(cardContentFrame, bg=self.bg_color)
        cardLabelFrame.grid(row=0, column=0, sticky="w")
        tk.Label(cardLabelFrame, text="Tarjeta de credito", font=("Arial", 11),
            bg=self.bg_color, fg="#757575").pack(anchor="w")
        self.cardValueLabel = tk.Label(cardLabelFrame, text=self.getMaskedCardNumber(), font=("Arial", 11, "bold"),
            bg=self.bg_color, fg="#212121")
        self.cardValueLabel.pack(anchor="w", pady=(3, 0))
        
        # Botón Editar / Agregar según si hay tarjeta
        has_card = bool(self.userData.get('tarjetaCredito')) and len(str(self.userData.get('tarjetaCredito'))) >= 4
        if has_card:
            btn_label = "Editar"
            btn_cmd = self.showEditCardDialog
        else:
            btn_label = "Agregar"
            # cuando no hay tarjeta, abrir directamente la ventana para agregar (sin verificación)
            btn_cmd = self.showNewCardDialog

        btnEditCard = tk.Button(cardContentFrame, text=btn_label, command=btn_cmd,
            bg=self.bg_color, fg="black", font=("Arial", 10), cursor="hand2", relief=tk.SOLID,
            borderwidth=1, padx=18, pady=4)
        btnEditCard.grid(row=0, column=1, padx=(15, 0), sticky="e")
        
        # Contraseña con botón Editar (alineados)
        passwordMainFrame = tk.Frame(fieldsFrame, bg=self.bg_color)
        passwordMainFrame.pack(pady=(0, 30))
        
        passwordContentFrame = tk.Frame(passwordMainFrame, bg=self.bg_color)
        passwordContentFrame.pack()
        
        # Label y valor de contraseña
        passwordLabelFrame = tk.Frame(passwordContentFrame, bg=self.bg_color)
        passwordLabelFrame.grid(row=0, column=0, sticky="w")
        tk.Label(passwordLabelFrame, text="Contraseña", font=("Arial", 11),
            bg=self.bg_color, fg="#757575").pack(anchor="w")
        tk.Label(passwordLabelFrame, text="••••••••", font=("Arial", 11, "bold"),
            bg=self.bg_color, fg="#212121").pack(anchor="w", pady=(3, 0))
        
        # Botón Editar
        btnEditPassword = tk.Button(passwordContentFrame, text="Editar",
                    command=self.showChangePasswordDialog,
                    bg=self.bg_color, fg="black",
                    font=("Arial", 10),
                    cursor="hand2", relief=tk.SOLID,
                    borderwidth=1, padx=18, pady=4)
        btnEditPassword.grid(row=0, column=1, padx=(15, 0), sticky="e")
        
        # Botones centrados
        buttonsFrame = tk.Frame(fieldsFrame, bg=self.bg_color)
        buttonsFrame.pack()
        
        # Botón Registrar Cara
        btnRegisterFace = tk.Button(buttonsFrame, text="Registrar Cara",
                    command=self.registerFace,
                    bg=self.bg_color, fg="black",
                    font=("Arial", 11),
                    cursor="hand2", relief=tk.SOLID,
                    borderwidth=1, padx=45, pady=8)
        btnRegisterFace.pack(pady=(0, 12))
        
        # Botón Guardar Cambios
        btnSave = tk.Button(buttonsFrame, text="Guardar Cambios",
                command=self.saveChanges,
                bg=self.bg_color, fg="black",
                font=("Arial", 11),
                cursor="hand2", relief=tk.SOLID,
                borderwidth=1, padx=35, pady=8)
        btnSave.pack()
        
    def getMaskedCardNumber(self):
        """Retorna el número de tarjeta enmascarado"""
        card = self.userData.get("tarjetaCredito", "") or ""
        if not card or len(card) < 4:
            return "No registrada"
        try:
            return "xxxx xxxx xxxx " + card[-4:]
        except Exception:
            return "No registrada"
    
    def showEditCardDialog(self):
        """Muestra diálogo para verificar tarjeta actual - Paso 1"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Cambiar Tarjeta - Paso 1 de 2")
        dialog.geometry("400x300")
        dialog.configure(bg="white")
        dialog.transient(self.root)
        dialog.grab_set()
        # actualizar visual y persistir si hace falta
        if self.updateCardDisplay():
            self.save_user_data()
        
        # Centrar diálogo
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        contentFrame = tk.Frame(dialog, bg="white", padx=20, pady=20)
        contentFrame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(contentFrame, text="Paso 1: Verifique su tarjeta actual",
                font=("Arial", 12, "bold"), bg="white").pack(pady=(0, 5))
        
        tk.Label(contentFrame, text="Ingrese el CVV y fecha de caducidad de su tarjeta actual\npara verificar que es el propietario",
                font=("Arial", 9), bg="white", fg="#666", justify="center").pack(pady=(0, 15))
        
        tk.Label(contentFrame, text=f"Tarjeta: {self.getMaskedCardNumber()}",
                font=("Arial", 10), bg="white").pack(anchor="w", pady=(0, 15))
        
        # Frame para CVV y Fecha
        bottomFrame = tk.Frame(contentFrame, bg="white")
        bottomFrame.pack(fill=tk.X, pady=10)
        
        # CVV
        cvvFrame = tk.Frame(bottomFrame, bg="white")
        cvvFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(cvvFrame, text="CVV", font=("Arial", 10, "bold"),
                bg="white").pack(anchor="w")
        
        entryCvv = tk.Entry(cvvFrame, font=("Arial", 12),
                           relief=tk.SOLID, borderwidth=1, width=8)
        entryCvv.pack(fill=tk.X, pady=(5, 0), ipady=5)
        
        # Fecha de caducidad
        fechaFrame = tk.Frame(bottomFrame, bg="white")
        fechaFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(fechaFrame, text="Fecha caducidad",
                font=("Arial", 10, "bold"), bg="white").pack(anchor="w")
        
        entryFecha = tk.Entry(fechaFrame, font=("Arial", 12),
                             relief=tk.SOLID, borderwidth=1)
        entryFecha.pack(fill=tk.X, pady=(5, 0), ipady=5)
        entryFecha.insert(0, "MM/AA")
        entryFecha.config(fg="gray")
        
        # Evento para placeholder
        def onFechaFocus(event):
            if entryFecha.get() == "MM/AA":
                entryFecha.delete(0, tk.END)
                entryFecha.config(fg="black")
        
        def onFechaFocusOut(event):
            if entryFecha.get() == "":
                entryFecha.insert(0, "MM/AA")
                entryFecha.config(fg="gray")
        
        entryFecha.bind("<FocusIn>", onFechaFocus)
        entryFecha.bind("<FocusOut>", onFechaFocusOut)
        
        # Botones
        buttonFrame = tk.Frame(contentFrame, bg="white")
        buttonFrame.pack(pady=20)
        
        def verificarYContinuar():
            cvv = entryCvv.get()
            fecha = entryFecha.get()
            
            # Validaciones
            if len(cvv) != 3 or not cvv.isdigit():
                messagebox.showerror("Error", "El CVV debe tener 3 dígitos", parent=dialog)
                return
            
            if cvv != self.userData["cvv"]:
                messagebox.showerror("Error", "CVV incorrecto", parent=dialog)
                return
            
            if fecha == "MM/AA" or len(fecha) != 5 or fecha[2] != "/":
                messagebox.showerror("Error", "Formato de fecha inválido (MM/AA)", parent=dialog)
                return
            
            if fecha != self.userData["fechaCaducidad"]:
                messagebox.showerror("Error", "Fecha de caducidad incorrecta", parent=dialog)
                return
            
            # Si todo es correcto, abrir ventana para nueva tarjeta
            dialog.destroy()
            self.showNewCardDialog()
        
        btnSiguiente = tk.Button(buttonFrame, text="Siguiente",
                                command=verificarYContinuar,
                                bg="white", fg="black",
                                font=("Arial", 10),
                                cursor="hand2", relief=tk.SOLID,
                                borderwidth=1, padx=20, pady=8)

        btnSiguiente.pack(side=tk.LEFT, padx=5)
        
        btnCancelar = tk.Button(buttonFrame, text="Cancelar",
                               command=dialog.destroy,
                               bg="white", fg="black",
                               font=("Arial", 10),
                               cursor="hand2", relief=tk.SOLID,
                               borderwidth=1, padx=20, pady=8)
        btnCancelar.pack(side=tk.LEFT, padx=5)
    
    def showNewCardDialog(self):
        """Muestra diálogo para ingresar nueva tarjeta - Paso 2"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Cambiar Tarjeta - Paso 2 de 2")
        dialog.geometry("400x340")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()

        # Centrar diálogo
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        contentFrame = tk.Frame(dialog, bg=self.bg_color, padx=20, pady=20)
        contentFrame.pack(fill=tk.BOTH, expand=True)

        tk.Label(contentFrame, text="Paso 2: Ingrese los datos de su nueva tarjeta",
                 font=("Arial", 11, "bold"), bg=self.bg_color).pack(pady=(0, 5))

        tk.Label(contentFrame, text="Complete todos los campos con la información de su nueva tarjeta",
                 font=("Arial", 9), bg=self.bg_color, fg="#666").pack(pady=(0, 15))

        # Número de la tarjeta
        tk.Label(contentFrame, text="Número de la Tarjeta",
                 font=("Arial", 10, "bold"), bg=self.bg_color).pack(anchor="w")

        entryNumero = tk.Entry(contentFrame, font=("Arial", 12), relief=tk.SOLID, borderwidth=1)
        entryNumero.pack(fill=tk.X, pady=(5, 15), ipady=5)

        # Frame para CVV y Fecha
        bottomFrame = tk.Frame(contentFrame, bg=self.bg_color)
        bottomFrame.pack(fill=tk.X, pady=10)

        # CVV
        cvvFrame = tk.Frame(bottomFrame, bg=self.bg_color)
        cvvFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(cvvFrame, text="CVV", font=("Arial", 10, "bold"), bg=self.bg_color).pack(anchor="w")

        entryCvv = tk.Entry(cvvFrame, font=("Arial", 12), relief=tk.SOLID, borderwidth=1, width=8)
        entryCvv.pack(fill=tk.X, pady=(5, 0), ipady=5)

        # Fecha de caducidad
        fechaFrame = tk.Frame(bottomFrame, bg=self.bg_color)
        fechaFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(fechaFrame, text="Fecha caducidad", font=("Arial", 10, "bold"), bg=self.bg_color).pack(anchor="w")

        entryFecha = tk.Entry(fechaFrame, font=("Arial", 12), relief=tk.SOLID, borderwidth=1)
        entryFecha.pack(fill=tk.X, pady=(5, 0), ipady=5)
        entryFecha.insert(0, "MM/AA")
        entryFecha.config(fg="gray")

        # Evento para placeholder
        def onFechaFocus(event):
            if entryFecha.get() == "MM/AA":
                entryFecha.delete(0, tk.END)
                entryFecha.config(fg="black")

        def onFechaFocusOut(event):
            if entryFecha.get() == "":
                entryFecha.insert(0, "MM/AA")
                entryFecha.config(fg="gray")

        entryFecha.bind("<FocusIn>", onFechaFocus)
        entryFecha.bind("<FocusOut>", onFechaFocusOut)

        # Botones
        buttonFrame = tk.Frame(contentFrame, bg=self.bg_color)
        buttonFrame.pack(pady=20)

        def guardarNuevaTarjeta():
            numero = entryNumero.get().replace(" ", "")
            cvv = entryCvv.get()
            fecha = entryFecha.get()

            # Validaciones
            if len(numero) != 16 or not numero.isdigit():
                messagebox.showerror("Error", "La tarjeta debe tener 16 dígitos", parent=dialog)
                return

            if len(cvv) != 3 or not cvv.isdigit():
                messagebox.showerror("Error", "El CVV debe tener 3 dígitos", parent=dialog)
                return

            if fecha == "MM/AA" or len(fecha) != 5 or fecha[2] != "/":
                messagebox.showerror("Error", "Formato de fecha inválido (MM/AA)", parent=dialog)
                return

            # Guardar nueva tarjeta con sus nuevos datos
            self.userData["tarjetaCredito"] = numero
            self.userData["cvv"] = cvv
            self.userData["fechaCaducidad"] = fecha
            self.updateCardDisplay()
            # Persistir los cambios
            try:
                self.save_user_data()
            except Exception:
                pass
            messagebox.showinfo("Éxito", "Tarjeta actualizada correctamente", parent=dialog)
            dialog.destroy()

        btnGuardar = tk.Button(buttonFrame, text="Guardar", command=guardarNuevaTarjeta,
                                bg=self.bg_color, fg="black", font=("Arial", 10), cursor="hand2",
                                relief=tk.SOLID, borderwidth=1, padx=20, pady=8)
        btnGuardar.pack(side=tk.LEFT, padx=5)

        btnCancelar = tk.Button(buttonFrame, text="Cancelar", command=dialog.destroy,
                                bg=self.bg_color, fg="black", font=("Arial", 10), cursor="hand2",
                                relief=tk.SOLID, borderwidth=1, padx=20, pady=8)
        btnCancelar.pack(side=tk.LEFT, padx=5)
    # ya no cerramos automáticamente la ventana al abrirla
    
    def updateCardDisplay(self):
        """Actualiza la visualización de la tarjeta"""
        if hasattr(self, 'cardValueLabel'):
            try:
                # actualizar texto en etiqueta
                self.cardValueLabel.config(text=self.getMaskedCardNumber())
            except Exception:
                pass
    
    def showChangePasswordDialog(self):
        """Muestra diálogo para cambiar contraseña - Paso 1: Verificar actual"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Cambiar Contraseña - Paso 1 de 2")
        dialog.geometry("350x260")
        dialog.configure(bg="white")
        dialog.transient(self.root)
        dialog.grab_set()
        # Nota: no ejecutar validación global aquí; se hace dentro del diálogo
        
        # Centrar diálogo
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        contentFrame = tk.Frame(dialog, bg="white", padx=30, pady=20)
        contentFrame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(contentFrame, text="Paso 1: Verifique su identidad",
                font=("Arial", 11, "bold"), bg="white").pack(pady=(0, 5))
        
        tk.Label(contentFrame, text="Ingrese su contraseña actual para continuar",
                font=("Arial", 9), bg="white", fg="#666").pack(pady=(0, 10))
        
        entryActual = tk.Entry(contentFrame, font=("Arial", 12), show="•",
                              relief=tk.SOLID, borderwidth=1)
        entryActual.pack(fill=tk.X, ipady=8)

        # enlace visible para recuperación (se pidió que aparezca en este paso)
        try:
            link_recover = tk.Label(contentFrame, text='¿Olvidaste tu contraseña?', fg='blue', bg='white', cursor='hand2', font=('Arial', 9, 'underline'))
            link_recover.pack(pady=(8, 4))
            link_recover.bind('<Button-1>', lambda e: self.openRecoveryOptions())
        except Exception:
            pass
        
        def verificarYContinuar():
            """Verifica la contraseña ingresada usando bcrypt/SistemaSeguridad o comparación directa."""
            pwd = entryActual.get()
            verified = False
            # Intentar verificar con bcrypt si está disponible
            try:
                import bcrypt
                stored_hash = None
                if isinstance(self.userData.get('contrasena'), str) and (self.userData.get('contrasena').startswith('$2') or len(self.userData.get('contrasena')) > 30):
                    stored_hash = self.userData.get('contrasena')
                else:
                    stored_hash = self.userData.get('contrasena') or self.userData.get('contrasenaHash') or self.userData.get('contrasena_hash')
                if stored_hash:
                    try:
                        verified = bcrypt.checkpw(pwd.encode('utf-8'), stored_hash.encode('utf-8'))
                    except Exception:
                        verified = False
            except Exception:
                verified = False

            if not verified:
                # intentar con SistemaSeguridad (registro.SistemaSeguridad.verificarContrasena)
                try:
                    SistemaSeguridad = None
                    import_attempts = [
                        lambda: __import__('inicioRegistro.registro', fromlist=['SistemaSeguridad']).SistemaSeguridad,
                        lambda: __import__('registro').SistemaSeguridad,
                    ]
                    import sys
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    if current_dir not in sys.path:
                        sys.path.insert(0, current_dir)
                    parent_dir = os.path.dirname(current_dir)
                    if parent_dir not in sys.path:
                        sys.path.insert(0, parent_dir)
                    for attempt in import_attempts:
                        try:
                            SistemaSeguridad = attempt()
                            break
                        except Exception:
                            continue
                    if SistemaSeguridad is not None:
                        ss = SistemaSeguridad()
                        stored_hash = self.userData.get('contrasena') or self.userData.get('contrasenaHash') or self.userData.get('contrasena_hash')
                        if not stored_hash:
                            # intentar leer desde usuarios.json
                            try:
                                users_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataBase', 'usuarios.json')
                                if os.path.exists(users_file):
                                    with open(users_file, 'r', encoding='utf-8') as f:
                                        users = json.load(f)
                                    for u in users:
                                        name = u.get('usuario') or u.get('username') or u.get('user')
                                        if name and name == self.userData.get('username'):
                                            stored_hash = u.get('contrasenaHash') or u.get('contrasena_hash') or u.get('contrasena')
                                            break
                            except Exception:
                                stored_hash = None
                        if stored_hash:
                            try:
                                verified = ss.verificarContrasena(pwd, stored_hash)
                            except Exception:
                                verified = False
                except Exception:
                    verified = False

            # último recurso: comparación en texto plano si el registro lo tuviera
            if not verified:
                try:
                    if str(self.userData.get('contrasena', '')) == pwd:
                        verified = True
                except Exception:
                    verified = False

            if verified:
                dialog.destroy()
                self.showNewPasswordDialog()
            else:
                messagebox.showerror("Error", "Contraseña incorrecta", parent=dialog)
        
        buttonFrame = tk.Frame(contentFrame, bg="white")
        buttonFrame.pack(pady=12)
        
        btnSiguiente = tk.Button(buttonFrame, text="Siguiente",
                                command=verificarYContinuar,
                                bg="white", fg="black",
                                font=("Arial", 10),
                                cursor="hand2", relief=tk.SOLID,
                                borderwidth=1, padx=20, pady=8)
        btnSiguiente.pack(side=tk.LEFT, padx=5)
        
        btnCancelar = tk.Button(buttonFrame, text="Cancelar",
                               command=dialog.destroy,
                               bg="white", fg="black",
                               font=("Arial", 10),
                               cursor="hand2", relief=tk.SOLID,
                               borderwidth=1, padx=20, pady=8)
        btnCancelar.pack(side=tk.LEFT, padx=5)
    
    def showNewPasswordDialog(self):
        """Muestra diálogo para ingresar nueva contraseña - Paso 2"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Cambiar Contraseña - Paso 2 de 2")
        dialog.geometry("380x340")
        dialog.configure(bg="white")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrar diálogo
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        contentFrame = tk.Frame(dialog, bg="white", padx=30, pady=30)
        contentFrame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(contentFrame, text="Paso 2: Establezca su nueva contraseña",
                font=("Arial", 11, "bold"), bg="white").pack(pady=(0, 5))
        
        tk.Label(contentFrame, text="Mínimo 8 caracteres alfanuméricos",
                font=("Arial", 9), bg="white", fg="#666").pack(pady=(0, 15))
        
        tk.Label(contentFrame, text="Nueva contraseña",
                font=("Arial", 10, "bold"), bg="white").pack(anchor="w", pady=(0, 5))
        
        entryNueva = tk.Entry(contentFrame, font=("Arial", 12), show="•",
                             relief=tk.SOLID, borderwidth=1)
        entryNueva.pack(fill=tk.X, ipady=8, pady=(0, 15))
        
        tk.Label(contentFrame, text="Confirmar contraseña",
                font=("Arial", 10, "bold"), bg="white").pack(anchor="w", pady=(0, 5))
        
        entryConfirmar = tk.Entry(contentFrame, font=("Arial", 12), show="•",
                                 relief=tk.SOLID, borderwidth=1)
        entryConfirmar.pack(fill=tk.X, ipady=8)
        
        def verificarContrasenas():
            nueva = entryNueva.get()
            confirmar = entryConfirmar.get()
            
            # Validar longitud mínima
            if len(nueva) < 8:
                self.showPasswordErrorDialog("La contraseña debe tener al menos 8 caracteres", dialog)
                return
            
            # Validar que sea alfanumérica
            if not nueva.isalnum():
                self.showPasswordErrorDialog("La contraseña debe contener solo letras y números", dialog)
                return
            
            # Validar que las contraseñas coincidan
            if nueva != confirmar:
                self.showPasswordErrorDialog("Las contraseñas no coinciden", dialog)
                return
            
            # Si todo es correcto, guardar
            self.userData["contrasena"] = nueva
            # Persistir contraseña
            try:
                self.save_user_data()
            except Exception:
                pass
            messagebox.showinfo("Éxito", "Contraseña actualizada correctamente", parent=dialog)
            dialog.destroy()

    def _prompt_new_password_for_user(self, usuario):
        """Prompt the user twice for a new password and return bcrypt hash or None."""
        try:
            pwd1 = simpledialog.askstring('Nueva contraseña', f'Ingrese nueva contraseña para {usuario}:', show='*', parent=self.root)
            if not pwd1:
                return None
            pwd2 = simpledialog.askstring('Confirmar contraseña', 'Confirme la nueva contraseña:', show='*', parent=self.root)
            if pwd1 != pwd2:
                messagebox.showwarning('Error', 'Las contraseñas no coinciden')
                return None
            if len(pwd1) < 8:
                messagebox.showwarning('Error', 'La contraseña debe tener al menos 8 caracteres')
                return None
            # Hash using SistemaSeguridad from registro.py
            try:
                SistemaSeguridad = None
                import_attempts = [
                    lambda: __import__('inicioRegistro.registro', fromlist=['SistemaSeguridad']).SistemaSeguridad,
                    lambda: __import__('registro').SistemaSeguridad,
                ]
                import sys
                current_dir = os.path.dirname(os.path.abspath(__file__))
                if current_dir not in sys.path:
                    sys.path.insert(0, current_dir)
                parent_dir = os.path.dirname(current_dir)
                if parent_dir not in sys.path:
                    sys.path.insert(0, parent_dir)
                for attempt in import_attempts:
                    try:
                        SistemaSeguridad = attempt()
                        break
                    except Exception:
                        continue
                if SistemaSeguridad is None:
                    raise ImportError('No se encontró SistemaSeguridad')
                ss = SistemaSeguridad()
                new_hash = ss.hashContrasena(pwd1)
                return new_hash
            except Exception as e:
                messagebox.showerror('Error', f'Error al procesar la nueva contraseña: {e}')
                return None
        except Exception:
            return None

    def _recover_by_security_question(self):
        import os, json
        usuario = simpledialog.askstring('Recuperación', 'Ingrese su nombre de usuario:', parent=self.root)
        if not usuario:
            return
        # find usuarios.json
        try:
            possible = [
                os.path.join(os.path.dirname(__file__), '..', 'dataBase', 'usuarios.json'),
                os.path.join(os.getcwd(), 'dataBase', 'usuarios.json'),
                os.path.join(os.path.dirname(__file__), 'dataBase', 'usuarios.json')
            ]
            usuarios_path = None
            usuarios_list = []
            for p in possible:
                p = os.path.normpath(p)
                if os.path.exists(p):
                    usuarios_path = p
                    with open(p, 'r', encoding='utf-8') as f:
                        usuarios_list = json.load(f)
                    break
        except Exception:
            usuarios_list = []

        target = None
        for u in usuarios_list:
            name = (u.get('usuario') or u.get('username') or '')
            if name and name.lower() == usuario.lower():
                target = u
                break
        if not target:
            messagebox.showwarning('No encontrado', 'Usuario no encontrado en usuarios.json')
            return

        question = target.get('preguntaSeguridad') or target.get('pregunta_seguridad') or 'Pregunta de seguridad'
        encrypted_answer = target.get('respuestaSeguridad') or target.get('respuesta_seguridad')
        try:
            answer = simpledialog.askstring('Pregunta de seguridad', question, parent=self.root)
            if not answer:
                return
        except Exception:
            return

        # decrypt via SistemaSeguridad
        try:
            SistemaSeguridad = None
            import_attempts = [
                lambda: __import__('inicioRegistro.registro', fromlist=['SistemaSeguridad']).SistemaSeguridad,
                lambda: __import__('registro').SistemaSeguridad,
            ]
            for attempt in import_attempts:
                try:
                    SistemaSeguridad = attempt()
                    break
                except Exception:
                    continue
            if SistemaSeguridad is None:
                raise ImportError('No se pudo importar SistemaSeguridad')
            ss = SistemaSeguridad()
            stored = ''
            if encrypted_answer:
                try:
                    stored = ss.desencriptar(encrypted_answer)
                except Exception:
                    stored = encrypted_answer
            if stored and stored.strip().lower() == answer.strip().lower():
                new_hash = self._prompt_new_password_for_user(usuario)
                if not new_hash:
                    messagebox.showinfo('Cancelado', 'No se actualizó la contraseña')
                    return
                try:
                    for u in usuarios_list:
                        name = (u.get('usuario') or u.get('username') or '')
                        if name and name.lower() == usuario.lower():
                            u['contrasenaHash'] = new_hash
                            u['contrasena_hash'] = new_hash
                            break
                    if usuarios_path:
                        with open(usuarios_path, 'w', encoding='utf-8') as f:
                            json.dump(usuarios_list, f, indent=4, ensure_ascii=False)
                        messagebox.showinfo('Éxito', 'Contraseña actualizada correctamente')
                except Exception as e:
                    messagebox.showerror('Error', f'No se pudo actualizar usuarios.json: {e}')
            else:
                messagebox.showwarning('Incorrecto', 'Respuesta incorrecta')
        except Exception as e:
            messagebox.showerror('Error', f'Error validando respuesta: {e}')

    def _recover_by_face(self):
        """Recupera contraseña mediante reconocimiento facial."""
        import io, base64
        try:
            # Asegurar que face_gui esté en el path
            import sys
            repo_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
            if repo_root not in sys.path:
                sys.path.insert(0, repo_root)

            try:
                from inicioRegistro import face_gui
            except ImportError:
                try:
                    import runpy
                    face_gui_path = os.path.join(repo_root, 'inicioRegistro', 'face_gui.py')
                    if os.path.exists(face_gui_path):
                        face_gui = runpy.run_path(face_gui_path)
                    else:
                        raise ImportError(f"No se encontró {face_gui_path}")
                except Exception as e:
                    messagebox.showerror('Error', f'No se pudo cargar el módulo de captura: {e}')
                    return

            # Primero intentar leer usuarios.json para ver si hay rostros registrados
            usuarios_list = []
            usuarios_path = None
            try:
                possible = [
                    os.path.join(repo_root, 'dataBase', 'usuarios.json'),
                    os.path.join(os.getcwd(), 'dataBase', 'usuarios.json'),
                    os.path.join(os.path.dirname(__file__), 'dataBase', 'usuarios.json')
                ]
                for p in possible:
                    p = os.path.normpath(p)
                    if os.path.exists(p):
                        usuarios_path = p
                        with open(p, 'r', encoding='utf-8') as f:
                            usuarios_list = json.load(f)
                        break
            except Exception as e:
                messagebox.showerror('Error', f'No se pudo leer usuarios.json: {e}')
                return

            # Verificar si hay usuarios con rostro registrado
            has_faces = False
            for u in usuarios_list:
                if u.get('face_enc'):
                    has_faces = True
                    break
            if not has_faces:
                messagebox.showwarning('Aviso', 'No hay usuarios con rostro registrado en el sistema.')
                return

            # prepare Fernet key if available
            fernet = None
            try:
                clave_paths = [
                    os.path.join(repo_root, 'dataBase', 'clave.key'),
                    os.path.join(os.getcwd(), 'dataBase', 'clave.key'),
                    os.path.join(os.path.dirname(__file__), 'dataBase', 'clave.key'),
                ]
                key_bytes = None
                for kp in clave_paths:
                    kp = os.path.normpath(kp)
                    if os.path.exists(kp):
                        with open(kp, 'rb') as fk:
                            key_bytes = fk.read()
                        break
                if key_bytes and Fernet is not None:
                    fernet = Fernet(key_bytes)
            except Exception:
                pass  # no critical if encryption not available

            # Capturar rostro actual
            messagebox.showinfo('Instrucción', 'Se abrirá la cámara para reconocimiento facial.\nMire directamente a la cámara y mantenga una expresión neutral.')
            mean_face, _ = face_gui.register_face_gui(return_array=True)
            if mean_face is None:
                messagebox.showwarning('Aviso', 'No se pudo capturar el rostro. Inténtelo de nuevo.')
                return

            # Comparar con rostros almacenados
            best_user = None
            best_dist = float('inf')
            for u in usuarios_list:
                try:
                    enc = u.get('face_enc')
                    if not enc:
                        continue

                    # Intentar desencriptar si está cifrado
                    try:
                        if fernet:
                            try:
                                b64 = fernet.decrypt(enc.encode()).decode('utf-8')
                            except Exception:
                                b64 = enc
                        else:
                            b64 = enc
                    except Exception:
                        continue

                    # Decodificar array NumPy
                    try:
                        b = base64.b64decode(b64)
                        arr = np.load(io.BytesIO(b))
                        # Asegurar mismo tipo y forma
                        arr = arr.astype(np.float32).flatten()
                        current = mean_face.astype(np.float32).flatten()
                        # Calcular distancia euclidiana
                        d = np.linalg.norm(arr - current)
                        if d < best_dist:
                            best_dist = d
                            best_user = u.get('usuario') or u.get('username')
                    except Exception as e:
                        print(f"Error comparando rostro: {e}")
                        continue
                except Exception:
                    continue

            # Umbral más estricto (ajustado según pruebas)
            if best_user and best_dist < 12000:  # umbral más estricto
                new_hash = self._prompt_new_password_for_user(best_user)
                if not new_hash:
                    messagebox.showinfo('Cancelado', 'No se actualizó la contraseña')
                    return

                # Actualizar contraseña
                updated = False
                try:
                    for u in usuarios_list:
                        name = (u.get('usuario') or u.get('username') or '')
                        if name and name == best_user:
                            u['contrasenaHash'] = new_hash
                            u['contrasena_hash'] = new_hash
                            u['contrasena'] = new_hash
                            updated = True
                            break

                    if updated and usuarios_path:
                        with open(usuarios_path, 'w', encoding='utf-8') as f:
                            json.dump(usuarios_list, f, indent=4, ensure_ascii=False)
                        messagebox.showinfo('Éxito', f'Contraseña actualizada correctamente para {best_user}')
                    else:
                        raise Exception('No se encontró el usuario para actualizar')
                except Exception as e:
                    messagebox.showerror('Error', f'No se pudo actualizar la contraseña: {e}')
            else:
                messagebox.showwarning('No reconocido', 
                    'No se encontró una coincidencia facial segura.\n' + 
                    'Asegúrese de mirar directamente a la cámara\n' +
                    'y mantener una expresión neutral.')
        except Exception as e:
            messagebox.showerror('Error', f'Error en la recuperación facial: {e}')

    def openRecoveryOptions(self):
        """Muestra el diálogo para elegir método de recuperación (rostro / pregunta)."""
        try:
            dlg = tk.Toplevel(self.root)
            dlg.title('Recuperar contraseña')
            dlg.geometry('320x140')
            dlg.resizable(False, False)
            tk.Label(dlg, text='Elige un método de recuperación:', font=('Arial', 11)).pack(pady=(12,8))

            btn_frame = tk.Frame(dlg)
            btn_frame.pack(pady=6)

            def _by_face():
                dlg.destroy()
                try:
                    self._recover_by_face()
                except Exception as e:
                    messagebox.showerror('Error', f'Error en recuperación por rostro: {e}')

            def _by_question():
                dlg.destroy()
                try:
                    self._recover_by_security_question()
                except Exception as e:
                    messagebox.showerror('Error', f'Error en recuperación por pregunta: {e}')

            b1 = tk.Button(btn_frame, text='Por reconocimiento facial', width=22, command=_by_face)
            b1.pack(pady=4)
            b2 = tk.Button(btn_frame, text='Por pregunta de seguridad', width=22, command=_by_question)
            b2.pack(pady=4)

            b_cancel = tk.Button(dlg, text='Cancelar', command=dlg.destroy)
            b_cancel.pack(pady=(6,0))
            dlg.transient(self.root)
            dlg.grab_set()
            self.root.wait_window(dlg)
        except Exception:
            try:
                self.root.destroy()
            except Exception:
                pass
        
        
    def showPasswordErrorDialog(self, mensaje, parentDialog):
        """Muestra diálogo de error con opción de volver"""
        errorDialog = tk.Toplevel(parentDialog)
        errorDialog.title("Error")
        errorDialog.geometry("350x180")
        errorDialog.configure(bg="white")
        errorDialog.transient(parentDialog)
        errorDialog.grab_set()
        
        # Centrar diálogo
        errorDialog.update_idletasks()
        x = (errorDialog.winfo_screenwidth() // 2) - (errorDialog.winfo_width() // 2)
        y = (errorDialog.winfo_screenheight() // 2) - (errorDialog.winfo_height() // 2)
        errorDialog.geometry(f"+{x}+{y}")
        
        contentFrame = tk.Frame(errorDialog, bg="white", padx=30, pady=30)
        contentFrame.pack(fill=tk.BOTH, expand=True)
        
        # Ícono y mensaje de error
        tk.Label(contentFrame, text="⚠️", font=("Arial", 30), bg="white").pack(pady=(0, 10))
        
        tk.Label(contentFrame, text=mensaje,
                font=("Arial", 10), bg="white", fg="#d32f2f",
                wraplength=280, justify="center").pack(pady=(0, 20))
        
        btnVolver = tk.Button(contentFrame, text="Volver",
                             command=errorDialog.destroy,
                             bg="white", fg="black",
                             font=("Arial", 10),
                             cursor="hand2", relief=tk.SOLID,
                             borderwidth=1, padx=30, pady=8)
        btnVolver.pack()
    
    def registerFace(self):
        # Registrar el rostro usando inicioRegistro.face_gui
        try:
            # Pedir contraseña actual por seguridad
            try:
                pwd = simpledialog.askstring('Confirmar contraseña', 'Ingrese su contraseña actual para confirmar el registro de rostro:', show='*', parent=self.root)
            except Exception:
                pwd = None

            if not pwd:
                try:
                    messagebox.showinfo('Cancelado', 'Registro de rostro cancelado')
                except Exception:
                    pass
                return

            # Verificar contraseña: preferir bcrypt, luego SistemaSeguridad, luego comparación directa
            verified = False
            try:
                import bcrypt
                # buscar hash en userData: contrasenaHash, contrasena_hash, contrasena
                stored_hash = None
                if isinstance(self.userData.get('contrasena'), str) and (self.userData.get('contrasena').startswith('$2') or len(self.userData.get('contrasena')) > 30):
                    stored_hash = self.userData.get('contrasena')
                else:
                    # try other keys
                    stored_hash = getattr(self, 'userData', {}).get('contrasenaHash') or getattr(self, 'userData', {}).get('contrasena_hash') or getattr(self, 'userData', {}).get('contrasena')
                if stored_hash:
                    try:
                        verified = bcrypt.checkpw(pwd.encode('utf-8'), stored_hash.encode('utf-8'))
                    except Exception:
                        verified = False
            except Exception:
                verified = False

            if not verified:
                # intentar con SistemaSeguridad (registro.SistemaSeguridad.hash/verificar)
                try:
                    SistemaSeguridad = None
                    import_attempts = [
                        lambda: __import__('inicioRegistro.registro', fromlist=['SistemaSeguridad']).SistemaSeguridad,
                        lambda: __import__('registro').SistemaSeguridad,
                    ]
                    import sys
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    if current_dir not in sys.path:
                        sys.path.insert(0, current_dir)
                    parent_dir = os.path.dirname(current_dir)
                    if parent_dir not in sys.path:
                        sys.path.insert(0, parent_dir)
                    for attempt in import_attempts:
                        try:
                            SistemaSeguridad = attempt()
                            break
                        except Exception:
                            continue
                    if SistemaSeguridad is not None:
                        ss = SistemaSeguridad()
                        # stored hash may be in usuarios.json; try to read direct from usuarios.json if not present in self.userData
                        stored_hash = self.userData.get('contrasena') or self.userData.get('contrasenaHash') or self.userData.get('contrasena_hash')
                        if not stored_hash:
                            # intentar leer desde usuarios.json
                            try:
                                users_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataBase', 'usuarios.json')
                                if os.path.exists(users_file):
                                    with open(users_file, 'r', encoding='utf-8') as f:
                                        users = json.load(f)
                                    for u in users:
                                        name = u.get('usuario') or u.get('username') or u.get('user')
                                        if name and name == self.userData.get('username'):
                                            stored_hash = u.get('contrasenaHash') or u.get('contrasena_hash') or u.get('contrasena')
                                            break
                            except Exception:
                                stored_hash = None
                        if stored_hash:
                            try:
                                verified = ss.verificarContrasena(pwd, stored_hash)
                            except Exception:
                                verified = False
                except Exception:
                    verified = False

            if not verified:
                # último recurso: comparar texto plano (si userData tenía contraseña en texto)
                try:
                    if str(self.userData.get('contrasena', '')) == pwd:
                        verified = True
                except Exception:
                    verified = False

            if not verified:
                try:
                    messagebox.showerror('Error', 'Contraseña incorrecta. No se puede registrar el rostro.')
                except Exception:
                    pass
                return

            # Asegurar que la carpeta del repo esté en sys.path para poder importar inicioRegistro.face_gui
            try:
                import sys
                repo_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
                if repo_root not in sys.path:
                    sys.path.insert(0, repo_root)
            except Exception:
                pass

            try:
                from inicioRegistro import face_gui
            except Exception:
                try:
                    import face_gui
                except Exception:
                    messagebox.showerror("Error", "Cámara o módulo de captura no disponible")
                    return

            mean_face, name = face_gui.register_face_gui(return_array=True)
            if mean_face is None:
                messagebox.showwarning("Aviso", "No se pudo capturar la cara")
                return

            buf = io.BytesIO()
            np.save(buf, mean_face)
            buf.seek(0)
            raw = buf.read()
            b64 = base64.b64encode(raw).decode('ascii')

            # Intentar encriptar con clave.key si está disponible
            encrypted = b64
            try:
                if Fernet is not None:
                    clave_paths = [
                        os.path.join(os.path.dirname(__file__), '..', 'dataBase', 'clave.key'),
                        os.path.join(os.getcwd(), 'dataBase', 'clave.key'),
                        os.path.join(os.path.dirname(__file__), 'dataBase', 'clave.key'),
                    ]
                    key_bytes = None
                    for kp in clave_paths:
                        kp = os.path.normpath(kp)
                        if os.path.exists(kp):
                            with open(kp, 'rb') as fk:
                                key_bytes = fk.read()
                            break
                    if key_bytes:
                        f = Fernet(key_bytes)
                        try:
                            encrypted = f.encrypt(b64.encode()).decode('utf-8')
                        except Exception:
                            encrypted = b64
            except Exception:
                encrypted = b64

            # Guardar en userData y persistir usando save_user_data
            try:
                self.userData['face_enc'] = encrypted
                # marcar que tiene foto registrada
                self.userData['tieneFotoRegistrada'] = True
                self.save_user_data()
                messagebox.showinfo("Éxito", "Rostro registrado y guardado correctamente")
            except Exception as e:
                try:
                    messagebox.showerror("Error", f"No se pudo guardar el rostro: {e}")
                except Exception:
                    pass
        except Exception as e:
            try:
                messagebox.showerror("Error", f"Ocurrió un error al registrar el rostro: {e}")
            except Exception:
                pass
    
    def saveChanges(self):
        """Guarda los cambios realizados"""
        # Guardar todos los cambios hechos en userData
        try:
            self.save_user_data()
            # Cerrar la ventana actual y abrir la pantalla de dificultad
            try:
                # destruir ventana Tk
                try:
                    self.root.destroy()
                except Exception:
                    pass

                # Ejecutar el script de pantalla de dificultad directamente
                import runpy, os
                pd_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'juego', 'pantallaDificultad.py'))
                if os.path.exists(pd_path):
                    runpy.run_path(pd_path, run_name='__main__')
            except Exception as e:
                print(f"No se pudo abrir la pantalla de dificultad: {e}")
        except Exception:
            # ensure feedback even if save fails
            messagebox.showinfo("Guardar", "Los cambios han sido guardados correctamente")
    
    def changeProfilePhoto(self):
        """Permite cambiar la foto de perfil"""
        filename = filedialog.askopenfilename(
            title="Seleccionar imagen de perfil",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        
        if filename:
            try:
                img = Image.open(filename)
                
                # Recortar la imagen al centro en forma cuadrada
                width, height = img.size
                if width > height:
                    left = (width - height) // 2
                    top = 0
                    right = left + height
                    bottom = height
                else:
                    left = 0
                    top = (height - width) // 2
                    right = width
                    bottom = top + width
                
                img = img.crop((left, top, right, bottom))
                
                # Redimensionar a 100x100
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                
                # Convertir a RGB si es necesario
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Crear máscara circular
                mask = Image.new('L', (100, 100), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse([0, 0, 100, 100], fill=255)
                
                # Crear imagen de salida circular con fondo del color de página
                img_rgba = img.convert('RGBA')
                out = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
                # usar la máscara para pegar la imagen circular
                out.paste(img_rgba, (0, 0), mask)

                # Componer sobre fondo del color de la página para evitar borde blanco
                try:
                    bg_color = self.bg_color if hasattr(self, 'bg_color') and self.bg_color else '#FFFFFF'
                except Exception:
                    bg_color = '#FFFFFF'
                final_img = Image.new('RGB', (100, 100), bg_color)
                final_img.paste(out, (0, 0), out.split()[-1])

                # Dibujar borde suave (mismo color que el fondo) para integrarlo
                try:
                    draw = ImageDraw.Draw(final_img)
                    outline_width = max(2, int(min(100, 100) * 0.04))
                    draw.ellipse([outline_width//2, outline_width//2, 100 - (outline_width//2) - 1, 100 - (outline_width//2) - 1], outline=bg_color, width=outline_width)
                except Exception:
                    pass

                self.profileImage = ImageTk.PhotoImage(final_img)
                
                # Actualizar la imagen
                # Asegurarnos de tener username (leer session_user.json si hace falta)
                if not self.userData.get('username'):
                    try:
                        session_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataBase', 'session_user.json')
                        if os.path.exists(session_file):
                            with open(session_file, 'r', encoding='utf-8') as sf:
                                sdata = json.load(sf)
                                self.userData['username'] = sdata.get('usuario') or sdata.get('username') or self.userData.get('username')
                    except Exception:
                        pass

                # Guardar la imagen en dataBase/imagenes/<username>.png
                try:
                    repo_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
                    img_dir = os.path.join(repo_root, 'dataBase', 'imagenes')
                    os.makedirs(img_dir, exist_ok=True)
                    username = self.userData.get('username') or self.userData.get('usuario') or 'user'
                    img_filename = f"{username}.png"
                    img_path = os.path.join(img_dir, img_filename)
                    # Guardar la imagen final sin alpha sobre fondo del color de la página
                    try:
                        final_img.save(img_path, format='PNG')
                    except Exception:
                        # fallback a salvar el RGBA si final_img no existe
                        out.save(img_path, format='PNG')
                    # Guardar ruta relativa en userData
                    rel_path = os.path.join('dataBase', 'imagenes', img_filename)
                    self.userData['rutaFoto'] = rel_path
                    self.userData['foto'] = rel_path
                except Exception:
                    pass

                if self.updateProfileImage():
                    self.userData['tieneFotoRegistrada'] = True
                    self.save_user_data()
                    
                messagebox.showinfo("Éxito", "Foto de perfil actualizada")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen: {str(e)}")
    
    def updateProfileImage(self):
        """Actualiza la imagen de perfil y retorna True si se actualizó"""
        try:
            if hasattr(self, 'profileLabel'):
                self.profileLabel.config(image=self.profileImage)
                # mantener referencia para evitar garbage collection
                try:
                    self.profileLabel.image = self.profileImage
                except Exception:
                    pass
                return True
        except Exception:
            pass
        return False

# Crear ventana principal
if __name__ == "__main__":
    root = tk.Tk()
    app = userProfilePage(root)
    root.mainloop()