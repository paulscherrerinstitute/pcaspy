import pcaspy
import time

while True:
    d = pcaspy.gdd()
    d.put(range(1000000))
    time.sleep(0.2)
