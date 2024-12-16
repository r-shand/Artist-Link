from bs4 import BeautifulSoup
import requests
import requests.exceptions
import urllib.parse
from collections import deque
import re
import json
import time
import copy
import string
from utils import resource_path

running = False

def start(gui_manager):
    global running
    running = True
    main_scrape(gui_manager)

def stop():
    global running 
    running = False

def is_paused(gui_manager):
    return gui_manager.paused2

def timer(t, gui_manager):
    while t > 0:
        if running:
            if not is_paused(gui_manager):
                if(t == 1):
                    gui_manager.display_text_scrape("\nWaiting... " + str(t) + " second\n")
                else: gui_manager.display_text_scrape("\nWaiting... " + str(t) + " seconds\n")
                time.sleep(1)
                t -= 1
        if not running: return None


def main_scrape(gui_manager):
    try:
        global running
        with open(resource_path("scrapesettings.txt"), "r") as file:
            lines = file.readlines()
        # Extract the required information from the lines
        user_url = str(lines[0].split("~", 1)[1].strip())
        amount_links = int(lines[1].split("~", 1)[1].strip())
        webpage_content = {}
        urls = deque([user_url])
        scraped_urls = set()
        emails = set()
        count = 0
        filename = 'scrapelist.csv'
        # Check if the file is empty or not
        is_empty = False
        with open(resource_path(filename), 'a+', encoding='utf-8') as f:
            f.seek(0)  # Move the cursor to the beginning of the file
            is_empty = not bool(f.read(1))  # Check if the file is empty

        # Write the header if the file is empty
        if is_empty:
            with open(resource_path(filename), 'a', encoding='utf-8') as f:
                f.write("name,email,song\n")
        # Write the data (move the cursor to the end of the file before writing)
        with open(resource_path(filename), 'a', encoding='utf-8') as f:
            # Add your data-writing code here
            pass
        while running:
            if not is_paused(gui_manager):
                #our scrape main loop
                while(len(urls)):
                    timer(1, gui_manager)  # countdown for 1 second
                    if not running: break
                    count += 1
                    if(count == amount_links):
                        break
                    url = urls.popleft()
                    scraped_urls.add(url)
                    parts = urllib.parse.urlsplit(url)
                    base_url = '{0.scheme}://{0.netloc}'.format(parts)
                    path = url[:url.rfind('/') + 1] if '/' in parts.path else url
                    #print which request we are currently processing
                    gui_manager.display_text_scrape(f'Request [{count}] Processing {url}')
                    try:
                        response = requests.get(url)
                    #if our link is invalid search for next link in our deque
                    except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
                        continue

                    #getting the name from the soundcloud page
                    webpage_content = response.text
                    start_index = webpage_content.find("Stream") + len("Stream") + 1
                    end_index = webpage_content.find("music", start_index)
                    #if we can get the name, cool. if not, we set the name to NULL
                    if (start_index != -1 and end_index != -1):
                        name = webpage_content[start_index:end_index].strip()
                    else:
                        name = "NULL"
                    if(len(name) > 25):
                        start_index = name.find("by") + len("by") + 1
                        end_index = name.find("|", start_index)
                        if (start_index != -1 and end_index != -1):
                            name = name[start_index:end_index].strip()
                    if(len(name) > 25): continue
                    if all(c.isalpha() or c.isspace() for c in name): pass
                    else: continue

                    #test write to json
                    #with open('webpage_content.json', 'w') as f:
                    #    json.dump(webpage_content, f, indent=4)

                    #getting the most recent song name from soundcloud page
                    start_index = webpage_content.find("MusicRecording") + len("MusicRecording") + 1
                    if(start_index != -1):
                        webpage_content_trimmed = webpage_content[start_index:]
                        start_index = webpage_content_trimmed.find("href") + len("href") + 1
                        webpage_content_trimmed = webpage_content_trimmed[start_index:]
                        start_index = webpage_content_trimmed.find(">") + 1
                        webpage_content_trimmed = webpage_content_trimmed[start_index:]
                        end_index = webpage_content_trimmed.find("<")
                        song_title = webpage_content_trimmed[:end_index].strip()
                        song_title = song_title.replace("&amp;", "&")
                        if(len(song_title) == 0): song_title = "NULL"
                        elif(len(song_title) < 50 and all(c.isalpha() or c in string.punctuation or c.isdigit() or c.isspace() for c in song_title)):
                            regex_parentheses = r"\([^()]*\)|\[[^\[\]]*\]"
                            if "remix" in song_title.lower(): pass
                            else: song_title = re.sub(regex_parentheses, "", song_title)
                        else: song_title = "NULL"
                    else: song_title = "NULL"
                    
                    #regular expression for keyword filter, in this case we are looking for any email with any domain ending in .com
                    #not recommended to mess with unless you are familiar with regex
                    new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z]+.com", response.text, re.I))
                    filtered_emails = copy.deepcopy(new_emails)
                    #new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@(?!gmail\.com)[a-z]+.com", response.text, re.I))
                    #new_emails = set(re.findall(r"([a-z0-9\.\-+_]+@yahoo\.com|[a-z0-9\.\-+_]+@outlook\.com|[a-z0-9\.\-+_]+@hotmail\.com)", response.text, re.I))

                    #removes emails with keywords from filter.txt
                    with open(resource_path('filter.txt')) as f:
                        filtered_words = [word.strip() for word in f.readlines()]
                    filtered_words = [word.lower() for word in filtered_words]
                    filtered_emails = [line for line in new_emails if not any(word in line.lower() for word in filtered_words) and not line.lower().startswith('n')]
                    new_emails = filtered_emails

                    if(len(new_emails) > 0):
                        gui_manager.display_text_scrape("Email(s) found:" + str(list(new_emails)), '#C0FFC1')

                    #we will write the new email and name to the file if it is a new email and not a duplicate      
                    for line in new_emails:
                        if line not in emails:
                            with open(resource_path('scrapelist.csv'), 'a', encoding='utf-8') as f:
                                # Write the updated list to the file, one element per line:
                                f.write(str(name) + "," + str(line) + "," + str(song_title))
                                f.write("\n")
                    gui_manager.clear_text(gui_manager.scrapelist_widget)
                    gui_manager.load_list(resource_path('scrapelist.csv'), gui_manager.scrapelist_widget) 
                    emails.update(new_emails)

                    soup = BeautifulSoup(response.text, features="lxml")
                    for anchor in soup.find_all("a"):
                        link = anchor.attrs['href'] if 'href' in anchor.attrs else ''
                        if link.endswith(('/reposts', '/likes', '/comments', '/recommended', '/sets', '/tracks')):
                            continue  # skip this URL if it ends with one of the excluded paths
                        if link.startswith('/'):
                            link = base_url + link
                        elif not link.startswith('http'):
                            link = path + link
                        # check if link belongs to the same domain as the original URL
                        if urllib.parse.urlparse(link).netloc == urllib.parse.urlparse(user_url).netloc:
                            if not link in urls and not link in scraped_urls:
                                urls.append(link)
                    if not running: return None
                return None
            time.sleep(0.1)
        return None
        
    except Exception as e:
        error_message = f"Error: str({e})"
        gui_manager.display_text_scrape(error_message, '#FF0000')  # Display the error message in the output area with red color
        return None