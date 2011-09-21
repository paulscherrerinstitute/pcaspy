import pcaspy
import time

while True:
    d = pcaspy.gdd()
    d.put(range(1000000))
    v = d.get()
    time.sleep(0.2)
