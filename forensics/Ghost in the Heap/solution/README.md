# Solution — Ghost in the Heap

**Flag:** `polycyber{uDp_sUre_1s_fUN-uh}`

---

## Overview

The artifact is a 768 MB raw physical RAM dump from a QEMU guest. Inside the VM, a custom binary (`exfil_dns`) ran and performed the following sequence:

1. XOR-decoded an obfuscated flag from a static byte array.
2. Base64url-encoded the flag without padding.
3. Split the base64url string into chunks of up to 48 characters.
4. Built a valid DNS A-query for each chunk, encoding the chunk and its sequence metadata inside the QNAME labels.
5. Sent the queries over UDP to localhost on port 53 (no real DNS resolver required).
6. **Wiped** every plaintext buffer — the flag, the base64 string, and the raw DNS packets — using a volatile write loop.
7. Stored **obfuscated** copies of the DNS packets on the heap inside a custom structure tagged with the magic `CAPV2\x00\x00\x00` before the wipe.
8. Signalled readiness, then kept the process alive while the host dumped RAM.
9. Exited without freeing the heap — leaving the CAPV2 structure intact in the dump.

The trick: the plaintext is gone, but the heap still holds the obfuscated packets. Recovering the flag requires finding, decoding, and parsing those packets.

---

## Step 1 — Find the CAPV2 structure

Scan the raw dump for the 8-byte magic `CAPV2\x00\x00\x00`. Because the dump is a flat physical memory image and not an ELF core, a simple `bytes.find` over the entire file is sufficient.

```python
MAGIC = b"CAPV2\x00\x00\x00"
hits = [i for i in range(len(data)) if data[i:i+8] == MAGIC]
```

In practice a single hit is expected (one heap allocation for one run of the process).

---

## Step 2 — Parse the CAPV2 header

The structure immediately following the magic is:

```
Offset  Size  Field
  0       8   magic ("CAPV2\x00\x00\x00")
  8       4   count      — number of DNS packets (u32 LE)
 12       4   blob_len   — total bytes of the obfuscated blob (u32 LE)
 16       1   xormask    — random per-run XOR mask byte
 17       3   (reserved / padding)
 20    count×8  entry table  — each entry: u32 offset, u32 length (LE) into the blob
 20+count×8  blob_len  obfuscated packet bytes
```

```python
import struct
count, blob_len = struct.unpack_from("<II", data, base + 8)
xormask = data[base + 16]
entries_off = base + 20
blob_off   = entries_off + count * 8
```

---

## Step 3 — Deobfuscate each DNS packet

Each packet byte is XOR-encoded with a position-dependent key:

```
ciphertext[j] = plaintext[j] ^ xormask ^ ((packet_index * 131 + byte_index) & 0xFF)
```

Invert this for each entry:

```python
for i in range(count):
    off, ln = struct.unpack_from("<II", data, entries_off + i * 8)
    raw = data[blob_off + off : blob_off + off + ln]
    plain = bytearray(ln)
    for j in range(ln):
        k = (i * 131 + j) & 0xFF
        plain[j] = raw[j] ^ xormask ^ k
    packets.append(bytes(plain))
```

---

## Step 4 — Parse the DNS QNAME labels

Each decoded byte sequence is a real DNS query wire format. The structure is:

```
 0-1    Transaction ID
 2-3    Flags (0x0100 = standard query, RD set)
 4-5    QDCOUNT = 1
 6-11   AN/NS/AR counts = 0
12+     QNAME (length-prefixed labels, terminated by 0x00)
        followed by QTYPE (0x0001 = A) and QCLASS (0x0001 = IN)
```

The QNAME encodes exactly four labels:

| Position | Content | Example |
|----------|---------|---------|
| 0 | Base64url chunk of the flag | `cG9seWN5YmVy` |
| 1 | Sequence number `s%02d` | `s00` |
| 2 | Total chunk count `t%02d` | `t01` |
| 3 | Random session hex string | `3f9a1b2c` |

Parse by reading length-prefixed labels from offset 12:

```python
def parse_qname_labels(pkt):
    i = 12
    labels = []
    while True:
        ln = pkt[i]; i += 1
        if ln == 0:
            break
        labels.append(pkt[i:i+ln])
        i += ln
    # verify QTYPE=A QCLASS=IN
    assert pkt[i:i+4] == b"\x00\x01\x00\x01"
    return labels
```

---

## Step 5 — Reassemble and decode the flag

Collect the base64url chunks, sort by sequence number, concatenate, re-add padding, and decode:

```python
import base64
parts = {}
for pkt in packets:
    labels = parse_qname_labels(pkt)
    chunk, seqb, totalb = labels[0], labels[1], labels[2]
    seq   = int(seqb[1:3])
    total = int(totalb[1:3])
    parts[seq] = chunk

b64url = b"".join(parts[i] for i in range(total))
pad    = b"=" * ((4 - len(b64url) % 4) % 4)
flag   = base64.urlsafe_b64decode(b64url + pad).decode()
print(flag)  # polycyber{uDp_sUre_1s_fUN-uh}
```

---

## Running the provided solver

A ready-to-run script is included:

```bash
python3 solution/solve_novol.py challenge/dist/memdump.raw
```

Expected output:

```
polycyber{uDp_sUre_1s_fUN-uh}
```

No dependencies beyond the Python 3 standard library.

---

## Alternative — Volatility 3 plugin

A Volatility 3 plugin is provided in `tools/vol_plugins/capv2flag.py` for participants who prefer the conventional memory-forensics toolchain.

```bash
python3 vol.py -f challenge/dist/memdump.raw \
    --plugin-dirs tools/vol_plugins \
    capv2flag.CAPV2Flag
```

The plugin scans the physical layer (`FileLayer`) for the CAPV2 magic, runs the same decoding logic, and prints the flag alongside its physical offset.

---

## Why `strings` and `grep` don't work

The binary was designed to resist trivial recovery:

- The flag is never stored in plaintext in the executable — it is XOR-obfuscated in `.rodata` and materialised on the heap only briefly.
- The flag plaintext, the base64 string, and every raw DNS packet are overwritten with a `volatile uint8_t` loop before the dump is taken.
- Only the CAPV2 blob — with an additional rolling-XOR layer — survives in the heap.
- No ASCII domain suffix is appended to the QNAME, so `strings | grep` on the dump does not produce the flag in readable form.

The intended path is: **magic scan → header parse → XOR decode → DNS parse → base64url reassembly**.
