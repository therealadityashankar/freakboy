#!/usr/bin/env python3
import freakboy
import time

start = time.time()

chunk1 = freakboy.AudioData()
chunk2 = freakboy.AudioData()
chunk1.key_play_style = freakboy.msin

for _ in range(5):
    chunk2.drum_snare(0.5)
    chunk2.drum_snare(0.5)
    chunk2.add_silence(0.5)

for _ in range(15):
    chunk1.play_key(40, 0.5)

end = time.time()
print(end - start)

plai = freakboy.Player()
plai.add(chunk1, chunk2)
plai.play()

