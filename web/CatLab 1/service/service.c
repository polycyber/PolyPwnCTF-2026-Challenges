#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>

#define MAX_INPUT       4096
#define RESULT_BUF_SIZE 64
#define TRANSFORM_KEY   0x42

static const uint8_t MAGIC[4] = {'B', 'S', 'F', 0x01};

static uint8_t filebuf[MAX_INPUT];

static char outpath[32]   = "/tmp/result_.bsf";
static char find_args[64] = "-name 'result_*.bsf' -mmin +15 -delete";

typedef struct __attribute__((packed)) {
    uint8_t magic[4];
    uint8_t ident_len;
    uint8_t data_len;
} bsf_header_t;

static void remove_previous(void)
{
    if (access(outpath, F_OK) == 0)
        unlink(outpath);
}

static void transform(const uint8_t *in, uint16_t data_len, uint8_t *out)
{
    for (int i = 0; i < data_len; i++)
        out[i] = in[i] ^ TRANSFORM_KEY;
}

static void save(const uint8_t *buf, uint16_t data_len)
{
    FILE *f = fopen(outpath, "wb");
    if (f) {
        fwrite(buf, 1, data_len, f);
        fclose(f);
        printf("Transformation complete. Result saved to: %s\n", outpath);
    }

    char cmd[128];
    snprintf(cmd, sizeof(cmd), "find /tmp %s", find_args);
    system(cmd);
}

int main(void)
{
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);

    ssize_t n = read(STDIN_FILENO, filebuf, sizeof(bsf_header_t));
    if (n < (ssize_t)sizeof(bsf_header_t)) {
        fputs("Error: truncated specimen file", stderr);
        return 1;
    }

    bsf_header_t *hdr = (bsf_header_t *)filebuf;

    if (memcmp(hdr->magic, MAGIC, 4) != 0) {
        fputs("Error: invalid magic", stderr);
        return 1;
    }

    size_t payload = (size_t)hdr->ident_len + hdr->data_len;
    if (sizeof(bsf_header_t) + payload > MAX_INPUT) {
        fputs("Error: specimen too large", stderr);
        return 1;
    }

    size_t got = 0;
    while (got < payload) {
        ssize_t r = read(STDIN_FILENO,
                         filebuf + sizeof(bsf_header_t) + got,
                         payload - got);
        if (r <= 0) break;
        got += r;
    }
    if (got < payload) {
        fputs("Error: truncated specimen data", stderr);
        return 1;
    }

    uint8_t *ident_ptr = filebuf + sizeof(bsf_header_t);
    uint8_t *data_ptr  = ident_ptr + hdr->ident_len;

    printf("BioSynth-9 Transmogrification Engine v2.3\n");
    printf("Specimen: %.*s\n", (int)hdr->ident_len, ident_ptr);
    printf("Initiating transformation sequence...\n");

    snprintf(outpath, sizeof(outpath) + hdr->ident_len,
             "/tmp/result_%.*s.bsf", (int)hdr->ident_len, ident_ptr);

    remove_previous();

    uint8_t result[RESULT_BUF_SIZE];
    if (hdr->data_len > RESULT_BUF_SIZE)
        hdr->data_len = RESULT_BUF_SIZE;
    transform(data_ptr, hdr->data_len, result);
    save(result, hdr->data_len);

    return 0;
}
