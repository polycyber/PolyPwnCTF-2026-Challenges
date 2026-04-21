import os

SECRET_KEY = "pizza"
ALLOWED_MODES = ["dna", "rna"]
ALLOWED_LENGTHS = [5, 11, 17]
ALLOWED_SEQUENCE_CHARS = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMp. "

HOSTNAME = os.getenv("HOSTNAME", "127.0.0.1")
PORT = int(os.getenv("PORT", 3500))