import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import cv2
import numpy as np
import io
import base64
from cryptography.fernet import Fernet
import bcrypt
import traceback
import subprocess
import sys
try:
    # prefer package import when available
    from inicioRegistro import app_state
except Exception:
    # fallback to local import if run as a script
    try:
        import app_state
    except Exception:
        app_state = None


class LoginApp:
    def __init__(self, root):
        self.root = root
        # Reset transient runtime state each time the app starts
        try:
            if app_state:
                try:
                    app_state.reset_runtime_state()
                except Exception:
                    pass
        except Exception:
            pass
        self.root.title("Login")
        #fullscreen
        try:
            self.root.attributes('-fullscreen', True)
            self._fullscreen = True
        except Exception:
            try:
                self.root.state('zoomed')
                self._fullscreen = True
            except Exception:
                self.root.geometry("500x450")
                self._fullscreen = False
        self.root.configure(bg='#B41214')
        # bind keys to toggle fullscreen (Escape to exit, F11 to toggle)
        try:
            self.root.bind('<Escape>', lambda e: self._toggle_fullscreen())
            self.root.bind('<F11>', lambda e: self._toggle_fullscreen())
        except Exception:
            pass

        # state for autosave/placeholders
        self.fieldPlaceholders = {}
        self.fieldEdited = {}

        # main frame
        outer = tk.Frame(self.root, bg='#B41214')
        outer.pack(fill='both', expand=True)
        self.main_frame = tk.Frame(outer, bg='#B41214')
        self.main_frame.place(relx=0.5, rely=0.5, anchor='center')
        try:
            self.main_frame.configure(padx=20, pady=20)
        except Exception:
            pass
        # header links
        header_frame = tk.Frame(outer, bg='#B41214')
        header_frame.place(x=10, y=10, anchor='nw')

        self.helpLink = tk.Label(header_frame, text="Ayuda", fg='blue', bg='#B41214', cursor='hand2', font=('Arial', 9, 'underline'))
        self.helpLink.pack(side='left')
        self.creditsLink = tk.Label(header_frame, text="Creditos", fg='blue', bg='#B41214', cursor='hand2', font=('Arial', 9, 'underline'))
        self.creditsLink.pack(side='left', padx=(10, 0))

        # title
        self.titleLabel = tk.Label(self.main_frame, text="Inicio de Sesión", font=('Arial', 12), bg='#B41214')
        self.titleLabel.pack(pady=10)

        # helper to register widgets for autosave/placeholder behavior
        def registerWidget(widget, placeholder=None):
            wid = str(id(widget))
            if placeholder is not None:
                self.fieldPlaceholders[wid] = placeholder
            self.fieldEdited[wid] = False
            widget.bind('<Button-1>', lambda e, w=widget: self.autosaveOnClick(e, w))
            widget.bind('<FocusIn>', lambda e, w=widget, p=placeholder: self.clearPlaceholderOnFocus(e, w, p))
            widget.bind('<Key>', lambda e, w=widget: self.markEdited(w))
            if placeholder is not None:
                widget.bind('<FocusOut>', lambda e, w=widget, p=placeholder: self.restorePlaceholder(e, w, p))

        # username
        self.entryUsername = tk.Entry(self.main_frame, font=('Arial', 10), width=35)
        self.entryUsername.pack(pady=5, ipady=5)
        registerWidget(self.entryUsername, "usuario/email/telefono")

        # password (with show/hide button)
        pw_frame = tk.Frame(self.main_frame, bg='#B41214')
        pw_frame.pack(pady=5)
        self.entryPassword = tk.Entry(pw_frame, font=('Arial', 10), width=28, show='*')
        self.entryPassword.pack(side=tk.LEFT, ipady=5)
        registerWidget(self.entryPassword, "Contraseña")
        self.mostrarPass = False
        self.btnEye = tk.Button(pw_frame, text='👁', command=lambda: self._toggle_password_visibility(), bd=0)
        self.btnEye.pack(side=tk.LEFT, padx=4)

        # forgot password link
        self.forgotLink = tk.Label(self.main_frame, text="¿Olvidaste tu contraseña?", fg='blue', bg='#B41214', cursor='hand2', font=('Arial', 9, 'underline'))
        self.forgotLink.pack(pady=5)
        self.forgotLink.bind('<Button-1>', lambda e: self.goToRecovery())

        # login button
        self.loginBtn = tk.Button(self.main_frame, text="Login", font=('Arial', 10), width=15, command=self.attempt_login)
        self.loginBtn.pack(pady=10)

        # language selector (display names in native language)
        idioma_frame = tk.Frame(self.main_frame, bg='#B41214')
        idioma_frame.pack(anchor='e', pady=5, fill='x')

        # map display name -> internal key (display includes flag emoji)
        self.languageMapDisplayToKey = {
            '🇪🇸 Español': 'Español',
            '🇺🇸 English': 'Ingles',
            'Magyar': 'Hungaro'
        }
        display_values = list(self.languageMapDisplayToKey.keys())
        self.languageCombo = ttk.Combobox(idioma_frame, values=display_values, state='readonly', width=16)
        # set default using the display name with flag
        self.languageCombo.set('🇪🇸 Español')
        self.languageCombo.pack(anchor='e')
        self.languageCombo.bind('<<ComboboxSelected>>', lambda e: self.updateLanguage())
        registerWidget(self.languageCombo)

        # alternate methods separator
        separator_frame = tk.Frame(self.main_frame, bg='#B41214')
        separator_frame.pack(fill='x', pady=8)
        tk.Frame(separator_frame, bg='black', height=1).pack(side='left', fill='x', expand=True, padx=5)
        # keep on self so translations can update it dynamically
        self.otherMethodsLabel = tk.Label(separator_frame, text="Otros métodos de inicio de sesión", bg='#B41214', font=('Arial', 9))
        self.otherMethodsLabel.pack(side='left')
        tk.Frame(separator_frame, bg='black', height=1).pack(side='left', fill='x', expand=True, padx=5)

        # facial recognition button (will attempt face login)
        self.facialBtn = tk.Button(self.main_frame, text="Reconocimiento Facial", font=('Arial', 10), width=20, command=self.loginWithFace)
        self.facialBtn.pack(pady=8)

        # register link
        self.registerLink = tk.Label(self.main_frame, text="Registrarse", fg='blue', bg='#B41214', cursor='hand2', font=('Arial', 9, 'underline'))
        self.registerLink.pack(pady=5)
        self.registerLink.bind('<Button-1>', lambda e: self.goToRegister())

    # (datos.json deprecated) -- no delete button

        # try to load translations from idiomas.json; fallback to embedded small dict
        self.translations = self.loadTranslations()

        # apply initial language and try to load draft
        try:
            # if app state has a previously selected language, apply it to the combo
            lang = app_state.get_selected_language()
            # find display name for this lang key
            try:
                disp = next(k for k, v in self.languageMapDisplayToKey.items() if v == lang)
                self.languageCombo.set(disp)
            except Exception:
                # leave default
                pass
            self.updateLanguage()
        except Exception:
            pass
        try:
            self.loadDraft()
        except Exception:
            pass

        # entry widget list for deselecting
        self._entryWidgets = [self.entryUsername, self.entryPassword]
        try:
            self.main_frame.bind('<Button-1>', self.deselectOnClick)
            self.root.bind('<Button-1>', self.deselectOnClick)
        except Exception:
            pass

        try:
            self.root.after(50, lambda: self.root.focus_force())
        except Exception:
            pass

    # --- Login actions ---
    def _toggle_password_visibility(self):
        try:
            self.mostrarPass = not getattr(self, 'mostrarPass', False)
            self.entryPassword.config(show='' if self.mostrarPass else '*')
        except Exception:
            pass
        try:
            if hasattr(self, 'btnEye'):
                self.btnEye.config(text='🙈' if self.mostrarPass else '👁')
        except Exception:
            pass

    def _toggle_fullscreen(self, event=None):
        """Toggle fullscreen state (Escape / F11 handler)."""
        try:
            self._fullscreen = not getattr(self, '_fullscreen', False)
            try:
                self.root.attributes('-fullscreen', self._fullscreen)
            except Exception:
                try:
                    self.root.state('zoomed' if self._fullscreen else 'normal')
                except Exception:
                    pass
        except Exception:
            pass

    def attempt_login(self):
        try:
            username = self.entryUsername.get()
            password = self.entryPassword.get()
            if not username or username in {"usuario/email/telefono", ""}:
                messagebox.showwarning('Error', 'Ingrese usuario')
                return
            if not password or password == 'Contraseña':
                messagebox.showwarning('Error', 'Ingrese contraseña')
                return
            # Prefer usuarios.json (new canonical store) which uses bcrypt via SistemaSeguridad.
            ok = False
            other = None
            actual_username = username
            try:
                # try common locations for usuarios.json (now in dataBase folder)
                possible = [
                    os.path.join(os.path.dirname(__file__), '..', 'dataBase', 'usuarios.json'),
                    os.path.join(os.getcwd(), 'dataBase', 'usuarios.json'),
                    os.path.join(os.path.dirname(__file__), 'dataBase', 'usuarios.json')
                ]
                usuarios_path = None
                usuarios_list = []
                print(f'DEBUG LOGIN: Buscando usuarios.json en:')
                for p in possible:
                    p = os.path.normpath(p)
                    print(f'  - {p}: {"✅ existe" if os.path.exists(p) else "❌ no existe"}')
                    if os.path.exists(p):
                        usuarios_path = p
                        with open(p, 'r', encoding='utf-8') as f:
                            usuarios_list = json.load(f)
                        print(f'DEBUG LOGIN: Usuarios cargados: {len(usuarios_list)}')
                        break
                if usuarios_list:
                    # find matching user (case-insensitive)
                    print(f'DEBUG LOGIN: Buscando usuario "{username}"')
                    print(f'DEBUG LOGIN: Usuarios disponibles: {[u.get("usuario") or u.get("username") for u in usuarios_list]}')
                    target = None
                    for u in usuarios_list:
                        name = (u.get('usuario') or u.get('username') or '')
                        print(f'DEBUG LOGIN: Comparando "{username.lower()}" con "{name.lower()}"')
                        if name and name.lower() == username.lower():
                            target = u
                            print(f'DEBUG LOGIN: ✅ Usuario encontrado: {name}')
                            break
                    if target:
                        try:
                            # Use bcrypt directly instead of relying on SistemaSeguridad import
                            import bcrypt
                            
                            stored_hash = target.get('contrasenaHash') or target.get('contrasena_hash') or target.get('password') or ''
                            print(f'DEBUG LOGIN: Hash encontrado: {stored_hash[:20]}...' if stored_hash else 'DEBUG LOGIN: ❌ No hay hash de contraseña')
                            
                            if stored_hash:
                                # Verify password using bcrypt directly
                                try:
                                    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                                        print('DEBUG LOGIN: ✅ Contraseña correcta')
                                        ok = True
                                        other = target
                                        actual_username = target.get('usuario') or target.get('username') or username
                                    else:
                                        print('DEBUG LOGIN: ❌ Contraseña incorrecta')
                                except Exception as verify_error:
                                    print(f'DEBUG LOGIN: ❌ Error en bcrypt.checkpw: {verify_error}')
                            else:
                                print('DEBUG LOGIN: ❌ No hay hash de contraseña almacenado')
                        except ImportError:
                            print('DEBUG LOGIN: ❌ bcrypt no está disponible, intentando con SistemaSeguridad')
                            # Fallback: Try to import SistemaSeguridad
                            try:
                                # Robust import strategy that works from any directory
                                SistemaSeguridad = None
                                
                                # Try multiple import strategies
                                import_attempts = [
                                    lambda: __import__('inicioRegistro.registro', fromlist=['SistemaSeguridad']).SistemaSeguridad,
                                    lambda: __import__('registro').SistemaSeguridad,
                                ]
                                
                                # Add current directory to path and try again
                                current_dir = os.path.dirname(os.path.abspath(__file__))
                                if current_dir not in sys.path:
                                    sys.path.insert(0, current_dir)
                                    import_attempts.append(lambda: __import__('registro').SistemaSeguridad)
                                
                                # Try parent directory
                                parent_dir = os.path.dirname(current_dir)
                                if parent_dir not in sys.path:
                                    sys.path.insert(0, parent_dir)
                                    import_attempts.append(lambda: __import__('inicioRegistro.registro', fromlist=['SistemaSeguridad']).SistemaSeguridad)
                                
                                for attempt in import_attempts:
                                    try:
                                        SistemaSeguridad = attempt()
                                        break
                                    except (ImportError, ModuleNotFoundError):
                                        continue
                                
                                if SistemaSeguridad is None:
                                    raise ImportError("No se pudo importar SistemaSeguridad con ningún método")
                                
                                ss = SistemaSeguridad()
                                
                                stored_hash = target.get('contrasenaHash') or target.get('contrasena_hash') or target.get('password') or ''
                                if stored_hash and ss and ss.verificarContrasena(password, stored_hash):
                                    print('DEBUG LOGIN: ✅ Contraseña correcta (con SistemaSeguridad)')
                                    ok = True
                                    other = target
                                    actual_username = target.get('usuario') or target.get('username') or username
                                else:
                                    print('DEBUG LOGIN: ❌ Contraseña incorrecta (con SistemaSeguridad)')
                            except Exception as ss_error:
                                print(f'DEBUG LOGIN: ❌ Error con SistemaSeguridad: {ss_error}')
                        except Exception as e:
                            print(f'DEBUG LOGIN: ❌ Error verificando contraseña: {e}')
                            import traceback
                            traceback.print_exc()
                            # If something fails here, we'll fallback to legacy verifier below
                            ok = False
                            other = None
                    else:
                        print(f'DEBUG LOGIN: ❌ Usuario "{username}" no encontrado en usuarios.json')
            except Exception as e:
                print(f'DEBUG LOGIN: ❌ Error general: {e}')
                ok = False
                other = None

            # Fallback to legacy datos.json verification if usuarios.json didn't match
            matched_store = None
            if not ok:
                try:
                    from dataStore import verifyUser
                    ok, other = verifyUser(username, password)
                    if ok:
                        matched_store = 'datos'
                except Exception:
                    ok = False
                    other = None
            else:
                matched_store = 'usuarios'

            # Extra safety: ensure the authenticated username actually exists in one of the stores
            if ok:
                exists = False
                try:
                    # check usuarios.json for existence (now in dataBase folder)
                    repo_users = []
                    for p in [
                        os.path.join(os.path.dirname(__file__), '..', 'dataBase', 'usuarios.json'),
                        os.path.join(os.getcwd(), 'dataBase', 'usuarios.json'),
                        os.path.join(os.path.dirname(__file__), 'dataBase', 'usuarios.json')
                    ]:
                        pp = os.path.normpath(p)
                        if os.path.exists(pp):
                            with open(pp, 'r', encoding='utf-8') as f:
                                try:
                                    repo_users = json.load(f)
                                except Exception:
                                    repo_users = []
                            break
                    for u in repo_users:
                        name = (u.get('usuario') or u.get('username') or '')
                        if name and name.lower() == actual_username.lower():
                            exists = True
                            matched_store = 'usuarios'
                            break
                except Exception:
                    pass

                if not exists:
                    # check datos.json for legacy records
                    try:
                        datos_path = os.path.join(os.path.dirname(__file__), 'datos.json')
                        if os.path.exists(datos_path):
                            with open(datos_path, 'r', encoding='utf-8') as f:
                                try:
                                    datos = json.load(f)
                                except Exception:
                                    datos = []
                            for rec in datos:
                                if rec.get('username') and rec.get('username') == actual_username:
                                    exists = True
                                    matched_store = 'datos'
                                    break
                    except Exception:
                        pass

                if not exists:
                    # Reject: authentication succeeded but no user record exists
                    print(f"DEBUG: Auth succeeded for '{actual_username}' but no user record found; rejecting login")
                    ok = False
                    other = None
            if ok:
                # prefer the canonical stored username casing when available
                message = f"Bienvenido {actual_username}!"
                if other and other.get('selectedLanguage'):
                    message += f" (Idioma: {other.get('selectedLanguage')})"
                messagebox.showinfo('Éxito', message)
                # write session file so other processes (personalizacion) can read the current user
                try:
                    self._write_session_user(actual_username)
                    print(f'DEBUG: session_user.json escrito con usuario {actual_username}')
                except Exception:
                    print('DEBUG: no se pudo escribir session_user.json')
                # check personalizado flag and launch personalizacion if needed
                try:
                    personalizado = False
                    if other and isinstance(other, dict):
                        personalizado = bool(other.get('personalizado', False))
                except Exception:
                    personalizado = False
                try:
                    self.root.destroy()
                except Exception:
                    pass
                # If user is already personalized, open the difficulty pantalla; otherwise open personalizacion
                try:
                    if personalizado:
                        try:
                            self._launch_pantalla_dificultad()
                        except Exception as e:
                            messagebox.showerror('Error', f'No se pudo abrir Pantalla dificultad: {e}')
                    else:
                        try:
                            self._launch_personalizacion()
                        except Exception as e:
                            messagebox.showerror('Error', f'No se pudo abrir Personalización: {e}')
                except Exception:
                    pass
            else:
                messagebox.showwarning('Error', 'Usuario o contraseña incorrectos')
        except Exception as e:
            messagebox.showerror('Error', f'Error al verificar credenciales: {e}')

    def goToRegister(self):
        display = self.languageCombo.get()
        lang_key = self.languageMapDisplayToKey.get(display, 'Español')
        # persist selected language in shared app state for the running process
        try:
            app_state.set_selected_language(lang_key)
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass
        # Try several strategies to load the registro module and run it.
        mod = None
        try:
            # 1) plain import (works if registro is on sys.path)
            import registro
            mod = registro
        except Exception:
            try:
                # 2) try package-style import if running as part of a package
                import importlib
                mod = importlib.import_module('inicioRegistro.registro')
            except Exception:
                try:
                    # 3) load directly from the same directory by file path
                    import importlib.util
                    path = os.path.join(os.path.dirname(__file__), 'registro.py')
                    spec = importlib.util.spec_from_file_location('registro', path)
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        # Ensure the package name 'inicioRegistro' is present in sys.modules
                        try:
                            import sys
                            pkg_name = 'inicioRegistro'
                            pkg = sys.modules.get(pkg_name)
                            if pkg is None:
                                import types
                                pkg = types.ModuleType(pkg_name)
                                pkg.__path__ = [os.path.dirname(__file__)]
                                sys.modules[pkg_name] = pkg
                            # register the module under the package path
                            mod_name = pkg_name + '.registro'
                            sys.modules[mod_name] = mod
                        except Exception:
                            pass
                        spec.loader.exec_module(mod)
                except Exception as e:
                    messagebox.showerror('Error', f'No se pudo abrir registro: {e}')
                    return

        # call main() if available, else try to instantiate the class directly
        try:
            if mod is None:
                messagebox.showerror('Error', 'No se pudo cargar el módulo de registro')
                return
            if hasattr(mod, 'main'):
                mod.main(lang_key)
                return
            if hasattr(mod, 'RegistroUsuario'):
                try:
                    root2 = tk.Tk()
                    # try to reuse a centerWindow helper if present
                    if hasattr(mod, 'centerWindow'):
                        try:
                            mod.centerWindow(root2, width=500, height=650)
                        except Exception:
                            pass
                    # call constructor in a flexible way: try kwarg, then positional lang, then only root
                    ctor = mod.RegistroUsuario
                    try:
                        app = ctor(root2, selected_language=lang_key)
                    except TypeError:
                        try:
                            app = ctor(root2, lang_key)
                        except TypeError:
                            app = ctor(root2)
                    root2.mainloop()
                    return
                except Exception as e:
                    messagebox.showerror('Error', f'No se pudo abrir registro: {e}')
                    return
            messagebox.showerror('Error', 'El módulo registro no tiene main() ni RegistroUsuario()')
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo abrir registro: {e}')

    def goToRecovery(self):
        # show a small dialog with two recovery options
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
            # modal
            dlg.transient(self.root)
            dlg.grab_set()
            self.root.wait_window(dlg)
        except Exception:
            try:
                self.root.destroy()
            except Exception:
                pass

    def _prompt_new_password_for_user(self, usuario):
        """Prompt the user twice for a new password, validate and return hashed value or None."""
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
            # Use Registro.SistemaSeguridad.hashContrasena to create bcrypt hash
            try:
                # Robust import strategy that works from any directory
                SistemaSeguridad = None
                
                # Try multiple import strategies
                import_attempts = [
                    lambda: __import__('inicioRegistro.registro', fromlist=['SistemaSeguridad']).SistemaSeguridad,
                    lambda: __import__('registro').SistemaSeguridad,
                ]
                
                # Add current directory to path and try again
                import sys
                import os
                current_dir = os.path.dirname(os.path.abspath(__file__))
                if current_dir not in sys.path:
                    sys.path.insert(0, current_dir)
                    import_attempts.append(lambda: __import__('registro').SistemaSeguridad)
                
                # Try parent directory
                parent_dir = os.path.dirname(current_dir)
                if parent_dir not in sys.path:
                    sys.path.insert(0, parent_dir)
                    import_attempts.append(lambda: __import__('inicioRegistro.registro', fromlist=['SistemaSeguridad']).SistemaSeguridad)
                
                for attempt in import_attempts:
                    try:
                        SistemaSeguridad = attempt()
                        break
                    except (ImportError, ModuleNotFoundError):
                        continue
                
                if SistemaSeguridad is None:
                    raise ImportError("No se pudo importar SistemaSeguridad con ningún método")
                
                ss = SistemaSeguridad()
                new_hash = ss.hashContrasena(pwd1)
                return new_hash
            except Exception as e:
                messagebox.showerror('Error', f'Error al procesar la nueva contraseña: {e}')
                return None
        except Exception:
            return None

    def _recover_by_security_question(self):
        import os, json, sys
        # Ask for username or email
        usuario = simpledialog.askstring('Recuperación', 'Ingrese su nombre de usuario:', parent=self.root)
        if not usuario:
            return
        # find usuarios.json (now in dataBase folder)
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

        # find user record (case-insensitive)
        target = None
        for u in usuarios_list:
            name = (u.get('usuario') or u.get('username') or '')
            if name and name.lower() == usuario.lower():
                target = u
                break
        if not target:
            messagebox.showwarning('No encontrado', 'Usuario no encontrado en usuarios.json')
            return

        # get stored question and encrypted answer
        question = target.get('preguntaSeguridad') or target.get('pregunta_seguridad') or 'Pregunta de seguridad'
        encrypted_answer = target.get('respuestaSeguridad') or target.get('respuesta_seguridad')
        # ask question
        try:
            answer = simpledialog.askstring('Pregunta de seguridad', question, parent=self.root)
            if not answer:
                return
        except Exception:
            return

        # decrypt stored answer using SistemaSeguridad
        try:
            # Robust import strategy that works from any directory
            SistemaSeguridad = None
            
            # Try multiple import strategies
            import_attempts = [
                lambda: __import__('inicioRegistro.registro', fromlist=['SistemaSeguridad']).SistemaSeguridad,
                lambda: __import__('registro').SistemaSeguridad,
            ]
            
            # Add current directory to path and try again
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
                import_attempts.append(lambda: __import__('registro').SistemaSeguridad)
            
            # Try parent directory
            parent_dir = os.path.dirname(current_dir)
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
                import_attempts.append(lambda: __import__('inicioRegistro.registro', fromlist=['SistemaSeguridad']).SistemaSeguridad)
            
            for attempt in import_attempts:
                try:
                    SistemaSeguridad = attempt()
                    break
                except (ImportError, ModuleNotFoundError):
                    continue
            
            if SistemaSeguridad is None:
                raise ImportError("No se pudo importar SistemaSeguridad con ningún método")
            
            ss = SistemaSeguridad()
            stored = ''
            if encrypted_answer:
                try:
                    stored = ss.desencriptar(encrypted_answer)
                except Exception as e:
                    messagebox.showerror('Error', f'Error al desencriptar la respuesta guardada: {e}')
                    stored = encrypted_answer
            # compare answers (case-insensitive, strip)
            if stored and stored.strip().lower() == answer.strip().lower():
                # allow reset
                new_hash = self._prompt_new_password_for_user(usuario)
                if not new_hash:
                    messagebox.showinfo('Cancelado', 'No se actualizó la contraseña')
                    return
                # write back usuarios.json
                try:
                    # set both keys used in code to be safe
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
        import os, json, io, base64
        import numpy as np
        from cryptography.fernet import Fernet

        # capture
        messagebox.showinfo('Instrucción', 'Se abrirá la cámara para reconocimiento facial. Mire a la cámara.')
        face = self._capture_mean_face()
        if face is None:
            messagebox.showwarning('Error', 'No se capturó ningún rostro.')
            return

        # load usuarios.json and Fernet key
        usuarios_list = []
        try:
            possible = [
                os.path.join(os.path.dirname(__file__), '..', 'dataBase', 'usuarios.json'),
                os.path.join(os.getcwd(), 'dataBase', 'usuarios.json'),
                os.path.join(os.path.dirname(__file__), 'dataBase', 'usuarios.json')
            ]
            usuarios_path = None
            for p in possible:
                p = os.path.normpath(p)
                if os.path.exists(p):
                    usuarios_path = p
                    with open(p, 'r', encoding='utf-8') as f:
                        usuarios_list = json.load(f)
                    break
        except Exception:
            usuarios_list = []

        # prepare Fernet (clave.key now in dataBase folder)
        fernet = None
        try:
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
                fernet = Fernet(key_bytes)
        except Exception:
            fernet = None

        best_user = None
        best_dist = float('inf')
        try:
            for u in usuarios_list:
                try:
                    enc = u.get('face_enc')
                    if not enc or not fernet:
                        continue
                    try:
                        b64 = fernet.decrypt(enc.encode()).decode('utf-8')
                    except Exception:
                        b64 = enc
                    b = base64.b64decode(b64)
                    arr = np.load(io.BytesIO(b))
                    d = np.linalg.norm(arr.flatten().astype(np.float32) - face.flatten().astype(np.float32))
                    print(f'DEBUG: Distancia calculada para usuario {u.get("usuario")}: {d}')
                    if d < best_dist:
                        best_dist = d
                        best_user = u.get('usuario') or u.get('username')
                except Exception:
                    continue
        except Exception:
            pass

        print(f'DEBUG: Mejor coincidencia para recuperación: {best_user} con distancia {best_dist}')
        if best_user and best_dist < 15000:
            # allow reset
            new_hash = self._prompt_new_password_for_user(best_user)
            if not new_hash:
                messagebox.showinfo('Cancelado', 'No se actualizó la contraseña')
                return
            # update usuarios.json
            try:
                for u in usuarios_list:
                    name = (u.get('usuario') or u.get('username') or '')
                    if name and name == best_user:
                        u['contrasenaHash'] = new_hash
                        u['contrasena_hash'] = new_hash
                        break
                if usuarios_path:
                    with open(usuarios_path, 'w', encoding='utf-8') as f:
                        json.dump(usuarios_list, f, indent=4, ensure_ascii=False)
                    messagebox.showinfo('Éxito', f'Contraseña actualizada para {best_user}')
            except Exception as e:
                messagebox.showerror('Error', f'No se pudo actualizar usuarios.json: {e}')
        else:
            messagebox.showwarning('No reconocido', 'No se encontró una coincidencia facial segura.')

    def updateLanguage(self):
        """Apply translations to visible labels/placeholders when the language selection changes."""
        try:
            display = self.languageCombo.get()
        except Exception:
            display = None
        idioma = self.languageMapDisplayToKey.get(display, 'Español')
        try:
            app_state.set_selected_language(idioma)
        except Exception:
            pass
        trans = self.translations.get(idioma, self.translations.get('Español', {}))
        try:
            self.helpLink.config(text=trans.get('ayuda', self.helpLink.cget('text')))
            self.creditsLink.config(text=trans.get('creditos', self.creditsLink.cget('text')))
            self.titleLabel.config(text=trans.get('tituloLogin', self.titleLabel.cget('text')))
            self.forgotLink.config(text=trans.get('forgot', self.forgotLink.cget('text')))
            self.loginBtn.config(text=trans.get('login', self.loginBtn.cget('text')))
            self.registerLink.config(text=trans.get('registro', self.registerLink.cget('text')))
            # other methods label and facial button
            try:
                self.otherMethodsLabel.config(text=trans.get('otrosMedios', trans.get('otros_medios', self.otherMethodsLabel.cget('text'))))
            except Exception:
                pass
            try:
                self.facialBtn.config(text=trans.get('reconocimiento', self.facialBtn.cget('text')))
            except Exception:
                pass
        except Exception:
            pass

        # Update placeholders intelligently: only replace if current value equals any known placeholder
        try:
            usuario_current = self.entryUsername.get()
            posibles_usuario = set()
            # collect known placeholder variants (support camelCase and snake_case keys)
            for k in self.translations:
                d = self.translations.get(k, {})
                posibles_usuario.add(d.get('usuarioPlaceholder', ''))
                posibles_usuario.add(d.get('usuario_placeholder', ''))
                posibles_usuario.add(d.get('userPlaceholder', ''))
            # remove empty strings
            posibles_usuario.discard('')
            if usuario_current in posibles_usuario:
                self.entryUsername.delete(0, tk.END)
                # prefer camelCase key from current translation, fallback to any available
                new_placeholder = trans.get('usuarioPlaceholder', trans.get('usuario_placeholder', usuario_current))
                self.entryUsername.insert(0, new_placeholder)
                self.fieldEdited[str(id(self.entryUsername))] = True
        except Exception:
            pass

        try:
            password_current = self.entryPassword.get()
            posibles_pass = set()
            for k in self.translations:
                d = self.translations.get(k, {})
                posibles_pass.add(d.get('passwordPlaceholder', ''))
                posibles_pass.add(d.get('password_placeholder', ''))
                posibles_pass.add(d.get('passPlaceholder', ''))
            posibles_pass.discard('')
            if password_current in posibles_pass:
                self.entryPassword.delete(0, tk.END)
                new_pass = trans.get('passwordPlaceholder', trans.get('password_placeholder', password_current))
                self.entryPassword.insert(0, new_pass)
                self.fieldEdited[str(id(self.entryPassword))] = True
        except Exception:
            pass

        # Additionally, clear any unedited entry fields so placeholder text is removed
        # regardless of the language selected. Do not wipe fields the user has edited.
        try:
            for w in [self.entryUsername, self.entryPassword]:
                wid = str(id(w))
                if not self.fieldEdited.get(wid, False):
                    try:
                        w.delete(0, tk.END)
                    except Exception:
                        pass
        except Exception:
            pass

    def loadTranslations(self):
        """Load translations from idiomas.json in the same directory.

        Returns a dict mapping language keys (e.g. 'Español', 'Ingles', 'Hungaro') to
        translation dicts. Falls back to an embedded minimal set if the file can't be read.
        """
        path = os.path.join(os.path.dirname(__file__), 'idiomas.json')
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # ensure it's a dict
                    if isinstance(data, dict):
                        return data
        except Exception:
            pass
        # fallback translations (minimal)
        return {
            'Español': {
                'ayuda': 'Ayuda', 'creditos': 'Creditos', 'titulo': 'Inicio de Sesión',
                'forgot': '¿Olvidaste tu contraseña?', 'login': 'Login', 'registro': 'Registrarse',
                'usuario_placeholder': 'usuario/email/telefono', 'password_placeholder': 'Contraseña',
                'usuarioPlaceholder': 'usuario/email/telefono', 'passwordPlaceholder': 'Contraseña'
            },
            'Ingles': {
                'ayuda': 'Help', 'creditos': 'Credits', 'titulo': 'Sign In',
                'forgot': 'Forgot your password?', 'login': 'Login', 'registro': 'Register',
                'usuario_placeholder': 'user/email/phone', 'password_placeholder': 'Password',
                'usuarioPlaceholder': 'user/email/phone', 'passwordPlaceholder': 'Password'
            },
            'Hungaro': {
                'ayuda': 'Súgó', 'creditos': 'Kreditek', 'titulo': 'Bejelentkezés',
                'forgot': 'Elfelejtette a jelszavát?', 'login': 'Bejelentkezés', 'registro': 'Regisztráció',
                'usuario_placeholder': 'felhasználó/email/telefon', 'password_placeholder': 'Jelszó',
                'usuarioPlaceholder': 'felhasználó/email/telefon', 'passwordPlaceholder': 'Jelszó'
            }
        }

    # --- Face capture and login ---
    def _capture_mean_face(self, capture_count=10, timeout=15):
        try:
            cap = cv2.VideoCapture(0)
            if not cap or not cap.isOpened():
                try:
                    messagebox.showerror('Error', 'No se detectó una cámara disponible para reconocimiento facial.')
                except Exception:
                    pass
                try:
                    cap.release()
                except Exception:
                    pass
                return None
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            faces = []
            start = cv2.getTickCount()
            fps = 1.0 / cv2.getTickFrequency()
            count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                dets = face_cascade.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in dets:
                    f = gray[y:y+h, x:x+w]
                    f = cv2.resize(f, (100, 100))
                    faces.append(f.astype(np.float32))
                    count += 1
                cv2.imshow('Login facial - presione q para cancelar', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                if count >= capture_count:
                    break
                if (cv2.getTickCount() - start) * fps > timeout:
                    break
            cap.release()
            cv2.destroyAllWindows()
            if not faces:
                return None
            mean_face = np.mean(faces, axis=0).astype(np.uint8)
            return mean_face
        except Exception:
            try:
                cap.release()
            except Exception:
                pass
            try:
                cv2.destroyAllWindows()
            except Exception:
                pass
            return None

    def loginWithFace(self):
        # capture face
        messagebox.showinfo('Instrucción', 'Se abrirá la cámara para reconocimiento facial. Mire a la cámara.')
        print('DEBUG: Iniciando captura de rostro...')
        face = self._capture_mean_face()
        if face is None:
            print('DEBUG: No se capturó ningún rostro')
            messagebox.showwarning('Error', 'No se capturó ningún rostro.')
            return
        
        print(f'DEBUG: Rostro capturado exitosamente. Forma: {face.shape}, dtype: {face.dtype}')

        # compare against stored users
        # Prefer reading face encodings from usuarios.json (app's primary user file)
        users = []
        try:
            # try project root usuarios.json in dataBase folder
            possible = [
                os.path.join(os.path.dirname(__file__), '..', 'dataBase', 'usuarios.json'),
                os.path.join(os.getcwd(), 'dataBase', 'usuarios.json'),
                os.path.join(os.path.dirname(__file__), 'dataBase', 'usuarios.json')
            ]
            usuarios_path = None
            for p in possible:
                p = os.path.normpath(p)
                if os.path.exists(p):
                    usuarios_path = p
                    break
            usuarios_list = []
            if usuarios_path:
                print(f'DEBUG: Leyendo usuarios.json desde: {usuarios_path}')
                with open(usuarios_path, 'r', encoding='utf-8') as f:
                    usuarios_list = json.load(f)
                print(f'DEBUG: Se cargaron {len(usuarios_list)} usuario(s)')
        except Exception as e:
            print(f'DEBUG: Error cargando usuarios.json: {e}')
            usuarios_list = []

        # prepare Fernet from clave.key if available (now in dataBase folder)
        fernet = None
        try:
            # try common locations for clave.key (now in dataBase folder)
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
                fernet = Fernet(key_bytes)
                print('DEBUG: Clave Fernet cargada correctamente')
        except Exception as e:
            print(f'DEBUG: Error cargando clave.key: {e}')
            fernet = None

        # First pass: try usuarios.json entries (decrypt face_enc using clave.key Fernet)
        print('DEBUG: Iniciando comparación de rostros...')
        try:
            best_user = None
            best_dist = float('inf')
            usuarios_con_rostro = 0
            for u in usuarios_list:
                try:
                    enc = u.get('face_enc')
                    if not enc or not fernet:
                        continue
                    usuarios_con_rostro += 1
                    try:
                        b64 = fernet.decrypt(enc.encode()).decode('utf-8')
                    except Exception:
                        # not encrypted with clave.key? maybe it's plain base64
                        b64 = enc
                    b = base64.b64decode(b64)
                    arr = np.load(io.BytesIO(b))
                    d = np.linalg.norm(arr.flatten().astype(np.float32) - face.flatten().astype(np.float32))
                    print(f'DEBUG: Distancia calculada para usuario {u.get("usuario")}: {d}')
                    if d < best_dist:
                        best_dist = d
                        best_user = u.get('usuario') or u.get('username')
                except Exception:
                    continue
            # if a good match found, accept
            print(f'DEBUG: Usuarios con rostro procesados: {usuarios_con_rostro}')
            print(f'DEBUG: Mejor coincidencia: {best_user} con distancia {best_dist}')
            if best_user and best_dist < 15000:
                # try to extract personalizado flag
                try:
                    pflag = False
                    for u in usuarios_list:
                        if (u.get('usuario') or u.get('username')) == best_user:
                            pflag = bool(u.get('personalizado', False))
                            break
                except Exception:
                    pflag = False
                messagebox.showinfo('Éxito', f'¡Usuario reconocido: {best_user}!')
                try:
                    self.root.destroy()
                except Exception:
                    pass
                # write session user so personalizacion can find the user
                try:
                    self._write_session_user(best_user)
                    print(f'DEBUG: session_user.json escrito con usuario {best_user} (face login)')
                except Exception:
                    print('DEBUG: no se pudo escribir session_user.json (face login)')
                # If user is already personalized, open the difficulty pantalla; otherwise open personalizacion
                try:
                    if pflag:
                        try:
                            self._launch_pantalla_dificultad()
                        except Exception as e:
                            messagebox.showerror('Error', f'No se pudo abrir Pantalla dificultad: {e}')
                    else:
                        try:
                            self._launch_personalizacion()
                        except Exception as e:
                            messagebox.showerror('Error', f'No se pudo abrir Personalización: {e}')
                except Exception:
                    pass
                return
        except Exception:
            # fall back below
            pass

        # Only use usuarios.json entries now (datos.json deprecated). If usuarios.json had no entries, login will not find faces.
        best_user = None
        best_dist = float('inf')
        # usuarios_list already loaded earlier
        for u in usuarios_list:
            try:
                enc = u.get('face_enc')
                if not enc or not fernet:
                    continue
                try:
                    b64 = fernet.decrypt(enc.encode()).decode('utf-8')
                except Exception:
                    b64 = enc
                b = base64.b64decode(b64)
                arr = np.load(io.BytesIO(b))
                d = np.linalg.norm(arr.flatten().astype(np.float32) - face.flatten().astype(np.float32))
                print(f'DEBUG: Distancia calculada para usuario {u.get("usuario")}: {d}')
                if d < best_dist:
                    best_dist = d
                    best_user = u.get('usuario') or u.get('username')
            except Exception:
                continue

        # threshold: empirical; for our simple mean-face approach use a high threshold
        print(f'DEBUG: Mejor coincidencia: {best_user} con distancia {best_dist}')
        if best_user and best_dist < 15000:
            # try to extract personalizado flag from usuarios.json
            pflag = False
            try:
                for u in usuarios_list:
                    if (u.get('usuario') or u.get('username')) == best_user:
                        pflag = bool(u.get('personalizado', False))
                        break
            except Exception:
                pflag = False
            messagebox.showinfo('Éxito', f'Usuario reconocido: {best_user} - Personalizado: {pflag}')
            try:
                self.root.destroy()
            except Exception:
                pass
            if pflag:
                try:
                    self._launch_pantalla_dificultad()
                except Exception as e:
                    messagebox.showerror('Error', f'No se pudo abrir Pantalla dificultad: {e}')
            else:
                try:
                    self._launch_personalizacion()
                except Exception as e:
                    messagebox.showerror('Error', f'No se pudo abrir Personalización: {e}')
        else:
            messagebox.showwarning('No reconocido', 'No se encontró una coincidencia facial segura.')

    # datos.json functionality removed — the app now reads/writes only usuarios.json

    def _launch_personalizacion(self):
        """Try several ways to launch the personalizacion main. Raises on failure with diagnostic."""
        last_exc = None
        # 1) try direct package import
        try:
            import personalizacion.main as pmain
            pmain.main()
            return
        except Exception as e:
            last_exc = e

        # 2) try importlib
        try:
            import importlib
            mod = importlib.import_module('personalizacion.main')
            mod.main()
            return
        except Exception as e:
            last_exc = e

        # 3) try running the script directly as a subprocess (new Python process)
        try:
            repo_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
            script_path = os.path.join(repo_root, 'personalizacion', 'main.py')
            if os.path.exists(script_path):
                # Use same python executable
                python_exe = sys.executable or 'python'
                subprocess.run([python_exe, script_path], check=True)
                return
        except Exception as e:
            last_exc = e

        # if all attempts failed, raise a combined error
        raise RuntimeError(f'No se pudo iniciar personalizacion. Último error: {last_exc}')

    def _launch_pantalla_dificultad(self):
        """Try several ways to launch the juego.pantallaDificultad main. Raises on failure with diagnostic."""
        last_exc = None
        # 1) try direct package import
        try:
            import juego.pantallaDificultad as pd
            pd.main()
            return
        except Exception as e:
            last_exc = e

        # 2) try importlib
        try:
            import importlib
            mod = importlib.import_module('juego.pantallaDificultad')
            mod.main()
            return
        except Exception as e:
            last_exc = e

        # 3) try running the script directly as a subprocess (new Python process)
        try:
            repo_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
            script_path = os.path.join(repo_root, 'juego', 'pantallaDificultad.py')
            if os.path.exists(script_path):
                python_exe = sys.executable or 'python'
                subprocess.run([python_exe, script_path], check=True)
                return
        except Exception as e:
            last_exc = e

        raise RuntimeError(f'No se pudo iniciar pantallaDificultad. Último error: {last_exc}')

    def _write_session_user(self, username):
        """Write a small session file with the current username so other processes (personalizacion) can read it."""
        try:
            repo_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
            session_path = os.path.join(repo_root, 'dataBase', 'session_user.json')
            with open(session_path, 'w', encoding='utf-8') as f:
                json.dump({'usuario': username}, f, ensure_ascii=False)
        except Exception:
            # best-effort; ignore failures
            pass

    # --- Draft/autosave helpers ---
    def restorePlaceholder(self, event, widget, placeholder):
        try:
            if widget.get() == "":
                widget.insert(0, placeholder)
                self.fieldEdited[str(id(widget))] = False
        except Exception:
            pass

    def clearPlaceholderOnFocus(self, event, widget, placeholder):
        try:
            if placeholder is not None:
                cur = widget.get()
                if cur == placeholder:
                    widget.delete(0, tk.END)
                self.fieldEdited[str(id(widget))] = True
        except Exception:
            pass

    def deselectOnClick(self, event):
        try:
            if isinstance(event.widget, (tk.Entry, ttk.Combobox)):
                return
        except Exception:
            pass
        try:
            for w in getattr(self, '_entryWidgets', []):
                try:
                    w.selection_clear()
                except Exception:
                    pass
            try:
                self.root.focus_force()
            except Exception:
                try:
                    self.main_frame.focus_set()
                except Exception:
                    pass
        except Exception:
            pass

    def markEdited(self, widget):
        self.fieldEdited[str(id(widget))] = True

    def autosaveOnClick(self, event, widget):
        try:
            self.saveDraft()
        except Exception:
            pass

    def saveDraft(self):
        data = {}
        def addIfValid(key, widget, placeholder=None):
            try:
                val = widget.get()
            except Exception:
                return
            wid = str(id(widget))
            if placeholder is None:
                if val:
                    data[key] = val
            else:
                if val and val != placeholder:
                    data[key] = val
                elif self.fieldEdited.get(wid):
                    data[key] = val

        addIfValid('username', self.entryUsername, 'usuario/email/telefono')
        addIfValid('selectedLanguage', self.languageCombo)
        try:
            if self.fieldEdited.get(str(id(self.entryPassword)), False):
                data['passwordEntered'] = True
        except Exception:
            pass
        draft_path = os.path.join(os.path.dirname(__file__), 'loginDraft.json')
        try:
            with open(draft_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def loadDraft(self):
        draft_path = os.path.join(os.path.dirname(__file__), 'loginDraft.json')
        if not os.path.exists(draft_path):
            return
        try:
            with open(draft_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            return
        if 'username' in data:
            try:
                self.entryUsername.delete(0, tk.END)
                self.entryUsername.insert(0, data['username'])
                self.fieldEdited[str(id(self.entryUsername))] = True
            except Exception:
                pass
        if 'selectedLanguage' in data:
            try:
                # draft stores the display string; set combo and shared state accordingly
                try:
                    self.languageCombo.set(data['selectedLanguage'])
                except Exception:
                    self.languageCombo.set(data['selectedLanguage'])
                # also persist to app state if possible
                try:
                    lang_key = self.languageMapDisplayToKey.get(data['selectedLanguage'], 'Español')
                    app_state.set_selected_language(lang_key)
                except Exception:
                    pass
            except Exception:
                pass


def centerWindow(root, width=500, height=450):
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")


def main(selected_language=None):
    root = tk.Tk()
    centerWindow(root, width=500, height=450)
    app = LoginApp(root)
    # if caller passed a language key, apply it
    if selected_language:
        # find display name for the key
        try:
            disp = next(k for k, v in app.languageMapDisplayToKey.items() if v == selected_language)
            app.languageCombo.set(disp)
            app.updateLanguage()
        except Exception:
            pass
    root.mainloop()


if __name__ == "__main__":
    main()