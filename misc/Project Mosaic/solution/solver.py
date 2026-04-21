from scapy.all import *
from PIL import Image
import sys
from pyzbar.pyzbar import decode

def extract_packet_sequence(pcap_file):
    packets = rdpcap(pcap_file)
    sequence = []
    for pkt in packets:
        if TCP in pkt:
            sequence.append('TCP')
        elif UDP in pkt:
            sequence.append('UDP')
        elif ICMP in pkt:
            sequence.append('ICMP')

    return sequence

def find_qr_pattern(sequence):
    icmp_positions = [i for i, pkt_type in enumerate(sequence) if pkt_type == 'ICMP']
    distances = []
    for i in range(1, len(icmp_positions)):
        dist = icmp_positions[i] - icmp_positions[i-1]
        distances.append(dist)
    
    from collections import Counter
    distance_counts = Counter(distances)
    most_common_distance = distance_counts.most_common(1)[0][0]

    start_idx = 0
    for i in range(len(icmp_positions) - 5):
        consistent = True
        for j in range(5):
            if i+j+1 >= len(icmp_positions):
                consistent = False
                break
            dist = icmp_positions[i+j+1] - icmp_positions[i+j]
            if abs(dist - most_common_distance) > 2:  # Tolérance de 2
                consistent = False
                break
        
        if consistent:
            start_idx = icmp_positions[i] - (most_common_distance - 1)
            if start_idx < 0:
                start_idx = 0
            break
    
    return start_idx, most_common_distance - 1

def sequence_to_matrix(sequence, start_idx=0, width=None):

    if width is None:
        _, width = find_qr_pattern(sequence)
    
    matrix = []
    current_row = []
    
    i = start_idx
    while i < len(sequence):
        pkt_type = sequence[i]
        
        if pkt_type == 'ICMP':
            if current_row:
                if len(current_row) < width:
                    current_row.extend([False] * (width - len(current_row)))
                elif len(current_row) > width:
                    current_row = current_row[:width]
                
                matrix.append(current_row)
                current_row = []
        elif pkt_type == 'TCP':
            current_row.append(True)
        elif pkt_type == 'UDP':
            current_row.append(False)
        
        i += 1
    
    if current_row:
        if len(current_row) < width:
            current_row.extend([False] * (width - len(current_row)))
        elif len(current_row) > width:
            current_row = current_row[:width]
        matrix.append(current_row)
    
    height = len(matrix)
   
    return matrix

def matrix_to_image(matrix, scale=10):
    if not matrix:
        return None
    
    height = len(matrix)
    width = len(matrix[0]) if height > 0 else 0
    img = Image.new('1', (width * scale, height * scale), 1)
    pixels = img.load()
    
    for y in range(height):
        for x in range(width):
            color = 0 if matrix[y][x] else 1
            for dy in range(scale):
                for dx in range(scale):
                    pixels[x * scale + dx, y * scale + dy] = color
    
    return img

def decode_qr_image(img):

    decoded_objects = decode(img)
    return decoded_objects[0].data.decode('utf-8')

def solve_pcap(pcap_file, output_image="qrcode.png", auto_detect=True, manual_width=None):
    
    # Extract Sequence
    sequence = extract_packet_sequence(pcap_file)
    
    # Detect pattern
    start_idx, width = find_qr_pattern(sequence)

    
    # Convert into matrix
    matrix = sequence_to_matrix(sequence, start_idx, width)

    # Generate image
    img = matrix_to_image(matrix, scale=10)
    img.save(output_image)
    
    # Decode QR code
    flag = decode_qr_image(img)
    print(flag)
    
if __name__ == "__main__":
    PCAP_FILE = "challenge.pcap"
    OUTPUT_IMAGE = "qrcode_solved.png"
    
    USE_FULL_PCAP = True
    MANUAL_WIDTH = None
    
    solve_pcap(PCAP_FILE, OUTPUT_IMAGE, auto_detect=not USE_FULL_PCAP, manual_width=MANUAL_WIDTH)
