#!/bin/sh
set -e

# Start the BioSynth-9 daemon.
socat TCP-LISTEN:1337,fork,bind=127.0.0.1,reuseaddr EXEC:/opt/biosynth/biosynthd,su=biosynth,chdir=/opt/biosynth,stderr &

# Hand off to Apache
exec apache2-foreground
