import time

class Time_tracker:
    def __init__(self, name=''):
        self.initiation_time = time.time()
        self.name = name
        self.start = time.time()

    def get_time_stamp(self, name:str):
        print_string = f'{name} time is: {round(time.time()-self.start, 2)}'
        print(print_string)




