.text
loop:
lea data
adda idx
ldi
st temp
lea key
adda idx
ldi
xor temp
out
ld idx
add one
st idx
sub size
brnz loop
stop
.data
one: 1
size: 28
idx: 0
temp: 0
data: 154
111
67
8
243
197
28
186
173
97
73
157
244
185
118
159
156
116
61
90
222
235
56
2
92
253
204
166
key: 234
0
47
113
144
188
126
223
223
26
45
254
197
140
67
167
168
66
95
99
187
221
9
53
56
158
177
172
