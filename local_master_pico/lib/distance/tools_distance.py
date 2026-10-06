from distance.hcsr04 import HCSR04 
hc = HCSR04()

def GetDistance():
    distance = hc.GetDistance()
    return distance

