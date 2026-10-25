import json
import os

FILE = "/water_meter.json"
TEMP_FILE = "/water_meter.tmp"


def save_total_pulses(total_pulses):
    with open(TEMP_FILE, "w") as f:
        json.dump({"total_pulses": total_pulses}, f)
    print("current directory", os.getcwd())
    print(os.listdir("/"))
    os.rename(TEMP_FILE, FILE)
    print(os.listdir("/"))


def load_total_pulses():
    try:
        with open(FILE, "r") as f:
            data = json.load(f)
            return data["total_pulses"]

    except OSError:
        return 0