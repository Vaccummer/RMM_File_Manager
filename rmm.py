# Project: RMA File Manager
# Author: @Vaccummer https://github.com/Vaccummer
# Date: 2024-09-10
# utf-8
from time import strftime, localtime
from functools import partial
from shutil import move, rmtree
import stat
from os import path, makedirs, remove, listdir, scandir, getcwd, getlogin, environ, chmod
from argparse import ArgumentParser, RawTextHelpFormatter
from sys import argv, exit
from glob import glob

def delete_cb(func, path_f, exc_info):
    try:
        chmod(path_f, stat.S_IWRITE)
        func(path_f)
        return True
    except Exception as e:
        printr(f'{type(e).__name__} when "{format_path(path_f)}"->"/null", {e}')

def rm(path_t):
    try:
        remove(path_t)
        return True
    except Exception:
        chmod(path_t, stat.S_IWRITE)
        return True

def rm_auto(target_f):
    try:
        if target_f[0]:
            rmtree(target_f[1], onerror=delete_cb)
        else:
            rm(target_f[1])
        return True
    except Exception as e:
        printr(f'{type(e).__name__} when "{format_path(target_f[1])}"->"/null", {e}')
        return False

def is_path(path_f):
    if not isinstance(path_f, str):
        return False
    if path.exists(path_f):
        return True
    else:
        return False

def printl(text:str, log_path:str, print_check=True, end='\n'):
    if print_check:
        print(text, end=end)
    with open(log_path, 'a', encoding='utf-8') as f:

        f.write(text+end)

parser = ArgumentParser(description="RMA File Manager v1.0\n@Vaccummer   https://github.com/Vaccummer\n\nEnvironment Variable Name: $RMM_TRASH_DIR, $RMM_LOG_Path",
                                 formatter_class=RawTextHelpFormatter)
parser.add_argument("-p", "--permanent", help="Permanently delete the files", action="store_true")
parser.add_argument("-d", "--directory", help="Print the trash directory", action="store_true")
parser.add_argument("-l", "--list", help="List the files in the trash", action="store_true")
parser.add_argument("-c", "--clear", help="Clear the trash", action="store_true")
parser.add_argument("-f", "--fetch", help="Fetch the files from the trash", action="store_true")
parser.add_argument("paths", nargs='*', help="One or more file or directory paths to operate on")
args, unknown_args = parser.parse_known_args()
if unknown_args:
    print("Args parsing failed, please use rmm [-h] [-p] [-d] [-l] [-c] [-f] [paths ...]")
    exit(0)
default_trash_path = path.abspath('./rmm_trash')
default_log_path = path.abspath("./rmm.log")
trash_dir = environ.get('RMM_TRASH_DIR')
log_path = environ.get('RMM_LOG_Path')



if not (trash_dir and path.isdir(trash_dir)):
    trash_dir = default_trash_path
    makedirs(trash_dir, exist_ok=True)

if not (log_path and path.exists(path.dirname(log_path))):
    log_path = default_log_path

printr = partial(printl, log_path=log_path)

def format_path(path_f):
    dir_f, name_f = path.split(path_f)
    if dir_f == cwd_n:

        return f".\\{name_f}"
    elif dir_f == trash_dir:
        return f"$Trash\\{name_f}"
    else:
        return path_f

def mv(src:str, dst:str):
    try:
        move(src, dst)
        return True
    except Exception as e:
        printr(f'{type(e).__name__}: "{format_path(src)}"->"{format_path(dst)}", {e}')
        return False

def move_file(src:str, permenant:bool=False):
    if permenant:
        check_f = input(f'Are you sure to delete "{src}" ? (y/n): ')
        if check_f.lower() == 'y':
            if path.isdir(src):
                rmtree(src)
            else:
                rm(src)
    else:
        file_name = path.basename(src)
        dst = path.join(trash_dir, file_name)
        i_f = 1
        while path.exists(dst):
            file_name_t = file_name+f"_[{i_f}]"
            dst = path.join(trash_dir, file_name_t)
            i_f += 1
        mv(src, dst)
