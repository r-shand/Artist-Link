import tkinter as tk
import customtkinter as ctk
from PIL import ImageFont
from PIL import Image, ImageTk
import tkinter.font as tkFont
from tkinter import ttk
import threading
import queue
import os
import ctypes
import time
from utils import resource_path

class NonInt(Exception):
    def __init__(self, message):
        super().__init__(message)

class CustomTabWidget:
    def __init__(self, master=None):
        self.master = master

        #self.bg_img = ctk.CTkImage(light_image=Image.open(resource_path("images/bg1.jpg")), size=(800,20))

        # Create a frame for the switch
        self.top_frame = ctk.CTkFrame(master, fg_color="#221f1e") 
        self.top_frame.pack(side=tk.TOP, pady=(0, 0), fill=tk.X)

        self.mode_label = ctk.CTkLabel(self.top_frame,
                               text="Send",
                               fg_color=("white", "#221f1e"),
                               corner_radius=8)
        self.mode_label.pack(side=tk.LEFT)

        self.version_label = ctk.CTkLabel(self.top_frame,
                               text="Pre-Release 0.0.0",
                               fg_color=("white", "#221f1e"),
                               corner_radius=8)
        self.version_label.pack(side=tk.RIGHT, padx=5)

        # Create the switch
        self.tab_switch = ctk.CTkSwitch(self.top_frame, command=self.toggle_tabs, switch_width=50, fg_color="#989CFF", progress_color="#8BFBFC", text="Scrape")
        self.tab_switch.pack(side=tk.LEFT, padx=(5,5))

        # Create the frames
        self.tab1_frame = ctk.CTkFrame(master)
        self.tab2_frame = ctk.CTkFrame(master)

        self.show_frame(self.tab1_frame)

    def show_frame(self, frame):
        frame.pack(fill='both', expand=True)

        # Hide other frames
        for widget in self.master.winfo_children():
            if widget not in [self.top_frame, frame]:
                widget.pack_forget()

    def toggle_tabs(self):
        if self.tab_switch.get() == 1:
            self.show_frame(self.tab2_frame)
        else:
            self.show_frame(self.tab1_frame)
                

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")
# Set background colors
bg_color = "#252525"
fg_color = "#3B3B3B"
button_hover_color = "#A0A0A0"

