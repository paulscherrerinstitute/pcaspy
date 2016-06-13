from pcaspy.cas import gdd
import time

while True:
    d = gdd()
    d.put(range(1000000))
    v = d.get()
    time.sleep(0.2)
