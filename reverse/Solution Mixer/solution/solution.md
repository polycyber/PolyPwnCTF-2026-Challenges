## Solution (français)

En analysant le programme, on réalise que le scientifique utilise le flag comme clé pour encrypter ses solutions exceptionnelles (le flag est la clé). Cependant, il n'a pas fait attention et a fait fuiter plusieurs parties du flag, dans le but de simuler l'aléatoire dans le programme.

Comment retrouver les bits du flag:
0: Leaké dans le choix d'ajouter, ou non, 0.5 degré C de température
1: Leaké dans le temps de réaction simulé
2: Leaké dans le temps de réaction simulé
3: Leaké dans le MSB (Most Significant Bit) du R (Rouge) de la couleur aléatoire de la solution résultante
4: Leaké dans le MSB du G (Vert) de la couleur aléatoire de la solution résultante
5: Leaké dans le MSB du B (Bleu) de la couleur aléatoire de la solution résultante
6: Leaké parmi les solutions exceptionnelles encryptées (Le scientifique s'est trompé dans ce qu'il voulait afficher)
7: Pas nécessaire de le leaker

On peut ainsi exécuter le programme plusieurs fois et extraire les lettres du flag unes après l'autre

## Solution (anglais)

By analyzing the program, we realize that the scientist uses the flag as a key to encrypt his exceptional solutions (the flag is the key). However, he wasn't careful and leaked several parts of the flag in an attempt to simulate randomness in the program.

How to retrieve the bits of the flag:
0: Leaked in the choice to add, or not, 0.5°C to the temperature.
1: Leaked in the simulated reaction time.
2: Leaked in the simulated reaction time.
3: Leaked in the MSB (Most Significant Bit) of the R (Red) in the random color of the resulting solution.
4: Leaked in the MSB of the G (Green) in the random color of the resulting solution.
5: Leaked in the MSB of the B (Blue) in the random color of the resulting solution.
6: Leaked among the encrypted exceptional solutions (The scientist made a mistake in what he intended to display).
7: No need to leak it.

Thus, we can execute the program several times and extract the letters of the flag one by one.
