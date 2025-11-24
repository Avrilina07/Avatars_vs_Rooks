"""
Servidor único: maneja control (UDP 8080) y power (UDP 8090).
Publica eventos de pygame para controles y lanza login en POWER_ON.
"""
import socket
import threading
import pygame
import subprocess
import sys
import os
import time

controlPort = 8080
powerPort = 8090


class Server:
    def __init__(self, host='0.0.0.0'):
        self.host = host
        self.controlSock = None
        self.powerSock = None
        self._stop = threading.Event()
        self.loginProc = None

    def startServer(self):
        self._stop.clear()
        t1 = threading.Thread(target=self._controlLoop, daemon=True)
        t2 = threading.Thread(target=self._powerLoop, daemon=True)
        t1.start()
        t2.start()

    def stopServer(self):
        self._stop.set()
        try:
            if self.controlSock:
                self.controlSock.close()
        except:
            pass
        try:
            if self.powerSock:
                self.powerSock.close()
        except:
            pass
        self._terminateLogin()

    def _terminateLogin(self):
        try:
            if self.loginProc and self.loginProc.poll() is None:
                self.loginProc.terminate()
                time.sleep(0.5)
                if self.loginProc.poll() is None:
                    self.loginProc.kill()
        except Exception:
            pass
        finally:
            self.loginProc = None

    def _launchLogin(self):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        loginPath = os.path.join(base, 'inicioRegistro', 'login.py')
        if not os.path.exists(loginPath):
            print('server: login.py no encontrado en', loginPath)
            return
        if self.loginProc and self.loginProc.poll() is None:
            return
        try:
            cmd = [sys.executable, loginPath]
            self.loginProc = subprocess.Popen(cmd)
            print('server: login lanzado PID', self.loginProc.pid)
        except Exception as e:
            print('server: fallo al lanzar login:', e)

    def _controlLoop(self):
        try:
            self.controlSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.controlSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.controlSock.bind((self.host, controlPort))
            self.controlSock.settimeout(1.0)
        except Exception as e:
            print('server: no se pudo enlazar control UDP', controlPort, e)
            return
        print('server: control UDP escuchando en', self.host, controlPort)

        while not self._stop.is_set():
            try:
                data, addr = self.controlSock.recvfrom(1024)
                if not data:
                    continue
                text = data.decode('utf-8', errors='ignore').strip()
                # esperar formato: X,Y,B1,B2,B3,B4,B5,B6
                parts = [p for p in text.split(',') if p]
                if len(parts) >= 8:
                    try:
                        state = {
                            'x': int(parts[0]),
                            'y': int(parts[1]),
                            'b1': int(parts[2]),
                            'b2': int(parts[3]),
                            'b3': int(parts[4]),
                            'b4': int(parts[5]),
                            'b5': int(parts[6]),
                            'b6': int(parts[7])
                        }
                        ev = pygame.event.Event(pygame.USEREVENT + 1, controller=state)
                        pygame.event.post(ev)
                    except Exception:
                        pass
            except socket.timeout:
                continue
            except Exception as e:
                print('server control loop error:', e)
                time.sleep(0.1)

        try:
            self.controlSock.close()
        except:
            pass

    def _powerLoop(self):
        try:
            self.powerSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.powerSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.powerSock.bind((self.host, powerPort))
            self.powerSock.settimeout(1.0)
        except Exception as e:
            print('server: no se pudo enlazar power UDP', powerPort, e)
            return
        print('server: power UDP escuchando en', self.host, powerPort)

        while not self._stop.is_set():
            try:
                data, addr = self.powerSock.recvfrom(1024)
                if not data:
                    continue
                text = data.decode('utf-8', errors='ignore').strip()
                if text == 'POWER_ON':
                    self._launchLogin()
                elif text == 'POWER_OFF':
                    self._terminateLogin()
            except socket.timeout:
                continue
            except Exception as e:
                print('server power loop error:', e)
                time.sleep(0.1)

        try:
            self.powerSock.close()
        except:
            pass


_globalServer = None

def startServer():
    global _globalServer
    if _globalServer is None:
        _globalServer = Server()
        _globalServer.startServer()

def stopServer():
    global _globalServer
    if _globalServer:
        _globalServer.stopServer()
        _globalServer = None


if __name__ == '__main__':
    try:
        pygame.init()
    except Exception:
        pass
    startServer()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stopServer()
