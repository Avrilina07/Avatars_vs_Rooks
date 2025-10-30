import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw
import json
import os
import base64
try:
    from cryptography.fernet import Fernet
except Exception:
    Fernet = None

class userProfilePage:
    def __init__(self, root):
        self.root = root
        self.root.title("Perfil de Usuario")
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
        
        # Crear imagen circular
        # Intentar cargar foto guardada (rutaFoto / foto) si existe
        circularImg = None
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
                # ruta puede ser relativa (dataBase/imagenes/...) o absoluta
                abs_path = ruta if os.path.isabs(ruta) else os.path.normpath(os.path.join(repo_root, ruta))
                if os.path.exists(abs_path):
                    img = Image.open(abs_path).convert('RGBA')
                    # Ensure square and 100x100
                    w, h = img.size
                    if w != h:
                        if w > h:
                            left = (w - h) // 2
                            img = img.crop((left, 0, left + h, h))
                        else:
                            top = (h - w) // 2
                            img = img.crop((0, top, w, top + w))
                    img = img.resize((100, 100), Image.Resampling.LANCZOS)
                    # Ensure circular mask
                    mask = Image.new('L', (100, 100), 0)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse([0, 0, 100, 100], fill=255)
                    out = Image.new('RGBA', (100, 100), (255, 255, 255, 0))
                    out.paste(img, (0, 0), mask=img.split()[-1] if img.mode == 'RGBA' else mask)
                    out.putalpha(mask)
                    circularImg = out
        except Exception:
            circularImg = None

        if circularImg is None:
            circularImg = self.createCircularImage(100)

        # Ensure final image is RGB (no alpha) so Tkinter shows it reliably
        try:
            if circularImg.mode in ('RGBA', 'LA'):
                bg = Image.new('RGB', circularImg.size, (255, 255, 255))
                bg.paste(circularImg, mask=circularImg.split()[-1])
                final_img = bg
            else:
                final_img = circularImg.convert('RGB')
        except Exception:
            final_img = circularImg.convert('RGB')

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
        
        # Botón Editar
        btnEditCard = tk.Button(cardContentFrame, text="Editar",command=self.showEditCardDialog,
            bg=self.bg_color, fg="black", font=("Arial", 10),cursor="hand2", relief=tk.SOLID,
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
        card = self.userData["tarjetaCredito"]
        return "xxxx xxxx xxxx " + card[-4:]
    
    def showEditCardDialog(self):
        """Muestra diálogo para verificar tarjeta actual - Paso 1"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Cambiar Tarjeta - Paso 1 de 2")
        dialog.geometry("400x300")
        dialog.configure(bg="white")
        dialog.transient(self.root)
        dialog.grab_set()
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
        messagebox.showinfo("Éxito", "Tarjeta actualizada correctamente", parent=dialog)
        dialog.destroy()
    
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
        dialog.geometry("350x230")
        dialog.configure(bg="white")
        dialog.transient(self.root)
        dialog.grab_set()
        if self.validateAndUpdatePassword():
            self.save_user_data()
        
        # Centrar diálogo
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        contentFrame = tk.Frame(dialog, bg="white", padx=30, pady=30)
        contentFrame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(contentFrame, text="Paso 1: Verifique su identidad",
                font=("Arial", 11, "bold"), bg="white").pack(pady=(0, 5))
        
        tk.Label(contentFrame, text="Ingrese su contraseña actual para continuar",
                font=("Arial", 9), bg="white", fg="#666").pack(pady=(0, 15))
        
        entryActual = tk.Entry(contentFrame, font=("Arial", 12), show="•",
                              relief=tk.SOLID, borderwidth=1)
        entryActual.pack(fill=tk.X, ipady=8)
        
        def verificarYContinuar():
            if entryActual.get() == self.userData["contrasena"]:
                dialog.destroy()
                self.showNewPasswordDialog()
            else:
                messagebox.showerror("Error", "Contraseña incorrecta", parent=dialog)
        
        buttonFrame = tk.Frame(contentFrame, bg="white")
        buttonFrame.pack(pady=20)
        
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
            messagebox.showinfo("Éxito", "Contraseña actualizada correctamente", parent=dialog)
            dialog.destroy()
        
        buttonFrame = tk.Frame(contentFrame, bg="white")
        buttonFrame.pack(pady=20)
        
        btnVerificar = tk.Button(buttonFrame, text="Verificar",
                                command=verificarContrasenas,
                                bg="white", fg="black",
                                font=("Arial", 10),
                                cursor="hand2", relief=tk.SOLID,
                                borderwidth=1, padx=20, pady=8)
        btnVerificar.pack(side=tk.LEFT, padx=5)
        
        btnCancelar = tk.Button(buttonFrame, text="Cancelar",
                               command=dialog.destroy,
                               bg="white", fg="black",
                               font=("Arial", 10),
                               cursor="hand2", relief=tk.SOLID,
                               borderwidth=1, padx=20, pady=8)
        btnCancelar.pack(side=tk.LEFT, padx=5)
    
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
        """Simula el registro de cara"""
        result = messagebox.askyesno("Registrar Cara", 
                                     "¿Desea registrar su cara para el reconocimiento facial?\n\n" +
                                     "Esto permitirá un acceso más rápido y seguro.")
        if result:
            messagebox.showinfo("Éxito", 
                               "Su cara ha sido registrada correctamente.\n" +
                               "Ahora puede usar reconocimiento facial para iniciar sesión.")
            self.userData["tieneFotoRegistrada"] = True
    
    def saveChanges(self):
        """Guarda los cambios realizados"""
        # Guardar todos los cambios hechos en userData
        try:
            self.save_user_data()
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
                
                # Crear imagen de salida circular
                output = Image.new('RGB', (100, 100), (255, 255, 255))
                output.paste(img, (0, 0))
                output.putalpha(mask)
                
                self.profileImage = ImageTk.PhotoImage(output)
                
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
                    # Guardar con canal alpha
                    output.save(img_path, format='PNG')
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