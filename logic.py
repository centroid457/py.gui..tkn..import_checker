# print("file logic.py")
"""
HOW TO USE:
1. add in .gitignore line "__pycache__"
2. add this script to your project directory
3. add lines in your main script in place before first import line:
*********************
import logic
logic.Logic(path=__file__)
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
import threading
from time import sleep
from pathlib import Path

path_link_default = __file__
access_this_module_as_import = True  # at first need true to correct assertions!


class Logic:
    def __init__(self, path=path_link_default):
        # SETTINGS
        self.count_found_files_overcount_limit = 40      # if 0 - unlimited!
        # wo limitation if you pass global path with many files the tool can silently stop!
        self.MODULES_CAN_INSTALL = {
            # this names will use as known modules (which need installation in system)
            # in not installed modules set you can see which of then can be definitely installed
            # "IMPORT_NAME_IN_PROJECT": "PIP_INSTALL_NAME"
            # different names
            "contracts": "PyContracts",
            "PIL": "pillow",
            "wx": "wxPython",
            "nmap": "python-nmap",

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

        self.apply_path(path=path)
        return

    def apply_path(self, path=None):
        if path is not None:
            # if send path from outside, reload all data!
            self.path_link_received = Path(path)
            self.clear_data()
            self.create_data()
            return

        path = self.path_link_received
        if not path.exists():
            raise ValueError("Path not exists!!!")

        # by default find all modules in one level up (from current directory) with all subdirectories
        if path.is_dir():                             # if link was a directory
            self.path_dir_applied = Path(path)
        elif path.parent == Path(__file__).parent:    # if link is this file (direct start)
            self.path_dir_applied = Path(path).parent.parent
        else:
            self.path_dir_applied = Path(path).parent

        os.chdir(self.path_dir_applied)
        return

    # -------------------------------------------------------------
    # DATA
    def clear_data(self):
        # SETS/DICTS/LISTS
        self.modules_in_system_dict = {}
        self.python_versions_found = {}     # in system
        self.python_files_found_dict = {}
        self.modules_found_infiles = set()
        self.modules_found_infiles_bad = set()
        self.ranked_modules_dict = {}       # {modulename: [CanImport=True/False, Placement=ShortPathName, InstallNameIfDetected]}

        # COUNTERS
        self.count_python_versions = 0
        self.count_found_files = 0
        self.count_found_files_overcount = False
        self.count_found_modules = 0
        self.count_found_modules_bad = 0
        return

    def create_data(self):
        threading.Thread(target=self.generate_modules_in_system_dict).start()
        threading.Thread(target=self.find_python_interpreters).start()
        if not access_this_module_as_import: print("*"*80)

        self.apply_path()
        self.find_all_python_files()
        if not access_this_module_as_import: print("*"*80)

        self.find_all_importing_modules()
        self.rank_modules_dict()
        self._sort_ranked_modules_dict()
        self.generate_modules_found_infiles_bad()
        if not access_this_module_as_import: print("*"*80)
        return

    # -------------------------------------------------------------
    # VERSIONS
    def find_python_interpreters(self):
        self.python_versions_found = {}
        python_exe = sys.executable
        py_versions_sp = subprocess.Popen("py -0p", text=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        py_versions_lines_list = py_versions_sp.stdout.readlines()
        active_exe_found = False

        for line in py_versions_lines_list:
            mask = r'\s(\S+)\s+(\S.+)[\n]?'
            match = re.fullmatch(mask, line)
            if match:
                check_active_exe = (Path(match[2]).parent == Path(python_exe).parent)
                if check_active_exe:
                    active_exe_found = True
                found_py_version = match[1] + (" *" if check_active_exe else "")
                found_py_exe_path = match[2]

                full_version = self._get_exe_version(found_py_exe_path)
                self.python_versions_found.update({found_py_version: [full_version, found_py_exe_path]})

                cmd = f"{found_py_exe_path} -m pip install --upgrade pip"
                my_sp = subprocess.Popen(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if not active_exe_found:
            self.python_versions_found.update({"None *": [self._get_exe_version(python_exe), python_exe]})

        self.count_python_versions = len(self.python_versions_found)
        return

    def _get_exe_version(self, exe_path):
        full_version_sp = subprocess.Popen([exe_path, "-VV"], text=True, shell=True, stdout=subprocess.PIPE)
        full_version_list = full_version_sp.communicate()[0].split(" ")
        full_version = full_version_list[1] + "x" + full_version_list[-3]
        return full_version

    # -------------------------------------------------------------
    # FILES
    def find_all_python_files(self):
        self.python_files_found_dict = {}
        path = self.path_dir_applied
        for file_name in path.rglob(pattern="*.py*"):
            if os.path.splitext(file_name)[1] in (".py", ".pyw"):
                # print(file_name)
                self.count_found_files += 1
                if self.count_found_files == self.count_found_files_overcount_limit:
                    # print("TOO MANY FILES!!!")
                    self.count_found_files_overcount = True
                    break
                self.python_files_found_dict.update({file_name: set()})
                if not access_this_module_as_import: print(file_name)
        return

    # -------------------------------------------------------------
    # MODULES
    def generate_modules_in_system_dict(self):
        self.modules_in_system_dict = {}
        # produce dict - all modules detecting in system! in all available paths. (Build-in, Installed, located in current directory)
        # KEY=modulename:VALUE=location(CurDir|DLLs|lib|site-packages)
        for module_in_system in pkgutil.iter_modules():
            my_string = str(module_in_system.module_finder)
            mask = r".*\('(.+)'\)$"
            match = re.fullmatch(mask, my_string)[1]
            path_name = Path(match).name
            self.modules_in_system_dict.update({module_in_system.name:path_name})
        return

    def find_all_importing_modules(self):
        self.modules_found_infiles = set()
        file_list = self.python_files_found_dict
        # 1. find all import strings in all files
        # 2. parse all module names in them
        openhook = fileinput.hook_encoded(encoding="utf8", errors=None)
        for line in fileinput.input(files=file_list, mode="r", openhook=openhook):
            # print(f"[descriptor={fileinput.fileno():2}]\tfile=[{fileinput.filename()}]\tline=[{fileinput.filelineno()}]\t[{line}]")
            modules_found_inline = self._find_modulenames_set(line)
            self.python_files_found_dict[fileinput.filename()].update(modules_found_inline)
            self.modules_found_infiles.update(modules_found_inline)

        self.count_found_modules = len(self.modules_found_infiles)
        return

    def _find_modulenames_set(self, line):
        # find line with import-statements
        # return modulenames set
        modules_found_inline = set()

        line_wo_comments = line.split(sep="#")[0]
        found_modules_textgroup = self._find_modules_textgroup(line_wo_comments)

        if found_modules_textgroup not in [None, ]:
            modules_found_inline = self._split_modulenames_set(found_modules_textgroup)

        return modules_found_inline

    def _find_modules_textgroup(self, line):
        mask_import_as = r'\s*import\s+(.+?)(\s+as\s+.+)?[\t\r\n\f]*'
        mask_from_import = r'\s*from\s+(.+)\s+import\s+.*[\t\r\n\f]*'

        match1 = re.fullmatch(mask_import_as, line)
        match2 = re.fullmatch(mask_from_import, line)

        found = match1[1] if match1 else match2[1] if match2 else None
        return found

    def _split_modulenames_set(self, textgroup):
        # split text like "m1,m2" into {"m1", "m2"}
        text_wo_spaces = re.sub(r'\s', '', textgroup)
        modulenames_list_with_relative = text_wo_spaces.split(sep=",")
        modulenames_list_wo_relative = []
        for module in modulenames_list_with_relative:
            modulename_wo_relative = module.split(sep=".")[0]
            if modulename_wo_relative != "":
                modulenames_list_wo_relative.append(modulename_wo_relative)
                if not access_this_module_as_import: print(modulename_wo_relative)
        return set(modulenames_list_wo_relative)

    def rank_modules_dict(self):
        self.ranked_modules_dict = {}
        module_set = self.modules_found_infiles
        # detect module location if exist in system
        # generate dict like
        #       {modulename: [CanImport=True/False, Placement=ShortPathName, InstallNameIfDetected]}
        for module in module_set:
            self.ranked_modules_dict.update({module: self._rank_module_name(module)})
        # print(modules_in_files_ranked_dict)
        return

    def _rank_module_name(self, module_name):
        can_import = False
        short_pathname = self.modules_in_system_dict.get(module_name, None)
        detected_installname = self.MODULES_CAN_INSTALL.get(module_name, None)
        if pkgutil.find_loader(module_name) is not None:
            can_import = True
        elif list(Path.cwd().rglob(pattern=f"{module_name}*")) != []:
            can_import = True

        result = [can_import, short_pathname, detected_installname]
        return result

    def _sort_ranked_modules_dict(self):
        # sort dict with found modules
        sorted_dict_keys_list = sorted(self.ranked_modules_dict, key=lambda key: key.lower())
        self.ranked_modules_dict = dict(zip(sorted_dict_keys_list, [self.ranked_modules_dict[value] for value in sorted_dict_keys_list]))
        # print(ranked_modules_dict)
        return

    def generate_modules_found_infiles_bad(self):
        self.modules_found_infiles_bad = set()
        for m in self.ranked_modules_dict:
            if not self.ranked_modules_dict[m][0]:
                self.modules_found_infiles_bad.update({m})

        self.count_found_modules_bad = len(self.modules_found_infiles_bad)
        return


if __name__ == '__main__':
    access_this_module_as_import = False
    sample = Logic()

    # test correct parsing
    assert sample._split_modulenames_set("m1,m2 ,m3,    m4,\tm5") == set([f"m{i}" for i in range(1, 6)])

    assert sample._find_modulenames_set("import\tm1") == {"m1"}
    assert sample._find_modulenames_set("#import\tm1") == set()
    assert sample._find_modulenames_set(" import\t m1,m2") == {"m1", "m2"}
    assert sample._find_modulenames_set(" import\t m1 as m2") == {"m1"}
    assert sample._find_modulenames_set(" from m1 import m2 as m3") == {"m1"}
    assert sample._find_modulenames_set("#from m1 import m2 as m3") == set()
    assert sample._find_modulenames_set("import m1 #comment import m2") == {"m1"}
    # relative import (in packages)
    assert sample._find_modulenames_set(" from .. import m1 #comment import m2") == set()
    assert sample._find_modulenames_set(" from ..m1 import m2 #comment import m3") == set()
    assert sample._find_modulenames_set(" from . import m1 #comment import m2") == set()
    assert sample._find_modulenames_set(" from .m1 import m2 #comment import m3") == set()
    assert sample._find_modulenames_set(" from m1.m2 import m3 #comment import m4") == {"m1"}

    print("*"*80)
    print(f"[{sample.count_python_versions}]FOUND VERSIONS={sample.python_versions_found}")
    print()
    print(f"path=[{sample.path_dir_applied}]")
    print()
    print(f"[{sample.count_found_files}]FOUND FILES={sample.python_files_found_dict}")
    print()
    print(f"[{sample.count_found_modules}]FOUND MODULES={sample.ranked_modules_dict}")
    print()
    print(f"[{sample.count_found_modules_bad}]FOUND BAD MODULES={sample.modules_found_infiles_bad}")
    print("*"*80)
    input("Press ENTER to exit")
else:
    access_this_module_as_import = True