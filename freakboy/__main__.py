import freakboy
import time

plai = freakboy.Player()

plai.add_sound(0.5, frequency=300, amplitude=freakboy.mexp)
plai.play()

plai.close()
