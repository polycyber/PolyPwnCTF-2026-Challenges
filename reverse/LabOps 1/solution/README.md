# Solving

## Opening the WASM

While it's possible to do this challenge with other tools like WABT, it is recommended to use Ghidra for its ease of use and helpful utilities.

However, you need [this plugin](https://github.com/nneonneo/ghidra-wasm-plugin) for WASM to properly import. After that, before doing a first analysis on the binary, make sure to go in the configuration settings for the `Wasm Pre-Analyzer settings`, and set the C stack pointer to 0. This is because the stack pointer is at `.global0`.

## Identifying the license format

When going in the application, we are presented with a popup asking for a 24 character key, and so we will need to find its encoding to properly be able to generate keys.

Fortunately, symbols are avauilable, and so we can simply search for `license` in the list of functions to find relevant functions.

The simplest one we can find is `license_base.LicenseManager.validate`, however this function seems to depend on global states, making isolating certain parts of it a bit more difficult. But we see `LicenseManager` in the name, meaning we need to first identify the struct's layout.

If we go to `license.load`, we can see this code:

```c

void license.load(void)

{
  int iVar1;
  char *jsLicense;
  int jsLicenseLen;
  int iVar2;
  undefined4 *puVar3;
  
  jsLicense = (char *)0x0;
  jsLicenseLen = 0;
  iVar2 = 0;
  if (global_13 == 2) {
    *global_14 = *global_14 + -8;
    jsLicense = *(char **)*global_14;
    jsLicenseLen = ((undefined4 *)*global_14)[1];
    *global_14 = *global_14 + -4;
    iVar2 = *(int *)*global_14;
  }
  if (global_13 == 0) {
    jsLicense = (char *)import::env::emscripten_run_script_string
                                  (s_localStorage.getItem('license')_ram_0001d851);
    if (jsLicense == (char *)0x0) {
      return;
    }
    iVar1 = 0;
    do {
      jsLicenseLen = iVar1;
      iVar1 = jsLicenseLen + 1;
    } while (jsLicense[jsLicenseLen] != '\0');
  }
  if ((global_13 == 0 || iVar2 == 0) &&
     (license_base.LicenseManager.load(jsLicense,jsLicenseLen), global_13 == 1)) {
    *(undefined4 *)*global_14 = 0;
    *global_14 = *global_14 + 4;
    puVar3 = (undefined4 *)*global_14;
    *puVar3 = jsLicense;
    puVar3[1] = jsLicenseLen;
    *global_14 = *global_14 + 8;
    return;
  }
  return;
}
```

It seems to load a license key from the browser's local storage and send it off to `license_base.LicenseManager.load`. Now looking at `license_base.LicenseManager.load`, we see this:

```c
void license_base.LicenseManager.load(byte *license_key,int license_key_len)
{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = 0;
  iVar2 = 0;
  if (global_13 == 2) {
    *global_14 = *global_14 + -4;
    uVar1 = *(undefined4 *)*global_14;
    *global_14 = *global_14 + -4;
    iVar2 = *(int *)*global_14;
  }
  if ((global_13 == 0) && (license_key_len != 0)) {
    do {
      license_base.LicenseManager.advance((uint)*license_key);
      license_key = license_key + 1;
      license_key_len = license_key_len + -1;
    } while (license_key_len != 0);
  }
  if ((global_13 == 0 || iVar2 == 0) && (license_base.LicenseManager.validate(), global_13 == 1)) {
    *(undefined4 *)*global_14 = 0;
    *global_14 = *global_14 + 4;
    *(undefined4 *)*global_14 = uVar1;
    *global_14 = *global_14 + 4;
    return;
  }
  return;
}
```

The flow seems to be to `.advance` for every character in the license key, and then validate. If we checkout this function:

```c
void fixed_string.FixedString(24).push(undefined4 param1)
{
  undefined1 *puVar1;
  
  if (DAT_ram_00032db0 < 0x18) {
    puVar1 = &DAT_ram_00032db4 + DAT_ram_00032db0;
    DAT_ram_00032db0 = DAT_ram_00032db0 + 1;
    *puVar1 = (undefined1)param1;
  }
  return;
}

void license_base.LicenseManager.advance(undefined4 param1)
{
  int iVar1;
  
  iVar1 = global_13;
  fixed_string.FixedString(24).push(param1);
  if (global_13 == iVar1) {
    return;
  }
  do {
    halt_trap();
  } while( true );
}
```

From this, we can say that `DAT_ram_00032db0` is probably the length of the fixed width string, and `DAT_ram_00032db4` is where the data starts.

```c
void fixed_string.FixedString(24).push(undefined4 param1)
{
  char *pcVar1;
  
  if (g_license_key.length < 0x18) {
    pcVar1 = g_license_key.data + g_license_key.length;
    g_license_key.length = g_license_key.length + 1;
    *pcVar1 = (char)param1;
  }
  return;
}
```

After that, in `license_base.LicenseManager.validate`, we have a slightly bigger function.

The first interesting part seems to be here:

```c
if (g_license_key.length != 0x18) {
    uVar1 = 0x42;
    goto code_r0x80097d4a;
}
license_base.parseUnsignedBase26__anon_5795(param1,g_license_key.data,0x18);
```

We validate that the license is actually 24 characters, and then we parse an unsigned int in base 26.

```c

void license_base.parseUnsignedBase26__anon_5795
               (astruct *param1,char *string_value,int string_value_len)

{
  undefined2 uVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  int iVar4;
  ulonglong low;
  ulonglong high;
  byte cur_value;
  ulonglong uVar5;
  ulonglong local_20;
  ulonglong local_18;
  undefined1 local_10;
  char cur_char;
  
  iVar4 = global_13;
  if (string_value_len == 0) {
    low = 0;
    high = 0;
  }
  else {
    low = 0;
    high = 0;
    do {
      if (low == 0 && (high & 0xffffffffffffff) == 0) {
        uVar5 = 0;
        high = 0;
      }
      else {
        __multi3(&local_20,low,0,26,0);
        if (global_13 != iVar4) {
          do {
            halt_trap();
          } while( true );
        }
        uVar5 = local_18 + (high & 0xffffffffffffff) * 26;
        high = local_20;
        if (uVar5 >> 56 != 0 || uVar5 < local_18) {
          *(undefined2 *)&param1->error = 51;
          return;
        }
      }
      cur_char = *string_value;
      cur_value = cur_char + 191;
      if ((25 < (byte)(cur_char + 191U)) &&
         (cur_value = cur_char + 0x9f, 0x19 < (byte)(cur_char + 0x9fU))) {
        param1->field6_0x18 = DAT_ram_00023bb8;
        param1->error = DAT_ram_00023bb0;
        uVar1 = DAT_ram_00023ba8._4_2_;
        uVar2 = DAT_ram_00023ba8._6_1_;
        uVar3 = DAT_ram_00023ba8._7_1_;
        param1->high_8 = (undefined4)DAT_ram_00023ba8;
        param1->high_10 = uVar1;
        param1->high_11 = uVar2;
        param1->field_0xf = uVar3;
        param1->low = DAT_ram_00023ba0;
        return;
      }
      low = high + cur_value;
      high = (uVar5 & 0xffffffffffffff) + (ulonglong)(low < high);
      local_10 = (high & 0xffffffffffffff) != high;
      if ((bool)local_10) {
        *(undefined2 *)&param1->error = 0x33;
        return;
      }
      string_value = string_value + 1;
      string_value_len = string_value_len + -1;
    } while (string_value_len != 0);
  }
  param1->low = low;
  *(undefined2 *)&param1->error = 0;
  param1->high_8 = (uint)high;
  param1->high_11 = (byte)(high >> 0x30);
  param1->high_10 = (ushort)(high >> 0x20);
  return;
}
```

The return value in this case seems to be in `param1`. We can also see it seems to be some kind of array or structure that's around 32 bytes.
Interestingly, we seem to have two possible outputs, one of which assigns a bunch of constants, and the other setting to actual variables.

As an aside, you can use Zig to convert Zig to C with error values to see how the binary representation looks like, but I will skip this by mentioning that the situation where constants are assigned seems to be right after a comparison with a lot of bounds, probably checking for an error (maybe the string is too big).

We can then say that that member of the structure is an error code.

Also, we should note that a base 26 value made up of only letters can go up to 85 bits or 11 bytes (`log2(26 ** 18 - 1)`). This seems to fit perfectly in the remainder of the data set in the success case (4 + 4 + 2 + 1).

The first part of the code after parsing the value looks like this:

```c
license_base.parseUnsignedBase26__anon_5795(param1,g_license_key.data,0x18);
stack0xfffffff0 = 0;
name.length = 0;
name.data[0] = '\0';
name.data[1] = '\0';
name.data[2] = '\0';
name.data[3] = '\0';
high = (ulonglong)parsed_value.high_8 |
        (ulonglong)parsed_value.high_11 << 48 | (ulonglong)parsed_value.high_10 << 32;
expiration = (high >> 0x15 & 0x7fff) * 86400 + 1577836800;
low = parsed_value.low;
if ((parsed_value.low & 0xffffffffffff) != 0) {
  do {
    uVar10 = parsed_value.low & 0xffffffffffff;
    rshift_base_27 = uVar10 / 27;
    val_mod_27 = (int)parsed_value.low + (int)rshift_base_27 * -27;
    name_char = L' ';
    if ((val_mod_27 & 0xff) != 26) {
        name_char = val_mod_27 + L'A';
    }
    fixed_string.FixedString(10).push_front(&name,name_char);
    parsed_value.low = rshift_base_27;
  } while (26 < uVar10);
}
```

After some renaming, the logic can be identified.

For the timestamp, we can deduce it is the number of days since 2020-01-01, since if we search Google for 86400 we will find it's the number of seconds per day, and 1577836800 represents the timestamp in seconds for 2020-01-01.

After that, we see some conversion to letters or a space, which is probably for the name associated with the license key.

The next part looks something like this:

```c
smth1 = &param1[1].high_10;
smth2 = param1[1].high_8;
uVar9 = param1[1].low;
uVar10 = low >> 0x32 | high << 0xe;
uVar6 = *(uint *)(&DAT_ram_0002b108 + ((byte)param1[1].field6_0x18 & 3 ^ 2) * 4);
```

Until now, we haven't seen `param1` be set beyond what we had defined earlier. If we look at how it's set, we can see it's an optimization artifact:

```c
astruct parsed_value;
longlong expiration;
FixedString10 name;

...

param1 = &parsed_value;
```

As we can see, `param1[1]` is probably referring to the next values on the stack. A simple fix is to just add those variables as members in the struct.

Adding the fields to the struct now yields this decompilation:

```c
name_data = (param1->name).data;
name_length = (param1->name).length;
expiration = param1->expiration;
uVar9 = low >> 50 | high << 14;
uVar6 = *(uint *)(&DAT_ram_0002b108 + (*(byte *)((int)&param1[1].low + 2) & 3 ^ 2) * 4);

...

(uVar2 = (**(code **)((ulonglong)uVar6 * 4))(name_data,name_length,expiration,uVar9),
```

The important part here is the uVar6 function we need to decode. If we ignore how it's computed, and simply look at the data being offseted, we can see this:

```c
                             UINT_ARRAY_ram_0002b108                         XREF[2]:     license_base.LicenseManager.vali
                                                                                          license_base.LicenseManager.vali
    ram:0002b108 50 01 00        uint[4]
                 00 51 01 
                 00 00 52 
       ram:0002b108 [0]                    150h,         151h,         152h,         153h
```

Now if we multiply the `150h` by 4 to find what this ends up being, we find it is `0x540`. Also, by looking at the assembly, we see that this offset is relative to `table0`:

```c
ram:80097c8a 11 15 00        call_ind   type=0x15 table0
```

Going in `table0` at that offset:

```c
table0:00000540 07 ae 0b 80     addr      license_base.validateSilver  [336]
table0:00000544 c3 ae 0b 80     addr      license_base.validateGold    [337]
table0:00000548 49 ad 0b 80     addr      license_base.validateDemo    [338]
table0:0000054c 5e ad 0b 80     addr      license_base.validateBronze  [339]
```

Thus, we can conclude that whatever is referenced in `(int)&param1[1].low + 2` is probably the edition of the license. If we add some more bytes in the structure defined before, we get a nicer decompilation:

```c
aStack_40.field10_0x38._0_1_ = (byte)(aStack_40.low >> 0x30) & 3;

...

uVar5 = UINT_ARRAY_ram_0002b108[(byte)param1->field10_0x38 & 3 ^ 2];
```

From this, we can start to rebuild the structure of the key (from low to high):

- name (48 bits)
- edition (2 bits)
- checksum (35 bits, since we know it's the top 14 bits of the lower part, and the next field starts at `high >> 21`)
- timestamp in days since 2020-01-01 (15 bits)

All in all, we get a total of 100 bits.

*Note: For the checksum field, we can deduce it by seeing what the handlers for each license edition does. They usually seem to compare or compute that value.*

If we write a simply Python script to encode this:

```python
import calendar
import string
import datetime

def encode_base26(value: int) -> str:
    encoded = ""

    while value != 0:
        encoded = string.ascii_uppercase[value % 26] + encoded
        value //= 26

    encoded = "A" * max(0, 24 - len(encoded)) + encoded

    return encoded

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
```

## Bronze

If we decompile the `license_base.validateBronzeLicense` function, we see something like this:

```c
uint license_base.validateBronzeLicense
               (byte *name,int name_len,ulonglong expiration,ulonglong checksum)

{
  ulonglong uVar1;
  int iVar2;
  uint uVar3;
  ulonglong uVar4;
  byte cur_char;
  
  uVar1 = 0x28ac91b93;
  if (name_len != 0) {
    uVar3 = 0;
    iVar2 = 35;
    do {
      cur_char = *name;
      uVar4 = (ulonglong)(cur_char >> ((ulonglong)(iVar2 + (uVar3 / 0x23) * 0x23) & 0x3f));
      if (uVar3 % 0x23 == 0) {
        uVar4 = 0;
      }
      uVar1 = uVar1 ^ (uVar4 | (ulonglong)cur_char << uVar3 % 0x23) ^ (ulonglong)cur_char;
      name = name + 1;
      iVar2 = iVar2 + -7;
      uVar3 = uVar3 + 7;
      name_len = name_len + -1;
    } while (name_len != 0);
  }
  return (uint)(((((expiration & 0x3ff) - (expiration >> 10 & 0x1fff)) + uVar1) *
                 (expiration >> 0x17 & 0xfffff) + (expiration >> 0x2b) & 0x7ffffffff) ==
               (checksum & 0x7ffffffff));
}
```

While we could go ahead and reverse a seemingly complex loop, we can first take a step back to see what we need to do. In this case, the function computes a checksum based on `name` and `expiration`, and compares it with the provided checksum.

We can then simply copy-paste the logic and use the provided checksum.

In Python, it could look something like:

```python

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
```

## Silver

Looking at `license_bse.validateSilverLicense`:

```c
uint license_base.validateSilverLicense
               (char *name,uint name_len,ulonglong expiration,ulonglong checksum)

{
  int i;
  uint first;
  uint second;
  
  if (name_len != 0) {
    first = name_len;
    if ((name_len & 1) != 0) {
      first = name_len - 1;
      checksum = (ulonglong)(uint)(byte)name[first] << (first * (byte)name[first] & 0x3e) ^ checksum
      ;
    }
    if (name_len != 1) {
      i = first - 2;
      do {
        first = (uint)(byte)name[i];
        second = (uint)(byte)(name + i)[1];
        checksum = (ulonglong)first << (i * first & 0x3f) ^
                   (ulonglong)second << ((i + 1) * second & 0x3f) ^ checksum;
        i = i + -2;
      } while (i != -2);
    }
  }
  return (uint)(((checksum ^ expiration >> 35 ^ expiration) & 0x7ffffffff) == 0x13371337);
}
```

In this case, we seem to reverse the provided checksum so that it matches a starting value.

If we go step by step in reverse:

```python
def checksum_silver(name: bytes, expiration: int) -> int:
    checksum = (0x13371337 ^ (expiration >> 0x23) ^ expiration) & 0x7FFFFFFFF
```

After that, the name is split into 2 byte chunks and each byte is shifted and xored with the checksum: (also note the order, when decoding we go from i=len-1 -> i = 0)

```python
def checksum_silver(name: bytes, expiration: int) -> int:
    checksum = (0x13371337 ^ (expiration >> 0x23) ^ expiration) & 0x7FFFFFFFF

    for i in range(0, len(name), 2):
        first = name[i]
        second = name[i + 1]
        checksum = (checksum ^ (first << (i * first & 0x3f)) ^ (second << ((i + 1) * second & 0x3f))) & 0x7FFFFFFFF
    
    if len(name) % 2 != 0:
        checksum = (checksum ^ (name[-1] << ((len(name) - 1) * name[-1] & 0x3f))) & 0x7FFFFFFFF
    
    return checksum
```

Combining our previous encoding and checksum solver, we can generate license keys and view the flag in the app :)

## Gold

For the gold license, we can go to the `license_base.validateGoldLicense` function.

After setting up the arguments (`byte *name,uint name_len,ulonglong expiration,ulonglong checksum`), we should get a decompilation like so:

```c

uint license_base.validateGoldLicense
               (byte *name,uint name_len,ulonglong expiration,ulonglong checksum)

{
  uint i;
  uint u7_b;
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  byte u7_a;
  byte u7_c;
  byte u7_d;
  byte u7_e;
  
  u7_b = (uint)checksum;
  u7_a = (byte)checksum & 0x7f;
  u7_d = (byte)(u7_b >> 21) & 0x7f;
  u7_e = (byte)(checksum >> 28) & 0x7f;
  u7_c = (byte)(u7_b >> 14) & 0x7f;
  u7_b = u7_b >> 7 & 0x7f;
  i = 0x1ff;
  do {
    uVar1 = (name[i % name_len] ^ u7_e) & 0x7f;
    u7_e = (byte)uVar1;
    uVar4 = uVar1 ^ 0xffffffff;
    uVar2 = ((uVar1 * 0x104 + uVar4 * -0x3ae088fd) - (uint)u7_d) + (u7_d & uVar4) * 2 + 3 & 0x7f;
    u7_d = (byte)uVar2;
    uVar7 = (uint)u7_c;
    uVar8 = uVar2 ^ 0xffffffff;
    uVar3 = -uVar2;
    uVar5 = uVar3 & uVar2;
    uVar6 = uVar2 ^ uVar1;
    uVar9 = uVar2 | uVar7;
    uVar10 = uVar2 - 1;
    uVar3 = uVar4 * -0x5697fbe1 + uVar1 * -0x31a78f34 + uVar7 * -0x5c016e2e +
            (uVar7 & uVar1) * 0x5586294d + uVar2 * -0x27719a96 + uVar8 * 0x554354c9 +
            (uVar7 ^ uVar1) * -0x591d94ea + (uVar7 & uVar4 ^ uVar8) * -0x39ceb103 +
            (uVar2 ^ uVar3) * -0x19a1b247 + (uVar2 & uVar7) * 0x57ab0103 +
            (uVar3 & uVar7) * 0x1742b319 + (uVar5 & uVar1) * 0x7c4c6e99 +
            (uVar6 & uVar9 ^ 0xffffffff) * -0x2fb586ed +
            ((uVar7 | uVar1) ^ uVar10 ^ 0xffffffff) * -0x257d6f5 + (uVar5 ^ uVar8) * 0x6b6f85be +
            (uVar3 & uVar1 ^ uVar7) * 0x7da8290b + ((uVar3 | uVar1) ^ uVar2) * 0x4d2e9235 +
            (uVar7 ^ 0xffffffff | uVar4 | uVar6) * 0x19 + ((uVar6 | uVar5) ^ 0xffffffff) * 0x54 +
            ((uVar2 & uVar1 | uVar3) ^ uVar4) * 0x11 + (uVar2 | uVar1 | uVar7 | uVar10) * 0x1b +
            ((uVar3 ^ uVar7 | uVar10) & ((uVar2 | uVar1) ^ 0xffffffff)) * 0x1e +
            (((uVar9 ^ uVar3) & (uVar3 ^ uVar7)) - ((uVar9 | uVar3 & uVar1) ^ uVar3)) * 3 + 0x6d &
            0x7f;
    u7_c = (byte)uVar3;
    uVar4 = (uint)u7_a;
    uVar5 = uVar4 ^ 0xffffffff;
    uVar6 = (i & 3) + 1;
    uVar6 = ((uVar3 >> (uVar6 ^ 7) | uVar3 << uVar6) ^ 0xffffffff) & 0x7f;
    uVar7 = uVar4 & u7_b;
    uVar9 = uVar4 ^ uVar2;
    uVar10 = uVar6 | uVar4;
    u7_b = u7_b * -0xb81c2a6 + (u7_b ^ 0xffffffff) * -0x219ad35a + uVar8 * -0x5697fbe1 +
           uVar2 * -0x31a78f34 + uVar4 * -0x115889e2 + uVar5 * 0x554354c9 +
           (uVar4 ^ u7_b) * -0x19a1b247 + ((uVar2 | u7_b) ^ uVar4) * 0x4d2e9235 +
           uVar6 * -0x5c016e2e + (uVar7 & uVar2) * 0x7c4c6e99 + (uVar7 ^ uVar5) * 0x6b6f85be +
           (uVar6 & uVar4) * 0x57ab0103 + (uVar2 & u7_b ^ uVar6) * 0x7da8290b +
           (uVar6 & uVar2) * 0x5586294d + (uVar6 & u7_b) * 0x1742b319 +
           ((uVar9 | uVar7) ^ 0xffffffff) * 0x54 + (uVar6 ^ uVar2) * -0x591d94ea +
           (uVar10 & uVar9 ^ 0xffffffff) * -0x2fb586ed + ((uVar6 | uVar2) ^ u7_b) * -0x257d6f5 +
           ((uVar4 & uVar2 | u7_b) ^ uVar8) * 0x67964091 + (uVar6 & uVar8 ^ uVar5) * -0x39ceb103 +
           (uVar6 | u7_b ^ 0xffffffff | uVar4 | uVar2) * 0x1b +
           (uVar6 ^ 0xffffffff | uVar8 | uVar9) * 0x19 +
           ((uVar6 & u7_b | uVar4 | uVar2) ^ 0xffffffff) * 0x1e +
           (((uVar10 ^ u7_b) & (uVar6 ^ u7_b)) - ((uVar10 | uVar2 & u7_b) ^ u7_b)) * 3 + 0x13 & 0x7f
    ;
    u7_a = (byte)u7_b ^ u7_a;
    i = i - 1;
  } while (i != 0xffffffff);
  uVar4 = 0;
  i = (uint)(expiration ^ 0xbf10a0b58afbac17);
  if ((((uVar1 == (i >> 7 & 0x7f)) &&
       (uVar2 == ((uint)((expiration ^ 0xbf10a0b58afbac17) >> 0x1c) & 0x7f))) &&
      (uVar3 == (i >> 0xe & 0x7f))) && (u7_b == (i >> 0x15 & 0x7f))) {
    uVar4 = (uint)((uint)u7_a == (i & 0x7f));
  }
  return uVar4;
}
```

From what we can see, this seems like a complex algorithm. Firstly, we see the checksum is split into 7 bit chunks which I renamed to `u7_a`, `u7_b`, etc. These chunks then follow 512 iterations of assignments until we verify that the checksum matches with the expiration at the end.

The complex operations seen on the assignments to `u7_b` and `uVar3` seem quite complex, but are usually a result of mixed boolean arithmetic, where we add a lot of useless operations to a simple operation to make it seem complex.

A simple example for `a + b`:

```c
a + b = a + b * 1 = a + b * (77 - 76 + c * (d ^ d)) = ...
```

This loop continues on and on until you have a complex enough operation. More info about this technique can be found [here](https://plzin.github.io/posts/mba).

If you have already seen the internals of a hashing algorithm, this algorithm can also seem familiar as this function seems to be reversing a hash to validate its input, and the body of the hash (a = b, b = c, etc.) is similar to those seen in hashing functions.

### Reversing the body

The structure of the loop looks a bit like this

```c
u7_e = ...;
u7_d = ...;
u7_c = ...;
u7_b = ...;
u7_a = ...;
```

This helps us by making us able to islate each assignment and reverse each.

#### `u7_e`

`u7_e` is probably the easiest operation, as it only involves these operations:

```c
uVar1 = (name[i % name_len] ^ u7_e) & 0x7f;
u7_e = (byte)uVar1;
```

We can then say that:

```c
new_e = (name[i % name_len] ^ old_e) & 0x7f
```

#### `u7_d`

```c
uVar4 = uVar1 ^ 0xffffffff;
uVar2 = ((uVar1 * 0x104 + uVar4 * -0x3ae088fd) - (uint)u7_d) + (u7_d & uVar4) * 2 + 3 & 0x7f;
u7_d = (byte)uVar2;
```

If we create a basic C program with these operations, we can quickly see what the true operation really is:

```c
uint8_t op_d(uint8_t u7_d, uint32_t uVar1) {
    uint32_t uVar4 = uVar1 ^ 0xffffffff;
    uint8_t uVar2 = ((uVar1 * 0x104 + uVar4 * -0x3ae088fd) - (uint)u7_d) + (u7_d & uVar4) * 2 + 3 & 0x7f;

    printf("op_c: u7_d=%u (0x%x), uVar1=%u (0x%x) -> %u (0x%x)\n", u7_d, u7_d, uVar1, uVar1, uVar2, uVar2);

    return uVar2;
}

int main() {
    op_c(1, 0);
    op_c(0, 1);
    op_c(0, 0);
    op_c(1, 1);
    op_c(26, 92);
    printf("%u\n", 26 ^ 92);

    return 0;
}
```

Which will print:

```c
op_d: u7_d=1 (0x1), uVar1=0 (0x0) -> 1 (0x1)
op_d: u7_d=0 (0x0), uVar1=1 (0x1) -> 1 (0x1)
op_d: u7_d=0 (0x0), uVar1=0 (0x0) -> 0 (0x0)
op_d: u7_d=1 (0x1), uVar1=1 (0x1) -> 0 (0x0)
op_d: u7_d=26 (0x1a), uVar1=92 (0x5c) -> 70 (0x46)
70
```

We can then say that:

```c
new_d = old_d ^ uVar1 = (old_d ^ new_e) & 0x7f;
```

#### `u7_c`

For `u7_c`, we presented with a pretty big operation. If we isolate it and all its dependent variables that were optimzied out we get this program:
*Note: The optimized out variables are precomputed variables. For instance, if we do `a ^ b` multiple times in the expression, the compiler might optimize by setting a variable `c = a ^ b` before it and using `c` instead of always recomputing.*

```c
uint8_t op_c(uint8_t u7_d, uint8_t u7_c, uint32_t uVar1) {
    uint32_t uVar4 = uVar1 ^ 0xffffffff;
    uint32_t uVar2 = ((uVar1 * 0x104 + uVar4 * -0x3ae088fd) - (uint)u7_d) + (u7_d & uVar4) * 2 + 3 & 0x7f;
    u7_d = (uint8_t)uVar2;

    uint32_t uVar7 = (uint)u7_c;
    uint32_t uVar8 = uVar2 ^ 0xffffffff;
    uint32_t uVar3 = -uVar2;
    uint32_t uVar5 = uVar3 & uVar2;
    uint32_t uVar6 = uVar2 ^ uVar1;
    uint32_t uVar9 = uVar2 | uVar7;
    uint32_t uVar10 = uVar2 - 1;
    uint32_t result = uVar4 * -0x5697fbe1 + uVar1 * -0x31a78f34 + uVar7 * -0x5c016e2e +
            (uVar7 & uVar1) * 0x5586294d + uVar2 * -0x27719a96 + uVar8 * 0x554354c9 +
            (uVar7 ^ uVar1) * -0x591d94ea + (uVar7 & uVar4 ^ uVar8) * -0x39ceb103 +
            (uVar2 ^ uVar3) * -0x19a1b247 + (uVar2 & uVar7) * 0x57ab0103 +
            (uVar3 & uVar7) * 0x1742b319 + (uVar5 & uVar1) * 0x7c4c6e99 +
            (uVar6 & uVar9 ^ 0xffffffff) * -0x2fb586ed +
            ((uVar7 | uVar1) ^ uVar10 ^ 0xffffffff) * -0x257d6f5 + (uVar5 ^ uVar8) * 0x6b6f85be +
            (uVar3 & uVar1 ^ uVar7) * 0x7da8290b + ((uVar3 | uVar1) ^ uVar2) * 0x4d2e9235 +
            (uVar7 ^ 0xffffffff | uVar4 | uVar6) * 0x19 + ((uVar6 | uVar5) ^ 0xffffffff) * 0x54 +
            ((uVar2 & uVar1 | uVar3) ^ uVar4) * 0x11 + (uVar2 | uVar1 | uVar7 | uVar10) * 0x1b +
            ((uVar3 ^ uVar7 | uVar10) & ((uVar2 | uVar1) ^ 0xffffffff)) * 0x1e +
            (((uVar9 ^ uVar3) & (uVar3 ^ uVar7)) - ((uVar9 | uVar3 & uVar1) ^ uVar3)) * 3 + 0x6d &
            0x7f;
    ;

    printf("u7_d: %u, u7_c: %u, uVar1: %u -> %u\n", u7_d, u7_c, uVar1, result);

    return result;
}

int main() {
    op_c(0, 0, 0);
    op_c(1, 0, 0);
    op_c(2, 0, 0);
    op_c(3, 0, 0);

    puts("");

    op_c(0, 5, 0);
    op_c(1, 5, 0);
    op_c(2, 5, 0);
    op_c(3, 5, 0);

    puts("");

    op_c(0, 20, 10);
    op_c(1, 20, 10);
    op_c(2, 20, 10);
    op_c(3, 20, 10);

    return 0;
}
```

Ad we get the following output:

```c
u7_d: 0, u7_c: 0, uVar1: 0 -> 0
u7_d: 1, u7_c: 0, uVar1: 0 -> 127
u7_d: 2, u7_c: 0, uVar1: 0 -> 126
u7_d: 3, u7_c: 0, uVar1: 0 -> 125

u7_d: 0, u7_c: 5, uVar1: 0 -> 5
u7_d: 1, u7_c: 5, uVar1: 0 -> 4
u7_d: 2, u7_c: 5, uVar1: 0 -> 3
u7_d: 3, u7_c: 5, uVar1: 0 -> 2

u7_d: 10, u7_c: 20, uVar1: 10 -> 10
u7_d: 11, u7_c: 20, uVar1: 10 -> 9
u7_d: 8, u7_c: 20, uVar1: 10 -> 12
u7_d: 9, u7_c: 20, uVar1: 10 -> 11
```

While `u7_d` is computed from within this function, if we only base ourselves on the results, we can see that the operation is actually `u7_c - u7_d` on 7 bits.

Thus, we conclude that:

```c
new_c = (old_c - new_d) & 0x7f;
```

#### `u7_b`

By doing similar steps to `u7_c`, we isolate the block that calculates `u7_b` to identify the variables with an impact:

```c
uint8_t op_b(uint8_t u7_a, uint32_t i, uint8_t u7_c, uint8_t u7_b, uint8_t u7_d) {
    uint32_t uVar3 = u7_c;
    uint32_t uVar2 = u7_d;

    uint32_t uVar8 = uVar2 ^ 0xffffffff;

    uint32_t uVar4 = (uint)u7_a;
    uint32_t uVar5 = uVar4 ^ 0xffffffff;
    uint32_t uVar6 = (i & 3) + 1;
    uVar6 = ((uVar3 >> (uVar6 ^ 7) | uVar3 << uVar6) ^ 0xffffffff) & 0x7f;
    uint32_t uVar7 = uVar4 & u7_b;
    uint32_t uVar9 = uVar4 ^ uVar2;
    uint32_t uVar10 = uVar6 | uVar4;
    uint8_t result = u7_b * -0xb81c2a6 + (u7_b ^ 0xffffffff) * -0x219ad35a + uVar8 * -0x5697fbe1 +
           uVar2 * -0x31a78f34 + uVar4 * -0x115889e2 + uVar5 * 0x554354c9 +
           (uVar4 ^ u7_b) * -0x19a1b247 + ((uVar2 | u7_b) ^ uVar4) * 0x4d2e9235 +
           uVar6 * -0x5c016e2e + (uVar7 & uVar2) * 0x7c4c6e99 + (uVar7 ^ uVar5) * 0x6b6f85be +
           (uVar6 & uVar4) * 0x57ab0103 + (uVar2 & u7_b ^ uVar6) * 0x7da8290b +
           (uVar6 & uVar2) * 0x5586294d + (uVar6 & u7_b) * 0x1742b319 +
           ((uVar9 | uVar7) ^ 0xffffffff) * 0x54 + (uVar6 ^ uVar2) * -0x591d94ea +
           (uVar10 & uVar9 ^ 0xffffffff) * -0x2fb586ed + ((uVar6 | uVar2) ^ u7_b) * -0x257d6f5 +
           ((uVar4 & uVar2 | u7_b) ^ uVar8) * 0x67964091 + (uVar6 & uVar8 ^ uVar5) * -0x39ceb103 +
           (uVar6 | u7_b ^ 0xffffffff | uVar4 | uVar2) * 0x1b +
           (uVar6 ^ 0xffffffff | uVar8 | uVar9) * 0x19 +
           ((uVar6 & u7_b | uVar4 | uVar2) ^ 0xffffffff) * 0x1e +
           (((uVar10 ^ u7_b) & (uVar6 ^ u7_b)) - ((uVar10 | uVar2 & u7_b) ^ u7_b)) * 3 + 0x13 & 0x7f
    ;

    printf("u7_a: %u, i: %u, u7_c: %u, u7_b: %u, u7_d: %u -> %u\n", u7_a, i, u7_c, u7_b, u7_d, result);

    return result;
}

int main() {
    op_b(5, 5, 5, 5, 5);
    op_b(10, 5, 5, 5, 5);
    op_b(5, 10, 5, 5, 5);
    op_b(5, 5, 10, 5, 5);
    op_b(5, 5, 5, 10, 5);
    op_b(5, 5, 5, 5, 10);

    return 0;
}
```

Which prints:

```c
u7_a: 5, i: 5, u7_c: 5, u7_b: 5, u7_d: 5 -> 112
u7_a: 10, i: 5, u7_c: 5, u7_b: 5, u7_d: 5 -> 112
u7_a: 5, i: 10, u7_c: 5, u7_b: 5, u7_d: 5 -> 92
u7_a: 5, i: 5, u7_c: 10, u7_b: 5, u7_d: 5 -> 92
u7_a: 5, i: 5, u7_c: 5, u7_b: 10, u7_d: 5 -> 117
u7_a: 5, i: 5, u7_c: 5, u7_b: 5, u7_d: 10 -> 112
```

We can see that `i`, `u7_c` and `u7_b` all have an impact, so we can discard the others.

If we add a few more testcases:

```c
op_b(0, 0, 0, 0, 0);

puts("");

op_b(0, 0, 0, 10, 0);
op_b(0, 0, 0, 20, 0);

puts("");

op_b(0, 0, 10, 0, 0);
op_b(0, 1, 10, 0, 0);
op_b(0, 2, 10, 0, 0);
op_b(0, 3, 10, 0, 0);
op_b(0, 4, 10, 0, 0);
op_b(0, 5, 10, 0, 0);
op_b(0, 6, 10, 0, 0);

puts("");

op_b(0, 4, 10, 5, 0);

puts("");

op_b(0, 0, 0, 0, 0);
op_b(0, 0, 10, 0, 0);
op_b(0, 0, 15, 0, 0);
op_b(0, 1, 0, 0, 0);
op_b(0, 1, 10, 0, 0);
op_b(0, 1, 15, 0, 0);
```

We get the following:

```c
u7_a: 0, i: 0, u7_c: 0, u7_b: 0, u7_d: 0 -> 127

u7_a: 0, i: 0, u7_c: 0, u7_b: 10, u7_d: 0 -> 9
u7_a: 0, i: 0, u7_c: 0, u7_b: 20, u7_d: 0 -> 19

u7_a: 0, i: 0, u7_c: 10, u7_b: 0, u7_d: 0 -> 107
u7_a: 0, i: 1, u7_c: 10, u7_b: 0, u7_d: 0 -> 87
u7_a: 0, i: 2, u7_c: 10, u7_b: 0, u7_d: 0 -> 47
u7_a: 0, i: 3, u7_c: 10, u7_b: 0, u7_d: 0 -> 94
u7_a: 0, i: 4, u7_c: 10, u7_b: 0, u7_d: 0 -> 107
u7_a: 0, i: 5, u7_c: 10, u7_b: 0, u7_d: 0 -> 87
u7_a: 0, i: 6, u7_c: 10, u7_b: 0, u7_d: 0 -> 47

u7_a: 0, i: 4, u7_c: 10, u7_b: 5, u7_d: 0 -> 112

u7_a: 0, i: 0, u7_c: 0, u7_b: 0, u7_d: 0 -> 127
u7_a: 0, i: 0, u7_c: 10, u7_b: 0, u7_d: 0 -> 107
u7_a: 0, i: 0, u7_c: 15, u7_b: 0, u7_d: 0 -> 97
u7_a: 0, i: 1, u7_c: 0, u7_b: 0, u7_d: 0 -> 127
u7_a: 0, i: 1, u7_c: 10, u7_b: 0, u7_d: 0 -> 87
u7_a: 0, i: 1, u7_c: 15, u7_b: 0, u7_d: 0 -> 67
```

From this, we can conclude that `u7_b` is probably getting added as is, while `u7_c` and `i` are binded together somehow.

By converting these numbers to binary, we can see a pattern emerge:

```python
>>> f'{107:07b}' # i = 0, 4 : u7_c = 10
'1101011'
>>> f'{87:07b}' # i = 1, 5 : u7_c = 10
'1010111'
>>> f'{47:07b}' # i = 2, 6 : u7_c = 10
'0101111'
>>> f'{94:07b}' # i = 3 : u7_c = 10
'1011110'

>>> f'{87:07b}' # i = 1, u7_c = 10
'1010111'
>>> f'{67:07b}' # i = 1, u7_c = 15
'1000011'
```

As we can see, the bits are being rotated by a certain amount. In the 107 case, there is no shift (127 - 2 * 10 = 107), but in the 87 case for instance, we shift the result of the subtraction by 1.

As we can see, this happens a certain number of times before it resets. Indeed, it seems like it rotates left a maximum of 4 bits before wrapping back.

If we try to build the expression, we get something like this:

```c
new_b = (old_b - 1 - rotate_left(2 * new_c, i % 4)) & 0x7f
```

#### `u7_a`

For `u7_a`, it is quite simple, and is just:

```c
new_a = (new_b ^ old_a) & 0x7f
```

### Building the keygen

If we rebuild the operation from above, we get something like this (simplified):

```c
bool isValid() {
    u7_a = (checksum >> 0) & 0x7f;
    u7_b = (checksum >> 7) & 0x7f;
    u7_c = (checksum >> 14) & 0x7f;
    u7_d = (checksum >> 21) & 0x7f;
    u7_e = (checksum >> 28) & 0x7f;

    for (int i = 511; i >= 0; i--) {
        u7_e = name[i % len(name)] ^ u7_e;
        u7_d = u7_d ^ u7_e;
        u7_c = u7_c - u7_d;
        u7_b = u7_b - 1 - rotate_left(2 * u7_c, i % 4);
        u7_a = u7_b ^ u7_a;
    }


    modified_expiration = expiration ^ 0xbf10a0b58afbac17;

    return (
        u7_e == ((modified_expiration >> 7) & 0x7f) &&
        u7_d == ((modified_expiration >> 28) & 0x7f) &&
        u7_c == ((modified_expiration >> 15) & 0x7f) &&
        u7_b == ((modified_expiration >> 21) & 0x7f) &&
        u7_a == (modified_expiration & 0x7f)
    );
}
```

With this, we can then try to find a checksum for a given name and expiration by reversing this algorithm:

```python
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
```
