from zeroconf import ServiceInfo, Zeroconf
import socket
import time


# step-1: Set up basic details
desc = {'info': 'AirGesture Transfer Peer'}

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to an external IP (doesn't send anything)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

local_ip = get_local_ip()


service_info = ServiceInfo(
    "_http._tcp.local.",                   # Service Type
    "AirGesture._http._tcp.local.",        # Unique Name
    addresses=[socket.inet_aton(local_ip)],
    port=8000,                             # Any port you're running your app on
    properties=desc,
    server=f"{socket.gethostname()}.local."   # Local hostname
)

# Step 2: Start advertising
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


