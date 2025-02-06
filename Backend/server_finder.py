import ipaddress
from concurrent.futures import ThreadPoolExecutor
import netifaces
import requests
import threading

thread_local = threading.local()

def get_session():
    if not hasattr(thread_local, 'session'):
        thread_local.session = requests.Session()
    return thread_local.session

class ServerFinder:
    def __init__(self):
        self.possibles = ['172', '192', '127']
        self.ports = [9877, 9922, 5041, 2982, 7309]
        self.private_ip, self.subnetMask = self.get_private_ip_and_subnet()
        self.network = self.get_network()
        self.server = None

    def run(self):
        self.server = self.find_server()
        return self.server


    def get_private_ip_and_subnet(self):
        default_gws = netifaces.gateways().get('default', {})
        for interface in netifaces.interfaces():
            for addr in netifaces.ifaddresses(interface).get(netifaces.AF_INET, []):
                if (ip := addr['addr']).split('.')[0] in self.possibles:
                    if any(gw[1] == interface for gw in default_gws.values()):
                        return ip, addr['netmask']
        return None, None

    def get_network(self):
        if self.private_ip and self.subnetMask:
            return ipaddress.IPv4Network(f"{self.private_ip}/{self.subnetMask}", strict=False)
        return None

    def scan_port(self, ip):
        session = get_session()
        for port in self.ports:
            address = f"http://{ip}:{port}"
            try:
                response = session.head(address, timeout=0.1)
                if 200 <= response.status_code < 300:
                    return address
            except requests.exceptions.RequestException:
                continue
        return None

    def find_server(self):
        if not self.network:
            return None

        ips = (str(host) for host in self.network.hosts())

        with ThreadPoolExecutor(max_workers=100) as executor:
            results = executor.map(self.scan_port, ips, chunksize=10)
            for result in results:
                if result is not None:
                    executor.shutdown(wait=False, cancel_futures=True)
                    return result
        return None