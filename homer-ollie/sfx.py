"""Sintetiza los efectos de sonido sincronizados con la animación.

    python3 sfx.py build/timeline.json build/sfx.wav

timeline.json lo escribe record.js a partir de window.timeline (tiempos en segundos).
"""
import json
import sys
import wave

import numpy as np

SR = 44100
rng = np.random.default_rng(7)


def lowpass(x, cutoff):
    """Filtro de un polo, aplicado dos veces (12 dB/oct)."""
    a = np.exp(-2 * np.pi * cutoff / SR)
    for _ in range(2):
        y = np.empty_like(x)
        acc = 0.0
        for i, v in enumerate(x):
            acc = (1 - a) * v + a * acc
            y[i] = acc
        x = y
    return x


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


def add(buf, t0, sig):
    i = int(t0 * SR)
    if i >= len(buf):
        return
    sig = sig[: len(buf) - i]
    buf[max(i, 0): i + len(sig)] += sig[max(-i, 0):]


def mix(*sigs):
    out = np.zeros(max(len(x) for x in sigs))
    for x in sigs:
        out[: len(x)] += x
    return out


def decay_tone(freqs, dur, tau, amp):
    t = np.arange(int(dur * SR)) / SR
    return amp * np.exp(-t / tau) * sum(np.sin(2 * np.pi * f * t) for f in freqs) / len(freqs)


def noise_burst(dur, tau, amp, cutoff=None):
    n = rng.standard_normal(int(dur * SR))
    if cutoff:
        n = lowpass(n, cutoff) * 3
    t = np.arange(len(n)) / SR
    return amp * n * np.exp(-t / tau)


def main(timeline_path, out_path):
    tl = json.load(open(timeline_path))
    n = int(tl["loop"] * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)

    # rodar sobre el concreto: ruido grave + retumbo de las ruedas
    roll_env = np.zeros(n)
    for a, b in tl["rolling"]:
        roll_env += np.clip((t - a) / 0.05, 0, 1) * np.clip((b - t) / 0.05, 0, 1)
    rumble = lowpass(rng.standard_normal(n), 380) * 2.2 + 0.25 * np.sin(2 * np.pi * 62 * t)
    out += 0.22 * roll_env * rumble * (1 + 0.15 * np.sin(2 * np.pi * 7 * t))

    # juntas de la banqueta: "tac" de cada eje de ruedas
    for c in tl["clicks"]:
        add(out, c, mix(decay_tone([180, 760], 0.08, 0.018, 0.35), noise_burst(0.03, 0.006, 0.18, 2500)))

    # pop: golpe seco de la cola + raspado de la lija con el pie delantero
    pop = tl["pop"]
    add(out, pop, mix(decay_tone([520, 1250, 2600], 0.25, 0.028, 0.9), noise_burst(0.02, 0.004, 0.6)))
    scrape = highpass(rng.standard_normal(int(0.3 * SR)), 1800)
    add(out, pop + 0.06, 0.14 * scrape * np.sin(np.linspace(0, np.pi, len(scrape))))

    # viento durante el vuelo
    land = tl["land"]
    air = (t > pop) & (t < land)
    s = np.clip((t - pop) / (land - pop), 0, 1)
    wind = lowpass(rng.standard_normal(n), 700) * 2.5
    out += 0.16 * air * np.sin(np.pi * s) * wind

    # aterrizaje: golpe grave + chasquido de la tabla
    add(out, land, mix(decay_tone([70, 95], 0.6, 0.12, 1.0), decay_tone([420, 980], 0.2, 0.035, 0.6),
                       noise_burst(0.08, 0.02, 0.5, 3000)))

    # mismos fundidos que el video
    out *= np.clip(t / 0.3, 0, 1) * np.clip((tl["loop"] - t) / 0.35, 0, 1)
    out *= 0.89 / np.max(np.abs(out))

    with wave.open(out_path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((out * 32767).astype("<i2").tobytes())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
