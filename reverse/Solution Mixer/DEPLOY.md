Les participants auront accès aux fichiers `SolutionMixer` et `SolutionMixerServer`. Le serveur exécutera le binaire `SolutionMixerServer` et doit avoir le fichier `flag.txt` au même niveau dans l'arborescence des fichiers. Tous ces fichiers sont présents dans le dossier `files` de mon défi.

## Building

To build the binaries locally:
```bash
cd src
./build.sh
```

This will build to the `build/` directory and copy the binaries to `files/`.

## Docker

Build and run the Docker container (execute at `solution_mixer`):
```bash
docker build -t solution-mixer:latest -f src/Dockerfile .
docker run -p 34512:34512 --name solution-mixer solution-mixer:latest
```

