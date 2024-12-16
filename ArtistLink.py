from gui import GUI
from login import LoginGUI
import gmail
import scrape
import threading
import time

login_manager = LoginGUI()
authorized = False

gui_manager = GUI()
gmail_thread = None
scrape_thread = None

def main():
    # login
    try:
        login_manager.set_authorize_callback(authorize)
        while not authorized:
            login_manager.run()
        
        # Set the start and stop callbacks for the GUI
        gui_manager.set_start_callback(start_gmail_thread)
        gui_manager.set_stop_callback(stop_gmail_thread)
        gui_manager.set_reset_callback(reset_gmail_thread)

        gui_manager.set_start_callback2(start_scrape_thread)
        gui_manager.set_stop_callback2(stop_scrape_thread)
        gui_manager.set_reset_callback2(reset_scrape_thread)
        # Start the GUI event loop
        gui_manager.run()
    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(error_message)  # Print the error message in the console

def authorize():
    global authorized
    authorized = True

def reset_scrape_thread():
    try:
        # Check if the Gmail thread is still running
        global scrape_thread
        if(scrape_thread is None):
            scrape_thread = threading.Thread(target=scrape.start, args=(gui_manager,), daemon=True)
            scrape_thread.start()
        # Stop the Gmail functionality gracefully
        scrape.stop()
        # Wait for the thread to complete before exiting
        scrape_thread.join()

        scrape_thread = threading.Thread(target=scrape.start, args=(gui_manager,), daemon=True)
        scrape_thread.start()
    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(error_message)  # Print the error message in the console
        gui_manager.display_text(error_message, '#FF0000')  # Display the error message in the output area with red color

def start_scrape_thread():
    try:
        # Start the Gmail functionality in a separate daemon thread
        global scrape_thread
        scrape_thread = threading.Thread(target=scrape.start, args=(gui_manager,), daemon=True)
        scrape_thread.start()
    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(error_message)  # Print the error message in the console
        gui_manager.display_text_scrape(error_message, '#FF0000')  # Display the error message in the output area with red color


def stop_scrape_thread():
    try:
        # Check if the Gmail thread is still running
        if not scrape_thread.is_alive():
            return
        # Stop the Gmail functionality gracefully
        scrape.stop()
        # Wait for the thread to complete before exiting
        scrape_thread.join()
    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(error_message)  # Print the error message in the console
        gui_manager.display_text_scrape(error_message, '#FF0000')  # Display the error message in the output area with red color

def reset_gmail_thread():
    try:
        # Check if the Gmail thread is still running
        global gmail_thread
        if(gmail_thread is None):
            gmail_thread = threading.Thread(target=gmail.start, args=(gui_manager,), daemon=True)
            gmail_thread.start()
        # Stop the Gmail functionality gracefully
        gmail.stop()
        # Wait for the thread to complete before exiting
        gmail_thread.join()

        gmail_thread = threading.Thread(target=gmail.start, args=(gui_manager,), daemon=True)
        gmail_thread.start()
    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(error_message)  # Print the error message in the console
        gui_manager.display_text(error_message, '#FF0000')  # Display the error message in the output area with red color

def start_gmail_thread():
    try:
        # Start the Gmail functionality in a separate daemon thread
        global gmail_thread
        gmail_thread = threading.Thread(target=gmail.start, args=(gui_manager,), daemon=True)
        gmail_thread.start()
    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(error_message)  # Print the error message in the console
        gui_manager.display_text(error_message, '#FF0000')  # Display the error message in the output area with red color


def stop_gmail_thread():
    try:
        # Check if the Gmail thread is still running
        if not gmail_thread.is_alive():
            return
        # Stop the Gmail functionality gracefully
        gmail.stop()
        # Wait for the thread to complete before exiting
        gmail_thread.join()
    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(error_message)  # Print the error message in the console
        gui_manager.display_text(error_message, '#FF0000')  # Display the error message in the output area with red color

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(error_message)  # Print the error message in the console
