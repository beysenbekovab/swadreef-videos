# Синтез звуков на numpy по меткам из web/timeline.json → mix.wav (−14 LUFS, пик ≤ −1 dBTP).
# Голоса и музыки нет: тихая «ночная» подложка + тапы, перелёты, щипки и колокольчики.
import json, os, subprocess, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
TL = json.load(open(os.path.join(HERE, 'web/timeline.json')))
M, DUR = TL['marks'], TL['duration']
rng = np.random.default_rng(1405)          # сид — звук одинаков при любом перерендере


def t_(d): return np.arange(int(d * SR)) / SR


def bandnoise(n, lo, hi):
    spec = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    spec[(f < lo) | (f > hi)] = 0
    x = np.fft.irfft(spec, n)
    return x / (np.abs(x).max() + 1e-9)


def env(n, a, d):
    """атака a с, экспоненциальный спад d с"""
    t = np.arange(n) / SR
    return np.minimum(t / max(a, 1e-4), 1) * np.exp(-np.maximum(t - a, 0) / d)


def tap():
    n = int(.12 * SR)
    click = bandnoise(n, 2500, 9000) * env(n, .0005, .006) * .5
    thump = np.sin(2 * np.pi * 140 * t_(.12)) * env(n, .001, .03)
    return click + thump * .8


def pop():
    t = t_(.16)
    f = 420 + 520 * (1 - np.exp(-t / .03))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), .002, .045) * .7


def sweep(d, rising, gain=.5):
    """перелёт: плавный переход тёмного шума в светлый (или наоборот)"""
    n = int(d * SR)
    lo, hi = bandnoise(n, 150, 900), bandnoise(n, 1200, 7000)
    k = np.linspace(0, 1, n) if rising else np.linspace(1, 0, n)
    shape = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return (lo * (1 - k) + hi * k * .6) * shape * gain


def pluck(freq, d=1.4):
    """Karplus–Strong"""
    n, p = int(d * SR), int(SR / freq)
    buf = rng.uniform(-1, 1, p)
    out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = .996 * .5 * (buf[i % p] + buf[(i + 1) % p])
    return out * env(n, .002, .5) * .6


def bell(freq, d=2.2, gain=.35):
    t = t_(d)
    parts = [(1, 1), (2.76, .45), (5.4, .2), (8.93, .08)]
    x = sum(a * np.sin(2 * np.pi * freq * r * t) * np.exp(-t * (1.6 + r * .9)) for r, a in parts)
    return x * np.minimum(t / .003, 1) * gain


def chime(): return bell(880) + .6 * np.pad(bell(1318.5, 2.11), (int(.09 * SR), 0))[:int(2.2 * SR)]
def shimmer():
    out = np.zeros(int(1.8 * SR))
    for i, f in enumerate([1568, 1760, 2093, 2349, 2637]):
        s = bell(f, 1.2, .16); o = int(i * .07 * SR); out[o:o + len(s)] += s
    return out


BANK = {'tap': tap, 'pop': pop, 'pluck': lambda: pluck(440) + .5 * pluck(659.3),
        'lift': lambda: sweep(.7, True, .35), 'drop': lambda: sweep(.6, False, .3),
        'whoosh': lambda: sweep(.9, True, .5), 'chime': chime, 'shimmer': shimmer}

mix = np.zeros(int((DUR + 1) * SR))
# подложка: тихий «ночной воздух», на 9 дБ ниже эффектов
bed = bandnoise(len(mix), 80, 1400)
bed *= .5 + .5 * np.sin(2 * np.pi * np.arange(len(mix)) / SR / 7.3) ** 2
fade = np.minimum(np.arange(len(mix)) / SR / 1.5, 1) * np.clip((DUR - np.arange(len(mix)) / SR) / 1.5, 0, 1)
mix += bed * fade * .06

for kind, mark in TL['sfx']:
    s = BANK[kind](); o = int(M[mark] * SR)
    # перелёты стартуют чуть раньше метки, чтобы пик совпал с движением
    if kind in ('lift', 'drop', 'whoosh'): o = max(0, o - int(.15 * SR))
    mix[o:o + len(s)] += s[:len(mix) - o]

mix = mix[:int(DUR * SR)]
mix /= np.abs(mix).max() / .8
raw = os.path.join(HERE, 'mix_raw.wav')
with wave.open(raw, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    pcm = (np.clip(mix, -1, 1) * 32767).astype('<i2')
    w.writeframes(np.repeat(pcm, 2).tobytes())

# громкость: двухпроходный loudnorm до −14 LUFS
p = subprocess.run(['ffmpeg', '-hide_banner', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1:LRA=11:print_format=json',
                    '-f', 'null', '-'], capture_output=True, text=True).stderr
m = json.loads(p[p.rindex('{'):p.rindex('}') + 1])
af = (f"loudnorm=I=-14:TP=-1:LRA=11:linear=false:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
      f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}"
      ",volume=1.1dB,alimiter=limit=0.87:attack=1:release=60:level=false")   # добираем последний дБ лимитером
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af', af, '-ar', str(SR), os.path.join(HERE, 'mix.wav')], check=True)
os.remove(raw)
print('mix.wav', m['input_i'], '→ −14 LUFS')
