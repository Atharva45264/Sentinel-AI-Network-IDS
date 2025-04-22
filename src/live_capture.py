import pyshark
import pandas as pd

def extract_features(packet):
    try:
        features = {
            "timestamp": packet.sniff_time,
            "length": packet.length,
            "src_ip": packet.ip.src if hasattr(packet, 'ip') else None,
            "dst_ip": packet.ip.dst if hasattr(packet, 'ip') else None,
            "protocol": packet.transport_layer if hasattr(packet, 'transport_layer') else None,
            "src_port": packet[packet.transport_layer].srcport if hasattr(packet, 'transport_layer') else None,
            "dst_port": packet[packet.transport_layer].dstport if hasattr(packet, 'transport_layer') else None
        }
        return features
    except AttributeError:
        return None  # Ignore packets that don't have the required attributes

def capture_live_traffic(interface="Wi-Fi", packet_count=100):
    print(f"Capturing {packet_count} packets on {interface}...")
    capture = pyshark.LiveCapture(interface=interface)
    
    data = []
    
    for packet in capture.sniff_continuously(packet_count=packet_count):
        features = extract_features(packet)
        if features:
            data.append(features)
    
    df = pd.DataFrame(data)
    df.to_csv("live_packets.csv", index=False)
    print("Captured packets saved to live_packets.csv")

if __name__ == "__main__":
    capture_live_traffic(interface="Wi-Fi", packet_count=10)
