# freakboy
make music in python3 !

## installation

`pip3 install .`

for development installation

`pip3 install -e .`

## usage

simple example:

```python
import freakboy

chunk = freakboy.AudioData()

for _ in range(5):
    chunk.drum_snare(0.5)
    chunk.drum_snare(0.5)
    chunk.add_silence(0.5)

plai = freakboy.Player()
plai.add(chunk)
plai.play()
```
