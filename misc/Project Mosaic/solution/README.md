# Project_Mosaic

## Write-up FR

En inspectant le PCAP fourni, on peut remarquer un pattern régulier entre les paquets ICMP, UDP et TCP. Ceux-ci forment en réalité un QR code, avec les ICMP marquant des retours à la ligne, et les UDP et TCP des pixels noirs et blancs. Il est possible de recréer le QR Code manuellement ou à l'aide d'un script.

Le QR code mène vers une image. En regardant le lien vers lequel pointe le code, nous trouvons le flag dans l'URL.

## Write-up EN

By inspecting the provided PCAP, we can observe a regular pattern between the ICMP, UDP, and TCP packets. These actually form a QR code, with the ICMP packets marking line breaks, and the UDP and TCP packets representing black and white pixels. It is possible to recreate the QR code manually or using a script.

The QR code leads to an image. By examining the link the code points to, we find the flag in the URL.

## Flag

POLYCYBER{QR_C0D3_1N_PCAP}