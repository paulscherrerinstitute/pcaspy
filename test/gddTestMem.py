import pcas
import time

while True:
    d = pcas.gdd()
    d.put(range(1000000))
    time.sleep(0.2)
    d.dump()
