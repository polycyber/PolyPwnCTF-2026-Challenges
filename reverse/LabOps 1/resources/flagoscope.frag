#version 100
precision mediump float;

varying vec2 fragTexCoord;

uniform sampler2D texture0;
uniform float waviness;
uniform float stitchiness;
uniform float noise;
uniform float time;

const float PHI = 1.61803398874989484820459;

float random(vec2 st) {
    return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) *
        43758.5453123);
}

float goldNoise(in vec2 xy, in float seed) {
    return fract(tan(distance(xy * PHI, xy) * seed) * xy.x);
}

vec3 goldNoiseCol(in vec2 xy, in float seed) {
    return vec3(goldNoise(xy, seed + 0.1), goldNoise(xy, seed + 0.2), goldNoise(xy, seed + 0.3));
}

void main() {
    vec2 uv = fragTexCoord;

    // circle mask
    float mask = step(0.5, distance(uv, vec2(0.5, 0.5)));

    // stitch filter
    vec2 stitchSeedX = floor(uv * 10.0);
    vec2 stitchSeedY = floor((uv + vec2(stitchiness, stitchiness)) * 10.0);
    uv = mix(uv, vec2(random(stitchSeedX), random(stitchSeedY)), stitchiness);

    vec3 baseCol = texture2D(texture0, uv).rgb;

    // wave filter - see https://www.shadertoy.com/view/MsX3DN
    vec2 waveUv = uv;
    waveUv.x += sin(uv.y * 7.0 + time) * waviness * 10.0;
    waveUv.y += sin(uv.x * 9.0 + time * 1.2) * waviness / 2.0;
    vec3 waveCol = texture2D(texture0, waveUv).rgb;

    waveCol = mix(waveCol, goldNoiseCol(uv * 1000.0, fract(time)), noise);

    gl_FragColor = mix(vec4(waveCol, 1.0), vec4(0), mask);
}