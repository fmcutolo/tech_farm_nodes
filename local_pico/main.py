import time
from timersmanager import TimersManager # has to be located in Pico's Root directory!
from sensors import SensorsData
from rtc.tools_rtc import GetTemperatureOnBoard, ConvertCentigradeToFahrenheit, GetDateTime, SetDateTime, rtc_present
from eeprom.tools_eeprom import write_to_eeprom, read_from_eeprom, dump_eeprom, dump_eeprom_16, eeprom_present
from comm.tools_comm import InitializeComm, ThereIsARequest, GetMessage, GetCommand, TransmitMessage
from distance.tools_distance import GetDistance
from power.tools_power import GetVsys
from rgbleds.tools_rgbleds import SetRGBColor
from leds.tools_leds import LedTurnOn, LedTurnOff, LedToggle
from debug.tools_debug import DebugWrite, DebugAny, DebugGetByte

from machine import Pin

GP0  = 0    # is on PIN 1   input,  switch_input

print("I'm a node")
print("*")
print("*")
print("*")

switch_input  = Pin(GP0, Pin.IN, Pin.PULL_UP)
switch_value = switch_input.value()
DebugWrite(f"switch_value={switch_value}")

SetRGBColor('blue')
LedTurnOn()
SET_RTC_ON_BOOT = False 

THIS_BOARD_NAME         = "Picasso"
THIS_BOARD_LORA_ADDRESS = "104"
THIS_BOARD_VERSION      = "v1.01"
THIS_BOARD_INFO         = THIS_BOARD_NAME + " " + THIS_BOARD_LORA_ADDRESS + " " + THIS_BOARD_VERSION 
INFO_PROMPT             = THIS_BOARD_NAME +       THIS_BOARD_LORA_ADDRESS + ":"

TIMER_ID_DURATION_ALIVE = 1_000   #2000ms = 2 Seconds
DebugWrite("\nhello:")


""" Works!
DebugWrite("\nhello:")
while True:
    if DebugAny():
        from_keyboard = DebugGetByte()
        DebugWrite(f"got: {chr(from_keyboard[0])}")
        break
"""
CLOSED_DIST      = 10        # distance when mailbox is closed
MAIL_PRESENT_DIST = 8   # distance when mail is present
def CheckMailbox():
    last_state = None
    dist = GetDistance()
#             measure_distance()
    if dist is None:
        return 0, "NO_ECHO"

    # Detect mailbox open/close
    if dist > CLOSED_DIST:
        state = "OPEN"
    elif dist < MAIL_PRESENT_DIST:
        state = "MAIL_PRESENT"
    else:
        state = "CLOSED"  # no change
    return dist, state  #returns the tuple: (float, string)



my_timer = TimersManager()
my_timer.Start("index_alive_time", TIMER_ID_DURATION_ALIVE)

sensors_data = SensorsData()
#sensors_data.SaveIt("s1", switch_value)
sensors_data.SaveIt("s1", 1)
#temperature = read_temperature()
#sensors_data.SaveIt("t1", temperature)
sensors_data.SaveIt("t1", 55)
#voltage = read_supply_voltage()
#sensors_data.SaveIt("v1", voltage)
sensors_data.SaveIt("v1", 5.3)
#print(f"{INFO_PROMPT}Temperature: {temperature:.2f}°F, Supply Voltage: {voltage:.2f}V")

continuous_enabled = True
def ShowIt(debug_string, new_line_for_print = True):
    if not continuous_enabled:
        return
    
    if new_line_for_print:
        print(debug_string)
#        ext_uart.write(debug_string + "\n")
    else:
        print(debug_string,end="" )
#        ext_uart.write(debug_string)