def format_file_size(size:int):
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
    print("RMM File Manager v1.1")
    print("Author: @Vaccummer, https://github.com/Vaccummer")
    print('Environment Variables:')
    print('  $"RMM_TRASH_DIR", $"RMM_LOG_Path"')
    print("Options:")
    print("  -p, --permanent: Permanently delete the files")
    print("  -h, --help: List the files")
    print("  -l, --list: List the files in the trash")
    print("  -c, --clear: Clear the trash")
    print("  -d, --directory: Print the trash directory")
    print("  -f, --fetch: Fetch the files from the trash")
def print_trash_dir():
    if trash_dir == default_trash_path:
        printr(f"Trash directory is set to default: {default_trash_path}")
    else:
        printr(f'$RMM_TRASH_DIR: "{trash_dir}"')
def print_log_path():
    if log_path == default_log_path:
        printr(f"Log path is set to default: {default_trash_path}")
    else:
        printr(f'$RMM_LOG_Path: "{log_path}"')
def print_trash():
    files = listdir(trash_dir)
    file_time = [[path.getmtime(path.join(trash_dir, file_i)), path.getsize(path.join(trash_dir, file_i)), file_i] for file_i in files]
    file_time.sort(key=lambda x: x[0])
    printr(f"Files Num {len(files):>3} in Trash: ")
    for order_i, file_time_i in enumerate(file_time):
        time_i, size_i, file = file_time_i
        time_f = strftime('%Y-%m-%d %H:%M:%S', localtime(time_i))
        size, unit = format_file_size(size_i)
        printr(f'  {("["+str(order_i)+"]"):<5}', end="\t")
        printr(f'{time_f}', end="\t")
        printr(f'{(str(size)[0:6]+unit):>10}', end="\t")
        printr(f'{file}')
def clear_trash(paths:tuple, files:list):
    if not paths:
        paths = ('*',)
    if paths == ('*',) or paths == ('**',):
        doc_num = len(listdir(trash_dir))
        check_f = input(f"Are you sure to delete all {doc_num} objects in trash? (y/n): ")
        if check_f.lower() == 'y':
            rm_auto((True, trash_dir))
            makedirs(trash_dir, exist_ok=True)
            printr("Trash Bin Cleared Successfully!")
            exit(0)
        else:
            printr("Operation Cancelled!")
            exit(0)
    target_rm = []
    length_f = len(files)
    for path_i in paths:
        if path_i.isdigit() :
            if int(path_i)<length_f:
                target_rm.append(files[int(path_i)])
            else:
                printr(f"Index {path_i} out of range!")
                continue
        else:
            path_temp = glob(path.join(trash_dir, path_i))
            target_rm.extend([(path.isdir(path.join(trash_dir, path_i)), path.join(trash_dir, path_i)) for path_i in path_temp])
    if not target_rm:
        printr("No valid path to clear!")
        return
    else:
        dir_num = sum([1 for i in target_rm if i[0]])
        file_num = sum([1 for i in target_rm if not i[0]])
        if len(target_rm) == 1:
            check_f = input(f'Are you sure to delete "{path.basename(target_rm[0][1])}" in trash? (y/n): ')
        else:
            check_f = input(f"Are you sure to delete these {dir_num} dirs, {file_num} files in trash? (y/n): ")
        if check_f.lower() == 'y':
            for i in target_rm:
                rm_auto(i)
            printr("Target Cleared Successfully!")
        else:
            printr("Operation Cancelled!")
            return
