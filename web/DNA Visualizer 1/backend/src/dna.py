from fastapi import HTTPException

from src.constants import ALLOWED_SEQUENCE_CHARS
from src.models import DNAGeneration

import subprocess, sys


def parse_sequence(raw_sequence: str):
    new_seq = []
    for c in raw_sequence.encode("ascii", errors="ignore"):
        if chr(c) not in ALLOWED_SEQUENCE_CHARS:
            raise HTTPException(400, "Parser found illegal character in sequence!")

    for b in bytes(raw_sequence, "utf-8", errors='ignore'):
        new_seq.append(b%128)

    return bytes(new_seq).decode("ascii")

def generate_molecule(gen: DNAGeneration, profile):
    seq = parse_sequence(gen.sequence)
    molecule = seq[:profile['length']]
    print("=======   ", molecule)
    # res = subprocess.run("echo "+molecule, shell=True, capture_output = True)
    # res = subprocess.run("echo aaa; echo bbbbb;".split(" "), shell=True, capture_output = True)

    command = f"src/format_molecule.sh {profile['mode']} {molecule}"
    res = subprocess.run(command, capture_output=True, shell=True, timeout=3)

    return molecule, f"{res.stdout.decode()}{res.stderr.decode()}"
