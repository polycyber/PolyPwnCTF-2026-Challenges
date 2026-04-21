# DNA Visualizer 2

## Write-up

### Français

Suite à la première parti de ce défi, vous aurez sûrement remarqué qu'il y a un deuxième fichier de flag nommé `secretdnasequenceflag.txt`. Cependant ce n'est pas possible de l'afficher avec un simple cat, puisque la séquence est coupée! En effet, il y a une taille de séquence maximale.

![](./images/flag_fail_length.png)

Il faut se souvenir que dans le "DNA Profile" il y avait une taille de séquence, et en observant le réseau nous voyons que celle-ci est stockée dans un cookie "profile" : `profile:"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtb2RlIjoiZG5hIiwibGVuZ3RoIjoxN30.HcYODTtab527_vNwgRvS1PKBd6bjJZTqvWiY9cIiR7k"`

Ce cookie contient un token JWT, qui peut être décodé avec des outils comme CyberChef:

![alt text](./images/cyberchef_1.png)

Cependant, si l'on essaie de modifier la taille on voit que cela échoue car le serveur vérifie la signature du JWT, donc il faut trouver la clé secrète qui a été utilisée pour signer, ou bien trouver une façon de lire le fichier avec la limite de 17 octets. Les deux étaient possibles!

**Option 1: Déchiffrer la clé avec des tables de mots de passe**

Utilisant un outil comme hashcat, vous pouvez déchiffrer le secret par force brute, ou utilisant des listes de mot de passes comme `rockyou.txt`.

Voir: https://security.stackexchange.com/questions/262106/crack-jwt-hs256-with-hashcat

Une fois cela fait, vous trouvez que le secret est `pizza`. Vous pouvez ainsi reconstruire un JWT avec une taille arbitraire, par exemple 100: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtb2RlIjoiZG5hIiwibGVuZ3RoIjoxMDB9.7MUihs3xm_C2ktRQHwCq612AMX3YxnkWNmBrORBabwY`.

En utilisant ce cookie, c'est possible d'injecter une commande comme `⻠cat nsecretdnasequenceflag.txt` qui donnera le 2ème flag.

**Option 2 (bonus): Lire le flag en moins de 17 octets**

En cherchant d'autres caractères Unicode, vous verrez que certains permettent d'injecter des caractères comme `*`!

Les plus prometteurs que j'ai trouvé étaient dans la section des caractères chinois, mais il fallait gérer les 2 autres octets qui sont créés. Je n'ai pas trouvé de façon d'exécuter `cat *`, cependant j'ai trouvé le caractère `䠪` dont les octets forment `d *` si tronqué en ASCII. C'était donc possible d'exécuter `head *` avec l'injection suivante: `⻠hea䠪`. Et on se retrouvait donc avec une autre façon d'avoir le 2ème flag. :)

![](./images/head_bonus_injection.png)

Si vous avez trouvé d'autres moyens de lire le flag en moins de 17 octets, n'hésitez pas à me partager votre payload! (mon discord est `majkiwi`)

### English

Following the first part of this challenge, you will surely have noticed that there is a second flag file named `secretdnasequenceflag.txt`. However, it is not possible to display it with a simple cat command, since the sequence is cut off! Indeed, there is a maximum sequence length.

![](./images/flag_fail_length.png)

Remember that in the “DNA Profile” there was a sequence size, and by observing the network we see that it is stored in a “profile” cookie: `profile:"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtb2RlIjoiZG5hIiwibGVuZ3RoIjoxN30.HcYODTtab527_vNwgRvS1PKBd6bjJZTqvWiY9cIiR7k"`

This cookie contains a JWT token, which can be decoded with tools such as CyberChef:

![alt text](./images/cyberchef_1.png)

However, if we try to change the size, we see that it fails because the server checks the JWT signature, so we need to find the secret key that was used to sign it, or find a way to read the file with the 17-byte limit. Both were possible!


**Option 1: Decrypt the key with password tables**

Using a tool such as hashcat, you can decrypt the secret by brute force, or using password lists such as `rockyou.txt`.

See: https://security.stackexchange.com/questions/262106/crack-jwt-hs256-with-hashcat

Once you have done this, you will find that the secret is `pizza`. You can then reconstruct a JWT with an arbitrary size, for example 100: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtb2RlIjoiZG5hIiwibGVuZ3RoIjoxMDB9.7MUihs3xm_C2ktRQHwCq612AMX3YxnkWNmBrORBabwY`.

Using this cookie, it is possible to inject a command such as `⻠cat nsecretdnasequenceflag.txt`, which will give the second flag.

**Option 2 (bonus): Read the flag in less than 17 bytes**

When searching for other Unicode characters, you will see that some allow you to inject characters such as `*`!

The most promising ones I found were in the Chinese character section, but I had to deal with the two other bytes that are created. I couldn't find a way to execute `cat *`, but I did find the character `䠪`, whose bytes form `d *` when truncated to ASCII. It was therefore possible to execute `head *` with the following injection: `⻠hea䠪`. And so we end up with another way to get the second flag. :)

![](./images/head_bonus_injection.png)

If you found other ways to read the flag in less than 17 bytes, I would love to know your payload! (my discord is `majkiwi`)


## Flag

`polycyber{dn4_is_m4k1ng_m3_h4ngry}`