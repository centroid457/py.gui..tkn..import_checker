# print("file get_data.py")
"""
HOW TO USE:
1. add in .gitignore line "__pycache__"
2. add this script to your project directory
3. add lines in your main script in place before first import line:
*********************
import import_checker
import_checker.main(file_as_path=__file__)
*********************
WHAT IT WILL DO
Find all import lines in all files in the directory with recursion!
Lines only with SPACE symbols before specific code words.
Check modules which will import in project.
Find not installed.
Offer try to install.
---------------------
WHY DON'T USE MODULEFINDER???
Because it work incorrect! can't find TIME and SYS modules!
---------------------
TEST LINES
import pystray
import TEST_MODULE_1 #test comment
#import TEST_MODULE_2
"""

import re
import os
import sys
import pkgutil
import fileinput
import subprocess
from time import sleep
from pathlib import Path


# #################################################
# COMMON VARS & CONSTANTS
# #################################################
# INPUT
filefullname_as_link_path = __file__    # default value

# OUTPUT
python_files_found_in_directory_dict = {}
ranked_modules_dict = {}        #{modulename: [CanImport=True/False, Placement=ShortPathName, InstallNameIfDetected]}

# SETTINGS
MODULES_CAN_INSTALL = {
    # this names will use as known modules (which need installation in system)
    # in not installed modules set you can see which of then can be definitely installed
    # "IMPORT_NAME_IN_PROJECT": "PIP_INSTALL_NAME"
    # different names
    "contracts": "PyContracts",
    "PIL": "pillow",
    "wx": "wxPython",

    # similar names
    "TEST_MODULE_1": "TEST_MODULE_1",
    "matplotlib": "matplotlib",
    "numpy": "numpy",
    "openpyxl": "openpyxl",
    "pandas": "pandas",
    "playsound": "playsound",
    "plotly": "plotly",
    "psutil": "psutil",
    "pygame": "pygame",
    "pyscreenshot": "pyscreenshot",
    "pystray": "pystray",
    "requests": "requests",
    "tabulate": "tabulate",
}

# INTERNAL
access_this_module_as_import = True     # at first need true to correct assertions!
python_versions_found = {}              # in system
path_find_wo_slash = None
modules_found_infiles = set()
modules_found_infiles_bad = set()
modules_in_system_dict = {}

# COUNTERS
count_found_files_overcount = False
count_found_files_overcount_limit = 20      # if 0 - unlimited!
                                        # wo limitation if you pass global path with many files the tool can silently stop!

count_python_versions = 0
count_found_files = 0
count_found_modules = 0
count_found_modules_bad = 0

# #################################################
# FUNCTIONS
# #################################################
def main(file_as_path=filefullname_as_link_path):
    global path_find_wo_slash
    find_python_interpreters()

    # by default find all modules in one level up (from current directory) with all subdirectories
    if Path(file_as_path).is_dir():                             # if link was a directory
        path_find_wo_slash = Path(file_as_path)
    elif Path(file_as_path).parent == Path(__file__).parent:    # if link is this file (direct start)
        path_find_wo_slash = Path(file_as_path).parent.parent
    else:
        path_find_wo_slash = Path(file_as_path).parent

    os.chdir(path_find_wo_slash)
    update_system_modules_dict()
    if not access_this_module_as_import: print("*"*80)
    find_all_python_files_generate(path=path_find_wo_slash)
    if not access_this_module_as_import: print("*"*80)
    find_all_importing_modules(python_files_found_in_directory_dict)
    rank_modules_dict_generate()
    sort_ranked_modules_dict()
    update_modules_found_infiles_bad()
    update_counters()
    if not access_this_module_as_import: print("*"*80)


