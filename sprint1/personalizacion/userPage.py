import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw
import json
import os

class userProfilePage:
    def __init__(self, root):
        self.root = root
        self.root.title("Perfil de Usuario")
        self.root.geometry("450x650")
        self.root.configure(bg="white")
        
        # Cargar datos del usuario actual
        self.userData = self.load_current_user()
        self.profileImage = None
        
        self.createWidgets()

    def load_current_user(self):
        """Carga los datos del usuario actual desde la base de datos"""
        try:
            # Leer usuario actual de session_user.json
            session_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                    'dataBase', 'session_user.json')
            with open(session_file, 'r') as f:
                current_user = json.load(f)
            
            # Buscar datos completos en usuarios.json
            users_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                    'dataBase', 'usuarios.json')
            with open(users_file, 'r') as f:
                users = json.load(f)
                
            # Encontrar usuario actual
            for user in users:
                if user['username'] == current_user['username']:
                    return user
        except Exception as e:
            print(f"Error cargando datos de usuario: {e}")
            return {
                "nombre": "",
                "apellidos": "",
                "username": "",
                "correo": "",
                "fechaNacimiento": "",
                "tarjetaCredito": "",
                "cvv": "",
                "fechaCaducidad": "",
                "contrasena": "",
                "fotoRegistrada": False
            }
    def save_user_data(self):
        """Guarda los cambios del usuario en la base de datos"""
        try:
            users_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                    'dataBase', 'usuarios.json')
            
            # Leer usuarios existentes
            with open(users_file, 'r') as f:
                users = json.load(f)
            
            # Actualizar datos del usuario actual
            for user in users:
                if user['username'] == self.userData['username']:
                    user.update(self.userData)
                    break
            
            # Guardar cambios
            with open(users_file, 'w') as f:
                json.dump(users, f, indent=4)
                
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
        mainFrame = tk.Frame(self.root, bg="white")
        mainFrame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Imagen de perfil
        profileFrame = tk.Frame(mainFrame, bg="white")
        profileFrame.pack(pady=(0, 10))
        
        # Crear imagen circular
        circularImg = self.createCircularImage(100)
        self.profileImage = ImageTk.PhotoImage(circularImg)
        
        self.profileLabel = tk.Label(profileFrame, image=self.profileImage, bg="white", cursor="hand2")
        self.profileLabel.pack()
        self.profileLabel.bind("<Button-1>", lambda e: self.changeProfilePhoto())
        
        # Username (título)
        usernameLabel = tk.Label(mainFrame, text=self.userData["username"],
                                 font=("Arial", 14), bg="white", fg="#424242")
        usernameLabel.pack(pady=(5, 30))
        
        # Campos de información
        fieldsFrame = tk.Frame(mainFrame, bg="white")
        fieldsFrame.pack()
        
        # Nombre y Apellidos en una fila
        nameFrame = tk.Frame(fieldsFrame, bg="white")
        nameFrame.pack(pady=(0, 20))
        
        # Nombre
        nombreBox = tk.Frame(nameFrame, bg="white")
        nombreBox.grid(row=0, column=0, padx=(0, 40))
        tk.Label(nombreBox, text="Nombre", font=("Arial", 11), 
                bg="white", fg="#757575").pack()
        tk.Label(nombreBox, text=self.userData["nombre"], font=("Arial", 11, "bold"), 
                bg="white", fg="#212121").pack(pady=(3, 0))
        
        # Apellidos
        apellidosBox = tk.Frame(nameFrame, bg="white")
        apellidosBox.grid(row=0, column=1)
        tk.Label(apellidosBox, text="Apellidos", font=("Arial", 11), 
                bg="white", fg="#757575").pack()
        tk.Label(apellidosBox, text=self.userData["apellidos"], font=("Arial", 11, "bold"), 
                bg="white", fg="#212121").pack(pady=(3, 0))
        
        # Correo (centrado)
        correoFrame = tk.Frame(fieldsFrame, bg="white")
        correoFrame.pack(pady=(0, 20))
        tk.Label(correoFrame, text="Correo", font=("Arial", 11),
                bg="white", fg="#757575").pack()
        tk.Label(correoFrame, text=self.userData["correo"], font=("Arial", 11, "bold"),
                bg="white", fg="#212121").pack(pady=(3, 0))
        
        # Fecha de nacimiento (centrado)
        fechaFrame = tk.Frame(fieldsFrame, bg="white")
        fechaFrame.pack(pady=(0, 20))
        tk.Label(fechaFrame, text="Fecha de nacimiento", font=("Arial", 11),
                bg="white", fg="#757575").pack()
        tk.Label(fechaFrame, text=self.userData["fechaNacimiento"], font=("Arial", 11, "bold"),
                bg="white", fg="#212121").pack(pady=(3, 0))
        
        # Tarjeta de crédito con botón Editar (alineados)
        cardMainFrame = tk.Frame(fieldsFrame, bg="white")
        cardMainFrame.pack(pady=(0, 20))
        
        cardContentFrame = tk.Frame(cardMainFrame, bg="white")
        cardContentFrame.pack()
        
        # Label y valor de tarjeta
        cardLabelFrame = tk.Frame(cardContentFrame, bg="white")
        cardLabelFrame.grid(row=0, column=0, sticky="w")
        tk.Label(cardLabelFrame, text="Tarjeta de credito", font=("Arial", 11),
                bg="white", fg="#757575").pack(anchor="w")
        self.cardValueLabel = tk.Label(cardLabelFrame, text=self.getMaskedCardNumber(), 
                                       font=("Arial", 11, "bold"),
                                       bg="white", fg="#212121")
        self.cardValueLabel.pack(anchor="w", pady=(3, 0))
        
        # Botón Editar
        btnEditCard = tk.Button(cardContentFrame, text="Editar",
                               command=self.showEditCardDialog,
                               bg="white", fg="black",
                               font=("Arial", 10),
                               cursor="hand2", relief=tk.SOLID,
                               borderwidth=1, padx=18, pady=4)
        btnEditCard.grid(row=0, column=1, padx=(15, 0), sticky="e")
        
        # Contraseña con botón Editar (alineados)
        passwordMainFrame = tk.Frame(fieldsFrame, bg="white")
        passwordMainFrame.pack(pady=(0, 30))
        
        passwordContentFrame = tk.Frame(passwordMainFrame, bg="white")
        passwordContentFrame.pack()
        
        # Label y valor de contraseña
        passwordLabelFrame = tk.Frame(passwordContentFrame, bg="white")
        passwordLabelFrame.grid(row=0, column=0, sticky="w")
        tk.Label(passwordLabelFrame, text="Contraseña", font=("Arial", 11),
                bg="white", fg="#757575").pack(anchor="w")
        tk.Label(passwordLabelFrame, text="••••••••", font=("Arial", 11, "bold"),
                bg="white", fg="#212121").pack(anchor="w", pady=(3, 0))
        
        # Botón Editar
        btnEditPassword = tk.Button(passwordContentFrame, text="Editar",
                                    command=self.showChangePasswordDialog,
                                    bg="white", fg="black",
                                    font=("Arial", 10),
                                    cursor="hand2", relief=tk.SOLID,
                                    borderwidth=1, padx=18, pady=4)
        btnEditPassword.grid(row=0, column=1, padx=(15, 0), sticky="e")
        
        # Botones centrados
        buttonsFrame = tk.Frame(fieldsFrame, bg="white")
        buttonsFrame.pack()
        
        # Botón Registrar Cara
        btnRegisterFace = tk.Button(buttonsFrame, text="Registrar Cara",
                                    command=self.registerFace,
                                    bg="white", fg="black",
                                    font=("Arial", 11),
                                    cursor="hand2", relief=tk.SOLID,
                                    borderwidth=1, padx=45, pady=8)
        btnRegisterFace.pack(pady=(0, 12))
        
        # Botón Guardar Cambios
        btnSave = tk.Button(buttonsFrame, text="Guardar Cambios",
                           command=self.saveChanges,
                           bg="white", fg="black",
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
        dialog.configure(bg="white")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrar diálogo
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        contentFrame = tk.Frame(dialog, bg="white", padx=20, pady=20)
        contentFrame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(contentFrame, text="Paso 2: Ingrese los datos de su nueva tarjeta",
                font=("Arial", 11, "bold"), bg="white").pack(pady=(0, 5))
        
        tk.Label(contentFrame, text="Complete todos los campos con la información de su nueva tarjeta",
                font=("Arial", 9), bg="white", fg="#666").pack(pady=(0, 15))
        
        # Número de la tarjeta
        tk.Label(contentFrame, text="Número de la Tarjeta",
                font=("Arial", 10, "bold"), bg="white").pack(anchor="w")
        
        entryNumero = tk.Entry(contentFrame, font=("Arial", 12),
                              relief=tk.SOLID, borderwidth=1)
        entryNumero.pack(fill=tk.X, pady=(5, 15), ipady=5)
        
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
    
    def updateCardDisplay(self):
        """Actualiza la visualización de la tarjeta"""
        if hasattr(self, 'cardValueLabel'):
            self.cardValueLabel.config(text=self.getMaskedCardNumber())
        
        btnGuardar = tk.Button(buttonFrame, text="Guardar",
                              command=guardarNuevaTarjeta,
                              bg="white", fg="black",
                              font=("Arial", 10),
                              cursor="hand2", relief=tk.SOLID,
                              borderwidth=1, padx=20, pady=8)
        btnGuardar.pack(side=tk.LEFT, padx=5)
        
        btnCancelar = tk.Button(buttonFrame, text="Cancelar",
                               command=dialog.destroy,
                               bg="white", fg="black",
                               font=("Arial", 10),
                               cursor="hand2", relief=tk.SOLID,
                               borderwidth=1, padx=20, pady=8)
        btnCancelar.pack(side=tk.LEFT, padx=5)
    
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
                if self.updateProfileImage():
                    self.userData['tieneFotoRegistrada'] = True
                    self.save_user_data()
                    
                messagebox.showinfo("Éxito", "Foto de perfil actualizada")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen: {str(e)}")
    
    def updateProfileImage(self, widget):
        """Actualiza recursivamente la imagen de perfil"""
        if hasattr(self, 'profileLabel'):
            self.profileLabel.config(image=self.profileImage)

# Crear ventana principal
if __name__ == "__main__":
    root = tk.Tk()
    app = userProfilePage(root)
    root.mainloop()