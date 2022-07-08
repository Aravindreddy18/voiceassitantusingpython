from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import time
from time import ctime
import pyttsx3
import speech_recognition as sr
import pytz
import subprocess
import webbrowser as wb
from tkinter import *
import pyjokes
import keyboard
import wikipedia

name_file = open("Assistant_name", "r")
name_assistant = name_file.read()

engine = pyttsx3.init('sapi5')  
voices = engine.getProperty('voices')  
engine.setProperty('voice', voices[1].id)
   
def speak(text):
    engine.say(text)
    print(name_assistant + " : "  +  text)
    engine.runAndWait()

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ["january", "february", "march", "april", "may", "june","july", "august", "september","october","november", "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENTIONS = ["rd", "th", "st", "nd"]

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
            print(said)
        except Exception as e:
            print("Exception: " + str(e))

    return said.lower()


def authenticate_google():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service


def get_events(day, service):
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)

    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    else:
        speak(f"You have {len(events)} events on this day.")

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("-")[0])
            if int(start_time.split(":")[0]) < 12:
                start_time = start_time + "am"
            else:
                start_time = str(int(start_time.split(":")[0])-12) + start_time.split(":")[1]
                start_time = start_time + "pm"

            speak(event["summary"] + " at " + start_time)


def get_date(text):
    text = text.lower()
    today = datetime.date.today()

    if text.count("today") > 0:
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENTIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

    if month < today.month and month != -1:  
        year = year+1

    if month == -1 and day != -1:  
        if day < today.day:
            month = today.month + 1
        else:
            month = today.month

    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") >= 1:
                dif += 7

        return today + datetime.timedelta(dif)

    if day != -1:
        return datetime.date(month=month, day=day, year=year)

def note(text):
    date = datetime.datetime.now()
    file_name = str(date).replace(":", "-") + "-note.txt"
    with open(file_name, "w") as f:
        f.write(text)

    subprocess.Popen(["notepad.exe", file_name])


def Process_audio():
    WAKE = "hello sam"
    SERVICE = authenticate_google()

    while True:
      print("Listening")
      text = get_audio()

      if text.count(WAKE) > 0:
        speak("I am ready")
        text = get_audio()


        CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy"]
        for phrase in CALENDAR_STRS:
            if phrase in text:
                date = get_date(text)
                if date:
                    get_events(date, SERVICE)
                else:
                    speak("I didn't quite get that")

        NOTE_STRS = ["make a note", "write this down", "remember this", "type this"]
        for phrase in NOTE_STRS:
            if phrase in text:
                speak("What would you like me to write down? ")
                write_down = get_audio()
                note(write_down)
                speak("I've made a note of that.")

        CAMERA_STRS = ["open camera", "turn on camera"]
        for phrase in CAMERA_STRS:
            if phrase in text:
                 os.system('start explorer shell:appsfolder\Microsoft.WindowsCamera_8wekyb3d8bbwe!App')

        CHROME_STRS = ["open chrome"]
        for phrase in CHROME_STRS:
            if phrase in text:
                 os.system('start explorer shell:appsfolder\Chrome')

        TIME_STRS = ["what is the time"]
        for phrase in TIME_STRS:
            if phrase in text:
                 speak("the time is:" + ctime())

        MAPS_STRS = ["open map"]
        for phrase in MAPS_STRS:
            if phrase in text:
                 os.system('start explorer shell:appsfolder\Microsoft.WindowsMaps_8wekyb3d8bbwe!App')

        SKYPE_STRS = ["open skype"]
        for phrase in SKYPE_STRS:
            if phrase in text:
                 os.system('start explorer shell:appsfolder\Microsoft.SkypeApp_kzf8qxf38zg5c!App')

        if "hello" in text:
            speak("hello how are you?")  

        WEATHER_STRS = ["how is the weather"]
        for phrase in WEATHER_STRS:
            if phrase in text:
                 os.system('start explorer shell:appsfolder\Microsoft.BingWeather_8wekyb3d8bbwe!App')

        YOUTUBE_STRS = ["open youtube"]
        for phrase in YOUTUBE_STRS:
            if phrase in text:
                 wb.open('http://www.youtube.com')

        SEARCH_STRS = ["search"]
        for phrase in SEARCH_STRS:
            if phrase in text:
                speak("What do you want to search for?")
                search_one = get_audio()
                url = 'http://google.com/search?q=' + search_one
                wb.get().open(url)
                speak("This is what i found")

        JOKE_STRS = ["tell a joke"]
        for phrase in JOKE_STRS:
            if phrase in text:
               speak(pyjokes.get_joke())


def change_name():

  name_info = name.get()

  file=open("Assistant_name", "w")

  file.write(name_info)

  file.close()

  settings_screen.destroy()

  screen.destroy()


def change_name_window():
   
      global settings_screen
      global name


      settings_screen = Toplevel(screen)
      settings_screen.title("Settings")
      settings_screen.geometry("500x500")
      settings_screen.iconbitmap('')

     
      name = StringVar()

      current_label = Label(settings_screen, text = "Current name: "+ name_assistant)
      current_label.pack()

      enter_label = Label(settings_screen, text = "Please enter your Virtual Assistant's name below")
      enter_label.pack(pady=10)  
     

      Name_label = Label(settings_screen, text = "Name")
      Name_label.pack(pady=10)
     
      name_entry = Entry(settings_screen, textvariable = name)
      name_entry.pack()


      change_name_button = Button(settings_screen, text = "Ok", width = 10, height = 1, command = change_name)
      change_name_button.pack(pady=10)




keyboard.add_hotkey("F4", Process_audio)


def wikipedia_screen(text):


  wikipedia_screen = Toplevel(screen)
  wikipedia_screen.title(text)
  wikipedia_screen.iconbitmap('app_icon.ico')

  message = Message(wikipedia_screen, text= text)
  message.pack()


def main_screen():

      global screen
      screen = Tk()
      screen.title(name_assistant)
      screen.geometry("250x300")
      screen.iconbitmap('Marcus-Roberto-Google-Play-Google-Voice-Search.ico')


      name_label = Label(text = name_assistant,width = 300, bg = "black", fg="white", font = ("Calibri", 13))
      name_label.pack()


      microphone_photo = PhotoImage(file = "microphone.png")
      microphone_button = Button(image=microphone_photo, command = Process_audio)
      microphone_button.pack(pady=10)

      settings_photo = PhotoImage(file = "settings.png")
      settings_button = Button(image=settings_photo, command = change_name_window)
      settings_button.pack(pady=10)


      screen.mainloop()


main_screen()