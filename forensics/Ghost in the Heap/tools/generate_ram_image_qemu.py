from __future__ import annotations

import argparse
import os
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)


def build_static_exfil(out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "gcc",
            "-O2",
            "-static",
            "-s",
            "-Wall",
            "-Wextra",
            "-std=c11",
            "-o",
            str(out_path),
            str(ROOT / "src" / "exfil_dns.c"),
        ]
    )

def ensure_readable_kernel(build_dir: Path, kernel_path: Path) -> Path:
    try:
        with open(kernel_path, "rb"):
            return kernel_path
    except Exception:
        pass

    ver = os.uname().release
    deb_dir = build_dir / "kernelpkg"
    deb_dir.mkdir(parents=True, exist_ok=True)
    deb_name = f"linux-image-{ver}_*.deb"

    # Download the installed kernel package (no root required)
    run(["bash", "-lc", f"cd {deb_dir} && apt-get download -y linux-image-{ver} >/dev/null"])
    # Extract vmlinuz from the deb
    run(["bash", "-lc", f"cd {deb_dir} && rm -rf extracted && mkdir extracted && dpkg-deb -x linux-image-{ver}_*.deb extracted"])
    extracted_kernel = deb_dir / "extracted" / "boot" / f"vmlinuz-{ver}"
    if not extracted_kernel.exists():
        raise SystemExit(f"failed to extract kernel to {extracted_kernel}")
    return extracted_kernel


def write_initramfs(initramfs_dir: Path, exfil_bin: Path) -> None:
    (initramfs_dir / "bin").mkdir(parents=True, exist_ok=True)
    (initramfs_dir / "sbin").mkdir(parents=True, exist_ok=True)
    (initramfs_dir / "proc").mkdir(parents=True, exist_ok=True)
    (initramfs_dir / "sys").mkdir(parents=True, exist_ok=True)
    (initramfs_dir / "dev").mkdir(parents=True, exist_ok=True)
    (initramfs_dir / "tmp").mkdir(parents=True, exist_ok=True)

    shutil.copy2("/usr/bin/busybox", initramfs_dir / "bin" / "busybox")
    shutil.copy2(exfil_bin, initramfs_dir / "sbin" / "exfil_dns")

    init = initramfs_dir / "init"
    init.write_text(
        """#!/bin/busybox sh
set -eu

/bin/busybox --install -s /bin

mount -t proc none /proc
mount -t sysfs none /sys

echo "[init] booted"

# Run exfil process; it will wipe plaintext buffers and print READY_FOR_CORE when safe.
# Keep arguments minimal to avoid leaving obvious ASCII markers in RAM.
/sbin/exfil_dns --keepalive 120 >/tmp/exfil.out 2>/tmp/exfil.err &
PID=$!

echo "[init] exfil pid=$PID"

# Wait for marker before we consider memory dump safe.
for i in $(seq 1 300); do
  if grep -q READY_FOR_CORE /tmp/exfil.err 2>/dev/null; then
    echo "READY_FOR_DUMP"
    break
  fi
  /bin/busybox usleep 100000
done

# Keep running so host can dump memory.
while true; do
  /bin/busybox sleep 1
done
"""
    )
    init.chmod(0o755)


def pack_initramfs(initramfs_dir: Path, out_gz: Path) -> None:
    out_gz.parent.mkdir(parents=True, exist_ok=True)
    # cpio must run inside directory so file paths are relative
    cmd = f"cd {initramfs_dir} && find . -print0 | cpio --null -ov --format=newc | gzip -9 > {out_gz}"
    run(["bash", "-lc", cmd])


