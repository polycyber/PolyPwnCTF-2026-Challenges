# res = hex(0xc78e - 0x80808080)

strt = "¦"

print(strt)
print(ord(strt))
print(hex(ord(strt)))
print(hex(ord(strt)+0x8080))
print(hex(int(strt.encode().hex(), 16)))
res = hex(int(strt.encode().hex(), 16) - 0x8080)
print("   ", res)

# res = "0x"+hex(ord(' ')).strip("0x")+hex(ord('|')).strip("0x")+hex(ord(' ')).strip("0x")+hex(ord(';')).strip("0x")
res = "0x"
# create = " | ;"
create = " &a"
# create = "| "
for c in create:
    res = res+"{:02x}".format(ord(c))

print("       ", res)
rev = (int(res, 16) + 0x8080)
print(rev.bit_length())
print(hex(rev))
final_rev = rev.to_bytes(length=((rev.bit_length()+7)//8), byteorder='big').decode()
print(final_rev)
# res = hex(int(strt.encode(), 16) - 0x80808080)





# print(res)