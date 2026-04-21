#include "Cpu.h"
#include "ISA.h"

#include <sstream>

namespace Disassembler {

template <InstructionSet ISA>
std::string disassemble(const std::array<uint16_t, UINT8_MAX>& MEM, uint8_t dataOffset = UINT8_MAX) {
    std::unordered_map<uint8_t, std::string> opcodeMap;
    for (const auto& [name, code] : ISA::opcodes) {
        opcodeMap[code] = name;
    }

    std::stringstream output;

    std::unordered_map<uint8_t, std::string> labelAddresses;

    int nVariable = 0;
    int nLabel = 0;

    size_t pc = 0;
    // first pass, identify labels
    while (pc < dataOffset) {
        uint16_t instruction = MEM[pc++];

        uint8_t data = instruction & 0xFF;
        if (data != 0) {
            if (labelAddresses.find(data) != labelAddresses.end()) {
                continue;
            }

            if (data < dataOffset) {
                labelAddresses[data] = "label_" + std::to_string(nLabel++);
            } else {
                labelAddresses[data] = "var_" + std::to_string(nVariable++);
            }
        }
    }

    pc = 0;
    output << ".text" << std::endl;
    while (pc < UINT8_MAX) {
        if (pc == dataOffset) {
            output << ".data" << std::endl;
        }

        uint16_t instruction = MEM[pc++];

        if (labelAddresses.find(pc - 1) != labelAddresses.end()) {
            output << labelAddresses[pc - 1] << ": ";
        }

        if (pc > dataOffset) {
            output << instruction << std::endl;
            continue;
        }

        uint8_t opcode = instruction >> 8;
        uint8_t data = instruction & 0xFF;

        output << opcodeMap[opcode];
        if (data != 0) {
            output << " " << labelAddresses[data];
        }
        output << std::endl;
    }

    return output.str();
}

}  // namespace Disassembler
