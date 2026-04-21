import datetime

# The Flag: "DOC" (Short example for testing)
FLAG = "polycyber{M4R7ymcf1Y}"
# The specific date: Nov 12, 1955
# Lightning strikes at 10:04 PM
start_time = datetime.datetime(2015, 10, 21, 22, 4, 0)

def text_to_bits(text):
    return ''.join(format(ord(c), '08b') for c in text)

bits = "011100000110111101101100011110010110001101111001011000100110010101110010011110110100110100110100010100100011011101111001011011010110001101100110001100010101100101111101"

print(f"Encoding '{FLAG}' as {bits}")

with open("build_timeline.sh", "w") as f:
    f.write("#!/bin/bash\n# Temporal Sync Script\n\n")
    
    for i, bit in enumerate(bits):
        # Move forward one day for each bit
        current_date = start_time + datetime.timedelta(days=i)
        # ISO 8601 Format: 1955-11-12T22:04:00
        iso_date = current_date.strftime("%Y-%m-%dT%H:%M:%S")
        
        if bit == '1':
            f.write(f'echo "Temporal Bit {i}: HIGH" > flux_status.txt\n')
            f.write(f'git add flux_status.txt\n')
            f.write(f'GIT_AUTHOR_DATE="{iso_date}" GIT_COMMITTER_DATE="{iso_date}" '
                    f'git commit -m "Buffer sync at bit {i}" --quiet\n')
        else:
            # We still want the time to pass, but no commit = dark square (0)
            f.write(f'# Bit {i} is LOW, skipping date {iso_date}\n')

print("Script 'build_timeline.sh' created. Run it inside a git repo.")
