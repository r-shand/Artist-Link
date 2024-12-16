import sys
import json
import imaplib
import email as em
import csv
import smtplib
import importlib
import time
import re
import gspread
import templates
import random
import threading
import dns.resolver
from email.message import EmailMessage
from validate_email import validate_email
from utils import resource_path

running = False

def start(gui_manager):
    global running
    running = True
    main_gmail(gui_manager)

def stop():
    global running 
    running = False

def is_paused(gui_manager):
    return gui_manager.paused

def is_valid_email(email):
    # First, check if the email address has a valid format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False

    # Next, check if the domain of the email address exists
    domain = email[email.index('@') + 1:]
    try:
        records = dns.resolver.resolve(domain, 'MX')
    except dns.resolver.NoAnswer:
        return False
    except dns.resolver.NXDOMAIN:
        return False
    except dns.exception.Timeout:
        return False

    # Finally, try to connect to the SMTP server of the domain to check if the email address exists
    smtp_server = records[0].exchange.to_text()
    try:
        with smtplib.SMTP(smtp_server) as smtp:
            code, _ = smtp.helo()
            if code != 250:
                return False
            code, _ = smtp.mail('test@example.com')
            if code != 250:
                return False
            code, _ = smtp.rcpt(email)
            if code == 250:
                return True
            if code == 451:
                return False
            if code == 550:
                return False
            return False
    except smtplib.SMTPConnectError:
        return False
    except smtplib.SMTPServerDisconnected:
        return False
    except smtplib.SMTPResponseException:
        return False
    except smtplib.SMTPSenderRefused:
        return False
    except smtplib.SMTPRecipientsRefused:
        return False
    except smtplib.SMTPDataError:
        return False

def customize(str, name, yourname, song_msg, link):
    new_str = str.replace("{name}", name).replace("{yourname}", yourname).replace("{link}", link).replace("{song_msg}", song_msg)
    return new_str

def customize_song(str, song):
    if(song == "NULL"): return ""
    new_str = str.replace("{song}", song)
    return new_str

def timer(t, gui_manager):
    while t > 0:
        if running:
            if not is_paused(gui_manager):
                if(t % 60 == 0):
                    minutes = t / 60
                    if(minutes >  1):
                        gui_manager.display_text("Waiting... " + str(int(minutes)) + " minutes")
                    else:
                        gui_manager.display_text("Waiting... " + str(minutes) + " minute")
                elif(t % 60 != 0 and t > 120):
                    minutes = int(t / 60)
                    seconds = t % 60
                    if(seconds > 1):
                        gui_manager.display_text("Waiting... " + str(minutes) + " minutes " + str(seconds) + " seconds")
                    else:
                        gui_manager.display_text("Waiting... " + str(minutes) + " minutes " + str(seconds) + " second")
                elif(t % 60 != 0 and t < 120 and t > 60):
                    minutes = 1
                    seconds = t % 60
                    if(seconds > 1):
                        gui_manager.display_text("Waiting... " + str(minutes) + " minute " + str(seconds) + " seconds")
                    else:
                        gui_manager.display_text("Waiting... " + str(minutes) + " minute " + str(seconds) + " second")
                elif(t < 60):
                    if(t > 1):
                        gui_manager.display_text("Waiting... " + str(t) + " seconds")
                    else:
                        gui_manager.display_text("Waiting... " + str(t) + " second\n")
                time.sleep(1)
                t -= 1
        if not running: return None

def getColumn(mails):
    if("ryan.hotdropapp@gmail.com" in mails): return 1
    elif("sophiasuen.hotdropapp@gmail.com" in mails): return 2
    elif("stephanie.hotdropapp@gmail.com" in mails): return 3
    elif("ronnie.hotdropapp@gmail.com" in mails): return 4
    elif("maddie.hotdropapp@gmail.com" in mails): return 5
    elif("mayixuan1026.hotdropapp@gmail.com" in mails): return 6
    elif("emmiekelly.hotdropapp@gmail.com" in mails): return 7
    elif("tori.hotdropapp@gmail.com" in mails): return 8
    elif("harris@hotdropapp.com" in mails): return 9
    elif("sophiatang.hotdropapp@gmail.com" in mails): return 10
    elif("linhluong.hotdropapp@gmail.com" in mails): return 11
    elif("chanel.hotdropapp@gmail.com" in mails): return 12
    elif("sudarshan.hotdropapp@gmail.com" in mails): return 13
    elif("jannie.hotdropapp@gmail.com" in mails): return 14
    elif("farrelltjaja.hotdropapp@gmail.com" in mails): return 15
    elif("fullermoore.hotdropapp@gmail.com" in mails): return 16
    elif("aadilzakarya.hotdropapp@gmail.com" in mails): return 17
    elif("michelleparis.hotdropapp@gmail.com" in mails): return 18
    elif("tianyichen.hotdropapp@gmail.com" in mails): return 19
    elif("stephen@hotdropapp.com" in mails): return 20
    return 0

