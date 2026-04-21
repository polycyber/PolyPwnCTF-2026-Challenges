# Cryptochimie

## Write-up FR

Le texte est écrit avec des éléments chimiques.
Il faut faire correspondre chaque élément chimique avec son numéro atomique, puis décoder la chaine obtenue en code ascii.

HG AU OS AC HO AC DY TM PB MG LI TA OS CD RN SB HG TM PB TA AU ER TA HO PO TB DY OS SB MG B

Hg : Mercure, 80
Au : Or, 79
Os : Osmium, 76
Ac : Actinium, 89
Ho : Holmium, 67
Ac : Actinium, 89
Dy : Dysprosium, 66
Tm : Thulium, 69
Pb : Plomb, 82
Mg : Magnésium, 12
Li : Lithium, 3
Ta : Tantale, 73
Os : Osmium, 76
Cd : Cadmium, 48
Rn : Radon, 86
Sb : Antimoine, 51
Hg : Mercure, 80
Tm : Thulium, 69
Pb : Plomb, 82
Ta : Tantale, 73
Au : Or, 79
Er : Erbium, 68
Ta : Tantale, 73
Ho : Holmium, 67
Po : Polonium, 84
Tb : Terbium, 65
Dy : Dysprosium, 66
Os : Osmium, 76
Sb : Antimoine, 51
Mg : Magnésium, 12
B : Bore, 5

En convertissant ensuite les numéros trouvés avec leur correspondance en ASCII (possible d'utiliser CyberChef, "From decimal") : 
POLYCYBER{IL0V3PERIODICTABL3}

Les codes ascii des accolades sont 123 et 125, qui ont été encodés par deux éléments chimiques puisque le tableau périodique ne va que jusqu'à 118. On peut le deviner puisque 12, 3 et 5 ne sont pas imprimables en ascii (et le format de flag est connu).

## Write-up EN

The text is written using chemical elements.
You must match each chemical element with its atomic number, then decode the resulting string into ASCII code.

HG AU OS AC HO AC DY TM PB MG LI TA OS CD RN SB HG TM PB TA AU ER TA HO PO TB DY OS SB MG B

Hg: Mercury, 80
Au: Gold, 79
Os: Osmium, 76
Ac: Actinium, 89
Ho: Holmium, 67
Ac: Actinium, 89
Dy: Dysprosium, 66
Tm: Thulium, 69
Pb: Lead, 82
Mg: Magnesium, 12
Li: Lithium, 3
Ta: Tantalum, 73
Os: Osmium, 76
Cd: Cadmium, 48
Rn: Radon, 86
Sb: Antimony, 51
Hg: Mercury, 80
Tm: Thulium, 69
Pb: Lead, 82
Ta: Tantalum, 73
Au: Gold, 79
Er: Erbium, 68
Ta: Tantalum, 73
Ho: Holmium, 67
Po: Polonium, 84
Tb: Terbium, 65
Dy: Dysprosium, 66
Os: Osmium, 76
Sb: Antimony, 51
Mg: Magnesium, 12
B: Boron, 5

Then convert the numbers found to their ASCII equivalents (you can use CyberChef, “From decimal”): 
POLYCYBER{IL0V3PERIODICTABL3}

The ASCII codes for the curly brackets are 123 and 125, which have been encoded by two chemical elements since the periodic table only goes up to 118. We can guess this because 12, 3, and 5 are not printable in ASCII (and you know the flag format).

## Flag

`POLYCYBER{IL0V3PERIODICTABL3}`
`polycyber{il0v3periodictabl3}`
`polycyber{IL0V3PERIODICTABL3}`