def fetch_files(target_f, paths_f):
    length_f = len(files)
    all_pass = False
    for target_i in target_f:
        try:
            if target_i.isdigit():
                index_f = int(target_i)
                if index_f < length_f:
                    sign_f, src_f = paths_f[index_f]
                    sign_s = 'Directory' if sign_f else 'File'
                    base_f = path.basename(src_f)
                    dst = path.join(getcwd(), base_f)
                    if path.exists(dst):
                        if not all_pass:
                            check_f = input(f"{sign_s} {base_f} already exists, do you want to overwrite it? (y/n/a): ")
                            if check_f.lower() == 'a':
                                all_pass = True
                        if check_f.lower() == 'y' or all_pass:
                            rm_auto(paths_f[target_i])
                            result_f = mv(src_f, dst)
                            if result_f:
                                printr(f"{sign_s} {path.basename(dst)} was fetched!")
                        else:
                            continue
                    else:
                        result_f = mv(src_f, dst)
                        if result_f:
                            printr(f"{sign_s} {path.basename(dst)} was fetched!")
                else:
                    printr(f"Index {target_i} out of range!")
                    continue
            else:
                paths_temp = glob(path.join(trash_dir, target_i))
                if not paths_temp:
                    printr(f"Target {target_i} not found in trash!")
                    continue
                for src_f in paths_temp:
                    dst = path.join(getcwd(), path.basename(src_f))
                    is_dir_f = path.isdir(src_f)
                    sign_f = 'Directory' if is_dir_f else 'File'
                    if path.exists(dst):
                        check_f = input(f"{sign_f} {dst} already exists, do you want to overwrite it? (y/n): ")
                        if check_f.lower() == 'y':
                            rm_auto((0, src_f))
                            result_f = mv(src_f, dst)
                            if result_f:
                                printr(f"{sign_f} {path.basename(dst)} was fetched!")
                    else:
                        result_f = mv(src_f, dst) 
                        if result_f:
                            printr(f"{sign_f} {path.basename(dst)} was fetched!")
        except Exception as e:
            printr(f'{e.__name__}: "{format_path(target_i)}"->".", {e}')


if __name__ == "__main__":
    cwd_n = getcwd()
    user_str = f"{getlogin()}"
    cmd_n = ' '.join(argv)
    time_n = strftime('%Y-%m-%d %H:%M:%S', localtime())
    start_str = f'{time_n} {user_str}@{cwd_n}$ {cmd_n}'
    printr(start_str, print_check=False)
    temp_l = []

    for path_i in args.paths:
        if path_i not in temp_l:
            temp_l.append(path_i)
        else:
            continue
    args.paths = tuple(temp_l)

    if args.directory:
        print_trash_dir()
        exit(0)
    elif args.list:
        print_trash()
        exit(0)
    elif args.clear or args.fetch:
        files = [] 
        for entry_i in scandir(trash_dir):
            if entry_i.is_dir():
                files.append((True, entry_i.path))
            else:
                files.append((False, entry_i.path))
        if args.fetch:
            fetch_files(args.paths, files)
            exit(0)
        else:
            clear_trash(args.paths, files)
            exit(0)
    if not args.paths:
        print_help()
    paths = [path.abspath(path.expanduser(path_i)) for path_i in args.paths]
    path_n = []
    
    for path_i in paths:
        path_l = glob(path_i) if "**" not in path_i else glob(path_i, recursive=True)
        if len(path_l) == 0:

            continue
        path_n += path_l
    if len(path_n) == 0:
        printr("No valid path found!")
        exit(0)
    
    if args.permanent:
        # check_f = input(f"Are you sure you want to delete {len(paths)} objects? (y/n): ")
        # if check_f.lower() == 'y':
        for path_i in path_n:
                try:
                    move_file(path_i, args.permanent)
                except Exception as e:
                    printr(f"{path_i} Move Encountered Error: {e}")
        exit(0)
    else:
        for path_i in path_n:
            try:
                move_file(path_i, False)
            except Exception as e:
                printr(f"{path_i} Move Encountered Error: {e}")
        
        exit(0)