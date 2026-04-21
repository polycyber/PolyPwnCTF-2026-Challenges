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

prefix, suffix = z3.BitVecs("prefix suffix", 64)


def bytes_to_z3(data: bytes):
    return [z3.BitVecVal(x, 8) for x in data]


def add_z3_fnv(plain: list[z3.BitVecRef] | list[z3.BitVecNumRef], hashed: int):
    x = prefix
    x ^= z3.ZeroExt(56, plain[0]) << 7

    for i in range(0, len(plain), 8):
        chunk = plain[i : i + 8]

        if len(chunk) == 8:
            x = (pyhash_multiplier * x) ^ z3.Concat(*reversed(chunk))
        else:
            for b in chunk:
                x = (pyhash_multiplier * x) ^ z3.ZeroExt(56, b)

    x ^= z3.BitVecVal(len(plain), 64)
    x ^= suffix

    s.add(x == z3.BitVecVal(hashed, 64))


add_z3_fnv(bytes_to_z3(b"a"), 9173682920893085635)
add_z3_fnv(bytes_to_z3(b"b"), 9173682920571999040)
add_z3_fnv(bytes_to_z3(b"banana"), -330394288152634536)
add_z3_fnv(
    bytes_to_z3(b"teeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeest"), 2200288322705736818
)
add_z3_fnv(
    bytes_to_z3(
        b"fooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooob"
    ),
    -7350528708565132495,
)


# while s.check() == z3.sat:
#     model = s.model()

#     print(model)

# s.add(z3.Not(z3.And(prefix == model.eval(prefix), suffix == model.eval(suffix))))

secret = [z3.BitVec(f"s{x}", 8) for x in range(30)]
s.add(*[secret[i] == ord(v) for i, v in enumerate("POLYCYBER{")])
s.add(secret[-1] == ord("}"))

for x in secret[10:-1]:
    s.add(z3.Or(*[x == ord(y) for y in "_abeknorsty"]))

add_z3_fnv(secret, -7999328088387665657)
while s.check() == z3.sat:
    model = s.model()

    print(bytes([model.eval(t).as_long() for t in secret]))

    s.add(z3.Or(*[b != model.eval(b).as_long() for b in secret[10:-1]]))
