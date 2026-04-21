#!/bin/bash

mode="$1"
seq=$2
depth=0
out=""
# delim=".................................................."
delim="                                        "
NEWLINE=$'\n'
counts=(0 1 2 4 6 8 9 6 2 0)

seq="....${seq}...."

if [ "$mode" == "dna" ]
then
    for (( i=0; i<${#seq}; i++ )); do
        j=${counts[i % ${#counts[@]} ]}*2+8
        out="${out}\n${delim:0:$j}${seq:$i:1}"
        chr=${seq:$i:1}
        if [ "${seq:$i:1}" == "A" ] 
        then 
        chr="T" 
        fi
        
        if [ "${seq:$i:1}" == "T" ] 
        then 
        chr="A" 
        fi
        
        if [ "${seq:$i:1}" == "C" ] 
        then 
        chr="G" 
        fi
        
        if [ "${seq:$i:1}" == "G" ] 
        then 
        chr="C" 
        fi
        
        out="${out} - ${chr}"
    done

else
    for (( i=0; i<${#seq}; i++ )); do
        j=${counts[i % ${#counts[@]} ]}*2+8
        out="${out}\n${delim:0:$j}${seq:$i:1} - "
    done
fi

echo -e "$out"