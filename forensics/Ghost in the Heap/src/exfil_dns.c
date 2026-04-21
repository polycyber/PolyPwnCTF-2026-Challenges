// Build: gcc -O2 -Wall -Wextra -std=c11 -o exfil_dns src/exfil_dns.c
//
// This program crafts real DNS query payload bytes whose QNAME carries base64url
// chunks of a flag, sends them over UDP, and *retains* the crafted packets on
// the heap so they appear in an ELF core dump.

#define _GNU_SOURCE

#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/prctl.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>

// Flag is embedded in the executable image only in obfuscated form so the
// resulting core dump can't be solved via `strings | grep polycyber`.
static const uint8_t FLAG_XOR = 0xA5;
static const uint8_t FLAG_OBF[] = {
    0xd5, 0xca, 0xc9, 0xdc, 0xc6, 0xdc, 0xc7, 0xc0, 0xd7, 0xde,
    0xd0, 0xe1, 0xd5, 0xfa, 0xd6, 0xf0, 0xd7, 0xc0, 0xfa, 0x94,
    0xd6, 0xfa, 0xc3, 0xf0, 0xeb, 0x88, 0xd0, 0xcd, 0xd8,
};
static const int DEFAULT_DNS_PORT = 53;

static volatile sig_atomic_t g_stop = 0;
static void on_sig(int sig) {
  (void)sig;
  g_stop = 1;
}

static void secure_bzero(void *p, size_t n) {
  volatile uint8_t *vp = (volatile uint8_t *)p;
  while (n--)
    *vp++ = 0;
}

static char *materialize_flag(size_t *out_len) {
  size_t n = sizeof(FLAG_OBF);
  char *s = (char *)malloc(n + 1);
  if (!s)
    return NULL;
  for (size_t i = 0; i < n; i++)
    s[i] = (char)(FLAG_OBF[i] ^ FLAG_XOR);
  s[n] = '\0';
  if (out_len)
    *out_len = n;
  return s;
}

typedef struct {
  uint8_t magic[8];   // "CAPV2\0\0\0"
  uint32_t count;     // number of packets
  uint32_t blob_len;  // total bytes used in blob
  uint8_t xormask;    // per-dump mask
  uint8_t rsv[3];
  // followed by count entries:
  //   uint32_t off; uint32_t len;
  // followed by blob bytes (obfuscated packets)
} capv2_hdr_t;

// base64url without padding
static const char B64URL_ALPH[] =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";

static char *b64url_nopad(const uint8_t *in, size_t in_len, size_t *out_len) {
  // output length = ceil(in_len/3)*4 minus padding (0,1,2)
  size_t full = (in_len / 3) * 4;
  size_t rem = in_len % 3;
  size_t olen = full + (rem ? 4 : 0);
  if (rem == 1)
    olen -= 2;
  else if (rem == 2)
    olen -= 1;

  char *out = (char *)calloc(olen + 1, 1);
  if (!out)
    return NULL;

  size_t i = 0, o = 0;
  while (i + 3 <= in_len) {
    uint32_t v = ((uint32_t)in[i] << 16) | ((uint32_t)in[i + 1] << 8) |
                 ((uint32_t)in[i + 2]);
    out[o++] = B64URL_ALPH[(v >> 18) & 63];
    out[o++] = B64URL_ALPH[(v >> 12) & 63];
    out[o++] = B64URL_ALPH[(v >> 6) & 63];
    out[o++] = B64URL_ALPH[v & 63];
    i += 3;
  }
  if (rem == 1) {
    uint32_t v = ((uint32_t)in[i] << 16);
    out[o++] = B64URL_ALPH[(v >> 18) & 63];
    out[o++] = B64URL_ALPH[(v >> 12) & 63];
  } else if (rem == 2) {
    uint32_t v = ((uint32_t)in[i] << 16) | ((uint32_t)in[i + 1] << 8);
    out[o++] = B64URL_ALPH[(v >> 18) & 63];
    out[o++] = B64URL_ALPH[(v >> 12) & 63];
    out[o++] = B64URL_ALPH[(v >> 6) & 63];
  }

  if (out_len)
    *out_len = o;
  out[o] = '\0';
  return out;
}

static void write_u16(uint8_t *p, uint16_t v) {
  p[0] = (uint8_t)((v >> 8) & 0xFF);
  p[1] = (uint8_t)(v & 0xFF);
}

