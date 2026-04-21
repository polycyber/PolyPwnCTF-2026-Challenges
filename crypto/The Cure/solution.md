# The Cure

## Write-up EN

The file, marked as an image, does not open.

By using `strings` command, we can extract:

```bash
strings note.jpg
```

This will ouput the Base64-encoded string: `ZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5Sm1iR0ZuSWpvaVZVVTVUVmRWVGxwUmExWlRaVE5TU1UweE9YcE5NRTVUV2xoU1pscHFRbmxpV0ZaTlVWWTRlR014T0RSTk1tZG9WRzFTWmxaSGFFWllNVUpvWVZVME0wbFZOREpZZVVaUFdEQXhXbGg2UW0xYWEyeHFXbGd3UFNJc0ltNWhiV1VpT2lKS1lYTnZiaUlzSW1Ga2JXbHVJanAwY25WbGZRLkZ0eGtrWTYzRGNXdGc3VVVHdDVpME4ycU80NkFYWUl1NlJnU0JkcDcxWTA=`. Using the terminal or a tool like CyberChef, we can decode the Base64 string to reveal the plaintext:

```bash
echo "ZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5Sm1iR0ZuSWpvaVZVVTVUVmRWVGxwUmExWlRaVE5TU1UweE9YcE5NRTVUV2xoU1pscHFRbmxpV0ZaTlVWWTRlR014T0RSTk1tZG9WRzFTWmxaSGFFWllNVUpvWVZVME0wbFZOREpZZVVaUFdEQXhXbGg2UW0xYWEyeHFXbGd3UFNJc0ltNWhiV1VpT2lKS1lYTnZiaUlzSW1Ga2JXbHVJanAwY25WbGZRLkZ0eGtrWTYzRGNXdGc3VVVHdDVpME4ycU80NkFYWUl1NlJnU0JkcDcxWTA=" | base64 -d
```

This will output another ciphertext: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmbGFnIjoiVUU5TVdVTlpRa1ZTZTNSSU0xOXpNME5TWlhSZlpqQnliWFZNUVY4eGMxODRNMmdoVG1SZlZHaEZYMUJoYVU0M0lVNDJYeUZPWDAxWlh6Qm1aa2xqWlgwPSIsIm5hbWUiOiJKYXNvbiIsImFkbWluIjp0cnVlfQ.FtxkkY63DcWtg7UUGt5i0N2qO46AXYIu6RgSBdp71Y0`.

We can distinguish three parts seperated by a "`.`". It represents a JWT token.

Using `jwt.io`, we can decode the token to see the payload to contain: `"flag": "UE9MWUNZQkVSe3RIM19zM0NSZXRfZjBybXVMQV8xc184M2ghTmRfVGhFX1BhaU43IU42XyFOX01ZXzBmZkljZX0="`.

We can retrieve the flag by decoding the Base64 string.

## Write-up FR

Voici la traduction en français :

Le fichier, marqué comme une image, ne s'ouvre pas.

En utilisant la commande `strings`, nous pouvons extraire :

```bash
strings note.jpg
```

Cela affichera la chaîne encodée en Base64 : `ZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5Sm1iR0ZuSWpvaVZVVTVUVmRWVGxwUmExWlRaVE5TU1UweE9YcE5NRTVUV2xoU1pscHFRbmxpV0ZaTlVWWTRlR014T0RSTk1tZG9WRzFTWmxaSGFFWllNVUpvWVZVME0wbFZOREpZZVVaUFdEQXhXbGg2UW0xYWEyeHFXbGd3UFNJc0ltNWhiV1VpT2lKS1lYTnZiaUlzSW1Ga2JXbHVJanAwY25WbGZRLkZ0eGtrWTYzRGNXdGc3VVVHdDVpME4ycU80NkFYWUl1NlJnU0JkcDcxWTA=`. En utilisant le terminal ou un outil comme CyberChef, nous pouvons décoder la chaîne Base64 pour révéler le texte brut :

```bash
echo "ZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5Sm1iR0ZuSWpvaVZVVTVUVmRWVGxwUmExWlRaVE5TU1UweE9YcE5NRTVUV2xoU1pscHFRbmxpV0ZaTlVWWTRlR014T0RSTk1tZG9WRzFTWmxaSGFFWllNVUpvWVZVME0wbFZOREpZZVVaUFdEQXhXbGg2UW0xYWEyeHFXbGd3UFNJc0ltNWhiV1VpT2lKS1lYTnZiaUlzSW1Ga2JXbHVJanAwY25WbGZRLkZ0eGtrWTYzRGNXdGc3VVVHdDVpME4ycU80NkFYWUl1NlJnU0JkcDcxWTA=" | base64 -d
```

Cela produira un autre texte chiffré : `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmbGFnIjoiVUU5TVdVTlpRa1ZTZTNSSU0xOXpNME5TWlhSZlpqQnliWFZNUVY4eGMxODRNMmdoVG1SZlZHaEZYMUJoYVU0M0lVNDJYeUZPWDAxWlh6Qm1aa2xqWlgwPSIsIm5hbWUiOiJKYXNvbiIsImFkbWluIjp0cnVlfQ.FtxkkY63DcWtg7UUGt5i0N2qO46AXYIu6RgSBdp71Y0`.

Nous pouvons distinguer trois parties séparées par un "`.`". Cela représente un jeton JWT.

En utilisant `jwt.io`, nous pouvons décoder le jeton pour voir que la charge utile (payload) contient : `"flag": "UE9MWUNZQkVSe3RIM19zM0NSZXRfZjBybXVMQV8xc184M2ghTmRfVGhFX1BhaU43IU42XyFOX01ZXzBmZkljZX0="`.

Nous pouvons récupérer le flag en décodant cette chaîne Base64.

## Flag

`POLYCYBER{tH3_s3CRet_f0rmuLA_1s_83h!Nd_ThE_PaiN7!N6_!N_MY_0ffIce}`