def main_gmail(gui_manager):
    try:
        global running
        #this list of users will bypass the do not re-send email list from spreadsheet database 
        with open(resource_path('always_send.txt'), 'r') as file:
            # Read all the lines in the file and store them in a list
            lines = file.readlines()
            always_send = [line.strip() for line in lines]

        # Open the CSV file
        with open(resource_path('list.csv'), newline='') as csvfile:
            reader = csv.reader(csvfile)
            # Skip the header row if it exists
            next(reader, None)
            # Create an empty dictionary
            data = {}
            # Loop through each row in the CSV file
            for row in reader:
                # Add the name and email to the dictionary
                data[row[0]] = {'email': row[1], 'song': row[2]}

        sa = gspread.service_account(resource_path("service_account.json"))
        sh = sa.open("Email Database")
        wks = sh.worksheet("Sent History")
        all = wks.get_all_values()
        history = [value for row in all for value in row if value != '']

        #get fields from settings.txt and populate it into a list
        information = []
        with open(resource_path('settings.txt'), 'r') as file:
            # loop over each line in the file
            for line in file:
                # split the line at the ':' character and extract the value
                value = line.strip().split(':')[1]
                # add the value to the list
                information.append(value)

        #sending from text template or html template
        MODE = "html"
        #emails of sender
        SENDERS = information[0].split(",")
        SENDERS = [substring.strip() for substring in SENDERS]
        #keys that authorizes bot to access email for each email
        APP_PASSWORDS = information[1].split(",")
        APP_PASSWORDS = [substring.strip() for substring in APP_PASSWORDS]
        #this is so sender displays name as "Ryan | HotDrop" instead of the email name
        DISPLAY_NAME = information[2]
        #this is for ACTUALLY SPAMMING THE SHIT OUT OF PEOPLE. keep this at 1 for HotDrop purposes
        REQUESTS = 1
        #this is your name that will be written in the content of your emails
        YOUR_NAME = information[3]
        #your affiliate link
        LINK = "https://"+str(information[4])
        #stop the program after sending this many emails
        CT_MAX = int(information[5])
        #email text as html
        #imported from templates.py
        BODY_HTML_LIST = templates.BODY_HTML_LIST
        #email subject
        #imported from templates.py
        SUBJECT_LIST = templates.SUBJECT_LIST
        #song message list imported from templates.py
        SONG_MSG_LIST = templates.SONG_TEXT
        #getting column length
        COL_INDEX = getColumn(SENDERS)
        if(COL_INDEX == 0): 
            gui_manager.display_text("\nYou have not provided an authorized sender email. \nPlease provide your HotDrop email address in the settings field\n", '#D50000')
            sys.exit()
        values = wks.col_values(COL_INDEX)
        ROW = len(values) + 1
        addNewEmails = []
        #counting how many emails we send
        ct = 0
        while running:
            if not is_paused(gui_manager):
                #smtp server calls
                if(len(SENDERS) == len(APP_PASSWORDS) and len(SENDERS) >= 1):
                    
                    #looping throigh all recipients in my list initialized earlier
                    for name, values in data.items():
                        #read through csv to get recipient name and recipient address
                        n = name #name
                        r = values['email'] #recipient
                        SONG_MSG_LIST_INDEX = random.randint(0, len(SONG_MSG_LIST)-1)
                        song_msg = customize_song(SONG_MSG_LIST[SONG_MSG_LIST_INDEX], values['song']) #sentence with song mentioned in it

                        #set up smtp server login
                        smtpserver = smtplib.SMTP('smtp.gmail.com', '587')
                        smtpserver.ehlo()
                        smtpserver.starttls()
                        smtpserver.ehlo()
                        if(ct >= CT_MAX): break
                        #which email we will be sending from
                        iteration = ct % len(SENDERS)
                        smtpserver.login(SENDERS[iteration], APP_PASSWORDS[iteration])

                        all = wks.get_all_values()
                        #history of all emails we've sent to. entire database from spreadsheet
                        history = [value for row in all for value in row if value != '']
                        
                        #initializing and defining out msg object. filling in the attributes before we send our email
                        msg = EmailMessage()
                        #email text as string read from file
                        MESSAGE_FILES = templates.MESSAGE_FILES
                        MESSAGE_FILES_INDEX = random.randint(0, len(MESSAGE_FILES)-1)
                        message_file = MESSAGE_FILES[MESSAGE_FILES_INDEX]
                        with open(resource_path(message_file), "r") as file:
                            BODY = file.read()
                        #email text as html read from list of templates in templates.py
                        BODY_LIST_INDEX = random.randint(0, len(BODY_HTML_LIST)-1)
                        if(MODE == "text"):
                            msg.set_content(customize(BODY, n, YOUR_NAME, song_msg, LINK))
                        elif(MODE == "html"):
                            msg.set_content(customize(BODY_HTML_LIST[BODY_LIST_INDEX], n, YOUR_NAME, song_msg, LINK), subtype='html')
                        #get the random subject index from list in templates.py
                        SUBJECT_LIST_INDEX = random.randint(0, len(SUBJECT_LIST)-1)
                        #set up email with the proper fields
                        msg['Subject'] = SUBJECT_LIST[SUBJECT_LIST_INDEX]
                        #this is so sender displays name as "Ryan | HotDrop" instead of the email name
                        FROM = f'"{DISPLAY_NAME}" <{SENDERS[iteration]}>'
                        msg['From'] = FROM
                        msg['To'] = r 
                        msg_id = em.utils.make_msgid()
                        msg['Message-ID'] = msg_id

                        if(r in history and r not in always_send):
                            gui_manager.display_text(f"We have already sent to {r}. Skipping...\n")
                            continue

                        is_valid = is_valid_email(r)
                        if is_valid:
                            gui_manager.display_text(f"{r} is a valid email address!\n", '#C0FFC1')
                        else:
                            gui_manager.display_text(f"{r} is not a valid email address. Skipping...\n")
                            continue

                        if(r not in history or r in always_send):
                            addNewEmails.append(r)
                            ROW = ROW + 1
                            for i in range(REQUESTS):
                                #timer to wait in between each email send (2-4 minutes)
                                wait = random.randint(120, 240)
                                timer(wait, gui_manager)
                                if not running: return None
                                smtpserver.sendmail(SENDERS[iteration], r, msg.as_string()) 
                                #gui_manager.display_text(msg.as_string())
                                ct = ct + 1
                                
                                gui_manager.display_text(SENDERS[iteration] + " sent to " + r)
                            if(r not in history):
                                wks.update_cell(ROW, COL_INDEX, r)
                            if(REQUESTS == 1):
                                gui_manager.display_text("Successfully sent email to:\n " + r +"\n", '#C0FFC1')
                            elif(REQUESTS > 1):
                                gui_manager.display_text("Successfully spammed " + REQUESTS + " emails to " + r + "\n",'#C0FFC1')
                            
                            if("@gmail.com" in r):
                                #wait for email to process
                                gui_manager.display_text("Email processing...\n")
                                timer(10, gui_manager)
                                if not running: return None
                                #did the email go to spam? gmails only
                                msg_id = msg['Message-ID'][1:-1]
                                if msg_id:
                                    result = smtpserver.noop()
                                    if result[0] == 250:
                                        gui_manager.display_text('The email was delivered to the recipient\'s inbox\n', '#C0FFC1')
                                    elif result[0] == 550:
                                        gui_manager.display_text('The email was sent to the recipient\'s spam folder. Terminating email send sequence\n', '#D50000')
                                        timer(5, gui_manager)
                                        running = False
                                    else:
                                        gui_manager.display_text('The email was not found in the recipient\'s inbox or spam folder\n')
                                else:
                                    gui_manager.display_text('The Message-ID header field is not set in the email message\n')
                            #stop smtp session, will round-robin to the next login
                            smtpserver.quit()

                elif len(SENDERS) == 0:
                    gui_manager.display_text("Sender list is empty\n")
                elif len(APP_PASSWORDS) != len(SENDERS):
                    gui_manager.display_text("Failed to find a corresponding sender email to app password pair. \nThe amount of app passwords and sender emails must be the same\n",'#D50000')
                if(not addNewEmails and len(SENDERS) > 0 and len(APP_PASSWORDS) == len(SENDERS)):
                    gui_manager.display_text("You have already previously sent out emails to all users on your recipient list. No new emails have been sent out\n")
                elif(addNewEmails and len(SENDERS) > 0 and len(APP_PASSWORDS) == len(SENDERS)):
                    gui_manager.display_text("Successfully sent " + str(ct) + " emails!\n", '#C0FFC1')
                running = False
                #raise Exception
            time.sleep(0.1)
        return None
    except Exception as e:
        error_message = f"Error: str({e})\n"
        gui_manager.display_text(error_message, '#FF0000')  # Display the error message in the output area with red color
        return None