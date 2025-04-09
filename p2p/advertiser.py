# External Imports
from zeroconf import ServiceInfo, Zeroconf
import socket
import time
import json

# Internal Imports
from utils.uuid_generator import generateUUID
from utils.get_current_local_ip import get_local_ip

# Basic Details of the peer
desc = {'info': 'AirGesture Transfer Peer'}



def startAdvertising(local_ip: str, unique_name: str, desc: dict = desc, port_number: int = 8005):
    service_info = ServiceInfo(
        "_http._tcp.local.",                       # Service Type
        F"{unique_name}._http._tcp.local.",        # Unique Name
        addresses=[socket.inet_aton(local_ip)],
        port=port_number,                          # Any port you're running your app on
        properties=desc,
        server=f"{socket.gethostname()}.local."    # Local hostname
    )

    # Advertising to Peers in local subnet
    zeroconf = Zeroconf()
    print(f"[+] Advertising this device on {local_ip}")

    zeroconf.register_service(service_info)

    try:
        while True:
            print("ADVERTISING")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[-] Stopping advertisement")
        zeroconf.unregister_service(service_info)
        zeroconf.close()


def advertiserPipeline():
    current_device_local_ip = get_local_ip()
    service_unique_name = "Convoy"+generateUUID()
    startAdvertising(current_device_local_ip, service_unique_name)


if __name__ == "__main__":
    advertiserPipeline()