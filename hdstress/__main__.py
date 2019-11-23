import os
import sys
import math
import argparse
import time
import queue
import copy
import random

import threading

from utils import print_verbose, print_err, format_human

import worker

DEFAULT_FILESIZE = 100  # 100MB
DEFAULT_THREADS  = 1

# argparse Object

args = None
 

def parse_commanline():
    global args
    # Parse command line and set default values for parameters
    parser = argparse.ArgumentParser()
    
    parser.add_argument("path", help="File size in MBytes", type=str)
    parser.add_argument("-t", "--test-size", help="Test size in GiB, 0 to full filesystem",
                        type=int, default=0)
    parser.add_argument("-s", "--file-size", help="File size in MBytes",
                    type=int, default=DEFAULT_FILESIZE)
    parser.add_argument("-j", "--jobs", help="Concurrent writes/reads",
                    type=int, default=DEFAULT_THREADS)
    
    # Advanced arguments
    parser.add_argument("-2", action='store_true',
                        help="Only verify created files in a previous run",
                        default=False)
    
    args = parser.parse_args()
    
    # Setup values    
    setattr(args, "file_size", args.file_size * 2 ** 20)    
    setattr(args, "test_size", args.test_size * 2 ** 30)
    setattr(args, "tmp_dir", "hd-stress.tmp")
    setattr(args, "files_dir", 1024)    
    # setattr(args,"file_size",2**20)
    
    # Check and setup some parameters
    args.jobs = args.jobs if args.jobs > 0 else 1
    print(args.jobs)
    setattr(args, "work_dir", args.path + "/" + args.tmp_dir)
    if not check_dir(args.path):
        print_err("Not valid directory at {}".format(args.path))
        sys.exit(255)    
    
    if not check_dir(args.work_dir, create=True):   
        print_err("Cannot continue, {} is not a directory".
                  format(args.work_dir))
        sys.exit(255)    
    
    
    # Check available space    
    disk = os.statvfs(args.work_dir)
    fs_free = disk.f_bsize * disk.f_bfree
    if fs_free <= args.test_size:
        print_err("Test size ({}) is larger available free space ({})".format(
            format_human(args.test_size), format_human(fs_free)))
        sys.exit(255)
    if args.test_size == 0:
        args.test_size = fs_free
    
    return args



def check_dir(path, create=False):
    # Check if 'path' exists and is a dir
    if os.path.exists(path) and not os.path.isdir(path):
        return False
    if os.path.exists(path) and os.path.isdir(path):
        return True
    # Dir not exists, create it?
    if create:            
        try:
            os.mkdir(path)
            return True
        except:
            return False
    return False
    
                
def calc_files_dirs(test_size, file_size=100 * 2 ** 20, max_files=1024):
    # return: (array dirs_list, array filse_list)
    files_required = int(test_size / file_size) + 1
    dirs_required = int(files_required / max_files) + 1 
    # Making dirs
    res_dirs = []
    res_files = []
    print_verbose("Required {} files {} dirs  ({} files per dir)".format(
        files_required, dirs_required, max_files))        
    while  dirs_required > 0: 
        res_dirs.append(
            args.work_dir + "/" + "{:09d}".format(dirs_required))
        dirs_required -= 1
    index = 0
    counter = max_files
    while files_required > 0:
        file_path = "{}/{:09d}".format(res_dirs[index], counter)
        #file_path = args.work_dir + "/" + file_name
        res_files.append(file_path)
        counter -= 1
        if counter < 0:
            counter = max_files
            index += 1
        files_required -= 1
        
    return (res_dirs, res_files)

def pass1(dirs_list, files_list):
    """ Create files_queue using a pattern
       @return List of files created
    """
    files_created = []         
    
    print_verbose("Test size {}, file size {}.".format(
                    format_human(args.test_size),
                    format_human(args.file_size)))        
    
   
    # Creating temporal dirs    
    for dir_name in dirs_list:
        if not check_dir(dir_name, create=True):
            print_err("Cannot continue, {} is not a directory".format(new_dir))
        else:
            print_verbose("Created directory {}".format(dir_name))
    
    # Create worker queue, if jobs > 1 create a random list        
    files_queue = queue.Queue()
    
    
    if args.jobs > 1:
        reordered_files = files_list.copy()
        while len(reordered_files) > 0:
            index = random.randint(0,len(reordered_files)-1)
            files_queue.put(reordered_files[index])
            del reordered_files[index]
    else:        
        for f_name in files_list:
            files_queue.put(f_name)
            
    # Starting workkers
    threads = []
    for i in range(args.jobs):
        print_verbose("Started writer job {}".format(i+1))
        th = worker.Writer(files_queue, files_created)
        th.start()
        threads.append(th)
    files_queue.join()
    for th in threads:
        files_queue.put(None)
    for th in threads:
        th.join()
    return files_created



def pass2(files_list):
    """ 
    Read files_list and verify file contents
    @return: Queue of files with error    
    """
    files_failed_list = []
    files_queue = queue.Queue()
                
    # Starting workkers
    worker.Reader.mFilesTotal = len(files_list)
    threads = []
    for i in range(args.jobs):
        print_verbose("Started reader job {}".format(i+1))
        th = worker.Reader(files_queue,files_failed_list)
        th.start()
        threads.append(th)
        
    # Send work to queue
    if args.jobs > 1:  # Create random queue 
        reordered_files = files_list.copy()
        while len(reordered_files) > 0:
            index = random.randint(0,len(reordered_files) -1 )
            files_queue.put(reordered_files[index])
            del reordered_files[index]
    else:        
        for f_name in files_list:
            files_queue.put(f_name)
        
    # Wait queue ends
    files_queue.join()
    for th in threads:
        files_queue.put(None)      
    for th in threads:
        th.join()
    return files_failed_list

      
def pass3(dirs_list, files_list):
    # TODO: Remove dirs
    print_verbose("Removing files ")
    for file_name in files_list:
        os.remove(file_name)
    dirs_list.append(args.work_dir)    
    for d in dirs_list:
        try:
            os.rmdir(d)
        except OSError as e:
            print_err("Cannot delete directory '{}': {}".format(
                d,e.strerror))        
    print_verbose("Files removed. Test finished")        
       

args = parse_commanline()

files_failed_list = []
files_list = []
dirs_list = []


if getattr(args, '2', False):
    # Only do pass 2
    existent_files_list = []
    print_verbose("Running only pass 2, files verification")        
    for root, dirs, files in os.walk(args.work_dir, topdown=False):
        for name in files:            
            existent_files_list.append(os.path.join(root, name))
    print_verbose("Found {} files".format(len(existent_files_list)))
    files_failed_list = pass2(existent_files_list)
else:
    # Do pass1 pass2 and pass3
    dirs_list, files_list = calc_files_dirs(
        args.test_size, args.file_size, args.files_dir)        
    
    files_queue = pass1(dirs_list, files_list)
    files_failed_list = pass2(files_queue) 
    if len(files_failed_list) > 0:
        print_err("Error: Test not passed, temporary files not removed")
    else:
        pass3(dirs_list,files_list)
      
if len(files_failed_list) > 0:    
    print_verbose("List of files failed:",)
    for file_name in files_failed_list:
       print(file_name)
    