def qmp_cmd(sock: Path, payload: str) -> str:
    # Minimal QMP client using socat for simplicity.
    # QMP requires greeting read + capabilities enable.
    cmd = (
        "python3 - <<'PY'\n"
        "import json, socket, sys, time\n"
        f"sock_path={str(sock)!r}\n"
        "s=socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)\n"
        "s.connect(sock_path)\n"
        "s.settimeout(2)\n"
        "greet=s.recv(4096)\n"
        "s.sendall((json.dumps({'execute':'qmp_capabilities'})+'\\n').encode())\n"
        "resp=s.recv(4096)\n"
        f"s.sendall(({payload!r} + \"\\n\").encode())\n"
        "out=b''\n"
        "t0=time.time()\n"
        "while time.time()-t0<15:\n"
        "  try:\n"
        "    out+=s.recv(4096)\n"
        "    if b'\"return\"' in out or b'\"error\"' in out:\n"
        "      break\n"
        "  except Exception:\n"
        "    pass\n"
        "print(out.decode(errors='ignore'))\n"
        "s.close()\n"
        "PY"
    )
    return subprocess.check_output(["bash", "-lc", cmd], text=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", default=f"/boot/vmlinuz-{os.uname().release}", help="Kernel image to boot")
    ap.add_argument("--ram-mb", type=int, default=768, help="Guest RAM size in MB")
    ap.add_argument("--out", default=str(ROOT / "challenge" / "dist" / "memdump.raw"), help="Output RAM dump path")
    args = ap.parse_args()

    build_dir = ROOT / "build"
    build_dir.mkdir(exist_ok=True)
    exfil_bin = build_dir / "exfil_dns.static"
    build_static_exfil(exfil_bin)

    with tempfile.TemporaryDirectory() as td:
        initdir = Path(td) / "initramfs"
        initdir.mkdir(parents=True, exist_ok=True)
        write_initramfs(initdir, exfil_bin)
        initramfs_gz = build_dir / "initramfs.cpio.gz"
        pack_initramfs(initdir, initramfs_gz)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        out_path.unlink()

    qmp_sock = build_dir / "qmp.sock"
    if qmp_sock.exists():
        qmp_sock.unlink()

    kernel = ensure_readable_kernel(build_dir, Path(args.kernel))

    qemu_cmd = [
        "qemu-system-x86_64",
        "-machine",
        "pc,accel=kvm:tcg",
        "-m",
        str(args.ram_mb),
        "-cpu",
        "host",
        "-kernel",
        str(kernel),
        "-initrd",
        str(build_dir / "initramfs.cpio.gz"),
        "-nographic",
        "-no-reboot",
        "-append",
        "console=ttyS0 init=/init loglevel=7 panic=-1",
        "-qmp",
        f"unix:{qmp_sock},server,nowait",
    ]

    qemu_log = build_dir / "qemu_serial.log"
    if qemu_log.exists():
        qemu_log.unlink()

    proc = subprocess.Popen(
        qemu_cmd,
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    try:
        # Wait for READY_FOR_DUMP on serial
        t0 = time.time()
        ready = False
        with open(qemu_log, "w", encoding="utf-8", errors="ignore") as lf:
            while time.time() - t0 < 120:
                line = proc.stdout.readline() if proc.stdout else ""
                if line:
                    lf.write(line)
                    lf.flush()
                    if "READY_FOR_DUMP" in line:
                        ready = True
                        break
                else:
                    time.sleep(0.05)
        if not ready:
            tail = ""
            try:
                tail = "".join(open(qemu_log, "r", encoding="utf-8", errors="ignore").read().splitlines(True)[-40:])
            except Exception:
                pass
            raise SystemExit("guest did not reach READY_FOR_DUMP within 120s\n--- qemu tail ---\n" + tail)

        # Dump raw physical RAM using HMP pmemsave (avoids QEMU's default ELF core output)
        size = args.ram_mb * 1024 * 1024
        hmp = f'pmemsave 0 0x{size:x} {out_path}'
        payload = '{"execute":"human-monitor-command","arguments":{"command-line":' + repr(hmp) + "}}"
        qmp_cmd(qmp_sock, payload)
        print(f"[+] wrote RAW RAM dump to {out_path} ({out_path.stat().st_size} bytes)")
    finally:
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


