# Correspondances avant l'apocalypse

## Write-up FR

Le texte est chiffré par substitution. Chaque lettre de l'alphabet (+ les espaces) correspond à une autre lettre, déterminée aléatoirement.
La seule façon de décoder le message est donc d'utiliser les fréquences des caractères, les mots courants et les règles linguistiques, sachant que le texte est en anglais.

Pour déterminer les fréquences des caractères et les représenter, on peut utiliser par exemple ce script :

```
alphabet ="abcdefghijklmnopqrstuvwxyz "
dico = {letter : text.count(letter)/len(text) for letter in alphabet}
print(dico)

import matplotlib.pyplot as plt
plt.bar(dico.keys(),dico.values())
```

On voit alors d'abord que "y" est beaucoup plus présent que les autres caractères et plus que les fréquences des lettres en anglais, on détermine alors qu'il s'agit de l'espace. On pouvait aussi le deviner puisqu'il suit chaque signe de ponctuation.

On peut ensuite voir que le deuxième caractère le plus présent dans notre texte est le "x", à 0.11 (en retirant les espaces du décompte de fréquences). Cela correspondrait donc au "e", la lettre la plus fréquente en anglais avec une fréquence similaire. La deuxième lettre la plus fréquente avec 0.096 est le "l" qui correspond donc au "t".

Les fréquences du texte ne sont pas toujours les mêmes fréquences que celles de la lange anglaise mais en regardant ensuite des mots qui apparaissent au fur et à mesure dans le texte, on peut déterminer de plus en plus de lettres. On peut aussi s'appuyer sur les fréquences des bigrammes et trigrammes de la langue anglaise.

On finit par trouver le texte suivant : 

>I'm afraid someone will find my discoveries, and I don't want them to fall into the wrong hands. If what I've done in this lab is understood by people with bad intentions, they could do terrible things… maybe even destroy humanity! Our ecosystem is based on fragile balances, and my inventions could disrupt the viability of our world. I cannot bring myself to let this knowledge be lost, but at the same time, I do not trust humans to use it wisely. Some people would try to seize the power granted by this knowledge. A war would then break out over this unequal power, and humanity would descend into madness! No, I'm sure I can't keep this secret for too long. I have to destroy it. Or maybe I could secure it with a very secret password? For example, if I randomly substituted all the letters in my text, it would be impossible to guess which letter corresponds to which, right? Yes, I'll do that to protect my password, which will grant access to all my terrible discoveries. My password will start with polycyber, followed by the classic braces often used in ctf flags. Inside the braces will be the name of the eighty-fourth chemical element, a dash, the last name of the first woman to win a nobel prize, and the year she won it.



## Write-up EN

The text is encrypted using a substitution cipher. Each letter of the alphabet (and spaces) corresponds to another letter, determined at random.
The only way to decode the message is therefore to use character frequencies, common words, and linguistic rules, knowing that the text is in English.

To determine character frequencies and display them, you can for example use this script:

```
alphabet ="abcdefghijklmnopqrstuvwxyz "
dico = {letter : text.count(letter)/len(text) for letter in alphabet}
print(dico)

import matplotlib.pyplot as plt
plt.bar(dico.keys(),dico.values())
```

We first observe that “y” appears much more often than the other characters, and more often than letter frequencies in English; we therefore determine that it represents the space. This could also be guessed since it follows every punctuation mark.

We can then see that the second most frequent character in our text is “x”, at 0.11 (after removing spaces from the frequency count). This would therefore correspond to “e”, the most frequent letter in English with a similar frequency. The second most frequent letter, at 0.096, is “l”, which therefore corresponds to “t”.

The frequencies in the text do not always match the standard frequencies of the English language, but by looking at words that gradually appear in the text, you can determine more and more letters. You can also rely on the frequencies of bigrams and trigrams in the English language.

You eventually end up finding the following text:

>I'm afraid someone will find my discoveries, and I don't want them to fall into the wrong hands. If what I've done in this lab is understood by people with bad intentions, they could do terrible things… maybe even destroy humanity! Our ecosystem is based on fragile balances, and my inventions could disrupt the viability of our world. I cannot bring myself to let this knowledge be lost, but at the same time, I do not trust humans to use it wisely. Some people would try to seize the power granted by this knowledge. A war would then break out over this unequal power, and humanity would descend into madness! No, I'm sure I can't keep this secret for too long. I have to destroy it. Or maybe I could secure it with a very secret password? For example, if I randomly substituted all the letters in my text, it would be impossible to guess which letter corresponds to which, right? Yes, I'll do that to protect my password, which will grant access to all my terrible discoveries. My password will start with polycyber, followed by the classic braces often used in ctf flags. Inside the braces will be the name of the eighty-fourth chemical element, a dash, the last name of the first woman to win a nobel prize, and the year she won it.


## Flag

`polycyber{polonium-curie-1912}`
`polycyber{polonium-curie1912}`
