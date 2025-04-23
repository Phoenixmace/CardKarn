import time

class Time_tracker:
    def __init__(self, name=''):
        self.initiation_time = time.time()
        self.name = name
        self.start = time.time()

    def get_time_stamp(self, name:str):
        print_string = f'{name} time is: {round(time.time()-self.start, 2)}'
        print(print_string)

class Loop_time:
    def __init__(self, name='', print_frequency=10):
        self.name = name
        self.print_frequency = print_frequency
        self.loop_number = 1
        self.loop_times = []
    def loop_start(self):
        self.loop_start_time = time.time()
    def loop_end(self):
        self.loop_times.append(time.time()-self.loop_start_time)
        self.loop_times = self.loop_times[:-30]
        self.loop_number += 1
        if self.loop_number%self.print_frequency == 0:
            print_string = f'average {self.name} time is: {round(sum(self.loop_times)/len(self.loop_times), 2)}'
            print(print_string)