InitializeComm()
if rtc_present():
    if SET_RTC_ON_BOOT:
        year  = 2025 # Can be yyyy or yy format
        month = 12
        mday  = 22
        hour = 8 # 24 hour format only
        minute = 16
        second = 0 # Optional
        weekday = 6 # Optional
        datetime = (year, month, mday, hour, minute, second, weekday)
        SetDateTime(datetime)

    print("RTC initialized.")

    year,  month, day, weekday, hour, minutes, seconds = GetDateTime() 
    print("RTC current time (raw):")
    print(f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minutes:02d}:{seconds:02d}")

    centigrade = GetTemperatureOnBoard()
    fahrenheit = ConvertCentigradeToFahrenheit(centigrade)
    print("DS3231 temperature:", centigrade, "°C ", "  ", fahrenheit, "°F")
else:
    print("No rtc found")
    
if eeprom_present():
        data = b"cats_and_dogs"
        write_to_eeprom(0,data)

        # # Read back
        result = read_from_eeprom(0,len(data))
        
        print("Read:", result)
        print("As text:", result.decode())

        dump_eeprom(0, 10)
        dump_eeprom_16(0, 32)
else:
    print("no eeprom found")

debug_alive_indicator_counter = 0

print("in loop:")
while True:
    if my_timer.Expired("index_alive_time"):
        LedToggle()

        my_timer.Start("index_alive_time", TIMER_ID_DURATION_ALIVE)
        circular_counter = debug_alive_indicator_counter % 10
        debug_alive_indicator_counter += 1
        if (debug_alive_indicator_counter % 100) == 0:
            #print("@")
            ShowIt(str(circular_counter))

            #temperature = read_temperature()
            #sensors_data.SaveIt("t1", temperature)
            #voltage = read_vsys_voltage()
            #sensors_data.SaveIt("v1", voltage)
            #ShowIt(f"\n{INFO_PROMPT}Temperature: {temperature:.2f}°F, Supply Voltage: {voltage:.2f}V")
        else:
            #s = f"{circular_counter}"
            ShowIt(f"{circular_counter}", new_line_for_print=False)
            
        vsys_voltage = GetVsys()
        sensors_data.SaveIt("v1",vsys_voltage)
        print("VSYS = {:.3f} V".format(vsys_voltage))
        DebugWrite("VSYS = {:.3f} V".format(vsys_voltage))
        switch_value = switch_input.value()
        sensors_data.SaveIt("s1",switch_value)
        DebugWrite(f"XXswitch_value={switch_value}")


        result = CheckMailbox()
        if result is not None:
            distance, state = result
            sensors_data.SaveIt("h1", distance)
            print(f"distance={distance} state={state}")
            DebugWrite(f"  distance={distance:.1f} inches:  {state}\n")
            if state is "OPEN":
                SetRGBColor("green")
            elif state is "CLOSED":
                SetRGBColor("blue")
            elif state is "MAIL_PRESENT":
                SetRGBColor("red")
            else:
                SetRGBColor("off")            
        
    if ThereIsARequest():
        print("there's a message!")
        received_message = GetMessage()
        print("received message:", received_message)
        command = GetCommand(received_message)
        #master_id = lora.GetMasterId(received_message)
        ShowIt(f"{INFO_PROMPT} command = {command}")
        #ShowIt(f"{INFO_PROMPT} master_id = {master_id}")
        #command_response=+RCV=104,40,v1=5.04_t1=72.25_dt=0_s1=0_h1=19.39_db=0,-24,10
        #sensors_values = "v1=5.04_t1=72.25_dt=0_s1=0_h1=19.39_db=0"   
        if "Helpin" in command:
            sensors_data.SaveIt("db",received_message[17])
            sensors_values = sensors_data.GetSensors()
            transmit_message = "AT+SEND=100," + str(len(sensors_values)) + "," + sensors_values 
            print(f"{INFO_PROMPT} transmit_message: {transmit_message}")
            local_response = TransmitMessage(transmit_message)
            print(f"{INFO_PROMPT} local_response: {local_response}")

        elif "Info" in command:
            transmit_message = "AT+SEND=100," + str(len(THIS_BOARD_INFO)) + "," + THIS_BOARD_INFO
            print(f"{INFO_PROMPT} transmit_message: {transmit_message}")
            local_response = TransmitMessage(transmit_message)
            print(f"{INFO_PROMPT} local_response: {local_response}")