class GUI:
    def __init__(self, title="ArtistLink"):
        self.root = ctk.CTk()
        self.root.title(title)
        #self.root.geometry("800x650")
        self.root.protocol("WM_DELETE_WINDOW", self.handle_close)

        # Center the window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 800
        window_height = 650
        x_coordinate = (screen_width // 2) - (window_width // 2)
        y_coordinate = (screen_height // 2) - (window_height // 2) - 75
        self.root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        # Create a main frame to hold the message area and control buttons
        self.main_frame = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bg=bg_color)
        self.main_frame.pack(expand=True, fill='both')

        # Create a main frame to hold the message area and control buttons
        self.scrape_frame = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bg=bg_color)
        self.scrape_frame.pack(expand=True, fill='both')

        # Create the custom tab widget
        self.custom_tab_widget = CustomTabWidget(self.root)

        # Place main_frame in tab1
        self.main_frame = tk.PanedWindow(self.custom_tab_widget.tab1_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bg=bg_color)
        self.main_frame.pack(expand=True, fill='both')
        # Place scrape frame in tab2
        self.scrape_frame = tk.PanedWindow(self.custom_tab_widget.tab2_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bg=bg_color)
        self.scrape_frame.pack(expand=True, fill='both')

        self.setup_send_frame() #SEND FRAME 
        self.setup_scrape_frame() #SCRAPE FRAME  

    #===================================================

    #                     SEND FRAME

    #===================================================
        
    def setup_send_frame(self):

        #local for send frame style
        light = "#989CFF"
        dark = "#6669B9"

        # Output
        self.output_frame = ctk.CTkFrame(master=self.main_frame, fg_color=fg_color)
        self.main_frame.add(self.output_frame)
        self.output_label = ctk.CTkLabel(self.output_frame, text="Feed", font=("Roboto", 18))
        self.output_label.grid(row=0, column=0, columnspan=2)
        self.output_widget = ctk.CTkTextbox(master=self.output_frame, wrap='word', 
                                            height=10, width=50, corner_radius=10, 
                                            fg_color=bg_color, border_width=2, border_spacing=1, 
                                            border_color=light, scrollbar_button_color=dark, 
                                            scrollbar_button_hover_color=light)
        self.output_widget.grid(row=1, column=0, sticky='nsew', padx=6)  # Use grid instead of pack
        self.output_frame.columnconfigure(0, weight=1)
        self.output_frame.rowconfigure(1, weight=1)
        # Create a pause/resume button
        self.paused = False
        self.pause_resume_button = ctk.CTkButton(self.output_frame,
                                  text='Pause',
                                  command=self.toggle_pause_resume,
                                  state='normal',
                                  width=70,
                                  height=30,
                                  fg_color=dark,
                                  hover_color=light,
                                  text_color='#FFFFFF')
        self.pause_resume_button.grid(row=3, column=0, sticky='w', pady=5, padx=(5, 2))
        # Start
        self.start_button = ctk.CTkButton(self.output_frame,
                                  text='Start',
                                  command=self.start,
                                  state='normal',
                                  width=70,
                                  height=30,
                                  fg_color='#66B967',
                                  hover_color='#9DDD95',
                                  text_color='#FFFFFF')
        self.start_button.grid(row=3, column=0, sticky='w', pady=5, padx=(77, 2))
        #Stop
        self.stop_button = ctk.CTkButton(self.output_frame,
                                  text='Stop',
                                  command=self.stop,
                                  state='disabled',
                                  width=70,
                                  height=30,
                                  fg_color='#CA5151',
                                  hover_color='#F38484',
                                  text_color='#FFFFFF')
        self.stop_button.grid(row=3, column=0, sticky='w', pady=5, padx=(149, 5))
        self.reset_button = ctk.CTkButton(self.output_frame,
                                  text='Reset',
                                  command=self.reset,
                                  state='normal',
                                  width=70,
                                  height=30,
                                  fg_color='#F4B300',
                                  hover_color='#FFCF4C',
                                  text_color='#FFFFFF')
        self.reset_button.grid(row=3, column=0, sticky='w', pady=5, padx=(221, 5))
        self.output_frame.rowconfigure(3, weight=0)
        self.output_frame.rowconfigure(1, weight=1)

        # Input List
        self.input_frame = ctk.CTkFrame(master=self.main_frame, fg_color=fg_color)
        self.main_frame.add(self.input_frame, stretch='always')
        self.input_label = ctk.CTkLabel(self.input_frame, text="Input List", font=("Roboto", 18))
        self.input_label.grid(row=0, column=0, columnspan=2)  # Use grid instead of pack
        self.input_widget = ctk.CTkTextbox(self.input_frame, wrap='none', height=10, width=50, 
                                            corner_radius=10, fg_color=bg_color, border_width=2, border_spacing=1, 
                                            border_color=light, scrollbar_button_color=dark, 
                                            scrollbar_button_hover_color=light)
        self.input_widget.grid(row=1, column=0, sticky='nsew', padx=6)  # Use grid instead of pack
        self.input_frame.columnconfigure(0, weight=1)
        self.input_frame.rowconfigure(1, weight=1)
        # Save button for input
        self.save_button_input = ctk.CTkButton(self.input_frame,
                                  text='Save',
                                  command=lambda: self.save_file(resource_path('list.csv'), self.input_widget),
                                  state='normal',
                                  width=70,
                                  height=30,
                                  fg_color='#6669B9',
                                  hover_color='#989CFF',
                                  text_color='#FFFFFF')
        self.save_button_input.grid(row=3, column=0, sticky='w', pady=5, padx=5)
        self.input_frame.rowconfigure(3, weight=0)  
        self.clear_button_input = ctk.CTkButton(self.input_frame,
                                  text='Clear',
                                  command=lambda: self.clear_text(self.input_widget),
                                  state='normal',
                                  width=70,
                                  height=30,
                                  fg_color='#6669B9',
                                  hover_color='#989CFF',
                                  text_color='#FFFFFF')
        self.clear_button_input.grid(row=3, column=0, sticky='w', pady=5, padx=77)
        self.input_frame.rowconfigure(3, weight=0)     

        # Create a PanedWindow to hold the always send text box and settings
        self.right_pane = tk.PanedWindow(self.main_frame, orient=tk.VERTICAL, sashrelief=tk.RAISED, bg=bg_color)
        self.main_frame.add(self.right_pane, stretch='always')

        # Always Send
        self.always_send_frame = ctk.CTkFrame(master=self.right_pane, fg_color=fg_color)     
        self.right_pane.add(self.always_send_frame, stretch='always')
        self.always_send_label = ctk.CTkLabel(self.always_send_frame, text="Always Send", font=("Roboto", 18))
        self.always_send_label.grid(row=0, column=0, columnspan=2)  # Use grid instead of pack
        self.always_send_widget = ctk.CTkTextbox(self.always_send_frame, wrap='none', height=10, width=10, 
                                                corner_radius=10, fg_color=bg_color,border_width=2, border_spacing=1, 
                                                border_color=light, scrollbar_button_color=dark, 
                                                scrollbar_button_hover_color=light)
        self.always_send_widget.grid(row=1, column=0, sticky='nsew', padx=6)  # Use grid instead of pack
        self.always_send_frame.columnconfigure(0, weight=1)
        self.always_send_frame.rowconfigure(1, weight=1)

        #save button for always send
        self.always_send_save_button = ctk.CTkButton(self.always_send_frame,
                                  text='Save',
                                  command=lambda: self.save_file(resource_path('always_send.txt'), self.always_send_widget),
                                  state='normal',
                                  width=70,
                                  height=30,
                                  fg_color='#6669B9',
                                  hover_color='#989CFF',
                                  text_color='#FFFFFF')
        self.always_send_save_button.grid(row=3, column=0, sticky='w', pady=5, padx=5)
        self.always_send_frame.rowconfigure(3, weight=0) 

        #loads
        self.load_list(resource_path('always_send.txt'), self.always_send_widget)
        self.load_list(resource_path('list.csv'), self.input_widget) 
        
        # Settings
        self.settings_frame = ctk.CTkFrame(master=self.right_pane, fg_color=fg_color)
        self.right_pane.add(self.settings_frame, stretch='always')
        self.settings_labels = []
        self.settings_entries = []

        with open(resource_path('settings.txt'), 'r') as f:
            lines = f.readlines()

        for line in lines:
            label_text = line.split(':', 1)[0]
            entry_text = line.split(':', 1)[1].strip()

            text_box_width = 50  # Set the desired width for all settings text boxes

            label = ctk.CTkLabel(self.settings_frame, text=label_text, font=("Roboto", 14))
            label.pack(side=tk.TOP)
            self.settings_labels.append(label)

            frame = ctk.CTkFrame(master=self.settings_frame, fg_color=fg_color)
            frame.pack(side=tk.TOP, fill='x', expand=True)

            entry = ctk.CTkTextbox(frame, width=text_box_width, 
                                   height=1, wrap='none', 
                                   corner_radius=10, border_width=1, 
                                   border_spacing=1, border_color=light, 
                                   scrollbar_button_color=dark,
                                   scrollbar_button_hover_color=light, fg_color=bg_color)
            entry.insert(tk.END, entry_text)
            
            entry.pack(side=tk.LEFT, fill='both', expand=True, padx=6)
            self.settings_entries.append(entry)   

        # Save button for settings
        self.save_button_settings = ctk.CTkButton(self.settings_frame,
                                  text='Save Settings',
                                  command=self.save_settings,
                                  state='normal',
                                  width=70,
                                  height=30,
                                  fg_color='#6669B9',
                                  hover_color='#989CFF',
                                  text_color='#FFFFFF')
        self.save_button_settings.pack(side=tk.BOTTOM, anchor=tk.W, pady=5, padx=5)

    def toggle_pause_resume(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_resume_button.configure(text="Resume")
        else:
            self.pause_resume_button.configure(text="Pause")

    def reset(self):
        self.start_button.configure(state='disabled')
        self.clear_text(self.output_widget)
        self.on_reset()
        time.sleep(1)
        self.stop_button.configure(state='normal')
        self.reset_button.configure(state='normal')

    def on_reset(self):
        pass

    def start(self):
        self.start_button.configure(state='disabled')
        self.on_start()  # A callback function to be set by the user
        time.sleep(1)
        self.stop_button.configure(state='normal')
        

    def on_start(self):
        pass

    def stop(self):
        self.stop_button.configure(state='disabled')
        self.start_button.configure(state='normal')
        self.clear_text(self.output_widget)
        self.on_stop()  # A callback function to be set by the user

    def on_stop(self):
        pass

    def set_reset_callback(self, func):
        self.on_reset = func

    def set_stop_callback(self, func):
        self.on_stop = func

    def set_start_callback(self, func):
        self.on_start = func

    def save_file(self, filename, widget):
        try:
            content = widget.get(1.0, tk.END).strip()
            with open(resource_path(filename), 'w') as file:
                file.write(content)
            self.root.update()  # Ensure the text widget is updated before displaying the message
            if "list.csv" in filename:
                self.display_text("send list successfully saved", '#C0FFC1')
            elif "always_send.txt" in filename:
                self.display_text("always send list successfully saved", '#C0FFC1')
            else: self.display_text(f"'{filename}' successfully saved", '#C0FFC1')
        except Exception as e:
            error_message = f"Error: {str(e)}"
            print(error_message)  # Print the error message in the console
            self.display_text(error_message, '#FF0000')  # Display the error message in the output area with red color
    
    def display_text(self, text, color="#F8FF00"):
        start_index = self.output_widget.index(tk.END + "-1l")
        # Insert the text
        self.output_widget.insert(tk.END, text + '\n')
        # Create a tag for the specified color, if not already created
        self.output_widget.tag_config(color, foreground=color)
        # Apply the color tag to the inserted text
        end_index = self.output_widget.index(tk.END + "-1c")
        self.output_widget.tag_add(color, start_index, end_index) 
        # Scroll to the end
        self.output_widget.see(tk.END)
    
    def save_settings(self):
        try:
            with open(resource_path('settings.txt'), 'r') as f:
                lines = f.readlines()
            updated_lines = []
            for i, line in enumerate(lines):
                label_text = line.split(':', 1)[0]
                entry_text = self.settings_entries[i].get('1.0', tk.END).strip()
                updated_line = f'{label_text}:{entry_text}\n'
                updated_lines.append(updated_line)
                if(i == 5):
                    if not entry_text.isdigit(): raise NonInt("")
            with open(resource_path('settings.txt'), 'w') as f:
                f.writelines(updated_lines)
            self.display_text("'settings.txt' successfully saved", '#C0FFC1')
        except NonInt as e:
            error_message = f"Please input a valid integer for Max Emails"
            self.display_text(error_message, '#FF0000') 
        except Exception as e:
            error_message = f"Error: str({e})\n"
            self.display_text(error_message, '#FF0000') 

    
    #===================================================

    #                   SCRAPE FRAME   

    #===================================================
    

    def setup_scrape_frame(self):
        dark = "#4D8FBD"
        light = "#96D4FF"
        # Output
        self.output_frame2 = ctk.CTkFrame(master=self.scrape_frame, fg_color=fg_color)
        self.scrape_frame.add(self.output_frame2)
        self.output_label2 = ctk.CTkLabel(self.output_frame2, text="Feed", font=("Roboto", 18))
        self.output_label2.grid(row=0, column=0, columnspan=2)
        self.output_widget2 = ctk.CTkTextbox(master=self.output_frame2, wrap='word', 
                                            height=10, width=50, corner_radius=10, 
                                            fg_color=bg_color, border_width=2, border_spacing=1, 
                                            border_color=light, scrollbar_button_color=dark, 
                                            scrollbar_button_hover_color=light)
        self.output_widget2.grid(row=1, column=0, sticky='nsew', padx=6)  # Use grid instead of pack
        self.output_frame2.columnconfigure(0, weight=1)
        self.output_frame2.rowconfigure(1, weight=1)
        # Create a pause/resume button
        self.paused2 = False
        self.pause_resume_button2 = ctk.CTkButton(self.output_frame2,
                                  text='Pause',
                                  command=self.toggle_pause_resume2,
                                  state='normal',
                                  width=70,
                                  height=30,
                                  fg_color=dark,
                                  hover_color=light,
                                  text_color='#FFFFFF')
        self.pause_resume_button2.grid(row=3, column=0, sticky='w', pady=5, padx=(5, 2))
        # Start
        self.start_button2 = ctk.CTkButton(self.output_frame2,
                                  text='Start',
                                  command=self.start2,
                                  state='normal',
                                  width=70,
                                  height=30,
                                  fg_color='#66B967',
                                  hover_color='#9DDD95',
                                  text_color='#FFFFFF')
        self.start_button2.grid(row=3, column=0, sticky='w', pady=5, padx=(77, 2))
        #Stop
        self.stop_button2 = ctk.CTkButton(self.output_frame2,
                                  text='Stop',
                                  command=self.stop2,
                                  state='disabled',
                                  width=70,
                                  height=30,
                                  fg_color='#CA5151',
                                  hover_color='#F38484',
                                  text_color='#FFFFFF')
        self.stop_button2.grid(row=3, column=0, sticky='w', pady=5, padx=(149, 5))
        self.reset_button2 = ctk.CTkButton(self.output_frame2,
                                  text='Reset',
                                  command=self.reset2,
                                  state='normal',
                                  width=70,
                                  height=30,
                                  fg_color='#F4B300',
                                  hover_color='#FFCF4C',
                                  text_color='#FFFFFF')
        self.reset_button2.grid(row=3, column=0, sticky='w', pady=5, padx=(221, 5))
        self.output_frame2.rowconfigure(3, weight=0)
        self.output_frame2.rowconfigure(1, weight=1)

        # Scrape List
        self.scrapelist_frame = ctk.CTkFrame(master=self.scrape_frame, fg_color=fg_color)
        self.scrape_frame.add(self.scrapelist_frame, stretch='always')
        self.scrapelist_label = ctk.CTkLabel(self.scrapelist_frame, text="Scrape List", font=("Roboto", 18))
        self.scrapelist_label.grid(row=0, column=0, columnspan=2)  # Use grid instead of pack
        self.scrapelist_widget = ctk.CTkTextbox(self.scrapelist_frame, wrap='none', height=10, width=50, 
                                            corner_radius=10, fg_color=bg_color, border_width=2, border_spacing=1, 
                                            border_color=light, scrollbar_button_color=dark, 
                                            scrollbar_button_hover_color=light)
        self.scrapelist_widget.grid(row=1, column=0, sticky='nsew', padx=6)  # Use grid instead of pack
        self.scrapelist_frame.columnconfigure(0, weight=1)
        self.scrapelist_frame.rowconfigure(1, weight=1)
        # Save button for input
        self.save_button_scrapelist = ctk.CTkButton(self.scrapelist_frame,
                                  text='Save',
                                  command=lambda: self.save_file_scrape(resource_path('scrapelist.csv'), self.scrapelist_widget),
                                  state='normal',
                                  width=70,
                                  height=30,
                                  fg_color=dark,
                                  hover_color=light,
                                  text_color='#FFFFFF')
        self.save_button_scrapelist.grid(row=3, column=0, sticky='w', pady=5, padx=5)
        self.scrapelist_frame.rowconfigure(3, weight=0)  
        self.clear_button_scrapelist = ctk.CTkButton(self.scrapelist_frame,
                                  text='Clear',
                                  command=lambda: self.clear_text(self.scrapelist_widget),
                                  state='normal',
                                  width=70,
                                  height=30,
                                  fg_color=dark,
                                  hover_color=light,
                                  text_color='#FFFFFF')
        self.clear_button_scrapelist.grid(row=3, column=0, sticky='w', pady=5, padx=77)
        self.scrapelist_frame.rowconfigure(3, weight=0)     

        # Create a PanedWindow to hold the always send text box and settings
        self.right_pane_scrape = tk.PanedWindow(self.scrape_frame, orient=tk.VERTICAL, sashrelief=tk.RAISED, bg=bg_color)
        self.scrape_frame.add(self.right_pane_scrape, stretch='always')

        # Filter Keywords
        self.filter_frame = ctk.CTkFrame(master=self.right_pane_scrape, fg_color=fg_color)     
        self.right_pane_scrape.add(self.filter_frame, stretch='always')
        self.filter_label = ctk.CTkLabel(self.filter_frame, text="Filter Keywords", font=("Roboto", 18))
        self.filter_label.grid(row=0, column=0, columnspan=2)  # Use grid instead of pack
        self.filter_widget = ctk.CTkTextbox(self.filter_frame, wrap='none', height=10, width=10, 
                                                corner_radius=10, fg_color=bg_color,border_width=2, border_spacing=1, 
                                                border_color=light, scrollbar_button_color=dark, 
                                                scrollbar_button_hover_color=light)
        self.filter_widget.grid(row=1, column=0, sticky='nsew', padx=6)  # Use grid instead of pack
        self.filter_frame.columnconfigure(0, weight=1)
        self.filter_frame.rowconfigure(1, weight=1)

        #save button for always send
        self.filter_save_button = ctk.CTkButton(self.filter_frame,
                                  text='Save',
                                  command=lambda: self.save_file_scrape(resource_path('filter.txt'), self.filter_widget),
                                  state='normal',
                                  width=70,
                                  height=30,
                                  fg_color=dark,
                                  hover_color=light,
                                  text_color='#FFFFFF')
        self.filter_save_button.grid(row=3, column=0, sticky='w', pady=5, padx=5)
        self.filter_frame.rowconfigure(3, weight=0) 

        #loads
        self.load_list(resource_path('filter.txt'), self.filter_widget)
        self.load_list(resource_path('scrapelist.csv'), self.scrapelist_widget) 
        
        # Settings
        with open(resource_path("scrapesettings.txt"), "r") as file:
            lines = file.readlines()
        # Extract the required information from the lines
        user_url = str(lines[0].split("~", 1)[1].strip())
        amount_links = 0
        try:
            amount_links = int(lines[1].split("~", 1)[1].strip())
        except ValueError:
            self.display_text_scrape("You need to input a valid number for amount of links to process", '#C0FFC1')

        self.scrape_settings_frame = ctk.CTkFrame(master=self.right_pane_scrape, fg_color=fg_color)
        self.right_pane_scrape.add(self.scrape_settings_frame, stretch='always')
        self.scrape_settings_entries = []
        #First Entry, Link
        link_text = "Soundcloud Link"
        entry_text = user_url
        text_box_width = 50  # Set the desired width for all settings text boxes
        link_label = ctk.CTkLabel(self.scrape_settings_frame, text=link_text, font=("Roboto", 14))
        link_label.pack(side=tk.TOP)
        link_frame = ctk.CTkFrame(master=self.scrape_settings_frame, fg_color=fg_color)
        link_frame.pack(side=tk.TOP, fill='x', expand=True)
        link_entry = ctk.CTkTextbox(link_frame, width=text_box_width, 
                                   height=1, wrap='none', 
                                   corner_radius=10, border_width=1, 
                                   border_spacing=1, border_color=light, 
                                   scrollbar_button_color=dark,
                                   scrollbar_button_hover_color=light, fg_color=bg_color)
        link_entry.insert(tk.END, entry_text)
        link_entry.pack(side=tk.LEFT, fill='both', expand=True, padx=6)
        self.scrape_settings_entries.append(link_entry)
        #Second Entry, Requests
        requests_text = "Requests"
        entry_text = str(amount_links)
        text_box_width = 50  # Set the desired width for all settings text boxes
        requests_label = ctk.CTkLabel(self.scrape_settings_frame, text=requests_text, font=("Roboto", 14))
        requests_label.pack(side=tk.TOP)
        requests_frame = ctk.CTkFrame(master=self.scrape_settings_frame, fg_color=fg_color)
        requests_frame.pack(side=tk.TOP, fill='x', expand=True)
        requests_entry = ctk.CTkTextbox(requests_frame, width=text_box_width, 
                                   height=1, wrap='none', 
                                   corner_radius=10, border_width=1, 
                                   border_spacing=1, border_color=light, 
                                   scrollbar_button_color=dark,
                                   scrollbar_button_hover_color=light, fg_color=bg_color)
        requests_entry.insert(tk.END, entry_text)
        requests_entry.pack(side=tk.LEFT, fill='both', expand=True, padx=6)
        self.scrape_settings_entries.append(requests_entry)   

        # Save button for settings
        self.save_button_scrape_settings = ctk.CTkButton(self.scrape_settings_frame,
                                  text='Save Scrape Settings',
                                  command=self.save_scrape_settings,
                                  state='normal',
                                  width=70,
                                  height=30,
                                  fg_color='#6669B9',
                                  hover_color='#989CFF',
                                  text_color='#FFFFFF')
        self.save_button_scrape_settings.pack(side=tk.BOTTOM, anchor=tk.W, pady=5, padx=5)

        
    def toggle_pause_resume2(self):
        self.paused2 = not self.paused2
        if self.paused2:
            self.pause_resume_button2.configure(text="Resume")
        else:
            self.pause_resume_button2.configure(text="Pause")

    def reset2(self):
        self.start_button2.configure(state='disabled')
        self.clear_text(self.output_widget2)
        self.on_reset2()
        time.sleep(1)
        self.stop_button2.configure(state='normal')
        self.reset_button2.configure(state='normal')

    def on_reset2(self):
        pass

    def start2(self):
        self.start_button2.configure(state='disabled')
        self.on_start2()  # A callback function to be set by the user
        time.sleep(1)
        self.stop_button2.configure(state='normal')

    def on_start2(self):
        pass

    def stop2(self):
        self.stop_button2.configure(state='disabled')
        self.start_button2.configure(state='normal')
        self.clear_text(self.output_widget2)
        self.on_stop2()  # A callback function to be set by the user

    def on_stop2(self):
        pass

    def set_reset_callback2(self, func):
        self.on_reset2 = func

    def set_stop_callback2(self, func):
        self.on_stop2 = func

    def set_start_callback2(self, func):
        self.on_start2 = func
    
    def save_file_scrape(self, filename, widget):
        try:
            content = widget.get(1.0, tk.END).strip()
            with open(resource_path(filename), 'w') as file:
                file.write(content)
            self.root.update()  # Ensure the text widget is updated before displaying the message
            if "scrapelist.csv" in filename:
                self.display_text_scrape(f"scrape list successfully saved", '#C0FFC1')
            elif "filter.txt" in filename:
                self.display_text_scrape(f"filter list successfully saved", '#C0FFC1')
            else: self.display_text_scrape(f"'{filename}' successfully saved", '#C0FFC1')
        except Exception as e:
            error_message = f"Error: {str(e)}"
            print(error_message)  # Print the error message in the console
            self.display_text_scrape(error_message, '#FF0000')  # Display the error message in the output area with red color

    def display_text_scrape(self, text, color="#F8FF00"):
        start_index = self.output_widget2.index(tk.END + "-1l")
        # Insert the text
        self.output_widget2.insert(tk.END, text + '\n')
        # Create a tag for the specified color, if not already created
        self.output_widget2.tag_config(color, foreground=color)
        # Apply the color tag to the inserted text
        end_index = self.output_widget2.index(tk.END + "-1c")
        self.output_widget2.tag_add(color, start_index, end_index) 
        # Scroll to the end
        self.output_widget2.see(tk.END)
    
    def save_scrape_settings(self):
        try:
            with open(resource_path('scrapesettings.txt'), 'r') as f:
                lines = f.readlines()
            updated_lines = []
            for i, line in enumerate(lines):
                entry_text = self.scrape_settings_entries[i].get('1.0', tk.END).strip()
                updated_line = f'~{entry_text}\n'
                updated_lines.append(updated_line)
                if(i == 1):
                    if not entry_text.isdigit(): raise NonInt("")
            with open(resource_path('scrapesettings.txt'), 'w') as f:
                f.writelines(updated_lines)
            self.display_text_scrape("scrape settings successfully saved", '#C0FFC1')
        except NonInt as e:
            error_message = f"Please input a valid integer for requests"
            self.display_text_scrape(error_message, '#FF0000') 
        except Exception as e:
            error_message = f"Error: str({e})\n"
            self.display_text_scrape(error_message, '#FF0000') 
    
    #===================================================

    #                   SHARED METHODS   

    #===================================================

    def clear_text(self, widget):
        widget.delete(1.0, tk.END)

    def run(self):
        self.root.mainloop()
        
    def handle_close(self):
        self.root.destroy()
        exit(0)  # Terminate the program immediately

    def load_list(self, filename, widget):
        try:
            with open(resource_path(filename), 'r') as file:
                content = file.read()
                widget.insert(tk.END, content)
        except FileNotFoundError:
            pass