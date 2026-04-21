.text
lea var_0
label_1:
ldi
brz label_0
out
adda var_1
br label_1
label_0:
ld var_2
add var_3
st var_2
st var_4
ld var_5
st var_6
add
ld var_7
st var_8
st var_9
label_3:
ld var_9
add var_4
st var_9
brno label_2
ld var_8
add var_1
st var_8
label_2:
ld var_6
sub var_1
st var_6
brnz label_3
add
ld var_9
xor var_8
and var_10
st var_9
sub var_11
brp label_4
brz label_4
ld var_9
add var_12
br label_5
label_4:
add var_13
label_5:
st var_9
in
sub var_9
brz label_6
ld var_1
st var_14
label_6:
ld var_15
sub var_1
st var_15
brnz label_0
ld var_14
brnz label_7
lea var_16
br label_8
label_7:
lea var_17
label_8:
ldi
out
adda var_1
brnz label_8
stop
.data
var_7: 0
var_1: 1
var_4: 0
var_6: 0
var_8: 0
var_9: 0
var_15: 32
var_10: 31
var_11: 26
var_12: 97
var_13: 48
var_14: 0
var_2: 36486
var_3: 64533
var_5: 683
var_0: 70
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
var_17: 87
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
var_16: 67
111
114
114
101
99
116
33
10
0
