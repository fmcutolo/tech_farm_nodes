from power.vsys import VSYS

voltage = VSYS()

def GetVsys():
    return voltage.read_vsys()