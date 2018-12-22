#!/usr/bin/env python3
import freakboy
import time

start = time.time()

chunk1 = freakboy.AudioData()
chunk2 = freakboy.AudioData()
drum_snare = freakboy.AudioData()
drum_snare.drum_snare(0.5)

for _ in range(5):
    chunk2.add_data(drum_snare.data)
    chunk2.add_data(drum_snare.data)
    chunk2.add_silence(0.5)

key = freakboy.AudioData()
key.play_key(60, 0.5)
for _ in range(15):
    chunk1.add_data(key.data)
end = time.time()
print(end - start)

plai = freakboy.Player()
plai.add(chunk1, chunk2)
plai.play()

