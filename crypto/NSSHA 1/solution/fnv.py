import z3

"""
fnv(const void *src, Py_ssize_t len)
{
    const unsigned char *p = src;
    Py_uhash_t x;
    Py_ssize_t remainder, blocks;
    union {
        Py_uhash_t value;
        unsigned char bytes[SIZEOF_PY_UHASH_T];
    } block;

#ifdef Py_DEBUG
    assert(_Py_HashSecret_Initialized);
#endif
    remainder = len % SIZEOF_PY_UHASH_T;
    if (remainder == 0) {
        /* Process at least one block byte by byte to reduce hash collisions
         * for strings with common prefixes. */
        remainder = SIZEOF_PY_UHASH_T;
    }
    blocks = (len - remainder) / SIZEOF_PY_UHASH_T;

    x = (Py_uhash_t) _Py_HashSecret.fnv.prefix;
    x ^= (Py_uhash_t) *p << 7;
    while (blocks--) {
        PY_UHASH_CPY(block.bytes, p);
        x = (PyHASH_MULTIPLIER * x) ^ block.value;
        p += SIZEOF_PY_UHASH_T;
    }
    /* add remainder */
    for (; remainder > 0; remainder--)
        x = (PyHASH_MULTIPLIER * x) ^ (Py_uhash_t) *p++;
    x ^= (Py_uhash_t) len;
    x ^= (Py_uhash_t) _Py_HashSecret.fnv.suffix;
    if (x == (Py_uhash_t) -1) {
        x = (Py_uhash_t) -2;
    }
    return x;
}
"""
pyhash_multiplier = 0xF4243

s = z3.Solver()

secret_len = 29
secret_bytes = [z3.BitVec(f"s{i}", 8) for i in range(secret_len)]
for b8 in secret_bytes[10:-1]:
    s.add(z3.Or(*[b8 == ord(x) for x in "_acehnorstu"]))

s.add(*[secret_bytes[i] == ord(v) for i, v in enumerate("POLYCYBER{")])
s.add(secret_bytes[-1] == ord("}"))

x = z3.BitVecVal(0, 64)
x ^= z3.ZeroExt(56, secret_bytes[0]) << 7

for i in range(0, secret_len, 8):
    chunk = secret_bytes[i : i + 8]

    if len(chunk) == 8:
        x = (pyhash_multiplier * x) ^ z3.Concat(*reversed(chunk))
    else:
        for b in chunk:
            x = (pyhash_multiplier * x) ^ z3.ZeroExt(56, b)

x ^= z3.BitVecVal(secret_len, 64)

s.add(x == z3.BitVecVal(-8352886505674939205, 64))

while s.check() == z3.sat:
    model = s.model()

    print(bytes([model.eval(t).as_long() for t in secret_bytes]))

    s.add(z3.Or(*[b != model.eval(b).as_long() for b in secret_bytes[10:-1]]))
