import threading
import time


from utils import print_verbose, print_err, format_human, get_free_space
from __init__ import BINARY_PATTERN
import __main__

class Writer(threading.Thread):

    def __init__(self,input_queue, output_list):
        threading.Thread.__init__(self)
        self.mInQueue = input_queue
        self.mOutList = output_list
        
    
    def run(self):        
        args = __main__.args # FIXME:
        total_files = self.mInQueue.qsize()
        while True:
            file_name = self.mInQueue.get()            
            if file_name is None:
                break            
            start_time = time.time()            
            self.createFile(file_name, BINARY_PATTERN, args.file_size)
            self.mOutList.append(file_name)
            elapsed_time = time.time() - start_time
            files_left = self.mInQueue.qsize()
            percent = int(50 * (total_files - files_left) / total_files)
            print_verbose("[{:02d}%,{},{} free] Created file {}  [{}/s]".format(
                percent,
                files_left, format_human(get_free_space(args.work_dir)), 
                file_name,
                format_human(int(args.file_size/elapsed_time))))            
            
            files_left -= 1
            self.mInQueue.task_done()                    
                        
    

    def createFile(self,file_name, binary_pattern, size=1024, seed=0):
        blocks = int (size / len(binary_pattern))
        try:
            with open(file_name, "wb") as binary_file:
                for i in range(blocks):            
                    res = binary_file.write(binary_pattern)
        except OSError as e:
            if e.errno == 28:
                print_verbose("Disk full")
            pass

class Reader(threading.Thread):
    
    mFilesTotal = 0
    mFilesProcessed = 0
    mLock = threading.Lock()

    def __init__(self,input_queue, output_list):
        threading.Thread.__init__(self)
        self.mInQueue = input_queue
        self.mOutList = output_list
        
        
        
    def run(self):
        while True:
            file_name = self.mInQueue.get()                        
            if file_name is None:
                break            
            offset = 0
            start_time = time.time()            
            with open(file_name, "rb") as binary_file:
                error = False
                while not error:
                    try:
                        res = binary_file.read(256)
                    except OSError as e:
                        error = True
                        print_err(e)                    
                    if not res:
                        break;
                    elif res != BINARY_PATTERN[0:len(res)]:                  
                      self.mOutList.append(file_name)
                      error = True
                    offset += len(res)                
            elapsed_time = time.time() - start_time
            files_left = Reader.mFilesTotal - Reader.mFilesProcessed
            percent = int(50 + 50 * Reader.mFilesProcessed / Reader.mFilesTotal)
            str_out = "[{:02d}% {} left {} err] File '{}' ".format(
                     percent, files_left, 
                     len(self.mOutList), 
                     file_name)
            if not error:
                str_out += "[{} {}/s] Ok".format(
                    format_human(offset),
                    format_human(int(offset/elapsed_time))
                    )
            else:
                str_out += "Error ar offset 0x{:X}".format(offset)
            print_verbose(str_out)
            with Reader.mLock:
                Reader.mFilesProcessed += 1
            self.mInQueue.task_done()
            
            

        
                
            