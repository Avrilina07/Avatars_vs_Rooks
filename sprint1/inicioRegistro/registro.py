"""Sistema de registro con reconocimiento facial y selector de banderas"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from inicioRegistro import app_state
from tkcalendar import Calendar
from datetime import datetime
import re
import json
import os
import bcrypt
from cryptography.fernet import Fernet
import numpy as np
import io
import base64
import cv2
from PIL import Image, ImageTk

class SistemaSeguridad:
    """Clase para manejar la encriptación y hashing de datos"""
    
    def __init__(self):
        # clave.key is now in dataBase folder
        repo_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
        self.archivoClave = os.path.join(repo_root, 'dataBase', 'clave.key')
        self.inicializarEncriptacion()
    
    def inicializarEncriptacion(self):
        """Crea o carga la clave de encriptación"""
        if os.path.exists(self.archivoClave):
            with open(self.archivoClave, 'rb') as f:
                clave = f.read()
        else:
            clave = Fernet.generate_key()
            with open(self.archivoClave, 'wb') as f:
                f.write(clave)
        
        self.cipher = Fernet(clave)
    
    def hashContrasena(self, contrasena):
        """Convierte la contraseña en un hash irreversible"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(contrasena.encode('utf-8'), salt).decode('utf-8')
    
    def verificarContrasena(self, contrasena, hashGuardado):
        """Verifica si la contraseña coincide con el hash"""
        return bcrypt.checkpw(contrasena.encode('utf-8'), hashGuardado.encode('utf-8'))
    
    def encriptar(self, dato):
        """Encripta datos sensibles (reversible)"""
        if dato and dato.strip():
            return self.cipher.encrypt(dato.encode()).decode()
        return ""
    
    def desencriptar(self, datoEncriptado):
        """Desencripta datos sensibles"""
        if datoEncriptado:
            return self.cipher.decrypt(datoEncriptado.encode()).decode()
        return ""


