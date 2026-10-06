import time
from comm.RYLR998 import CommDevice
comm_device = CommDevice()


def send_local_message(message):
    message += "\r\n"
    values = bytearray(message.encode("utf-8"))
    print(f"send_local_message(): {message}")
    
    comm_device.write_to(values)
    #uart.write(values)
    
    #WaitUntilTransmitterDone("Local message")

    #while uart.any() == 0:
    while comm_device.received_any() == 0:
        print("Waiting for local response.x..")
        time.sleep(0.2)

    rxData = bytes() # a byte array object
    while comm_device.received_any() > 0:
        rxData += comm_device.get_byte()
        last_byte = rxData[-1]
        if (last_byte == '\n'):
            break
    return rxData

def ThereIsARequest():
    there_is_a_request = False
    if comm_device.received_any():
        there_is_a_request = True
    return there_is_a_request


def GetMessage():
    print("In GetMessageNew!!")
    response = comm_device.get_line()
    print(f"GetMessageNew_Response:{response}")
    return response.decode('utf-8')[:-2]


def InitializeComm(this_board_lora_address="104", this_network_id = "18"):
    expected_response = b"+OK"
    while True:
        response = send_local_message("AT")
        print(f"local_response={response}")
        if expected_response in response:
            print(f"The string {expected_response} was found in the received data.\n")
            break
        else:
            print(f"The string {expected_response} was NOT found in the received data. trying again...")
            time.sleep(1)

    #response = send_local_message("AT+RESET")
    #print(f"reset local_response={response}")
    
    message = "AT+RESET\r\n"
    message = message.encode('utf-8')
    values = bytearray(message)
#    uart.write(values)
#    local_response = uart.readline()
    comm_device.write_to(values)
    local_response = comm_device.get_line()

    #ThereIsAnError(local_response)
    print(f"x local response={local_response}")
    #time.sleep(1)
    #local_response = uart.readline().decode('utf-8').strip()
    local_response = comm_device.get_line()
    print(f"y local response={local_response}")
    #ThereIsAnError(local_response)

    
    message = "AT+ADDRESS=" + this_board_lora_address + "\r\n"
    message = message.encode('utf-8')
    values = bytearray(message)
#    uart.write(values)
#    uart.write(values)
#    local_response = uart.readline()
    comm_device.write_to(values)
    local_response = comm_device.get_line()
    print(f"Response to ADDRESS:{local_response}")


#        message = "AT+NETWORKID=18\r\n"
    message = "AT+NETWORKID=" + this_network_id + "\r\n"
    message = message.encode('utf-8')
    values = bytearray(message)
#    uart.write(values)
#    local_response = uart.readline()
    comm_device.write_to(values)
    local_response = comm_device.get_line()
    print(f"Response to NETWORKID:{local_response}")
    
def GetCommand(received_message):
    # split(",") breaks the string into substrings separated by commas:
    string_list   = received_message.split(",")
    # string_list is now ["+RCV=100" , "7", "Helpin2", "-22,11"]   
    # so
    # string_list[0] = "+RCV=100"      Source of command
    # string_list[1] = "7"             Length of command string 
    # string_list[2] = "Helpin2"       Command string
    # string_list[3] = "-22,11"        Signal strength
    return string_list[2]
  
def TransmitMessage(message):
    message += "\r\n"            
    print("t1")
    values = bytearray(message.encode("utf-8"))
    print(f"values:{values}")
    comm_device.write_to(values)    
    print("t2")
    response = comm_device.get_line()
    print("t3")
    #  [:-2] specifies the range, everything up to the last 2 (but not including) characters
    #  Example if a = "1234\n\r", then a[:-2] = "1234"
    #  Note that all messages to/from LoRa end with "\n\r"
    return response.decode('utf-8')[:-2]
        
