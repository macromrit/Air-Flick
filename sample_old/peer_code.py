from zeroconf import ServiceBrowser, Zeroconf, ServiceListener
import subprocess
import time
import platform

# Peer Buffer: all discovered peers are stored here
discovered_peers = []


# step-1: a listener to detect devices in local subnet
class PeerListener(ServiceListener):
    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            ip = ".".join(map(str, info.addresses[0]))
            print(f"[+] Discovered peer: {ip}")
            discovered_peers.append(ip)


# step-2: ping function to find the nearest peer
def ping(ip):
    try:
        if platform.system().lower() == 'windows':
            command = ['ping', '-n', '1', ip]
        else:
            command = ['ping', '-c', '1', ip]

        output = subprocess.check_output(command, stderr=subprocess.DEVNULL)
        output_str = output.decode()

        if platform.system().lower() == 'windows':
            for line in output_str.split('\n'):
                if 'time=' in line:
                    time_str = line.split('time=')[1].split('ms')[0].strip()
                    time_ms = float(time_str)
                    return time_ms
        else:
            for line in output_str.split('\n'):
                if 'time=' in line:
                    time_ms = float(line.split('time=')[-1].split(' ')[0])
                    return time_ms

    except:
        return float('inf')  # Return a high number if ping fails
    

# step-3: Discover peers on local network and append it to the global buffer
def discover_peers(service_type="_http._tcp.local.", timeout=5):
    zeroconf = Zeroconf()
    listener = PeerListener()
    browser = ServiceBrowser(zeroconf, service_type, listener)
    print("[*] Scanning for peers...")
    time.sleep(timeout)
    zeroconf.close()
    return discovered_peers


# Step 4: Ranking peers by its ping
def rank_peers(peers):
    ping_results = {}
    for ip in peers:
        rtt = ping(ip)
        ping_results[ip] = rtt
        print(f"RTT to {ip}: {rtt:.2f} ms")

    sorted_peers = sorted(ping_results.items(), key=lambda x: x[1])
    print("\nNearest peer (lowest ping):")
    print(sorted_peers[0])
    return sorted_peers

def returnNearestPeer():
    peers = discover_peers()
    if peers:
        ranked = rank_peers(peers)
    else:
        print("[-] No peers found.")

if __name__ == "__main__":
    peers = discover_peers()
    if peers:
        ranked = rank_peers(peers)
    else:
        print("[-] No peers found.")