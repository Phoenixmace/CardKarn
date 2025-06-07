import threading


class ThreadingHandler():
    def __init__(self, thread_count=30):
        self.threads = []
        self.thread_count = thread_count
    def add_thread(self, target, args=()):
        while len(self.threads) >= self.thread_count:
            self.threads = [t for t in self.threads if t.is_alive()]
        thread = threading.Thread(target=target, args=args)
        self.threads.append(thread)
        thread.start()
    def start_process(self, param_list,target_function, process_message=f'Processing: '):
        for index, param in enumerate(param_list[:1]):
            self.add_thread(target_function, args=(param))
            print(f'{process_message} {round(index/len(param_list), 2)*100}%    {len(self.threads)}/{self.thread_count}')
        for thread in self.threads:
            thread.join()