# Nom du défi
Lab Attack 1

## Write-up
Parser les artéfacts avec un outil comme KAPE. Download gratuit (https://www.kroll.com/en/services/cyber/incident-response-recovery/kroll-artifact-parser-and-extractor-kape)
- Windows System Logs (KAPE + timeline explorer) -> Event ID 7045 (service)
- MFT (KAPE + Timeline explorer) -> Anydesk.exe (dans C:\Users\dr-moreau\Downloads)
- Non testé: Browsing history BrowsingHistoryView (BrowsingHistoryView) -> téléchargement de l'installateur d'Anydesk

## Flag

`POLYCYBER{anydesk}`