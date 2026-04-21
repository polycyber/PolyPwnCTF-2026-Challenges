# NSSHA (1)

## Identifying what we need to do
When reviewing the source code, we can immediately see that the server is able to send us the flag, but hashed using Python's built in `hash()` function.

To understand how this function works, it's best to go see [CPython's implementation](https://github.com/python/cpython/blob/3.14/Python/pyhash.c).

Unfortunately, there seems to be 3 hashing implementations:
- FNV
- Siphash13
- Siphash24

To know which one we are using, we need to identify `Py_HASH_ALGORITHM`. With a bit of Googling, we can identify that this value can be found in [`sys.hash_info`](https://github.com/python/cpython/blob/0575ce936d3f16ce2547ba17d2a22d90369779b5/Python/sysmodule.c#L1568).

We could have also searched the code and find [this snippet](https://github.com/python/cpython/blob/0575ce936d3f16ce2547ba17d2a22d90369779b5/Lib/test/test_sys.py#L671):

```python
# ...

algo = sysconfig.get_config_var("Py_HASH_ALGORITHM")
if sys.hash_info.algorithm in {"fnv", "siphash13", "siphash24"}:
    # ...
```

If we look at the source code again, we can identify that in the menu, there is a secret option 0 to allow debugging. This handler works by printing out `sys.<input>`, or if not found, `os.<input>`, where we control `<input>`.

```
[3] Exit
> 0
> hash_info
sys.hash_info(width=64, modulus=2305843009213693951, inf=314159, nan=0, imag=1000003, algorithm='fnv', hash_bits=64, seed_bits=128, cutoff=0)

[1] Create hash
```

We now know that the hashing algorithm used is `fnv`. However, by looking at Python's source again, we can see that another component that gets hashed is `_Py_HashSecret`.

By searching for references to this variable, we can identify [bootstrap_hash.c](https://github.com/python/cpython/blob/3.14/Python/bootstrap_hash.c). In this file, the initialization is done for the secret, and may be influenced by whether a "hash seed" is present. Looking around, we find that the environment variable `PYTHONHASHSEED` is responsible for setting this value. If we now dump `environ` (to dump `os.environ`), we see that `PYTHONHASHSEED` is `0`.

```
[3] Exit
> 0
> environ
environ({'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'HOSTNAME': '1f4a06ef1a77', 'TERM': 'xterm', 'PYTHONHASHSEED': '0', 'HOME': '/root'})

[1] Create hash
```

## Breaking the hash

To break the hash, it's not recommended to brute force. Even if we know the flag format, its length, and the characters it uses, the search space is still too big.

Given a flag with length 29, and with these characters inside the flag payload: `_acehnorstu`, with the payload being `29 - len('POLYCYBER{}') = 18` bytes long, we are still at `len('_acehnorstu') ** 18 = 5559917313492231481`.

The intended way to solve it was by solving it using Z3 or any other SMT solver.

To do this, we simply rewrite the FNV function with Z3 operations and bit vectors, and, for this challenge, ignore the hash secrets since they will be 0 because `PYTHONHASHSEED=0`.

The reference implementation is in [fnv.py](./fnv.py).

```sh
$ time python fnv.py
b'POLYCYBER{not_so_secure_hash}'
python fnv.py  6.23s user 0.03s system 98% cpu 6.370 total
```

*Note:* As an added bonus, we get no collisions :) Hooray!
