#Stop focus stealing on firefox: set browser.tabs.loadDivertedInBackground to ‘true’ in about:config

import requests, json, os, pandas as pd, datetime, webbrowser, re, tkinter as tk
from tkinter import ttk, Menu
from PIL import ImageTk, Image

os.chdir(os.path.dirname(__file__))

data_loaded = False
def load_items(dumpert_item):
    global df
    global data_loaded
    global last_item_id
    if data_loaded == False: 
        datum = []
        id = []       
        for pages in range(0,10):   
            jp = json.loads(requests.get("https://api-live.dumpert.nl/mobile_api/json/latest/{}".format(pages), headers={'x-dumpert-nsfw': '1'}).text)
            for item in jp["items"]:
                datum.append(datetime.datetime.strptime(item["date"][:-6],"%Y-%m-%dT%H:%M:%S"))
                id.append(item["id"])
                if item["id"] == dumpert_item:
                    break
            else:
                continue
            break
        df = pd.DataFrame({'datum': datum, 'id': id})
        last_item_id = id[0]
        data_loaded = True
        return df
    else:
        return df

def check_if_valid_url(dumpert_url):
    if dumpert_url[:28] == "https://www.dumpert.nl/item/":
        return True
    else:
        return False

def count_items(dumpert_url):
    global last_viewed_item
    if check_if_valid_url(dumpert_url) == False:
        return m.set("Geen geldige link")
    dumpert_item = re.sub('.*(?<=item\/)',"",dumpert_url)
    df = load_items(dumpert_item)
    if last_viewed_item == True:
        df.drop(df.tail(1).index, axis=0, inplace=True)
        last_viewed_item = False
    if len(df)>0 and len(df)<239:
        m.set(len(df.index))
    elif len(df)>=239:
        df.drop(df.index, axis=0, inplace=True)        
        m.set("Niet gevonden")
    else:
        m.set("Alles gezien")
    update_btn_count()

def update_btn_count():
    if len(df.index)==1:
        n.set('Laad {} item'.format(len(df.index)))    
    elif len(df.index)<10:
        n.set('Laad {} items'.format(len(df.index)))
    else:
        n.set('Laad 10 items')

def open_items(dumpert_url):  
    if check_if_valid_url(dumpert_url) == False:
        return m.set("Geen geldige link")    
    dumpert_item = re.sub('.*(?<=item\/)',"",dumpert_url)
    df = load_items(dumpert_item)
    for index, row in df[::-1].iterrows():
        webbrowser.get('C:/Program Files/Mozilla Firefox/firefox.exe %s').open("https://www.dumpert.nl/item/"+row["id"])
        if len(df.index) == 1:
            save_last_viewed_item(row["id"])        
        df.drop(index, axis=0, inplace=True)
    m.set("Alles gezien")
    update_btn_count()

def open_x_items(dumpert_url):
    count = 0
    if check_if_valid_url(dumpert_url) == False:
        return m.set("Geen geldige link")    
    dumpert_item = re.sub('.*(?<=item\/)',"",dumpert_url)
    df = load_items(dumpert_item)
    for index, row in df[::-1].iterrows():
        webbrowser.get('C:/Program Files/Mozilla Firefox/firefox.exe %s').open("https://www.dumpert.nl/item/"+row["id"])
        if len(df.index) == 1:
            save_last_viewed_item(row["id"])
        df.drop(index, axis=0, inplace=True)  
        count+=1
        if count==10 and not len(df.index)==count:
            save_last_viewed_item(row["id"])
            m.set("Nog te zien: {}".format(len(df.index)))
            break
        m.set("Alles gezien")
    update_btn_count()

def open_dumpert():
    webbrowser.get('C:/Program Files/Mozilla Firefox/firefox.exe %s').open("https://www.dumpert.nl")