class RegistroUsuario:
    def __init__(self, root, selected_language=None):
        self.root = root
        # if caller gave a language key, persist it to shared app state
        try:
            if selected_language:
                app_state.set_selected_language(selected_language)
        except Exception:
            pass
        # load translations
        try:
            with open(os.path.join(os.path.dirname(__file__), 'idiomas.json'), 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except Exception:
            self.translations = {"Español": {}}
        # default language: prefer shared app state if present
        try:
            self.lang = app_state.get_selected_language() or 'Español'
        except Exception:
            self.lang = selected_language or 'Español'
        self._t = lambda key: self.translations.get(self.lang, {}).get(key, key)

        # start fullscreen and keep content centered
        try:
            self.root.attributes('-fullscreen', True)
            self._fullscreen = True
        except Exception:
            try:
                self.root.state('zoomed')
                self._fullscreen = True
            except Exception:
               self.root.geometry("500x700")
               self._fullscreen = False
        # allow resize so toggling fullscreen works
        try:
            self.root.resizable(True, True)
        except Exception:
            pass
        # bind keys: F11 toggles fullscreen; Escape exits fullscreen and minimizes
        try:
            self.root.bind('<F11>', lambda e: self._toggle_fullscreen())
            self.root.bind('<Escape>', lambda e: self._exit_fullscreen_and_minimize())
        except Exception:
            pass

        # Inicializar sistema de seguridad
        self.seguridad = SistemaSeguridad()
        
        # Cargar banderas
        self.flags = {}
        self.load_flags()
        
        # usuarios.json is now in dataBase folder (project root)
        self.archivoUsuarios = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'dataBase', 'usuarios.json'))
        # temporary storage for a captured face encoding (encrypted string)
        self.capturedFace = None
        # temporary storage for a selected/taken profile image (bytes) and ext
        self.pending_profile_image = None
        self.pending_profile_image_ext = None
        self.profile_selected_label = None

        # Outer frame y main_frame centrado (como en login.py) para fullscreen
        outer = tk.Frame(self.root, bg='#B41214')
        outer.pack(fill='both', expand=True)
        self.main_frame = tk.Frame(outer, bg='#B41214', padx=20, pady=20)
        # colocar el frame en el centro de la ventana
        try:
            self.main_frame.place(relx=0.5, rely=0.5, anchor='center')
        except Exception:
            # fallback a pack si place no funciona en alguna plataforma
            self.main_frame.pack(expand=True, fill='both')
        # mantener compatibilidad con el resto del código que usa mainFrame
        mainFrame = self.main_frame

        # asegurar que al redimensionar la ventana el frame permanezca centrado
        def _keep_center(event=None):
            try:
                self.main_frame.place_configure(relx=0.5, rely=0.5)
            except Exception:
                pass
        try:
            self.root.bind('<Configure>', _keep_center)
        except Exception:
            pass
        
        # Título (centrado)
        titulo = tk.Label(mainFrame, text=self._t('tituloRegistro'), font=("Arial", 14, "bold"), bg='#B41214')
        titulo.pack(pady=(0, 20), fill='x')
        titulo.config(anchor='center')

        # Botón para ir a inicio de sesión
        btnLoginTop = tk.Button(mainFrame, text=self.translations.get(self.lang, {}).get('loginButton', 'Inicio de sesión'),
                                command=lambda: self.irInicioSesion(None), bg='#FFFFFF', fg='black')
        btnLoginTop.pack(pady=(0, 10))

        # Frame para nombre y apellidos
        frameNombreApellido = tk.Frame(mainFrame)
        frameNombreApellido.pack(pady=5)

        self.entryNombre = tk.Entry(frameNombreApellido, width=18, justify='center')
        self.entryNombre.pack(side=tk.LEFT, padx=5)
        self.entryNombre.insert(0, self._t('firstName'))
        self.entryNombre.bind('<FocusIn>', lambda e: self.limpiarPlaceholder(e, self._t('firstName')))

        self.entryApellidos = tk.Entry(frameNombreApellido, width=20, justify='center')
        self.entryApellidos.pack(side=tk.LEFT, padx=5)
        self.entryApellidos.insert(0, self._t('lastName'))
        self.entryApellidos.bind('<FocusIn>', lambda e: self.limpiarPlaceholder(e, self._t('lastName')))

        # Nombre de usuario + botón de foto (menú)
        frameUsuario = tk.Frame(mainFrame, bg='#B41214')
        frameUsuario.pack(pady=5)

        self.entryUsuario = tk.Entry(frameUsuario, width=28, justify='center')
        self.entryUsuario.pack(side=tk.LEFT, padx=(0, 5))
        self.entryUsuario.insert(0, self._t('username'))
        self.entryUsuario.bind('<FocusIn>', lambda e: self.limpiarPlaceholder(e, self._t('username')))

        # Single Menubutton that expands into Upload / Take Photo
        photo_label = self.translations.get(self.lang, {}).get('photoButtonLabel', 'Foto')
        self.photo_menubutton = tk.Menubutton(frameUsuario, text=photo_label, relief=tk.RAISED)
        photo_menu = tk.Menu(self.photo_menubutton, tearoff=0)
        upload_label = self.translations.get(self.lang, {}).get('uploadPhotoButton', 'Subir foto')
        take_label = self.translations.get(self.lang, {}).get('takePhotoButton', 'Tomar foto')
        photo_menu.add_command(label=upload_label, command=self.seleccionarFoto)
        photo_menu.add_command(label=take_label, command=self.tomarFoto)
        self.photo_menubutton.config(menu=photo_menu)
        self.photo_menubutton.pack(side=tk.LEFT)

        # small status label next to the button
        self.profile_selected_label = tk.Label(frameUsuario, text='', bg='#B41214')
        self.profile_selected_label.pack(side=tk.LEFT, padx=(6,0))

        # Correo electrónico
        self.entryEmail = tk.Entry(mainFrame, width=35, justify='center')
        self.entryEmail.pack(pady=5)
        self.entryEmail.insert(0, self._t('emailPlaceholder'))
        self.entryEmail.bind('<FocusIn>', lambda e: self.limpiarPlaceholder(e, self._t('emailPlaceholder')))

        # Contraseña
        framePass = tk.Frame(mainFrame)
        framePass.pack(pady=5)

        self.entryContrasena = tk.Entry(framePass, width=33, show="*", justify='center')
        self.entryContrasena.pack(side=tk.LEFT)
        self.entryContrasena.insert(0, self._t('password'))
        self.entryContrasena.bind('<FocusIn>', lambda e: self.activarPassword(e, self.entryContrasena))

        self.mostrarPass1 = False
        self.btnMostrar1 = tk.Button(framePass, text="👁", command=lambda: self.togglePassword(self.entryContrasena, 1))
        self.btnMostrar1.pack(side=tk.LEFT, padx=2)

        # Confirmar contraseña
        framePass2 = tk.Frame(mainFrame)
        framePass2.pack(pady=5)

        self.entryConfirmar = tk.Entry(framePass2, width=33, show="*", justify='center')
        self.entryConfirmar.pack(side=tk.LEFT)
        self.entryConfirmar.insert(0, self._t('confirmPassword'))
        self.entryConfirmar.bind('<FocusIn>', lambda e: self.activarPassword(e, self.entryConfirmar))

        self.mostrarPass2 = False
        self.btnMostrar2 = tk.Button(framePass2, text="👁", command=lambda: self.togglePassword(self.entryConfirmar, 2))
        self.btnMostrar2.pack(side=tk.LEFT, padx=2)

        # Etiqueta de requisitos de contraseña
        self.labelRequisitos = tk.Label(mainFrame, text=self._t('passwordRequirements'), 
                                        font=("Arial", 8), fg="gray")
        self.labelRequisitos.pack()

        # Fecha de nacimiento
        frameFecha = tk.Frame(mainFrame)
        frameFecha.pack(pady=10)

        tk.Label(frameFecha, text=self._t('birthdateLabel')).pack(side=tk.LEFT, padx=5)
        self.entryFecha = tk.Entry(frameFecha, width=15, justify='center')
        self.entryFecha.pack(side=tk.LEFT)
        self.entryFecha.insert(0, self._t('birthdate'))
        self.entryFecha.bind('<FocusIn>', lambda e: self.limpiarPlaceholder(e, self._t('birthdate')))
        tk.Button(frameFecha, text="📅", command=self.mostrarCalendario).pack(side=tk.LEFT, padx=5)

        # Número de teléfono CON BANDERA
        frameTelefono = tk.Frame(mainFrame, bg='#B41214')
        frameTelefono.pack(pady=5)

        # Label para mostrar la bandera
        self.flag_label = tk.Label(frameTelefono, bg='#B41214')
        self.flag_label.pack(side=tk.LEFT, padx=(0, 5))

        self.comboPrefijo = ttk.Combobox(frameTelefono, width=20, state="readonly")
        self.comboPrefijo.pack(side=tk.LEFT, padx=5)
        self.comboPrefijo['values'] = (
            "+93 Afganistán", "+355 Albania", "+49 Alemania", "+376 Andorra", "+244 Angola",
            "+1-268 Antigua y Barbuda", "+966 Arabia Saudita", "+213 Argelia", "+54 Argentina",
            "+374 Armenia", "+61 Australia", "+43 Austria", "+994 Azerbaiyán", "+1-242 Bahamas",
            "+880 Bangladés", "+1-246 Barbados", "+973 Baréin", "+32 Bélgica", "+501 Belice",
            "+229 Benín", "+375 Bielorrusia", "+591 Bolivia", "+387 Bosnia y Herzegovina",
            "+267 Botsuana", "+55 Brasil", "+673 Brunéi", "+359 Bulgaria", "+226 Burkina Faso",
            "+257 Burundi", "+975 Bután", "+238 Cabo Verde", "+855 Camboya", "+237 Camerún",
            "+1 Canadá", "+974 Catar", "+235 Chad", "+56 Chile", "+86 China", "+357 Chipre",
            "+57 Colombia", "+269 Comoras", "+850 Corea del Norte", "+82 Corea del Sur",
            "+506 Costa Rica", "+225 Costa de Marfil", "+385 Croacia", "+53 Cuba",
            "+45 Dinamarca", "+1-767 Dominica", "+593 Ecuador", "+20 Egipto", "+503 El Salvador",
            "+971 Emiratos Árabes Unidos", "+291 Eritrea", "+421 Eslovaquia", "+386 Eslovenia",
            "+34 España", "+1 Estados Unidos", "+372 Estonia", "+251 Etiopía", "+63 Filipinas",
            "+358 Finlandia", "+679 Fiyi", "+33 Francia", "+241 Gabón", "+220 Gambia",
            "+995 Georgia", "+233 Ghana", "+30 Grecia", "+1-473 Granada", "+502 Guatemala",
            "+224 Guinea", "+240 Guinea Ecuatorial", "+245 Guinea-Bisáu", "+592 Guyana",
            "+509 Haití", "+504 Honduras", "+36 Hungría", "+91 India", "+62 Indonesia",
            "+964 Irak", "+98 Irán", "+353 Irlanda", "+354 Islandia", "+972 Israel",
            "+39 Italia", "+1-876 Jamaica", "+81 Japón", "+962 Jordania", "+7 Kazajistán",
            "+254 Kenia", "+996 Kirguistán", "+686 Kiribati", "+965 Kuwait", "+856 Laos",
            "+266 Lesoto", "+371 Letonia", "+961 Líbano", "+231 Liberia", "+218 Libia",
            "+423 Liechtenstein", "+370 Lituania", "+352 Luxemburgo", "+389 Macedonia del Norte",
            "+261 Madagascar", "+60 Malasia", "+265 Malaui", "+960 Maldivas", "+223 Malí",
            "+356 Malta", "+212 Marruecos", "+692 Islas Marshall", "+230 Mauricio",
            "+222 Mauritania", "+52 México", "+691 Micronesia", "+373 Moldavia", "+377 Mónaco",
            "+976 Mongolia", "+382 Montenegro", "+258 Mozambique", "+95 Birmania",
            "+264 Namibia", "+674 Nauru", "+977 Nepal", "+505 Nicaragua", "+227 Níger",
            "+234 Nigeria", "+47 Noruega", "+64 Nueva Zelanda", "+968 Omán", "+31 Países Bajos",
            "+92 Pakistán", "+680 Palaos", "+507 Panamá", "+675 Papúa Nueva Guinea",
            "+595 Paraguay", "+51 Perú", "+48 Polonia", "+351 Portugal", "+44 Reino Unido",
            "+236 República Centroafricana", "+420 República Checa",
            "+243 República Democrática del Congo", "+1-809 República Dominicana", "+250 Ruanda",
            "+40 Rumania", "+7 Rusia", "+685 Samoa", "+378 San Marino",
            "+1-784 San Vicente y las Granadinas", "+239 Santo Tomé y Príncipe", "+221 Senegal",
            "+381 Serbia", "+248 Seychelles", "+232 Sierra Leona", "+65 Singapur", "+963 Siria",
            "+252 Somalia", "+94 Sri Lanka", "+27 Sudáfrica", "+249 Sudán", "+211 Sudán del Sur",
            "+46 Suecia", "+41 Suiza", "+597 Surinam", "+66 Tailandia", "+886 Taiwán",
            "+255 Tanzania", "+992 Tayikistán", "+670 Timor Oriental", "+228 Togo", "+676 Tonga",
            "+1-868 Trinidad y Tobago", "+216 Túnez", "+993 Turkmenistán", "+90 Turquía",
            "+688 Tuvalu", "+380 Ucrania", "+256 Uganda", "+598 Uruguay", "+998 Uzbekistán",
            "+678 Vanuatu", "+379 Ciudad del Vaticano", "+58 Venezuela", "+84 Vietnam",
            "+967 Yemen", "+253 Yibuti", "+260 Zambia", "+263 Zimbabue"
        )
        self.comboPrefijo.set(self._t('selectCountry'))
        
        # Vincular evento de selección para mostrar bandera
        self.comboPrefijo.bind('<<ComboboxSelected>>', self.on_country_select)

        self.entryTelefono = tk.Entry(frameTelefono, width=20, justify='center')
        self.entryTelefono.pack(side=tk.LEFT)
        self.entryTelefono.insert(0, self._t('phonePlaceholder'))
        self.entryTelefono.bind('<FocusIn>', lambda e: self.limpiarPlaceholder(e, self._t('phonePlaceholder')))

        # Pregunta de seguridad (alineada)
        frameSeguridad = tk.Frame(mainFrame)
        frameSeguridad.pack(pady=10, fill='x')

        # load question values from translations so they update with language
        q1 = self._t('sec_q_1')
        q2 = self._t('sec_q_2')
        q3 = self._t('sec_q_3')
        values = [v for v in (q1, q2, q3) if v]

        # Only show the combobox (dropdown) and the response entry side by side
        self.comboPregunta = ttk.Combobox(frameSeguridad, width=36, state="readonly", values=values)
        self.comboPregunta.pack(side=tk.LEFT, padx=(0,6))
        self.comboPregunta.set(self._t('securityQuestionPlaceholder'))

        self.entryRespuesta = tk.Entry(frameSeguridad, width=22, justify='center')
        self.entryRespuesta.pack(side=tk.LEFT, padx=6)
        self.entryRespuesta.insert(0, self._t('securityAnswerPlaceholder'))
        self.entryRespuesta.bind('<FocusIn>', lambda e: self.limpiarPlaceholder(e, self._t('securityAnswerPlaceholder')))

        # Datos de tarjeta (opcional)
        tk.Label(mainFrame, text=self._t('optionalCardData'), font=("Arial", 10), bg='#B41214').pack(pady=(15, 5))

        frameTarjeta = tk.Frame(mainFrame, bg='#B41214')
        frameTarjeta.pack(pady=5)

        self.entryTarjeta = tk.Entry(frameTarjeta, width=20, justify='center')
        self.entryTarjeta.pack(side=tk.LEFT, padx=5)
        self.entryTarjeta.insert(0, self._t('cardNumber'))
        self.entryTarjeta.bind('<FocusIn>', lambda e: self.limpiarPlaceholder(e, self._t('cardNumber')))

        self.entryMmaa = tk.Entry(frameTarjeta, width=8, justify='center')
        self.entryMmaa.pack(side=tk.LEFT, padx=5)
        self.entryMmaa.insert(0, self._t('cardExp'))
        self.entryMmaa.bind('<FocusIn>', lambda e: self.limpiarPlaceholder(e, self._t('cardExp')))

        self.entryCvc = tk.Entry(frameTarjeta, width=8, justify='center')
        self.entryCvc.pack(side=tk.LEFT, padx=5)
        self.entryCvc.insert(0, self._t('cardCVC'))
        self.entryCvc.bind('<FocusIn>', lambda e: self.limpiarPlaceholder(e, self._t('cardCVC')))

        # Botones
        frameBotones = tk.Frame(mainFrame, bg='#B41214')
        frameBotones.pack(pady=20)

        btnRegistrar = tk.Button(frameBotones, text=self._t('registerButton'), command=self.registrar, 
                      bg="#4CAF50", fg="white", padx=20, pady=5)
        btnRegistrar.pack(side=tk.LEFT, padx=10)

        btnInicio = tk.Button(frameBotones, text=self._t('registerFaceButton'), command=self.registrarRostro,
                      fg="blue", relief=tk.FLAT)
        btnInicio.pack(side=tk.LEFT)

    def load_flags(self):
        """Carga todas las banderas desde la carpeta bandera_paises"""
        # Mapeo de países a códigos ISO
        country_to_code = {
            "Afganistán": "AF", "Albania": "AL", "Alemania": "DE", "Andorra": "AD",
            "Angola": "AO", "Antigua y Barbuda": "AG", "Arabia Saudita": "SA",
            "Argelia": "DZ", "Argentina": "AR", "Armenia": "AM", "Australia": "AU",
            "Austria": "AT", "Azerbaiyán": "AZ", "Bahamas": "BS", "Bangladés": "BD",
            "Barbados": "BB", "Baréin": "BH", "Bélgica": "BE", "Belice": "BZ",
            "Benín": "BJ", "Bielorrusia": "BY", "Bolivia": "BO", 
            "Bosnia y Herzegovina": "BA", "Botsuana": "BW", "Brasil": "BR",
            "Brunéi": "BN", "Bulgaria": "BG", "Burkina Faso": "BF", "Burundi": "BI",
            "Bután": "BT", "Cabo Verde": "CV", "Camboya": "KH", "Camerún": "CM",
            "Canadá": "CA", "Catar": "QA", "Chad": "TD", "Chile": "CL", "China": "CN",
            "Chipre": "CY", "Colombia": "CO", "Comoras": "KM", 
            "Corea del Norte": "KP", "Corea del Sur": "KR", "Costa Rica": "CR",
            "Costa de Marfil": "CI", "Croacia": "HR", "Cuba": "CU", "Dinamarca": "DK",
            "Dominica": "DM", "Ecuador": "EC", "Egipto": "EG", "El Salvador": "SV",
            "Emiratos Árabes Unidos": "AE", "Eritrea": "ER", "Eslovaquia": "SK",
            "Eslovenia": "SI", "España": "ES", "Estados Unidos": "US", "Estonia": "EE",
            "Etiopía": "ET", "Filipinas": "PH", "Finlandia": "FI", "Fiyi": "FJ",
            "Francia": "FR", "Gabón": "GA", "Gambia": "GM", "Georgia": "GE",
            "Ghana": "GH", "Grecia": "GR", "Granada": "GD", "Guatemala": "GT",
            "Guinea": "GN", "Guinea Ecuatorial": "GQ", "Guinea-Bisáu": "GW",
            "Guyana": "GY", "Haití": "HT", "Honduras": "HN", "Hungría": "HU",
            "India": "IN", "Indonesia": "ID", "Irak": "IQ", "Irán": "IR",
            "Irlanda": "IE", "Islandia": "IS", "Israel": "IL", "Italia": "IT",
            "Jamaica": "JM", "Japón": "JP", "Jordania": "JO", "Kazajistán": "KZ",
            "Kenia": "KE", "Kirguistán": "KG", "Kiribati": "KI", "Kuwait": "KW",
            "Laos": "LA", "Lesoto": "LS", "Letonia": "LV", "Líbano": "LB",
            "Liberia": "LR", "Libia": "LY", "Liechtenstein": "LI", "Lituania": "LT",
            "Luxemburgo": "LU", "Macedonia del Norte": "MK", "Madagascar": "MG",
            "Malasia": "MY", "Malaui": "MW", "Maldivas": "MV", "Malí": "ML",
            "Malta": "MT", "Marruecos": "MA", "Islas Marshall": "MH",
            "Mauricio": "MU", "Mauritania": "MR", "México": "MX", "Micronesia": "FM",
            "Moldavia": "MD", "Mónaco": "MC", "Mongolia": "MN", "Montenegro": "ME",
            "Mozambique": "MZ", "Birmania": "MM", "Namibia": "NA", "Nauru": "NR",
            "Nepal": "NP", "Nicaragua": "NI", "Níger": "NE", "Nigeria": "NG",
            "Noruega": "NO", "Nueva Zelanda": "NZ", "Omán": "OM", "Países Bajos": "NL",
            "Pakistán": "PK", "Palaos": "PW", "Panamá": "PA", 
            "Papúa Nueva Guinea": "PG", "Paraguay": "PY", "Perú": "PE",
            "Polonia": "PL", "Portugal": "PT", "Reino Unido": "GB",
            "República Centroafricana": "CF", "República Checa": "CZ",
            "República Democrática del Congo": "CD", "República Dominicana": "DO",
            "Ruanda": "RW", "Rumania": "RO", "Rusia": "RU", "Samoa": "WS",
            "San Marino": "SM", "San Vicente y las Granadinas": "VC",
            "Santo Tomé y Príncipe": "ST", "Senegal": "SN", "Serbia": "RS",
            "Seychelles": "SC", "Sierra Leona": "SL", "Singapur": "SG", "Siria": "SY",
            "Somalia": "SO", "Sri Lanka": "LK", "Sudáfrica": "ZA", "Sudán": "SD",
            "Sudán del Sur": "SS", "Suecia": "SE", "Suiza": "CH", "Surinam": "SR",
            "Tailandia": "TH", "Taiwán": "TW", "Tanzania": "TZ", "Tayikistán": "TJ",
            "Timor Oriental": "TL", "Togo": "TG", "Tonga": "TO",
            "Trinidad y Tobago": "TT", "Túnez": "TN", "Turkmenistán": "TM",
            "Turquía": "TR", "Tuvalu": "TV", "Ucrania": "UA", "Uganda": "UG",
            "Uruguay": "UY", "Uzbekistán": "UZ", "Vanuatu": "VU",
            "Ciudad del Vaticano": "VA", "Venezuela": "VE", "Vietnam": "VN",
            "Yemen": "YE", "Yibuti": "DJ", "Zambia": "ZM", "Zimbabue": "ZW"
        }
        
        self.country_to_code = country_to_code
        
        # Ruta a la carpeta de banderas (ajustada a banderas_paises)
        flags_dir = os.path.join(os.path.dirname(__file__), '..', 'banderas_paises')
        
        try:
            for country, code in country_to_code.items():
                flag_path = os.path.join(flags_dir, f"{code}.png")
                if os.path.exists(flag_path):
                    try:
                        img = Image.open(flag_path)
                        # Redimensionar a 24x16 píxeles (proporción típica de banderas)
                        img = img.resize((24, 16), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        self.flags[country] = photo
                    except Exception as e:
                        print(f"Error cargando bandera {code}: {e}")
        except Exception as e:
            print(f"Error cargando banderas: {e}")
    
    def on_country_select(self, event=None):
        """Muestra la bandera del país seleccionado"""
        try:
            selection = self.comboPrefijo.get()
            # Extraer el nombre del país (después del código de teléfono)
            if ' ' in selection:
                country = ' '.join(selection.split(' ')[1:])
                if country in self.flags:
                    self.flag_label.config(image=self.flags[country])
                else:
                    self.flag_label.config(image='')
        except Exception as e:
            print(f"Error mostrando bandera: {e}")
    
    def limpiarPlaceholder(self, event, placeholder):
        if event.widget.get() == placeholder:
            event.widget.delete(0, tk.END)
    
    def activarPassword(self, event, entry):
        placeholders = ["Contraseña", "Confirmar contraseña"]
        if entry.get() in placeholders:
            entry.delete(0, tk.END)
            entry.config(show="*")
    
    def togglePassword(self, entry, num):
        if num == 1:
            self.mostrarPass1 = not self.mostrarPass1
            entry.config(show="" if self.mostrarPass1 else "*")
            try:
                if hasattr(self, 'btnMostrar1'):
                    self.btnMostrar1.config(text='🙈' if self.mostrarPass1 else '👁')
            except Exception:
                pass
        else:
            self.mostrarPass2 = not self.mostrarPass2
            entry.config(show="" if self.mostrarPass2 else "*")
            try:
                if hasattr(self, 'btnMostrar2'):
                    self.btnMostrar2.config(text='🙈' if self.mostrarPass2 else '👁')
            except Exception:
                pass
    
    def _toggle_fullscreen(self, state=None):
        """Toggle fullscreen (F11) or set explicit state (Escape sets False)."""
        try:
            if state is None:
                self._fullscreen = not getattr(self, '_fullscreen', False)
            else:
                self._fullscreen = bool(state)
            try:
                self.root.attributes('-fullscreen', self._fullscreen)
            except Exception:
                try:
                    self.root.state('zoomed' if self._fullscreen else 'normal')
                except Exception:
                    pass
        except Exception:
            pass
    
    def mostrarCalendario(self):
        """Abre una ventana con un calendario para seleccionar la fecha"""
        ventanaCal = tk.Toplevel(self.root)
        ventanaCal.title(self._t('selectDateWindowTitle'))
        ventanaCal.geometry("300x300")
        ventanaCal.resizable(False, False)
        
        ventanaCal.transient(self.root)
        ventanaCal.grab_set()
        
        from datetime import date
        today = date.today()
        try:
            max_date = today.replace(year=today.year - 11)
        except Exception:
            max_date = today.replace(year=today.year - 11, day=28)

        cal = Calendar(ventanaCal, selectmode='day', 
                      year=max_date.year, month=max_date.month, day=max_date.day,
                      date_pattern='dd/mm/yyyy', maxdate=max_date)
        cal.pack(pady=20, padx=20)
        
        def seleccionarFecha():
            fechaSeleccionada = cal.get_date()
            self.entryFecha.delete(0, tk.END)
            self.entryFecha.insert(0, fechaSeleccionada)
            ventanaCal.destroy()
        
        btnSeleccionar = tk.Button(ventanaCal, text=self._t('selectButton'), 
                    command=seleccionarFecha,
                    bg="#4CAF50", fg="white", padx=20, pady=5)
        btnSeleccionar.pack(pady=10)
    
    def validarEmail(self, email):
        """Valida que el email tenga un formato correcto"""
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return re.match(patron, email) is not None

    def validarContrasena(self, contrasena):
        """Valida que la contraseña cumpla con los requisitos"""
        if len(contrasena) < 8:
            return False, self._t('passwordTooShort')
        
        if not re.search(r'[a-zA-Z]', contrasena):
            return False, self._t('passwordNeedsLetter')
        
        if not re.search(r'[0-9]', contrasena):
            return False, self._t('passwordNeedsNumber')
        
        if not re.match(r'^[a-zA-Z0-9]+$', contrasena):
            return False, self._t('passwordInvalidChars')
        
        return True, "Contraseña válida"
    
    def usuarioExiste(self, usuario):
        """Verifica si el usuario ya existe en el archivo JSON"""
        if os.path.exists(self.archivoUsuarios):
            with open(self.archivoUsuarios, 'r', encoding='utf-8') as f:
                try:
                    usuarios = json.load(f)
                    for u in usuarios:
                        u_usuario = (u.get('usuario') or u.get('username') or '').lower()
                        if u_usuario and u_usuario == (usuario or '').lower():
                            return True
                except json.JSONDecodeError:
                    return False
        return False

    def updateLanguage(self, lang_key=None):
        """Refresh UI strings that depend on the current language"""
        try:
            if lang_key:
                self.lang = lang_key
            try:
                q1 = self._t('sec_q_1')
                q2 = self._t('sec_q_2')
                q3 = self._t('sec_q_3')
                values = [v for v in (q1, q2, q3) if v]
                if hasattr(self, 'comboPregunta'):
                    self.comboPregunta['values'] = values
                    try:
                        self.comboPregunta.set(self._t('securityQuestionPlaceholder'))
                    except Exception:
                        pass
            except Exception:
                pass

            try:
                if hasattr(self, 'labelRequisitos'):
                    self.labelRequisitos.config(text=self._t('passwordRequirements'))
            except Exception:
                pass
        except Exception:
            pass
    
    def guardarUsuario(self, datos):
        """Guarda el usuario en el archivo JSON"""
        if os.path.exists(self.archivoUsuarios):
            with open(self.archivoUsuarios, 'r', encoding='utf-8') as f:
                try:
                    usuarios = json.load(f)
                except json.JSONDecodeError:
                    usuarios = []
        else:
            usuarios = []
        
        usuarios.append(datos)
        
        with open(self.archivoUsuarios, 'w', encoding='utf-8') as f:
            json.dump(usuarios, f, indent=4, ensure_ascii=False)
    
    def registrar(self):
        """Registra un nuevo usuario con todos los datos encriptados"""
        nombre = self.entryNombre.get()
        apellidos = self.entryApellidos.get()
        usuario = self.entryUsuario.get()
        email = self.entryEmail.get()
        contrasena = self.entryContrasena.get()
        confirmar = self.entryConfirmar.get()
        fecha = self.entryFecha.get()
        prefijo = self.comboPrefijo.get()
        telefono = self.entryTelefono.get()
        pregunta = self.comboPregunta.get()
        respuesta = self.entryRespuesta.get()
        tarjeta = self.entryTarjeta.get()
        mmaa = self.entryMmaa.get()
        cvc = self.entryCvc.get()
        
        # Validaciones
        if nombre == self._t('firstName') or not nombre.strip():
            messagebox.showwarning(self._t('errorTitle'), self._t('enterName'))
            return
        
        if apellidos == self._t('lastName') or not apellidos.strip():
            messagebox.showwarning(self._t('errorTitle'), self._t('enterLastName'))
            return
        
        if usuario == self._t('username') or not usuario.strip():
            messagebox.showwarning(self._t('errorTitle'), self._t('enterUsername'))
            return
        
        if self.usuarioExiste(usuario):
            messagebox.showwarning(self._t('errorTitle'), self._t('usernameTaken'))
            return
        
        if email == self._t('emailPlaceholder') or not email.strip():
            messagebox.showwarning(self._t('errorTitle'), self._t('enterEmail'))
            return
        
        if not self.validarEmail(email):
            messagebox.showwarning(self._t('errorTitle'), self._t('invalidEmail'))
            return
        
        if contrasena == self._t('password') or not contrasena:
            messagebox.showwarning(self._t('errorTitle'), self._t('enterPassword'))
            return
        
        valida, mensaje = self.validarContrasena(contrasena)
        if not valida:
            messagebox.showwarning(self._t('errorTitle'), mensaje)
            return
        
        if contrasena != confirmar:
            messagebox.showwarning(self._t('errorTitle'), self._t('passwordsDontMatch'))
            return
        
        if fecha == self._t('birthdate') or not fecha.strip():
            messagebox.showwarning(self._t('errorTitle'), self._t('enterBirthdate'))
            return
        
        if prefijo == self._t('selectCountry'):
            messagebox.showwarning(self._t('errorTitle'), self._t('selectCountryError'))
            return
        
        if telefono == self._t('phonePlaceholder') or not telefono.strip():
            messagebox.showwarning(self._t('errorTitle'), self._t('enterPhone'))
            return
        
        if pregunta == self._t('securityQuestionPlaceholder'):
            messagebox.showwarning(self._t('errorTitle'), self._t('selectSecurityQuestion'))
            return
        
        if respuesta == self._t('securityAnswerPlaceholder') or not respuesta.strip():
            messagebox.showwarning(self._t('errorTitle'), self._t('enterSecurityAnswer'))
            return
        
        telefonoCompleto = f"{prefijo} {telefono}"
        
        datosUsuario = {
            'nombre': nombre,
            'apellidos': apellidos,
            'usuario': usuario,
            'email': self.seguridad.encriptar(email),
            'contrasenaHash': self.seguridad.hashContrasena(contrasena),
            'fechaNacimiento': fecha,
            'telefono': self.seguridad.encriptar(telefonoCompleto),
            'preguntaSeguridad': pregunta,
            'respuestaSeguridad': self.seguridad.encriptar(respuesta),
            'personalizado': False,
            'fechaRegistro': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        
        if tarjeta != "Número de tarjeta" and tarjeta.strip():
            datosUsuario['tarjeta'] = self.seguridad.encriptar(tarjeta)
        
        if mmaa != "MM/AA" and mmaa.strip():
            datosUsuario['mmaa'] = self.seguridad.encriptar(mmaa)
        
        if cvc != "CVC" and cvc.strip():
            datosUsuario['cvc'] = self.seguridad.encriptar(cvc)
        
        try:
            if getattr(self, 'capturedFace', None):
                datosUsuario['face_enc'] = self.capturedFace
                plain_b64 = getattr(self, 'capturedFacePlain', None)
            else:
                plain_b64 = None

            if getattr(self, 'pending_profile_image', None):
                try:
                    rel_path = self._save_profile_image(usuario)
                    if rel_path:
                        datosUsuario['profile_image'] = rel_path
                except Exception as e:
                    print(f"DEBUG: error guardando imagen de perfil: {e}")

            try:
                existing = []
                if os.path.exists(self.archivoUsuarios):
                    with open(self.archivoUsuarios, 'r', encoding='utf-8') as f:
                        try:
                            existing = json.load(f)
                        except Exception:
                            existing = []
                emails = set()
                phones = set()
                for u in existing:
                    try:
                        e_raw = u.get('email') or u.get('email_encrypted') or ''
                        e = self.seguridad.desencriptar(e_raw) if e_raw else ''
                    except Exception:
                        e = e_raw or ''
                    if e:
                        emails.add(e.strip().lower())
                    try:
                        t_raw = u.get('telefono') or u.get('telefono_encrypted') or ''
                        t = self.seguridad.desencriptar(t_raw) if t_raw else ''
                    except Exception:
                        t = t_raw or ''
                    if t:
                        phones.add(t.strip())

                if email and email.strip().lower() in emails:
                    messagebox.showwarning(self._t('errorTitle'), self._t('emailTaken') if self.translations.get(self.lang, {}).get('emailTaken') else 'El correo ya está registrado')
                    return
                if telefonoCompleto and telefonoCompleto.strip() in phones:
                    messagebox.showwarning(self._t('errorTitle'), self._t('phoneTaken') if self.translations.get(self.lang, {}).get('phoneTaken') else 'El teléfono ya está registrado')
                    return

            except Exception as e:
                print(f"DEBUG: error verificando duplicados: {e}")

            self.guardarUsuario(datosUsuario)

            self.capturedFace = None
            self.pending_profile_image = None
            self.pending_profile_image_ext = None
            if self.profile_selected_label:
                try:
                    self.profile_selected_label.config(text='')
                except Exception:
                    pass

            messagebox.showinfo(self._t('successTitle'), self._t('registerSuccessMessage').format(usuario=usuario))
            self.limpiarFormulario()
        except Exception as e:
            messagebox.showerror(self._t('errorTitle'), self._t('saveErrorMessage').format(error=str(e)))
    
    def limpiarFormulario(self):
        """Limpia todos los campos del formulario"""
        self.entryNombre.delete(0, tk.END)
        self.entryNombre.insert(0, self._t('firstName'))
        
        self.entryApellidos.delete(0, tk.END)
        self.entryApellidos.insert(0, self._t('lastName'))
        
        self.entryUsuario.delete(0, tk.END)
        self.entryUsuario.insert(0, self._t('username'))
        
        self.entryEmail.delete(0, tk.END)
        self.entryEmail.insert(0, self._t('emailPlaceholder'))
        
        self.entryContrasena.delete(0, tk.END)
        self.entryContrasena.insert(0, self._t('password'))
        self.entryContrasena.config(show="*")
        
        self.entryConfirmar.delete(0, tk.END)
        self.entryConfirmar.insert(0, self._t('confirmPassword'))
        self.entryConfirmar.config(show="*")
        
        self.entryFecha.delete(0, tk.END)
        self.entryFecha.insert(0, self._t('birthdate'))
        
        self.comboPrefijo.set(self._t('selectCountry'))
        
        self.entryTelefono.delete(0, tk.END)
        self.entryTelefono.insert(0, self._t('phonePlaceholder'))
        
        self.comboPregunta.set(self._t('securityQuestionPlaceholder'))
        
        self.entryRespuesta.delete(0, tk.END)
        self.entryRespuesta.insert(0, self._t('securityAnswerPlaceholder'))
        
        self.entryTarjeta.delete(0, tk.END)
        self.entryTarjeta.insert(0, self._t('cardNumber'))
        
        self.entryMmaa.delete(0, tk.END)
        self.entryMmaa.insert(0, self._t('cardExp'))
        
        self.entryCvc.delete(0, tk.END)
        self.entryCvc.insert(0, self._t('cardCVC'))
    
    def registrarRostro(self):
        """Capture face using face_gui"""
        try:
            try:
                from inicioRegistro import face_gui
            except Exception:
                try:
                    import face_gui
                except Exception:
                    messagebox.showerror(self._t('errorTitle'), self._t('cameraUnavailable'))
                    return

            mean_face, name = face_gui.register_face_gui(return_array=True)
            if mean_face is None:
                messagebox.showwarning(self._t('errorTitle'), self._t('faceCaptureFailed'))
                return

            buf = io.BytesIO()
            np.save(buf, mean_face)
            buf.seek(0)
            raw = buf.read()
            b64 = base64.b64encode(raw).decode('ascii')

            encrypted = self.seguridad.encriptar(b64)
            self.capturedFace = encrypted

            form_user = (getattr(self, 'entryUsuario', None) and self.entryUsuario.get()) or None
            form_user = form_user if form_user and form_user != self._t('username') else None

            target_name = None
            if form_user:
                target_name = form_user
            elif name:
                target_name = name

            if target_name and self.usuarioExiste(target_name):
                try:
                    if os.path.exists(self.archivoUsuarios):
                        with open(self.archivoUsuarios, 'r', encoding='utf-8') as f:
                            usuarios = json.load(f)
                    else:
                        usuarios = []

                    updated = False
                    for u in usuarios:
                        stored = (u.get('usuario') or u.get('username') or '').lower()
                        if stored and target_name and stored == target_name.lower():
                            u['face_enc'] = encrypted
                            if 'personalizado' not in u:
                                u['personalizado'] = False
                            updated = True
                            break

                    if updated:
                        with open(self.archivoUsuarios, 'w', encoding='utf-8') as f:
                            json.dump(usuarios, f, indent=4, ensure_ascii=False)
                        messagebox.showinfo(self._t('successTitle'), self._t('faceRegisterSuccessExisting').format(usuario=target_name))
                        return
                    else:
                        self.capturedFace = encrypted
                        messagebox.showinfo(self._t('successTitle'), self._t('faceRegisterStoredForNew'))
                        return
                except Exception as e:
                    messagebox.showerror(self._t('errorTitle'), self._t('saveErrorMessage').format(error=str(e)))
                    return

            self.capturedFace = encrypted
            messagebox.showinfo(self._t('successTitle'), self._t('faceRegisterStoredForNew'))
        except Exception as e:
            try:
                messagebox.showerror(self._t('errorTitle'), self._t('saveErrorMessage').format(error=str(e)))
            except Exception:
                pass

    def seleccionarFoto(self):
        """Permite al usuario seleccionar una imagen desde el dispositivo"""
        try:
            filetypes = [
                ("Imagen", "*.png;*.jpg;*.jpeg;*.bmp"),
                ("Todos los archivos", "*")
            ]
            path = filedialog.askopenfilename(title=self._t('selectPhotoFile') if self.translations.get(self.lang, {}).get('selectPhotoFile') else 'Seleccione imagen', filetypes=filetypes)
            if not path:
                return
            with open(path, 'rb') as f:
                data = f.read()
            _, ext = os.path.splitext(path)
            ext = ext.lower().lstrip('.')
            self.pending_profile_image = data
            self.pending_profile_image_ext = ext or 'jpg'
            if self.profile_selected_label:
                self.profile_selected_label.config(text=self._t('photoSelected') if self.translations.get(self.lang, {}).get('photoSelected') else f'Foto seleccionada')
        except Exception as e:
            print(f"DEBUG: error seleccionarFoto: {e}")
            try:
                messagebox.showerror(self._t('errorTitle'), self._t('saveErrorMessage').format(error=str(e)))
            except Exception:
                pass

    def tomarFoto(self):
        """Abre la cámara y captura una foto"""
        try:
            cap = cv2.VideoCapture(0)
            if not cap or not cap.isOpened():
                try:
                    messagebox.showerror(self._t('errorTitle'), self._t('cameraUnavailable'))
                except Exception:
                    pass
                try:
                    cap.release()
                except Exception:
                    pass
                return

            cv2.namedWindow('Tomar foto - presione Espacio para capturar, q para salir')
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                cv2.imshow('Tomar foto - presione Espacio para capturar, q para salir', frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                if key == ord(' '):
                    ok, jpg = cv2.imencode('.jpg', frame)
                    if ok:
                        data = jpg.tobytes()
                        self.pending_profile_image = data
                        self.pending_profile_image_ext = 'jpg'
                        if self.profile_selected_label:
                            try:
                                self.profile_selected_label.config(text=self._t('photoCaptured') if self.translations.get(self.lang, {}).get('photoCaptured') else 'Foto capturada')
                            except Exception:
                                pass
                    break

            cap.release()
            cv2.destroyAllWindows()
        except Exception as e:
            print(f"DEBUG: error tomarFoto: {e}")
            try:
                messagebox.showerror(self._t('errorTitle'), self._t('cameraUnavailable'))
            except Exception:
                pass

    def _save_profile_image(self, usuario):
        """Save pending_profile_image bytes into user_profiles/<usuario>/profile.<ext>"""
        try:
            if not getattr(self, 'pending_profile_image', None):
                return None
            repo_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
            profiles_dir = os.path.join(repo_root, 'user_profiles')
            os.makedirs(profiles_dir, exist_ok=True)
            safe_user = re.sub(r'[^a-zA-Z0-9._-]', '_', usuario)
            user_dir = os.path.join(profiles_dir, safe_user)
            os.makedirs(user_dir, exist_ok=True)
            ext = (self.pending_profile_image_ext or 'jpg').lower()
            filename = f'profile.{ext}'
            path = os.path.join(user_dir, filename)
            with open(path, 'wb') as f:
                f.write(self.pending_profile_image)
            rel = os.path.relpath(path, repo_root)
            return rel.replace('\\', '/')
        except Exception as e:
            print(f"DEBUG: _save_profile_image error: {e}")
            return None
    
    def irInicioSesion(self, event):
        try:
            try:
                self.root.destroy()
            except Exception:
                pass
            mod = None
            try:
                import login
                mod = login
            except Exception:
                try:
                    import importlib
                    mod = importlib.import_module('inicioRegistro.login')
                except Exception:
                    try:
                        import importlib.util
                        path = os.path.join(os.path.dirname(__file__), 'login.py')
                        spec = importlib.util.spec_from_file_location('login', path)
                        if spec and spec.loader:
                            mod = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(mod)
                    except Exception as e:
                        messagebox.showerror('Error', f'No se pudo abrir Login: {e}')
                        return

            if mod is None:
                messagebox.showerror('Error', 'No se pudo cargar el módulo de login')
                return
            if hasattr(mod, 'main'):
                try:
                    mod.main()
                    return
                except Exception:
                    pass
            if hasattr(mod, 'LoginApp'):
                try:
                    root2 = tk.Tk()
                    app = mod.LoginApp(root2)
                    root2.mainloop()
                    return
                except Exception as e:
                    messagebox.showerror('Error', f'No se pudo iniciar Login: {e}')
                    return
            messagebox.showerror('Error', 'El módulo login no tiene main() ni LoginApp()')
        except Exception as e:
            messagebox.showerror('Error', f'Error al abrir inicio de sesión: {e}')


if __name__ == "__main__":
    root = tk.Tk()
    app = RegistroUsuario(root)
    root.mainloop()