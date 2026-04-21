from sage.all import *
from Crypto.Util.number import long_to_bytes, inverse


n = 105312291668557186697918027513529248857806893649219117400977309697
e = 65537
c = 56084235340151536769364177314071579165242999204895873082547191150

# Theorem 1: All n > 1 can be factored as the product of two primes

factors = factor(n) # 618970019642690137449562111 * 170141183460469231731687303715884105727
p = factors[0][0]
q = factors[1][0]

# Theorem 2 - Euler's theorem: For n = p * q, where p and q are prime, φ(n) = (p-1)(q-1) See : https://en.wikipedia.org/wiki/Euler%27s_totient_function
phi = (p-1) * (q-1)

# Theorem 3 - Bézout's identity: For two integers a & b, there exists integers x & y (called Bézout coefficients) such as ax + by = gcd(a, b)
# See : https://en.wikipedia.org/wiki/B%C3%A9zout%27s_identity

# We are looking for d such as ed ≡ 1 (mod φ(n))
# d is the modular inverse of e mod φ(n)
# d can be found either by using egcd or pycryptodome's built-in inverse function. See : https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm
d = inverse(e, phi)

# Encrypt : c ≡ m ^ e (mod n)
# Decrypt : m ≡ c ^ d (mod n)
message = pow(c, d, n)

print(long_to_bytes(message)) # b'POLYCYBER{my_pQ_1$_LON6Er}'