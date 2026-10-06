import time

class Lora:
    def __init__(self, uart_to_use) -> None:
        self.uart = uart_to_use

    def send_local_message(self, message):
        message += "\r\n"
        values = bytearray(message.encode("utf-8"))
        print(f"send_local_message(): {message}")
        self.uart.write(values)
        #WaitUntilTransmitterDone("Local message")

        while self.uart.any() == 0:
            print("Waiting for local response...")
            time.sleep(0.2)

        rxData = bytes() # a byte array object
        while self.uart.any() > 0:
            rxData += self.uart.read(1)
            last_byte = rxData[-1]
            if (last_byte == '\n'):
                break
        return rxData

    def Initialize(self, this_board_lora_address, this_network_id = "18"):
        expected_response = b"+OK"
        while True:
            response = self.send_local_message("AT")
            print(f"local_response={response}")
            if expected_response in response:
                print(f"The string {expected_response} was found in the received data.\n")
                break
            else:
                print(f"The string {expected_response} was NOT found in the received data. trying again...")
                time.sleep(1)

        #response = self.send_local_message("AT+RESET")
        #print(f"reset local_response={response}")
        
        message = "AT+RESET\r\n"
        message = message.encode('utf-8')
        values = bytearray(message)
        self.uart.write(values)
        local_response = self.uart.readline()
        #self.ThereIsAnError(local_response)
        print(f"x local response={local_response}")
        #time.sleep(1)
        #local_response = self.uart.readline().decode('utf-8').strip()
        local_response = self.uart.readline()
        print(f"y local response={local_response}")
        #self.ThereIsAnError(local_response)

        
        message = "AT+ADDRESS=" + this_board_lora_address + "\r\n"
        message = message.encode('utf-8')
        values = bytearray(message)
        self.uart.write(values)
        local_response = self.uart.readline()
        print(f"Response to ADDRESS:{local_response}")


#        message = "AT+NETWORKID=18\r\n"
        message = "AT+NETWORKID=" + this_network_id + "\r\n"
        message = message.encode('utf-8')
        values = bytearray(message)
        self.uart.write(values)
        local_response = self.uart.readline()
        print(f"Response to NETWORKID:{local_response}")



    # def WaitUntilTransmitterDone(self, source):
    #    while True:
    #        print(".",end="") #does not 
    #        if self.uart.txdone():
    #          print(f"tx done for {source}")
    #          break    
    #    time.sleep(0.1)

    def ThereIsARequest(self):
        there_is_a_request = False
        if self.uart.any():
            there_is_a_request = True
        return there_is_a_request

    # def delete_me_GetMessage(self):
    #     if uart.any(): 
    #         # there must be antenna bytes    
    #         time.sleep(0.1)  # Give it time to collect all bytes that came through the antenna.
    #         rxData = bytes() # a byte array object

    #         while uart.any() > 0:
    #             rxData += uart.read(1)
    #             last_byte = rxData[-1] #[-1] gets the last byte in an array
    #             if (last_byte == '\n'):
    #                 break
         
        return rxData.decode('utf-8')[:-2]          
    def GetMessage(self):
        print("In GetMessageNew!!")
        response = self.uart.readline()
        print(f"GetMessageNew_Response:{response}")
        return response.decode('utf-8')[:-2]

# there must be antenna bytes    
#            time.sleep(0.1)  # Give it time to collect all bytes that came through the antenna.
#            rxData = bytes() # a byte array object

#            while self.uart.any() > 0:
#                rxData += self.uart.read(1)
#                last_byte = rxData[-1] #[-1] gets the last byte in an array
#                if (last_byte == '\n'):
#                    break
         
#        return response.decode('utf-8')[:-2]          


#    def TransmitMessage(self,switch_value, sensors_values):


    def TransmitMessage(self,message):
        message += "\r\n"            
        values = bytearray(message.encode("utf-8"))
        self.uart.write(values)
        response = self.uart.readline()
        #  [:-2] specifies the range, everything up to the last 2 (but not including) characters
        #  Example if a = "1234\n\r", then a[:-2] = "1234"
        #  Note that all messages to/from LoRa end with "\n\r"
        return response.decode('utf-8')[:-2]


    def GetCommand(self, received_message):
        # split(",") breaks the string into substrings separated by commas:
        string_list   = received_message.split(",")
        # string_list is now ["+RCV=100" , "7", "Helpin2", "-22,11"]   
        # so
        # string_list[0] = "+RCV=100"      Source of command
        # string_list[1] = "7"             Length of command string 
        # string_list[2] = "Helpin2"       Command string
        # string_list[3] = "-22,11"        Signal strength
        return string_list[2]

    def GetMasterId(self, received_message):
        string_list   = received_message.split(",")
        # for the above example, master id is in '+RCV=100'
        master_id = string_list[0].split("=")[1]   # interested in 
        return master_id