def find_python_interpreters():
    python_exe = sys.executable
    py_versions_sp = subprocess.Popen("py -0p", text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    py_versions_lines_list = py_versions_sp.stdout.readlines()

    for line in py_versions_lines_list:
        mask = r'\s(\S+)\s+(\S.+)[\n]?'
        match = re.fullmatch(mask, line)
        if match:
            found_py_version = match[1] + (" *" if Path(match[2]).parent == Path(python_exe).parent else "")
            found_py_exe_path = match[2]
            python_versions_found.update({found_py_version: found_py_exe_path})
    return


def find_all_python_files_generate(path=path_find_wo_slash):
    global count_found_files, count_found_files_overcount
    for file_name in path.rglob(pattern="*.py*"):
        if (#file_name != os.path.basename(__file__) and
            os.path.splitext(file_name)[1] in (".py", ".pyw")
            #and file_name.name != "__init__.py"
        ):
            #print(file_name)
            count_found_files += 1
            if count_found_files == count_found_files_overcount_limit:
                # print("TOO MANY FILES!!!")
                count_found_files_overcount = True
                break
            python_files_found_in_directory_dict.update({file_name: set()})
            if not access_this_module_as_import: print(file_name)
    return


def find_all_importing_modules(file_list):
    # 1. find all import strings in all files
    # 2. parse all module names in them
    openhook = fileinput.hook_encoded(encoding="utf8", errors=None)
    for line in fileinput.input(files=file_list, mode="r", openhook=openhook):
        # print(f"[descriptor={fileinput.fileno():2}]\tfile=[{fileinput.filename()}]\tline=[{fileinput.filelineno()}]\t[{line}]")
        modules_found_inline = _find_modulenames_set(line)
        python_files_found_in_directory_dict[fileinput.filename()].update(modules_found_inline)

    for module_set in python_files_found_in_directory_dict.values():
        modules_found_infiles.update(module_set)
    # print(modules_found_infiles)
    return


def _find_modulenames_set(line):
    # find line with import-statements
    # return modulenames set
    line_wo_comments = line.split(sep="#")[0]
    modules_found_inline = set()

    mask_import_as = r'\s*import\s+(.+?)(\s+as\s+.+)?[\t\r\n\f]*'
    mask_from_import = r'\s*from\s+(.+)\s+import\s+.*[\t\r\n\f]*'

    match1 = re.fullmatch(mask_import_as, line_wo_comments)
    match2 = re.fullmatch(mask_from_import, line_wo_comments)

    found_modulenames_group = match1[1] if match1 else match2[1] if match2 else None
    if found_modulenames_group not in [None, ]:
        modules_found_inline = _split_module_names_set(found_modulenames_group)

    return modules_found_inline


def _split_module_names_set(raw_modulenames_data):
    # split text like "m1,m2" into {"m1", "m2"}
    raw_modules_data_wo_spaces = re.sub(r'\s', '', raw_modulenames_data)
    module_names_list_with_relative = raw_modules_data_wo_spaces.split(sep=",")
    module_names_list_wo_relative = []
    for module in module_names_list_with_relative:
        module_name_wo_relative = module.split(sep=".")[0]
        if module_name_wo_relative != "":
            module_names_list_wo_relative.append(module_name_wo_relative)
            if not access_this_module_as_import: print(module_name_wo_relative)
    return set(module_names_list_wo_relative)


# test correct parsing
assert _split_module_names_set("m1,m2 ,m3,    m4,\tm5") == set([f"m{i}" for i in range(1, 6)])
assert _find_modulenames_set("import\tm1") == {"m1"}
assert _find_modulenames_set("#import\tm1") == set()
assert _find_modulenames_set(" import\t m1,m2") == {"m1", "m2"}
assert _find_modulenames_set(" import\t m1 as m2") == {"m1"}
assert _find_modulenames_set(" from m1 import m2 as m3") == {"m1"}
assert _find_modulenames_set("#from m1 import m2 as m3") == set()
assert _find_modulenames_set("import m1 #comment import m2") == {"m1"}
# relative import (in packages)
assert _find_modulenames_set(" from .. import m1 #comment import m2") == set()
assert _find_modulenames_set(" from ..m1 import m2 #comment import m3") == set()
assert _find_modulenames_set(" from . import m1 #comment import m2") == set()
assert _find_modulenames_set(" from .m1 import m2 #comment import m3") == set()
assert _find_modulenames_set(" from m1.m2 import m3 #comment import m4") == {"m1"}


def rank_modules_dict_generate(module_set=modules_found_infiles):
    # detect module location if exist in system
    # generate dict like
    #       {modulename: [CanImport=True/False, Placement=ShortPathName, InstallNameIfDetected]}
    for module in module_set:
        can_import = False
        short_pathname = modules_in_system_dict.get(module, None)
        detected_installname = MODULES_CAN_INSTALL.get(module, None)
        if pkgutil.find_loader(module) is not None:
            can_import = True
        elif list(Path.cwd().rglob(pattern=f"{module}*")) != []:
            can_import = True
        else:   # if first IF-expression will be False - real Import command will not help!)
            pass
            #try :
            #    exec(f'import {module}')
            #    can_import = True
            #except :
            #    pass

        ranked_modules_dict.update({module: [can_import, short_pathname, detected_installname]})
    # print(modules_in_files_ranked_dict)
    return


def sort_ranked_modules_dict():
    # sort dict with found modules
    global ranked_modules_dict
    sorted_dict_keys_list = sorted(ranked_modules_dict, key=lambda key: key.lower())
    ranked_modules_dict = dict(zip(sorted_dict_keys_list, [ranked_modules_dict[value] for value in sorted_dict_keys_list]))
    #print(ranked_modules_dict)
    return


def update_modules_found_infiles_bad():
    for m in ranked_modules_dict:
        if ranked_modules_dict[m][0] == False:
            modules_found_infiles_bad.update({m})


def update_system_modules_dict():
    # produce dict - all modules detecting in system! in all available paths. (Build-in, Installed, located in current directory)
    # KEY=modulename:VALUE=location(CurDir|DLLs|lib|site-packages)
    for module_in_system in pkgutil.iter_modules():
        my_string = str(module_in_system.module_finder)
        mask = r".*\('(.+)'\)$"
        match = re.fullmatch(mask, my_string)[1]
        path_name = Path(match).name
        modules_in_system_dict.update({module_in_system.name:path_name})

    #print(modules_in_system_dict)
    return


def update_counters():
    global count_python_versions, count_found_files, count_found_modules, count_found_modules_bad
    count_python_versions = len(python_versions_found)
    count_found_modules = len(ranked_modules_dict)
    count_found_modules_bad = len(modules_found_infiles_bad)
    return


if __name__ == '__main__':
    access_this_module_as_import = False
    main()
    print(f"[{count_python_versions}]FOUND VERSIONS={python_versions_found}")
    print()
    print(f"path=[{path_find_wo_slash}]")
    print()
    print(f"[{count_found_files}]FOUND FILES={python_files_found_in_directory_dict}")
    print()
    print(f"[{count_found_modules}]FOUND MODULES={ranked_modules_dict}")
    print()
    print(f"[{count_found_modules_bad}]FOUND BAD MODULES={modules_found_infiles_bad}")
    sleep(200)
else:
    access_this_module_as_import = True