refreshed = False
def refresh(dumpert_url):
    #m.set("Laden..")
    global refreshed
    if not 'df' in globals():
        return count_items(dumpert_url)
    if len(df.index)>0 and refreshed == False:
        return m.set("Nog niet alles gezien")
    global data_loaded
    data_loaded = False
    load_items(last_item_id)
    df.drop(df.tail(1).index, axis=0, inplace=True)
    if len(df.index)==0:
        m.set("Geen nieuwe filmpjes")
        refreshed = True
    elif len(df.index)==1:
        m.set("Er is 1 nieuw filmpje")
        update_btn_count()
        refreshed = False
    else:
        m.set("Er zijn {} nieuwe filmpjes".format(len(df.index)))
        update_btn_count()
        refreshed = False

last_viewed_item = False 
def load_items_from():
    global last_viewed_item
    global data_loaded
    data_loaded = False
    with open("last_viewed_item.txt", "rt") as f:
        last_loaded_id = f.readlines()
    dl.delete(0,tk.END)
    dl.insert(0,"https://www.dumpert.nl/item/{}".format(last_loaded_id[0]))
    last_viewed_item = True
    count_items("https://www.dumpert.nl/item/{}".format(last_loaded_id[0]))

def save_last_viewed_item(last_viewed_item):
    with open('last_viewed_item.txt', 'w') as f:
        f.write(last_viewed_item)



root = tk.Tk()

w = 140 # width for the Tk root
h = 400 # height for the Tk root

# get screen width and height
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen

# calculate x and y coordinates for the Tk root window
x = ws-w-30
y = (hs/2) - (h/2)
# set the dimensions of the screen and where it is placed
root.geometry('%dx%d+%d+%d' % (w, h, x, y))


#root.resizable(True, True)
#root.resizable(0,0)
root.title('Dumpert')

root.attributes("-toolwindow",1)
root.attributes("-topmost", True)

root.iconbitmap("dumpert-logo.ico")

img = ImageTk.PhotoImage(Image.open("dumpert.png"))
panel = tk.Label(root, image = img)
panel.pack(side = "top", fill = "both", expand = "yes")

m = tk.StringVar()
n = tk.StringVar()
n.set('Laad x items')

ttk.Button(root, text='Open dumpert.nl', command=lambda: open_dumpert()).pack(ipadx=5, ipady=5, expand=True)
ttk.Button(root, text='Open vanaf laatste', command=lambda: load_items_from()).pack(ipadx=5, ipady=5, expand=True)

tk.Label(root, text="Dumpert link:").pack(ipadx=5, ipady=5, expand=True)
dl = tk.Entry(root)
dl.pack(ipadx=5, ipady=5, expand=True)


right_click_menu = Menu(dl, tearoff=False)
#right_click_menu.add_command(label="Cut")
#right_click_menu.add_command(label="Copy")
right_click_menu.add_command(label="Paste", accelerator="Ctrl+V")
#right_click_menu.add_separator()

def right_click(e):
    right_click_menu.tk_popup(e.x_root+5, e.y_root+5)
#    right_click_menu.entryconfigure("Cut",command=lambda: e.widget.event_generate("<<Cut>>"))
#    right_click_menu.entryconfigure("Copy",command=lambda: e.widget.event_generate("<<Copy>>"))
    right_click_menu.entryconfigure("Paste",command=lambda: e.widget.event_generate("<<Paste>>"))

dl.bind("<Button-3>", right_click)



ttk.Button(root, text='Tel', command=lambda dumpert_url=dl.get(): count_items(dl.get())).pack(ipadx=5, ipady=5, expand=True)
ttk.Label(root, textvariable=m).pack(ipadx=5, ipady=5, expand=True)
ttk.Button(root, textvariable=n, command=lambda dumpert_url=dl.get(): open_x_items(dl.get())).pack(ipadx=5, ipady=5, expand=True)
#ttk.Button(root, text='Laad alles', command=lambda dumpert_url=dl.get(): open_items(dl.get())).pack(ipadx=5, ipady=5, expand=True)
ttk.Button(root, text='Refresh', command=lambda dumpert_url=dl.get(): refresh(dl.get())).pack(ipadx=5, ipady=5, expand=True)
ttk.Button(root, text='Exit', command=lambda: root.quit()).pack(ipadx=5, ipady=5, expand=True)


root.mainloop()
