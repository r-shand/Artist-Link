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
import gspread
from tkinter import messagebox
from utils import resource_path

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")
# Set background colors
bg_color = "#252525"
fg_color = "#3E3E3E"
button_hover_color = "#A0A0A0"

class LoginGUI:
    def __init__(self, title="ArtistLink"):
        self.root = ctk.CTk()
        self.root.title(title)
        #self.root.geometry("350x350")
        self.root.protocol("WM_DELETE_WINDOW", self.handle_close)
        self.root.config(bg=fg_color)

        # Center the window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 350
        window_height = 350
        x_coordinate = (screen_width // 2) - (window_width // 2)
        y_coordinate = (screen_height // 2) - (window_height // 2) - 75
        self.root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        light = "#B4FEFF"
        dark = "#71AB58"
        entry_text = "#9AC0C1"

        self.login_frame = ctk.CTkFrame(self.root, bg_color=fg_color, fg_color=bg_color, border_color=light, border_width=2)
        self.login_label = ctk.CTkLabel(self.login_frame, text="Log in", font=("Roboto", 22))
        text_box_width = 170  # Set the desired width for all settings text boxes  
        self.login_entries = []

        #First Entry, Username
        username_text = "Username"  
        self.username_label = ctk.CTkLabel(self.login_frame, text=username_text, font=("Roboto", 14))
        self.username_entry = ctk.CTkEntry(self.login_frame, width=text_box_width, 
                                    placeholder_text="User ID", placeholder_text_color=entry_text,
                                    corner_radius=10, border_width=2, 
                                    border_color=light, 
                                    fg_color=bg_color)
        self.login_entries.append(self.username_entry)

        #Second Entry, Requests
        password_text = "Password"
        self.password_label = ctk.CTkLabel(self.login_frame, text=password_text, font=("Roboto", 14))
        self.password_entry = ctk.CTkEntry(self.login_frame, width=text_box_width, 
                                    placeholder_text="Access Key", placeholder_text_color=entry_text,
                                    corner_radius=10, border_width=2, 
                                    border_color=light, 
                                    fg_color=bg_color, show="•")
        self.login_entries.append(self.password_entry)

        # Create a login button
        self.login_button = ctk.CTkButton(self.login_frame,
                                  text='Log in',
                                  command=self.login,
                                  state='normal',
                                  width=70,
                                  height=30,
                                  fg_color=bg_color,
                                  hover_color=light,
                                  text_color='#FFFFFF', 
                                  border_color=light,
                                  border_width=2)   

        self.login_label.grid(row=0, column=0, sticky="n", pady=30)
        self.username_label.grid(row=1, column=0, padx=120)
        self.username_entry.grid(row=2, column=0, padx=10, pady=(2,20))
        self.password_label.grid(row=3, column=0)
        self.password_entry.grid(row=4, column=0, padx=10, pady=(2,20))
        self.login_button.grid(sticky="n", pady=(0, 30))
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")     

    def login(self):
        username_str = self.username_entry.get()
        password_str = self.password_entry.get()
        if(username_str == "" and password_str != ""):
            messagebox.showinfo(title="Login Failed", message="Please fill out username field")
            return None
        elif(username_str != "" and password_str == ""):
            messagebox.showinfo(title="Login Failed", message="Please fill out access key field")
            return None
        elif(username_str == "" and password_str != ""):
            messagebox.showinfo(title="Login Failed", message="Please fill out both username and password fields")
            return None
        sa = gspread.service_account(resource_path("login-information.json"))
        sh = sa.open("Login Information")
        wks = sh.worksheet("Login Database")
        # Get all values in the sheet
        values = wks.get_all_values()
        # Iterate through the values, skipping the first row
        loggedin = False
        for row in values[1:]:
            username, password = row[:2]  # Assuming username and password are in the first two columns
            if username == username_str and password == password_str:
                loggedin = True
                self.authorize()
        if not loggedin:
            messagebox.showinfo(title="Login Failed", message="Please fill out username field")
            return None

    def handle_close(self):
        self.root.destroy()
        exit(0)  # Terminate the program immediately

    def run(self):
        self.root.mainloop()

    def set_authorize_callback(self, func):
        self.on_authorize = func
    
    def authorize(self):
        self.on_authorize()  # A callback function to be set by the user
        self.root.quit()
        self.root.destroy()

    def on_authorize(self):
        pass