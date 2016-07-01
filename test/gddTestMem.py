from pcaspy.cas import gdd
import time

while True:
    gddValue = gdd()
    gddValue.put(range(1000000))
    v = gddValue.get()
    gddCtrl = gdd.createDD(34) # gddAppType_dbr_ctrl_double
    gddCtrl[1].put('eV')
    gddCtrl[2].put(0)
    gddCtrl[3].put(1)
    gddCtrl[4].put(0)
    gddCtrl[5].put(1)
    gddCtrl[6].put(0)
    gddCtrl[7].put(1)
    gddCtrl[8].put(0)
    gddCtrl[9].put(1)
    gddCtrl[10].put(3)
    gddCtrl[11].put(gddValue)


    time.sleep(0.1)
