import os
import socket
import subprocess
import sys
import threading
import time
import tkinter as tk
import netifaces
import requests
import django

thread_local = threading.local()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()
from Client.models import Client


def get_session():
    if not hasattr(thread_local, 'session'):
        thread_local.session = requests.Session()
    return thread_local.session


class Runner:
    def __init__(self):
        self.possibles = ['172', '192', '127']
        self.ports = [9877, 9922, 5041, 2982, 7309]
        self.private_ip, self.subnet = self.get_private_ip_and_subnet()

    def get_private_ip_and_subnet(self):
        default_gws = netifaces.gateways().get('default', {})
        for interface in netifaces.interfaces():
            for addr in netifaces.ifaddresses(interface).get(netifaces.AF_INET, []):
                if (ip := addr['addr']).split('.')[0] in self.possibles:
                    if any(gw[1] == interface for gw in default_gws.values()):
                        return ip, addr['netmask']
        return None, None

    def scan_port(self, ip, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)

            result = sock.connect_ex((ip, port))
            print(f"port:{port} {result != 0}")
            return result != 0

    def scan_http(self, ip, port):
        session = get_session()
        address = f"http://{ip}:{port}"
        print(f"http: {port}")
        try:
            response = session.head(address, timeout=0.1)
            print(response.status_code)
            if 200 <= response.status_code < 300:
                print(False)
                return False
        except requests.exceptions.RequestException:
            pass
        return True

    def run(self):
        server_ip = self.private_ip if self.private_ip is not None else "127.0.0.1"
        port = None
        for p in self.ports:
            print(server_ip)
            res = self.scan_port(server_ip, p) and self.scan_http(server_ip,p)
            if res:
                port = p
                break
        server = f"{server_ip}:{port}"
        threading.Thread(target=self.start_django_server, daemon=True, args=[server]).start()
        self.run_gui()

    def start_django_server(self, server):
        try:
            os.system(f'cd .venv/scripts && activate && cd .. && cd .. && py manage.py runserver {server}')
            print(f"Server started at: {server}")
        except Exception as e:
            pass

    def refresh_list(self):
        try:
            # Clear the current contents of the listbox
            listbox.delete(0, tk.END)

            # Query all objects (you can add filtering or ordering as needed)
            objects = Client.objects.filter(status=0)

            # Insert each object into the listbox.
            for obj in objects:
                listbox.insert(tk.END, str(obj))

        except Exception as e:
            pass

        # Schedule the function to run again after 2000 milliseconds (2 seconds)
        root.after(2000, self.refresh_list)

    def on_closing(self):
        root.destroy()

    def run_gui(self):
        """
        Set up and run the Tkinter GUI.
        """
        global root, listbox
        root = tk.Tk()
        root.title("Django Desktop App - Live Model List")

        # Create a Listbox widget to display the model objects
        listbox = tk.Listbox(root, width=80, height=20)
        listbox.pack(padx=20, pady=20)

        # Start periodic refresh of the listbox
        root.after(0, self.refresh_list)  # start immediately

        # Ensure that closing the window stops the Django server (if needed)
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Start the Tkinter event loop
        root.mainloop()


Runner().run()