static size_t dns_write_qname(uint8_t *out, size_t out_cap, const char **labels,
                              size_t nlabels) {
  size_t o = 0;
  for (size_t i = 0; i < nlabels; i++) {
    size_t ln = strlen(labels[i]);
    if (ln > 63)
      return 0;
    if (o + 1 + ln > out_cap)
      return 0;
    out[o++] = (uint8_t)ln;
    memcpy(out + o, labels[i], ln);
    o += ln;
  }
  if (o + 1 > out_cap)
    return 0;
  out[o++] = 0;
  return o;
}

// Domain splitting helpers removed intentionally (we don't append a domain suffix
// to avoid leaving easy ASCII indicators in the dump).

static uint8_t *build_dns_query(const char *chunk, int seq, int total,
                                const char *session,
                                size_t *out_len) {
  // DNS header + QNAME + QTYPE/QCLASS
  uint8_t buf[512];
  memset(buf, 0, sizeof(buf));
  uint16_t tid = (uint16_t)(rand() & 0xFFFF);
  write_u16(buf + 0, tid);
  write_u16(buf + 2, 0x0100); // RD
  write_u16(buf + 4, 1);      // QDCOUNT
  // AN/NS/AR = 0

  char seq_label[16];
  snprintf(seq_label, sizeof(seq_label), "s%02d", seq);

  char total_label[16];
  snprintf(total_label, sizeof(total_label), "t%02d", total);

  const char *labels[64];
  size_t nlabels = 0;
  labels[nlabels++] = chunk;
  labels[nlabels++] = seq_label;
  labels[nlabels++] = total_label;
  labels[nlabels++] = session;

  size_t qname_len = dns_write_qname(buf + 12, sizeof(buf) - 12, labels, nlabels);
  if (qname_len == 0)
    return NULL;

  size_t off = 12 + qname_len;
  if (off + 4 > sizeof(buf))
    return NULL;
  write_u16(buf + off, 1);     // QTYPE A
  write_u16(buf + off + 2, 1); // QCLASS IN
  off += 4;

  uint8_t *out = (uint8_t *)malloc(off);
  if (!out)
    return NULL;
  memcpy(out, buf, off);
  // Wipe stack copy so plaintext DNS bytes don't remain in the core dump stack.
  secure_bzero(buf, sizeof(buf));
  *out_len = off;
  return out;
}

