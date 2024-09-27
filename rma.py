# Project: RMA File Manager
# Author: @Vaccummer https://github.com/Vaccummer
# Date: 2024-09-10
# utf-8
import shutil
import os
import argparse
import sys
import time 
from glob import glob

def is_path(path_f):
    if not isinstance(path_f, str):
        return False
    if os.path.exists(path_f):
        return True
    else:
        return False

parser = argparse.ArgumentParser(description="RMA File Manager v1.0\n@Vaccummer   https://github.com/Vaccummer\nEnvironment Variable Name: RMA_TRASH_DIR",
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-p", "--permanent", help="Permanently delete the files", action="store_true")
parser.add_argument("-d", "--directory", help="Print the trash directory", action="store_true")
parser.add_argument("-l", "--list", help="List the files in the trash", action="store_true")
parser.add_argument("-c", "--clear", help="Clear the trash", action="store_true")
parser.add_argument("-f", "--fetch", help="Fetch the files from the trash", action="store_true")
parser.add_argument("paths", nargs='*', help="One or more file or directory paths to operate on")
args= parser.parse_args()

default_trash_path = "/tmp/rma_trash"
rma_trash_dir = os.environ.get('RMA_TRASH_DIR')
rma_trash_dir = rma_trash_dir if is_path(rma_trash_dir) else default_trash_path


def move_file(src:str, permenant:bool=False):
    if permenant:
        check_f = input(f"Are you sure you want to delete {src}? (y/n): ")
        if check_f.lower() == 'y':
            if os.path.isfile(src):
                os.remove(src)
            elif os.path.isdir(src):
                shutil.rmtree(src)
    else:
        file_name = os.path.basename(src)
        dst = os.path.join(rma_trash_dir, file_name)
        while os.path.exists(dst):
            file_name = "(1)" + file_name
            dst = os.path.join(rma_trash_dir, file_name)
        shutil.move(src, dst)
def format_file_size(size:int, ):
    size = float(size)
    if size < 1024:
        return (size, "B")
    size /= 1024
    if size < 1024:
        return (size, "KB")
    size /= 1024
    if size < 1024:
        return (size, "MB")
    size /= 1024
    return (size, "GB")
def print_help():
    print("RMA File Manager v1.0")
    print("Author: @Vaccummer, https://github.com/Vaccummer")
    print("Environment Variables: RMA_TRASH_DIR")
    print("Options:")
    print("  -p, --permanent: Permanently delete the files")
    print("  -h, --help: List the files")
    print("  -l, --list: List the files in the trash")
    print("  -c, --clear: Clear the trash")
    print("  -d, --directory: Print the trash directory")
    print("  -f, --fetch: Fetch the files from the trash")
def print_trash_dir():
    if rma_trash_dir == default_trash_path:
        print(f"Trash directory is set to default: {default_trash_path}")
    else:
        print(rma_trash_dir)
def print_trash():
    files = os.listdir(rma_trash_dir)
    file_time = [[os.path.getmtime(os.path.join(rma_trash_dir, file_i)), os.path.getsize(os.path.join(rma_trash_dir, file_i)), file_i] for file_i in files]
    file_time.sort(key=lambda x: x[0])
    print(f"Files Num {len(files):>3} in Trash: ")
    for order_i, file_time_i in enumerate(file_time):
        time_i, size_i, file = file_time_i
        time_f = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time_i))
        size, unit = format_file_size(size_i)
        print(f'  {("["+str(order_i)+"]"):<5}', end="\t")
        print(f'{time_f}', end="\t")
        print(f'{(str(size)[0:6]+unit):>10}', end="\t")
        print(f'{file}')
def clear_trash():
    doc_num = len(os.listdir(rma_trash_dir))
    check_f = input(f"Are you sure you want to delete {doc_num} files in trash? (y/n): ")
    if check_f.lower() == 'y':
        shutil.rmtree(rma_trash_dir)
        os.makedirs(rma_trash_dir, exist_ok=True)
        print("Trash cleared successfully!")
def fetch_files(target_f, paths_f):
    if target_f in paths_f:
        src = os.path.join(rma_trash_dir, target_i)
        dst = os.path.join(os.getcwd(), target_i)
    elif isinstance(target_i, int) and target_i < len(paths_f):
        src = os.path.join(rma_trash_dir, files[target_i])
        dst = os.path.join(os.getcwd(), files[target_i])
    else:
        print("Target not found in trash!")
        return
    if os.path.exists(dst):
        check_f = input(f"File {dst} already exists, do you want to overwrite it? (y/n): ")
        if check_f.lower() == 'y':
            try:
                os.remove(dst)
                shutil.move(src, dst)
                print(f"File {os.path.basename(dst)} was merged!")
            except Exception as e:
                print(f"{dst} Merge Encountered Error: {e}")
    else:
        try:
            shutil.move(src, dst)
            print(f"File {os.path.basename(dst)} was fetched!")
        except Exception as e:
            print(f"{dst} Fetch Encountered Error: {e}")


if __name__ == "__main__":
    if args.directory:
        print_trash_dir()
        sys.exit(0)
    elif args.list:
        print_trash()
        sys.exit(0)
    elif args.clear:
        clear_trash()
        sys.exit(0)
    elif args.fetch:
        files = os.listdir(rma_trash_dir)
        paths = args.paths
        for target_i in paths:
            try:
                fetch_files(target_i, files)
            except Exception as e:
                print(f"{target_i} Fetch Encountered Error: {e}")
        sys.exit(0)
    paths = [os.path.abspath(os.path.expanduser(path_i)) for path_i in args.paths]
    path_n = []
    for path_i in paths:
        path_l = glob(path_i) if "**" not in path_i else glob(path_i, recursive=True)
        if len(path_l) == 0:
            continue
        path_n += path_l

    if len(path_n) == 0:
        print("No valid path found!")
        sys.exit(0)
    
    if args.permanent:
        check_f = input(f"Are you sure you want to delete {len(paths)} files? (y/n): ")
        if check_f.lower() == 'y':
            for path_i in path_n:
                try:
                    move_file(path_i, args.permanent)
                except Exception as e:
                    print(f"{path_i} Move Encountered Error: {e}")
        sys.exit(0)
    else:
        for path_i in path_n:
            try:
                move_file(path_i, args.permanent)
            except Exception as e:
                print(f"{path_i} Move Encountered Error: {e}")
        sys.exit(0)