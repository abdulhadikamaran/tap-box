import wave
import struct
import math
import os
import random

def generate_tone(filepath, duration, freq_func, vol_func, sample_rate=44100):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with wave.open(filepath, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        
        n_samples = int(sample_rate * duration)
        for i in range(n_samples):
            t = float(i) / sample_rate
            freq = freq_func(t)
            volume = vol_func(t)
            sample = freq * volume * 32767.0
            sample = max(-32768, min(32767, int(sample)))
            wav.writeframesraw(struct.pack('<h', sample))

def generate_all():
    assets = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
    os.makedirs(assets, exist_ok=True)
    
    # 1. Shoot 
    generate_tone(os.path.join(assets, 'shoot.wav'), 0.15,
        lambda t: math.sin(2 * math.pi * (800 - 4000*t) * t),
        lambda t: max(0, 1.0 - t/0.15) * 0.3)
        
    # 2. Death
    generate_tone(os.path.join(assets, 'explosion.wav'), 0.6,
        lambda t: random.random() * 2 - 1.0,
        lambda t: max(0, 1.0 - (t/0.6)**0.5) * 0.3)
        
    # 3. Shield Pickup
    def powerup_freq(t):
        if t < 0.1: return math.sin(2 * math.pi * 600 * t)
        elif t < 0.2: return math.sin(2 * math.pi * 800 * t)
        else: return math.sin(2 * math.pi * 1200 * t)
    generate_tone(os.path.join(assets, 'shield.wav'), 0.4,
        powerup_freq,
        lambda t: max(0, 1.0 - t/0.4) * 0.3)
        
    # 4. Win 
    def win_freq(t):
        f = 400
        if t > 0.2: f = 500
        if t > 0.4: f = 600
        if t > 0.6: f = 800
        return math.sin(2 * math.pi * f * t) + math.sin(2 * math.pi * f*1.5 * t)*0.5
    generate_tone(os.path.join(assets, 'win.wav'), 1.0,
        win_freq,
        lambda t: max(0, 1.0 - t)*0.3)
        
    # 5. UI Click
    generate_tone(os.path.join(assets, 'click.wav'), 0.05,
        lambda t: math.sin(2 * math.pi * 400 * t),
        lambda t: max(0, 1.0 - t/0.05) * 0.5)
        
    # 6. UI Error
    generate_tone(os.path.join(assets, 'error.wav'), 0.2,
        lambda t: math.sin(2 * math.pi * 150 * t) * (1 if int(t*400)%2==0 else -1),
        lambda t: max(0, 1.0 - t/0.2) * 0.6)

if __name__ == "__main__":
    generate_all()
