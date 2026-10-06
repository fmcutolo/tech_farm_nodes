class SensorsData:
    params = [
        {"label": "v1",  "value": 0.0}, #VSYS, place decimal point for float
        {"label": "t1",  "value": 0.0}, #place decimal point for float
        {"label": "dt",  "value": 0},   #date time stamp
        {"label": "s1",  "value": 0},
        {"label": "h1",  "value": 0},
        {"label": "db",  "value": 0},   #debug counter
    ]

    def SaveIt(self, label, value):
#        print(f"Top label={label} value={value}")
        if isinstance(value,float):
            formatted_value = f"{value:.2f}" # if its a float show it as a.bc
        else:
            formatted_value = str(value) # must be an int

#        print(f"bottom label={label} value={value}")
        for param in self.params:
            if param["label"] == label:
                param["value"] = formatted_value
                break
    
    def GetSensors(self):
        result = ""
        for param in self.params:
            result += param["label"] + "=" + str(param["value"]) + "_"
#            print(param["label"])
        result = result[:-1]    
        return result
