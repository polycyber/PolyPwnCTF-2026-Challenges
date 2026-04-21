# Nom du défi

## Write-up

On peut créer la fonction `loadCompiledProgram` dans `Cpu.h` pour mettre un
programme déjà compilé en mémoire :

```c++
void loadCompiledProgram(const std::string& filename) {
    std::filesystem::path file{filename};
    std::ifstream infile(file, std::ios::binary);
    infile.read(reinterpret_cast<char*>(MEM.data()), memorySize * sizeof(uint16_t));
}
```

Ensuite dans main:

```c++
CPU<ACC_MA_PWN> cpu;
cpu.loadCompiledProgram("program.bin");
cpu.runProgram();
```

## Flag

`polycyber{dc155846b9e617dc}`