int main(int argc, char **argv) {
  int dns_port = DEFAULT_DNS_PORT;
  int keepalive_secs = 20;

  // Allow gcore (ptrace) in environments with Yama ptrace restrictions.
  // This makes the process explicitly opt-in to being traced.
  (void)prctl(PR_SET_PTRACER, PR_SET_PTRACER_ANY, 0, 0, 0);

  for (int i = 1; i < argc; i++) {
    if (!strcmp(argv[i], "--port") && i + 1 < argc) {
      dns_port = atoi(argv[++i]);
    } else if (!strcmp(argv[i], "--keepalive") && i + 1 < argc) {
      keepalive_secs = atoi(argv[++i]);
    } else {
      fprintf(stderr,
              "usage: %s [--port 53] [--keepalive 20]\n",
              argv[0]);
      return 2;
    }
  }

  signal(SIGINT, on_sig);
  signal(SIGTERM, on_sig);

  srand((unsigned)time(NULL) ^ (unsigned)getpid());

  // Intentionally no domain suffix is appended to QNAME. This avoids leaving
  // easy ASCII indicators (like "exfil.poly") in the dump.

  // Materialize flag plaintext briefly (then wipe), and base64url-encode it.
  size_t flag_len = 0;
  char *flag_plain = materialize_flag(&flag_len);
  if (!flag_plain) {
    fprintf(stderr, "failed to materialize flag\n");
    return 1;
  }

  size_t b64_len = 0;
  char *b64 = b64url_nopad((const uint8_t *)flag_plain, flag_len, &b64_len);
  secure_bzero(flag_plain, flag_len + 1);
  free(flag_plain);
  if (!b64) {
    fprintf(stderr, "failed to b64 encode\n");
    return 1;
  }

  // Chunk base64 into <= 48-char labels
  const size_t chunk_len = 48;
  size_t nchunks = (b64_len + chunk_len - 1) / chunk_len;

  // Session marker (lets solver group chunks)
  char session[9];
  for (int i = 0; i < 8; i++) {
    int v = rand() & 0xF;
    session[i] = "0123456789abcdef"[v];
  }
  session[8] = '\0';

  // UDP socket
  int fd = socket(AF_INET, SOCK_DGRAM, 0);
  if (fd < 0) {
    fprintf(stderr, "socket: %s\n", strerror(errno));
    return 1;
  }

  struct sockaddr_in dst;
  memset(&dst, 0, sizeof(dst));
  dst.sin_family = AF_INET;
  dst.sin_port = htons((uint16_t)dns_port);
  // 127.0.0.1 without storing an ASCII string in memory
  dst.sin_addr.s_addr = htonl(0x7F000001u);

  // Create a heap-retained "capture" structure containing *obfuscated* DNS packets.
  // This prevents trivial recovery via `strings | grep` on the resulting core.
  //
  // Capacity sizing: our queries are < 512 bytes; store up to that per chunk.
  size_t cap_blob_cap = nchunks * 512;
  size_t cap_sz = sizeof(capv2_hdr_t) + (nchunks * 8) + cap_blob_cap;
  capv2_hdr_t *cap = (capv2_hdr_t *)calloc(1, cap_sz);
  if (!cap) {
    fprintf(stderr, "oom\n");
    return 1;
  }
  memcpy(cap->magic, "CAPV2\0\0\0", 8);
  cap->count = (uint32_t)nchunks;
  cap->xormask = (uint8_t)(0x80 ^ (rand() & 0x7F));
  uint8_t *entry_base = (uint8_t *)cap + sizeof(capv2_hdr_t);
  uint8_t *blob_base = entry_base + (nchunks * 8);
  uint32_t blob_off = 0;

  fprintf(stderr, "[exfil] pid=%d session=%s chunks=%zu\n", getpid(), session,
          nchunks);

  for (size_t i = 0; i < nchunks && !g_stop; i++) {
    char chunk[64];
    size_t off = i * chunk_len;
    size_t take = (b64_len - off) < chunk_len ? (b64_len - off) : chunk_len;
    memset(chunk, 0, sizeof(chunk));
    memcpy(chunk, b64 + off, take);
    chunk[take] = '\0';

    size_t pkt_len = 0;
    uint8_t *pkt = build_dns_query(chunk, (int)i, (int)nchunks, session, &pkt_len);
    if (!pkt) {
      fprintf(stderr, "failed to build packet\n");
      return 1;
    }
    (void)sendto(fd, pkt, pkt_len, 0, (struct sockaddr *)&dst, sizeof(dst));

    // Store obfuscated packet into capture blob + table entry.
    if (blob_off + (uint32_t)pkt_len > (uint32_t)cap_blob_cap) {
      fprintf(stderr, "capture overflow\n");
      return 1;
    }
    uint8_t *dstp = blob_base + blob_off;
    for (size_t j = 0; j < pkt_len; j++) {
      uint8_t k = (uint8_t)((i * 131u + j) & 0xFFu);
      dstp[j] = (uint8_t)(pkt[j] ^ cap->xormask ^ k);
    }
    // write entry (little endian)
    uint32_t *ent = (uint32_t *)(entry_base + i * 8);
    ent[0] = blob_off;
    ent[1] = (uint32_t)pkt_len;
    blob_off += (uint32_t)pkt_len;

    // Wipe plaintext packet and per-iteration chunk before core time.
    secure_bzero(pkt, pkt_len);
    free(pkt);
    secure_bzero(chunk, sizeof(chunk));

    usleep(80 * 1000); // slight spacing
  }

  // Ensure blob_len is written before we signal READY_FOR_CORE.
  *(volatile uint32_t *)&cap->blob_len = blob_off;
  __asm__ __volatile__("" ::: "memory");

  // Wipe base64 plaintext and free, so it won't appear in the core dump.
  secure_bzero(b64, b64_len + 1);
  free(b64);

  // Tell the generator it's safe to gcore us now.
  fprintf(stderr, "READY_FOR_CORE\n");
  fflush(stderr);

  // Keep alive so author can gcore us (post-wipe)
  for (int s = 0; s < keepalive_secs && !g_stop; s++) {
    usleep(1000 * 1000);
  }

  // Intentionally don't free `cap`; it must remain in heap in the core.
  close(fd);

  fprintf(stderr, "[exfil] exiting\n");
  return 0;
}


