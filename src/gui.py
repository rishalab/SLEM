import tkinter as tk
import os
import sys
from tkinter import ttk, StringVar, BooleanVar, filedialog, messagebox
from runner import Runner
import threading
import importlib

# Determine the base path
if getattr(sys, 'frozen', False):  # Running as a PyInstaller executable
    base_path = sys._MEIPASS
else:  # Running as a script
    base_path = os.path.dirname(os.path.abspath(__file__))

# Read files using the base path
module_config_path = os.path.join(base_path, "module.config")


class ScrollableFrame(tk.Frame):
    """A scrollable frame class to make any frame vertically scrollable."""

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        # Canvas and scrollbar setup
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Layout the scrollbar and canvas
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Mousewheel support for scrolling
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class GUI:
    def __init__(self, functionExtractor):
        self.root = tk.Tk()
        self.root.title("Software Library Energy Meter")
        self.df_count = 0
        # Set up modules dictionary
        self.modules = {}
        self.dataset = {}
        try:
            with open(module_config_path) as mcnf:
                names = mcnf.readlines()
                for name in names:
                    try:
                        self.modules[name] = importlib.import_module(
                            name.strip())
                    except:
                        print(f"Unable to import {name}")
        except Exception as e:
            print(f"{e}")

        self.functionExtractor = functionExtractor
        self.runner = Runner()
        self.function_args = {}

        # Initialize layout frames
        self.init_layout()

        # Initialize component variables
        self.function_checkboxes = {}
        self.function_tabs = {}

        # Start main loop
        self.root.mainloop()

    def init_layout(self):
        """Set up the layout frames for the UI."""
        # Header frame with title
        self.header_frame = tk.Frame(self.root)
        self.header_frame.pack(fill="x", pady=10)
        tk.Label(
            self.header_frame, text="Software Library Energy Meter",
            font=("Arial", 16, "bold")
        ).pack()

        # Left frame (scrollable) for module and function selection
        self.left_frame = ScrollableFrame(self.root)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Middle frame for notebook and status/output sections
        self.mid_frame = tk.Frame(self.root)
        self.mid_frame.pack(side="left", fill="both",
                            expand=True, padx=10, pady=10)

        # Notebook widget for function tabs
        self.notebook = ttk.Notebook(self.mid_frame)
        self.notebook.pack(fill="both", expand=True)

        # Default tab with welcome message
        self.default_tab = tk.Frame(self.notebook)
        self.notebook.add(self.default_tab, text="Welcome")
        tk.Label(
            self.default_tab,
            text="Welcome to the Software Library Energy Meter!\n\nSelect a module and function on the left to begin.",
            font=("Arial", 12), justify="center"
        ).pack(expand=True, padx=20, pady=20)

        # Bottom section for status and output display
        self.status_frame = tk.Frame(
            self.mid_frame, relief="sunken", borderwidth=1)
        self.status_frame.pack(fill="x", pady=10)

        # Loading label
        self.loading_label = tk.Label(
            self.status_frame, text="Status: Idle", font=("Arial", 10), fg="green")
        self.loading_label.pack(side="left", padx=10, pady=5)

        # Output text box
        self.output_text = tk.Text(
            self.status_frame, height=4, wrap="word", font=("Arial", 10))
        self.output_text.pack(fill="both", expand=True, padx=10, pady=5)

        # Initialize module dropdown and function list
        self.init_module_dropdown()
        self.init_function_list()

        # Right frame
        self.right_frame = tk.Frame(
            self.root, padx=10, pady=10, bg="#f5f5f5", relief="groove")
        self.right_frame.pack(side="right", fill="both",
                              expand=True, padx=10, pady=10)

        # Right frame for managing modules
        tk.Label(self.right_frame, text="Module Manager", font=(
            "Arial", 14, "bold"), bg="#f5f5f5").pack(pady=(10, 5))

        # Module list display
        self.module_listbox = tk.Listbox(
            self.right_frame, width=30, height=15, selectmode="single", font=("Arial", 12))
        self.module_listbox.pack(pady=10)

        # Input for adding a new module
        self.module_entry = tk.Entry(self.right_frame, width=25)
        self.module_entry.pack(pady=5)

        self.add_button = tk.Button(
            self.right_frame, text="Add Module", command=self.add_module)
        self.add_button.pack(pady=5)

        # Add a section below the module manager
        tk.Label(self.right_frame, text="Dataset Manager", font=(
            "Arial", 14, "bold"), bg="#f5f5f5").pack(pady=(10, 5))

        # Dataset table display using Treeview
        self.dataset_table = ttk.Treeview(
            self.right_frame,
            columns=("ID", "Dataset Name"),
            show="headings",
            height=10
        )
        self.dataset_table.heading("ID", text="ID")
        self.dataset_table.heading("Dataset Name", text="Dataset Name")
        self.dataset_table.column("ID", anchor="center", width=80)
        self.dataset_table.column("Dataset Name", anchor="w", width=200)
        self.dataset_table.pack(pady=10, fill="x")

    def load_modules(self):
        """Load modules from module.config and display them in the listbox and dropdown."""
        try:
            with open("module.config", "r") as f:
                self.modules = f.read().splitlines()
                self.module_listbox.delete(0, tk.END)  # Clear current list
                for module in self.modules:
                    self.module_listbox.insert(tk.END, module)

                # Update the module dropdown
                self.update_module_dropdown()
        except FileNotFoundError:
            messagebox.showerror("Error", "module.config file not found.")

    def add_module(self):
        """Add a new module to module.config and update the listbox and dropdown."""
        new_module = self.module_entry.get().strip()

        if not new_module:
            messagebox.showwarning(
                "Input Error", "Please enter a module name.")
            return

        if new_module in self.modules.keys():
            # self.module_dropdown["values"] = list(self.modules.keys())
            messagebox.showwarning(
                "Duplicate Module", f"Module '{new_module}' already exists.")
            return

        try:
            # Dynamically import the module to check if it exists and is valid
            imported_module = importlib.import_module(new_module)

            # Add spaces for padding around the module name
            # Add spaces before and after the module name
            padded_module = f"  {new_module}  "

            # Add the module to the module.config file
            with open(module_config_path, "a") as f:
                f.write(new_module + "\n")

            # Add to modules dictionary and update UI components
            self.modules[new_module] = imported_module
            # Insert padded module name
            self.module_listbox.insert(tk.END, padded_module)
            self.update_module_dropdown()  # Update the dropdown with the new module

            # Clear the entry widget
            self.module_entry.delete(0, tk.END)

            messagebox.showinfo(
                "Success", f"Module '{new_module}' added successfully.")
        except ModuleNotFoundError:
            messagebox.showerror("Error", f"Module '{new_module}' not found.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def update_module_dropdown(self):
        """Update the module dropdown with the current list of modules."""
        self.module_dropdown["values"] = list(self.modules.keys())

    def init_module_dropdown(self):
        """Create dropdown for module selection."""
        tk.Label(self.left_frame.scrollable_frame,
                 text="Select Module:", font=("Arial", 10)).pack(anchor="w")
        self.module_var = StringVar()
        self.module_dropdown = ttk.Combobox(
            self.left_frame.scrollable_frame, textvariable=self.module_var,
            values=list(self.modules.keys()), state="readonly"
        )
        self.module_dropdown.pack(fill="x", pady=(5, 15))
        self.module_dropdown.bind("<<ComboboxSelected>>", self.load_functions)

        tk.Label(self.left_frame.scrollable_frame,
                 text="Select File:", font=("Arial", 10)).pack(anchor="w")

        self.file_var = StringVar()
        self.file_entry = ttk.Entry(self.left_frame.scrollable_frame,
                                    textvariable=self.file_var,
                                    state="readonly")
        self.file_entry.pack(fill="x", pady=(5, 5))

        self.browse_button = ttk.Button(
            self.left_frame.scrollable_frame,
            text="Browse",
            command=self.choose_file
        )
        self.browse_button.pack(anchor="w", pady=(0, 15))

        tk.Label(self.left_frame.scrollable_frame,
                 text="Select Dataset:", font=("Arial", 10)).pack(anchor="w")

        self.data_var = StringVar()
        self.data_entry = ttk.Entry(self.left_frame.scrollable_frame,
                                    textvariable=self.data_var,
                                    state="readonly")
        self.data_entry.pack(fill="x", pady=(5, 5))

        self.browse_data_button = ttk.Button(
            self.left_frame.scrollable_frame,
            text="Browse",
            command=self.choose_dataset
        )
        self.browse_data_button.pack(anchor="w", pady=(0, 15))

    def choose_file(self):
        """Open file dialog to choose a file and update the entry field."""
        file_path = filedialog.askopenfilename(
            title="Select a File",
            filetypes=(("Python Files", "*.py"), ("All Files", "*.*"))
        )
        if file_path:
            self.file_var.set(file_path)
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            try:
                # Dynamically import the module
                spec = importlib.util.spec_from_file_location(
                    module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Add the module to the dictionary
                self.modules[module_name] = module
                self.module_dropdown['values'] = list(self.modules.keys())

                # Select the newly added module in the dropdown
                self.module_var.set(module_name)

                # Provide success feedback
                self.output_text.insert(
                    "1.0", f"Module '{module_name}' loaded successfully.\n")
                sys.path.append("/".join(file_path.split("/")[:-1]))
            except Exception as e:
                self.output_text.insert("1.0", f"""Failed to load module '{
                                        module_name}': {e}\n""")

    def choose_dataset(self):
        """Open file dialog to choose a file and update the entry field."""
        file_path = filedialog.askopenfilename(
            title="Select a File",
            filetypes=(("CSV Files", "*.csv"),)
        )
        if file_path:
            self.data_var.set(file_path)
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            try:
                # Add the dataset to the dictionary
                self.dataset[f'df_{self.df_count}'] = file_path
                self.df_count += 1

                # Insert a message in the output text box
                self.output_text.insert(
                    "1.0", f"df_{self.df_count - 1} added: {module_name}\n")

                # Update the dataset table (Treeview)
                self.dataset_table.insert(
                    "", "end", values=(f"df_{self.df_count - 1}", module_name)
                )
            except Exception as e:
                print(f"{module_name} could not be loaded: {e}")

    def init_function_list(self):
        """Create scrollable list of function checkboxes."""
        tk.Label(self.left_frame.scrollable_frame, text="Functions:",
                 font=("Arial", 10)).pack(anchor="w")

        # Frame for function checkboxes with scrollbar
        self.function_frame = tk.Frame(self.left_frame.scrollable_frame)
        self.function_frame.pack(fill="both", expand=True)

    def load_functions(self, event):
        """Load functions of the selected module into checkboxes."""
        for widget in self.function_frame.winfo_children():
            widget.destroy()

        module_name = self.module_var.get()
        functions = self.functionExtractor(self.modules[module_name])
        self.function_args.clear()
        self.function_checkboxes.clear()

        for func_name in functions:
            self.function_args[func_name] = functions[func_name]
            var = BooleanVar()
            chk = tk.Checkbutton(
                self.function_frame, text=func_name, variable=var,
                command=lambda f=func_name, v=var: self.toggle_function(f, v)
            )
            chk.pack(anchor="w")
            self.function_checkboxes[func_name] = var

    def toggle_function(self, func_name, var):
        """Toggle display of function arguments in tabs based on checkbox state."""
        if var.get():
            self.add_function_tab(func_name)
        else:
            self.remove_function_tab(func_name)

    def add_function_tab(self, func_name):
        """Add selected function's arguments in a new tab with inputs and a Run button."""
        if func_name not in self.function_tabs:
            module_name = self.module_var.get()
            function_info = self.function_args[func_name]

            # Create a new scrollable tab for the function
            func_frame = ScrollableFrame(self.notebook)
            self.notebook.add(func_frame, text=func_name)
            self.function_tabs[func_name] = func_frame

            # Add argument entry fields inside the scrollable frame
            arg_entries = {}
            row = 0
            for arg in function_info:
                tk.Label(func_frame.scrollable_frame, text=f"{arg}:").grid(
                    row=row, column=0, sticky="w", padx=5, pady=5)
                entry = tk.Entry(func_frame.scrollable_frame)
                entry.grid(row=row, column=1, sticky="w", padx=5, pady=5)
                arg_entries[arg] = entry
                row += 1

            # Frequency and Interval fields
            tk.Label(func_frame.scrollable_frame, text="Frequency:").grid(
                row=row, column=0, sticky="w", padx=5, pady=5)
            freq_entry = tk.Entry(func_frame.scrollable_frame, width=10)
            freq_entry.grid(row=row, column=1, sticky="w", padx=5, pady=5)

            tk.Label(func_frame.scrollable_frame, text="Interval (s):").grid(
                row=row, column=2, sticky="w", padx=5, pady=5)
            interval_entry = tk.Entry(func_frame.scrollable_frame, width=10)
            interval_entry.grid(row=row, column=3, sticky="w", padx=5, pady=5)

            # Run button
            run_button = tk.Button(
                func_frame.scrollable_frame, text="Run",
                command=lambda: self.run_function(
                    module_name, func_name, arg_entries, freq_entry, interval_entry)
            )
            run_button.grid(row=row, column=4, padx=5, pady=5)

    def remove_function_tab(self, func_name):
        """Remove function's tab from the notebook."""
        if func_name in self.function_tabs:
            func_frame = self.function_tabs.pop(func_name)
            self.notebook.forget(func_frame)

    def run_function(self, module_name, func_name, arg_entries, freq_entry, interval_entry):
        """Run the specified function with arguments, frequency, and interval."""
        # Show loading
        self.loading_label.config(text="Status: Running...", fg="blue")
        self.output_text.delete("1.0", tk.END)

        # Gather function arguments
        args = {}
        for arg, entry in arg_entries.items():
            value = entry.get()
            if value:
                args[arg] = value

        frequency = int(freq_entry.get() or 0)
        interval = int(interval_entry.get() or 0)

        # Run function in a new thread to avoid UI freeze
        threading.Thread(
            target=lambda: self.execute_function(
                module_name, func_name, args, frequency, interval)
        ).start()

    def execute_function(self, module_name, func_name, args, frequency, interval, csv=""):
        """Execute the function and update output display."""
        try:
            output = self.runner.run(
                module_name, func_name, args, frequency, interval, csv, self.dataset)
            self.output_text.insert("1.0", f"Output:\n{output}")
        except Exception as e:
            self.output_text.insert("1.0", f"Error: {e}")
        finally:
            self.loading_label.config(text="Status: Idle", fg="green")
