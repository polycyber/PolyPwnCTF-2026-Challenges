import calendar
import sys
import string
import datetime

def checksum_bronze(name: bytes, expiration: int):
    uVar2 = 0x28AC91B93

    name_len = len(name)
    if name_len != 0:
        uVar4 = 0
        iVar3 = 0x23
        idx = 0

        while name_len != 0:
            bVar1 = name[idx]

            shift = (iVar3 + (uVar4 // 0x23) * 0x23) & 0x3F
            uVar5 = (bVar1 >> shift) & ((1 << 64) - 1)

            if uVar4 % 0x23 == 0:
                uVar5 = 0

            uVar2 ^= (uVar5 | ((bVar1 << (uVar4 % 0x23)) & ((1 << 64) - 1))) ^ bVar1

            idx += 1
            iVar3 -= 7
            uVar4 += 7
            name_len -= 1

    return (
        (((expiration & 0x3FF) - ((expiration >> 10) & 0x1FFF)) + uVar2)
        * ((expiration >> 0x17) & 0xFFFFF)
        + (expiration >> 0x2B)
    ) & 0x7FFFFFFFF


def generate_license(name: bytes, expiration: datetime.date, edition: int) -> str:
    if len(name) != 10 or not all(
        c in string.ascii_uppercase.encode() + b" " for c in name
    ):
        raise ValueError("need [A-Z ]+ and len 10")

    if edition < 0 or 3 < edition:
        raise ValueError("edition needs to be 0-3")

    name_value = 0
    for c in name:
        name_value *= 27
        name_value += 26 if c == ord(" ") else c - ord("A")

    expiration_value = (expiration - datetime.date(2020, 1, 1)).days

    if edition == 0:
        checksum = 0
    elif edition == 1:
        checksum = checksum_bronze(name, calendar.timegm(expiration.timetuple()))
    elif edition == 2:
        checksum = checksum_silver(name, calendar.timegm(expiration.timetuple()))
    elif edition == 3:
        checksum = checksum_gold(name, calendar.timegm(expiration.timetuple()))
    else:
        raise Exception()

    full_value = (
        ((expiration_value & ((1 << 15) - 1)) << 85)  # [99:85]
        | ((checksum & ((1 << 35) - 1)) << 50)  # [84:50]
        | (edition << 48)  # [49:48]
        | (name_value & ((1 << 48) - 1))  # [47:0]
    )

    return encode_base26(full_value)


def checksum_silver(name: bytes, expiration: int) -> int:
    checksum = (0x13371337 ^ (expiration >> 0x23) ^ expiration) & 0x7FFFFFFFF

    for i in range(0, len(name), 2):
        first = name[i]
        second = name[i + 1]
        checksum = (checksum ^ (first << (i * first & 0x3f)) ^ (second << ((i + 1) * second & 0x3f))) & 0x7FFFFFFFF
    
    if len(name) % 2 != 0:
        checksum = (checksum ^ (name[-1] << ((len(name) - 1) * name[-1] & 0x3f))) & 0x7FFFFFFFF
    
    return checksum

def rotate_left(n, d, width=7):
    d %= width
    return ((n << d) | (n >> (width - d))) & ((1 << width) - 1)

def checksum_gold(name: bytes, expiration: int) -> int:
    expiration ^= 0xbf10a0b58afbac17

    a = expiration & 0x7f
    b = (expiration >> 21) & 0x7f
    c = (expiration >> 14) & 0x7f
    d = (expiration >> 28) & 0x7f
    e = (expiration >> 7) & 0x7f

    for i in range(512):
        a = (b ^ a) & 0x7f
        b = (b + 1 + rotate_left(2 * c, i % 4)) & 0x7f
        c = (c + d) & 0x7f
        d = (d ^ e) & 0x7f
        e = (name[i % len(name)] ^ e) & 0x7f
    
    return (e << 28) | (d << 21) | (c << 14) | (b << 7) | a

def encode_base26(value: int) -> str:
    encoded = ""

    while value != 0:
        encoded = string.ascii_uppercase[value % 26] + encoded
        value //= 26

    encoded = "A" * max(0, 24 - len(encoded)) + encoded

    return encoded


if __name__ == "__main__":
    for i, typ in enumerate(['demo', 'bronze', 'silver', 'gold']):
        print(
            typ,
            generate_license(
                sys.argv[1].encode(),
                datetime.date(2026, 8, 1),
                i,
            )
        )
