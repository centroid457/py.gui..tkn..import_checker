# print("file frame.py")
import subprocess
import sys
import os
import re
from pathlib import Path
from tkinter import Tk, Frame, Button, Label, BOTH, Listbox, Scrollbar
from tkinter import ttk

filefullname_as_link_path_default = __file__


def main(file_as_path=filefullname_as_link_path_default):
    update_data(file_as_path)
    root = Tk()
    app = Gui(root=root, parent=root, file_as_path=file_as_path)
    if access_this_module_as_import and get_data.count_found_modules_bad == 0:
        root.after(1000, root.destroy)
    app.mainloop()


def update_data(file_as_path=filefullname_as_link_path_default):
    if get_data.count_found_modules == 0:
        get_data.main(file_as_path)


# #################################################
# GUI
# #################################################
class Gui(Frame):
    """ main GUI window """
    def __init__(self, root=None, parent=None, file_as_path=filefullname_as_link_path_default):
        self.file_as_path = file_as_path
        update_data(file_as_path)
        super().__init__(root)
        self.root = root
        self.parent_main = parent
        self.gui_root_configure()

        self.create_gui_structure()
        self.window_move_to_center()


    def gui_root_configure(self):
        # ROOT_METHODS
        self.root.title("IMPORT CHECHER")
        self.root.geometry("800x500+100+100")   #("WINXxWINY+ShiftX+ShiftY")
        self.root.resizable(width=True, height=True)	# заблокировать возможность изменения размеров границ! В том числе на весь экран!!!
        #self.root.maxsize(1000, 1000)
        self.root.minsize(300, 300)
        self.root.overrideredirect(False)
        self.root.state('normal')     # normal/zoomed/iconic/withdrawn
        # self.root.iconbitmap(r'ERROR.ico')    =ONLY FILENAME! NO fileobject

        # WM_ATTRIBUTES
        self.root.wm_attributes("-topmost", False)
        self.root.wm_attributes("-disabled", False)
        self.root.wm_attributes("-fullscreen", False)
        self.root.wm_attributes("-transparentcolor", None)

        # WGT_PARAMETERS
        self.root["bg"] = "#005500" if get_data.count_found_modules_bad == 0 else "#FF0000"
        self.root["fg"] = None
        self.root["width"] = None
        self.root["height"] = None
        self.root["bind"] = None
        self.root["relief"] = "raised"  # "flat"/"sunken"/"raised"/"groove"/"ridge"
        self.root["borderwidth"] = 5


    def wgt_parameters_apply(self, wgt, dict_pointer):
        for key in dict_pointer:
            try:
                wgt[key] = dict_pointer[key]
            except:
                pass
                print(f"The object have no attribute [self.root[{key}]]")
        return


    def window_move_to_center(self):
        self.root.update_idletasks()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) / 2
        y = (screen_height - window_height) / 2
        self.root.geometry('+%d+%d' % (x, y))


    # #################################################
    # FRAMES
    # #################################################
    def create_gui_structure(self):
        self.parent_main.columnconfigure(0, weight=1)
        self.parent_main.rowconfigure([0, ], weight=0)          # INFO
        self.parent_main.rowconfigure([1, 2,], weight=1)        # VERSIONS, FILES
        self.parent_main.rowconfigure([3, ], weight=10)         # MODULES
        pad_external = 10

        # ======= FRAME-1 (INFO) ====================
        self.frame_info = Frame(self.parent_main)
        self.frame_info.grid(row=0, sticky="nsew", padx=pad_external, pady=pad_external)

        self.fill_frame_info(self.frame_info)

        # ======= FRAME-2 (VERSIONS) ====================
        self.frame_versions = Frame(self.parent_main)
        self.frame_versions.pack_propagate(0)
        self.frame_versions.grid(row=1, sticky="snew", padx=pad_external, pady=2)

        self.fill_frame_versions(self.frame_versions)

        # ======= FRAME-3 (FILES) ====================
        self.frame_files = Frame(self.parent_main)
        self.frame_files.pack_propagate(1)
        self.frame_files.grid(row=2, sticky="snew", padx=pad_external, pady=2)

        self.fill_frame_files(self.frame_files)

        # ======= FRAME-4 (MODULES) ====================
        self.frame_modules = Frame(self.parent_main)
        self.frame_modules.grid(row=3, sticky="snew", padx=pad_external, pady=2)

        self.fill_frame_modules(self.frame_modules)


    def fill_frame_info(self, parent):
        btn = Button(parent, text=f"miss\n checking\n modules")
        btn["bg"] = "#aaaaFF"
        btn["command"] = self.root.destroy
        btn.pack(side="left")

        lable = Label(parent)
        lable["font"] = ("", 15)
        lable.pack(side="left", fill="x", expand=1)
        if get_data.count_found_modules_bad > 0:
            lable["text"] = f"BAD SITUATION:\nYOU NEED INSTALL [{get_data.count_found_modules_bad}] modules"
            lable["bg"] = "#FF9999"
        else:
            lable["text"] = f"GOOD:\nALL MODULES ARE PRESENT!"
            lable["bg"] = "#99FF99"
        return


    def fill_frame_versions(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure([1], weight=1)
        parent.grid_rowconfigure([0, 2], weight=0)

        lable = Label(parent, bg="#d0d0d0")
        lable["text"] = f"FOUND python [{get_data.count_python_versions}]VERSIONS:"
        lable.grid(column=0, row=0, columnspan=2, sticky="snew")

        self.listbox_versions = Listbox(parent, height=4, bg=None, font=('Courier', 9))
        self.listbox_versions.grid(column=0, row=1, sticky="snew")

        self.scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.listbox_versions.yview)
        self.scrollbar.grid(column=1, row=1, sticky="sn")

        self.listbox_versions['yscrollcommand'] = self.scrollbar.set

        # STATUS FRAME
        frame_status_version = Frame(parent)
        frame_status_version.grid(column=0, columnspan=2, row=2, sticky="ew")

        btn = Button(frame_status_version, text=f"RESTART by selected")
        btn["bg"] = "#aaaaFF"
        btn["command"] = lambda: self.program_restart(python_exe=self.status_versions["text"]) if self.listbox_versions.curselection() != () else None
        btn.pack(side="left")

        self.status_versions = ttk.Label(frame_status_version, text="...SELECT item...", anchor="w")
        self.status_versions.pack(side="left")
        self.listbox_versions.bind("<<ListboxSelect>>", self.change_status_versions)

        # fill listbox
        versions_dict = get_data.python_versions_found
        for ver in versions_dict:
            self.listbox_versions.insert('end', ver.ljust(10, " ") + versions_dict[ver])
            if ver.endswith("*"):
                if get_data.count_found_modules_bad == 0:
                    self.listbox_versions.itemconfig('end', bg="#99FF99")
                else:
                    self.listbox_versions.itemconfig('end', bg="#FF9999")
        return

    def change_status_versions(self, event):
        #print(self.listbox_versions.curselection())
        selected_list = (0,) if self.listbox_versions.curselection() == () else self.listbox_versions.curselection()
        selected_version = self.listbox_versions.get(selected_list)
        for ver in get_data.python_versions_found:
            if selected_version.startswith(ver):
                self.status_versions["text"] = get_data.python_versions_found[ver]
        return


    def fill_frame_files(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure([1], weight=1)
        parent.grid_rowconfigure([0, 2], weight=0)

        lable = Label(parent, bg="#d0d0d0")
        lable["text"] = f"FOUND python [{get_data.count_found_files}]FILES:"
        lable.grid(column=0, row=0, columnspan=2, sticky="snew")

        self.listbox_files = Listbox(parent, height=6, bg="#55FF55", font=('Courier', 9))
        self.listbox_files.grid(column=0, row=1, sticky="snew")

        self.scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.listbox_files.yview)
        self.scrollbar.grid(column=1, row=1, sticky="sn")

        self.listbox_files['yscrollcommand'] = self.scrollbar.set

        self.status_files = ttk.Label(parent, text="...SELECT item...", anchor="w")
        self.status_files.grid(column=0, columnspan=2, row=2, sticky="ew")
        self.listbox_files.bind("<<ListboxSelect>>", self.change_status_files)

        # fill listbox
        files_dict = get_data.python_files_found_in_directory_dict
        for file in files_dict:
            self.listbox_files.insert('end', file.resolve())
            if not files_dict[file].isdisjoint(get_data.modules_found_infiles_bad):
                self.listbox_files.itemconfig('end', bg = "#FF9999")
        return

    def change_status_files(self, event):
        #print(self.listbox_files.curselection())
        selected_list = (0,) if self.listbox_files.curselection() == () else self.listbox_files.curselection()
        selected_filename = self.listbox_files.get(*selected_list)
        self.status_files["text"] = get_data.python_files_found_in_directory_dict[Path(selected_filename)]
        return


    def fill_frame_modules(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure([1], weight=10)
        parent.grid_rowconfigure([0, 2], weight=0)

        lable = Label(parent, bg="#d0d0d0")
        lable["text"] = f"FOUND importing [{get_data.count_found_modules}]modules:"
        lable.grid(column=0, row=0, columnspan=2, sticky="snew")

        self.listbox_modules = Listbox(parent, height=8, bg="#55FF55", font=('Courier', 9))
        self.listbox_modules.grid(column=0, row=1, sticky="snew")

        self.scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.listbox_modules.yview)
        self.scrollbar.grid(column=1, row=1, sticky="sn")

        self.listbox_modules['yscrollcommand'] = self.scrollbar.set

        # STATUS FRAME
        frame_status_modules = Frame(parent)
        frame_status_modules.grid(column=0, columnspan=2, row=2, sticky="ew")

        btn_module_install = Button(frame_status_modules, text=f"INSTALL")
        btn_module_install["bg"] = "#aaaaFF"
        btn_module_install["command"] = lambda: self.btn_module_action("install")
        btn_module_install.pack(side="left")

        btn_module_update = Button(frame_status_modules, text=f"upgrade")
        btn_module_update["bg"] = "#aaaaFF"
        btn_module_update["command"] = lambda: self.btn_module_action("upgrade")
        btn_module_update.pack(side="left")

        btn_module_delete = Button(frame_status_modules, text=f"DELETE")
        btn_module_delete["bg"] = "#aaaaFF"
        btn_module_delete["command"] = lambda: self.btn_module_action("delete")
        btn_module_delete.pack(side="left")


        self.status_modules = ttk.Label(frame_status_modules, text="...SELECT item...", anchor="w")
        self.status_modules.pack(side="left")
        self.listbox_modules.bind("<<ListboxSelect>>", self.change_status_modules)

        # fill listbox
        for module in get_data.ranked_modules_dict:
            #[CanImport=True/False, Placement=ShortPathName, InstallNameIfDetected]
            can_import, short_pathname, detected_installname = get_data.ranked_modules_dict[module]
            bad_module_index = 0
            if can_import:
                self.listbox_modules.insert('end', "%-20s \t[%s]"%(module, short_pathname))
            else:
                self.listbox_modules.insert(bad_module_index, "%-20s \t[%s]"%(module, short_pathname))
                self.listbox_modules.itemconfig(bad_module_index, bg = "#FF9999")
                bad_module_index += 1

        self.change_status_modules(None)
        return


    def change_status_modules(self, event):
        #print(self.listbox_modules.curselection())
        selected_list = (0,) if self.listbox_modules.curselection() == () else self.listbox_modules.curselection()
        selected_data = self.listbox_modules.get(*selected_list)
        selected_module_w_spaces = selected_data.split("\t")[0]
        self.selected_module = re.sub(r"\s", "", selected_module_w_spaces)
        self.status_modules["text"] = self.selected_module
        return


    def btn_module_action(self, mode):
        if mode not in ("install", "delete", "upgrade"):
            sys.stderr.write("WRONG PARAMETER MODE")
            return
        elif mode == "install":
            mode_cmd = "install"
        elif mode == "upgrade":
            mode_cmd = "install --upgrade"
        elif mode == "delete":
            mode_cmd = "uninstall"
        modulename = self.selected_module
        module_data = get_data.ranked_modules_dict[self.selected_module]
        modulename_cmd = modulename if module_data[2] is None else module_data[2]

        subprocess.run(f"py -m pip {mode_cmd} {modulename_cmd}")
        self.program_restart()
        return


    def program_restart(self, python_exe=sys.executable):
        """Restarts the current program.
        Note: this function does not return. Any cleanup action (like
        saving data) must be done before calling this function."""
        #python_exe = sys.executable

        # If you want to work with correct restart button DO NOT USE ANY PRINT-function befor!!!!
        # else programm will not actually restart (in PyCharm will not start after second Restart)
        os.execl(python_exe, python_exe, *sys.argv)


if __name__ == '__main__':
    access_this_module_as_import = False
    import get_data
    main()
else:
    from . import get_data  # main, python_files_found_in_directory_list, ranked_modules_dict
    access_this_module_as_import = True
