.text
lea flag
loopPrintFlag:
ldi
brz loopMain
out
adda one
br loopPrintFlag
loopMain:
ld seed
add addv
st seed
st multiplyInputLeft
ld mulv
st multiplyInputRight
; multiply
ld zero
st multiplyOutputHigh
st multiplyOutputLow
loopMultiply:
ld multiplyOutputLow
add multiplyInputLeft
st multiplyOutputLow
brno loopMultiplyCheck
overflow:
ld multiplyOutputHigh
add one
st multiplyOutputHigh
loopMultiplyCheck:
ld multiplyInputRight
sub one
st multiplyInputRight
brnz loopMultiply
; after multiply
ld multiplyOutputLow
xor multiplyOutputHigh
and compareModulo
st multiplyOutputLow
sub alphabetSize
brp chooseDigit
brz chooseDigit
letter:
ld multiplyOutputLow
add asciiAlphaOffset
br compareInput
chooseDigit:
add asciiDigitsOffset
compareInput:
st multiplyOutputLow
in
sub multiplyOutputLow
brz compareSuccess
ld one
st errorInFlag
compareSuccess:
ld flagSize
sub one
st flagSize
brnz loopMain
ld errorInFlag
brnz printFailure
lea successText
br printAndExit
printFailure:
lea errorText
printAndExit:
ldi
out
adda one
brnz printAndExit
stop

.data
zero: 0
one: 1
multiplyInputLeft: 0
multiplyInputRight: 0
multiplyOutputHigh: 0
multiplyOutputLow: 0
flagSize: 32
compareModulo: 31
alphabetSize: 26
asciiAlphaOffset: 97
asciiDigitsOffset: 48
errorInFlag: 0

seed: 36486
addv: 64533
mulv: 683
flag: 70
108
97
103
32
40
115
105
122
101
32
51
50
41
58
32
0
errorText: 87
114
111
110
103
32
102
108
97
103
33
10
0
successText: 67
111
114
114
101
99
116
33
10
0
