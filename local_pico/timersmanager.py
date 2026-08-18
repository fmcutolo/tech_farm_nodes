import time

class TimersManager:
    def __init__(self) -> None:
        self.small = {}

    def Start(self,id_key,duration):
        start_time = time.ticks_ms()  #micro_python
#        start_time = time.time()  
        self.small[id_key] = [start_time, duration]

    def ReStart(self,id_key):
        start_time = time.ticks_ms()  #micro_python
        #start_time = time.time() 
        #first get the list
        self.small[id_key][0] = start_time

    def Expired(self,id_key):
        timer_expired = False
        the_timer = self.small[id_key]
        if time.ticks_ms() - the_timer[0] >= the_timer[1]: #micro_python
        #if time.time() - the_timer[0] >= the_timer[1]:
            timer_expired = True 
        return timer_expired


# tm = TimersManager()
# tm.Start("special", 1)
# tm.Start("mail_check", 9)
# a_counter = 0
# while True:
#     if (tm.Expired("special")):
#         print(f"{a_counter} special expired")
#         a_counter += 1
#         tm.ReStart("special")
#     if tm.Expired("mail_check"):
#         print("mail_check expired")
#         break


# print("finished!")