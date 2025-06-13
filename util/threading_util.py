import threading
from util.data_util import json_util
from util.database import sql_util
from tqdm import tqdm

json_lock = threading.Lock()
db_lock = threading.Lock()
db_connection = sql_util.get_cursor()
db_cursor = db_connection[1]
db_connector = db_connection[0]

class ThreadingHandler():
    def __init__(self, thread_count=30):
        self.lock = threading.Lock()
        self.threads = []
        self.thread_count = thread_count
    def add_thread(self, target, args=()):
        while len(self.threads) >= self.thread_count:
            self.threads = [t for t in self.threads if t.is_alive()]
        thread = threading.Thread(target=target, args=args)
        self.threads.append(thread)
        thread.start()

    def start_process(self, param_list,target_function, process_message=f'Processing', saving_instructions=None):# isntructions as [(filename, frequency, subfolders, json)] if not json search shared memory
        bar_format = '{desc:<5.5}{percentage:3.0f}%|{bar:100}{r_bar}'.replace('5', str(len(process_message) +20))
        for index, param in (pbar := tqdm(iterable=enumerate(param_list), desc=process_message, ascii="-#",bar_format=bar_format, total=(len(param_list)+self.thread_count))):
            # bar display
            pbar_description = f'{len(self.threads)}/{self.thread_count} threads | {process_message}'
            bar_format = '{desc:<5.5}{percentage:3.0f}%|{bar:100}{r_bar}'.replace('5', str(len(pbar_description)+1))
            pbar.set_description(pbar_description)
            pbar.bar_format = bar_format

            # actually start a thread
            self.add_thread(target_function, args=(param))

            # save data every x iterations
            if saving_instructions:
                for saving_instruction in saving_instructions:
                    if (index+1)%saving_instruction[1]==0:
                        for thread in self.threads:
                            thread.join()
                        pbar.set_description(f'saving data | {process_message}')
                        try:
                            if not saving_instruction[3]:
                                json_util.dump_data(saving_instruction[0], data=json_util.get_shared_data(saving_instruction[0], subfolder=saving_instruction[2]), subfolder=saving_instruction[2])
                            else:
                                json_util.dump_data(saving_instruction[0], data=saving_instruction[3], subfolder=saving_instruction[2])
                        except:
                            print('something went wrong while saving data: ', saving_instruction[0])
        for thread in self.threads:
            thread.join()

