import RPi.GPIO as GPIO
import datetime
import subprocess
import time
import webbrowser
from selenium import webdriver
import random
import argparse
import os
import signal



'''
...............CLASSES................
'''

class ATime:
    #Initiation functions
    
    def __init__(self, time_string, arith_type = None, value = None, time_type = None):
        if arith_type is not None:
            self.FromOtherTimeString(time_string, arith_type, value, time_type)
        else:
            self.TimeString = time_string
            self.HourInt, self.MinInt = self.GetHourMinIntFromTimeString()

    def FromOtherTimeString(self, other_time_string, arith_type, value, time_type):
        other_hour_int, other_min_int = self.GetHourMinIntFromTimeString(other_time_string)
        if time_type == "hour":
            if arith_type == "add":
                new_hour = self.AddHourTime(value, other_hour_int)
            elif arith_type == "sub":
                new_hour = self.SubHourTime(value, other_hour_int)
            else:
                print("Incorrect arith_type")
                input()
            self.HourInt = new_hour
            self.MinInt = other_min_int
        elif time_type == "min":
            if arith_type == "add":
                new_hour, new_min = self.AddMinTime(value, other_hour_int, other_min_int)
            elif arith_type == "sub":
                new_hour, new_min = self.SubMinTime(value, other_hour_int, other_min_int)
            else:
                print("Incorrect arith_type")
                input()
            self.HourInt = new_hour
            self.MinInt = new_min
        else:
            print("Incorrect time_type")
            input()

        self.UpdateTimeString()

    def GetHourMinIntFromTimeString(self, other_time_string = None): #not sure exactly how to classify this func
        if other_time_string == None:
            hour = self.TimeString[0:2]
            minute = self.TimeString[3:5]
        else:
            hour = other_time_string[0:2]
            minute = other_time_string[3:5]
        hour_int = int(hour)
        min_int = int(minute)
        return hour_int, min_int

    # Method Functions

    def UpdateTimeString(self):
        hour = str(self.HourInt)
        if self.HourInt < 10:
            hour = "0" + hour
        minute = str(self.MinInt)
        if self.MinInt < 10:
            minute = "0" + minute
        self.TimeString = hour + ":" + minute

    def AddHourTime(self, value, other_hour_int = None):
        if other_hour_int == None:
            new_hour = self.HourInt + value
        else:
            new_hour = other_hour_int + value
        if new_hour > 23:
            new_hour = new_hour - 24
        if other_hour_int == None:
            self.HourInt = new_hour
            self.UpdateTimeString()
        else:
            return new_hour

    def AddMinTime(self, value, other_hour_int = None, other_min_int = None):
        if other_hour_int == None:
            new_min = self.MinInt + value
        else:
            new_min = other_min_int + value
        if new_min > 59:
            if other_hour_int is not None:
                new_hour = other_hour_int + int(new_min / 60)
            new_min = new_min % 60
            if other_hour_int is not None:
                return new_hour, new_min
        if other_hour_int == None:
            self.MinInt = new_min
            self.UpdateTimeString()
        else:
            return other_hour_int, new_min

    def SubHourTime(self, value, other_hour_int = None):
        if other_hour_int == None:
            new_hour = self.HourInt - value
        else:
            new_hour = other_hour_int - value
        if new_hour < 0:
            new_hour = new_hour + 24
        if other_hour_int == None:
            self.HourInt = new_hour
            self.UpdateTimeString()
        else:
            return new_hour

    def SubMinTime(self, value, other_hour_int = None, other_min_int = None):
        if other_hour_int == None:
            new_min = self.MinInt - value
        else:
            new_min = other_min_int - value
        if new_min < 0:
            if other_hour_int is not None:
                new_hour = other_hour_int - int(new_min / -60) - 1
            new_min = new_min % 60
            if other_hour_int is not None:
                return new_hour, new_min
        if other_hour_int == None:
            self.MinInt = new_min
            self.UpdateTimeString()
        else:
            return other_hour_int, new_min

    def GreaterThan(self, other):
        if self.HourInt > other.HourInt:
            return True
        elif self.HourInt == other.HourInt:
            if self.MinInt > other.MinInt:
                return True
            else:
                return False
        else:
            return False
            

'''
...............HELPER FUNCTIONS................
'''

def get_all_alarm_times(alarm_time):
    heater_time = ATime(alarm_time.TimeString, "sub", 1, "min")
    heater_off_time = ATime(alarm_time.TimeString, "add", 30, "min")               
    return heater_time, heater_off_time

def pick_random_url_from_file():
    # Pick random url
    with open("/home/pi/Desktop/Random_urls") as f:
        urls = f.readlines()
    random.seed()
    rand_url_index = random.randint(0, len(urls) - 1)
    url = urls[rand_url_index]

    # Delete url from "Random_url" and move to "PlayedVideos" 
    iterator = 0
    with open("/home/pi/Desktop/Random_urls", "w") as f_source:
        for i in range(0, len(urls)):
            if i == rand_url_index:
                pass
            else:
                f_source.write(urls[i])
    
    return url

def play_youtube_video(url):
    subprocess.Popen("amixer cset numid=3 1", shell=True)
    #webbrowser.open(url)
    browser = webdriver.Firefox()
    browser.maximize_window()
    browser.get(url)
    #subprocess.Popen("xdotool mousemove 1700 900 click 1", shell=True) #click to wake up screen
    '''
    time.sleep(30)
    subprocess.Popen("xdotool mousemove 1000 500 click 1", shell=True) #click on play video
    time.sleep(5)
    subprocess.Popen("xdotool mousemove 485 610 click 1", shell=True) #Click pause
    time.sleep(40)
    subprocess.Popen("xdotool mousemove 485 610 click 1", shell=True) #Click play
    time.sleep(5)
    #subprocess.Popen("xdotool mousemove 1270 610 click 1", shell=True) #Click on full screen
    time.sleep(5)
    '''

def run_send_email_and_monitor(scriptWithArgs):
    proc = subprocess.Popen(scriptWithArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out, err = proc.communicate()
    
    #Print out the stdout from the script:
    out_str = str(out)
    out_str = out_str[2:-1]
    print(out_str)

    #If the script encountered an error, print error to leapfad (by using print statement)
    err_str = str(err)
    err_str = err_str[2:-1]
    if (err_str != ""):
        print("\nThe following error was encountered:\n" + err_str)
        return -1
    
def run_script_and_monitor(scriptWithArgs): #This function takes the script with args as a list, just as it would be typed in terminal...use to relay standard error and output (will not work for execute_send_email)
    proc = subprocess.Popen(scriptWithArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out, err = proc.communicate()
    
    #Print out the stdout from the script:
    out_str = str(out)
    out_str = out_str[2:-1]
    #print(out_str) #for some reason this line is causing 3 new lines to appear once a minute, but they aren't in out_str...? so....something about the stdout pipe I guess?

    #If the script encountered an error, send in email
    err_str = str(err)
    err_str = err_str[2:-1]
    if (err_str != ""):
        returnVal = run_send_email_and_monitor(["python2", "/home/pi/Desktop/Git_repo/Pi_Room_Automation/gmail/execute_send_email.py", "email", "-v", "SendErrorMessage", "-b", err_str])
        if returnVal != -1:
            print("\nAn error was encountered...check email for error message")

def monitor_alarm_and_place_used_url(url, alarm_time_up, alarm_time_down): # This function takes 5 min
    elapsed_alarm_time = 0
    while True:
        if elapsed_alarm_time > 300: # When mic circuit created use that instead of timing to figure if an alarm isn't being played
            # Alarm didn't work...I didn't get up
            print("\nAlarm placed in FailedVideos :/\n")
            with open("/home/pi/Desktop/FailedVideos", "a") as f:
                f.write(url)
            subprocess.Popen("omxplayer -o local /home/pi/Desktop/staring_at_the_sun.mp3", shell=True) #the default really should be an annoying alarm...figure that out...
            time.sleep(10)
            break
        elif not GPIO.input(alarm_time_up):
            # Alarm was favorited
            print("\nAlarm Placed in FavoritedVideos!\n") 
            with open("/home/pi/Desktop/FavoritedVideos", "a") as f:
                f.write(url)
            break
        elif not GPIO.input(alarm_time_down):
            # Alarm worked, not a favorite though
            print("\nAlarm Placed in PlayedVideos\n")
            with open("/home/pi/Desktop/PlayedVideos", "a") as f:
                f.write(url)
            break
        elapsed_alarm_time += 1
        time.sleep(1)

def change_alarm_manual(alarm_time,alarm_time_up, alarm_time_down, hour_increment, min_increment):
    
    alarm_time_temp = ATime(alarm_time.TimeString) #create temp alarm time
    print ("\n~~~~~~~~~Alarm Time Changer~~~~~~~~~~~")
    time.sleep(2)
                    
    #Change hour state
    print("\n  Change Hour:", end="\r")
    time.sleep(2) #hold change hour message for 2 seconds
    seconds_up_held = 0
    seconds_down_held = 0
    seconds_idle = 0
    print ("  New Alarm Time = ", alarm_time_temp.TimeString , end="\r")
    
    while seconds_up_held < 2 and seconds_down_held < 2 and seconds_idle < 15:
        if not GPIO.input(alarm_time_down):
            seconds_idle = 0
            while True:
                if GPIO.input(alarm_time_down):
                    alarm_time_temp.SubHourTime(hour_increment)
                    print ("  New Alarm Time = ", alarm_time_temp.TimeString , end="\r")
                    break
                else:
                    seconds_down_held = seconds_down_held + 0.1
                    if seconds_down_held > 2:
                        break #This should exit out of the whole alarm change state
                time.sleep(0.1)
        elif not GPIO.input(alarm_time_up):
            seconds_idle = 0
            while True:
                if GPIO.input(alarm_time_up):
                    alarm_time_temp.AddHourTime(hour_increment)
                    print ("  New Alarm Time = ", alarm_time_temp.TimeString , end="\r")
                    break
                else:
                    seconds_up_held = seconds_up_held + 0.1
                    if seconds_up_held > 2:
                        break #This should exit out of the whole alarm change state
                time.sleep(0.1)
        else:
            seconds_idle = seconds_idle + 0.1
            seconds_up_held = 0
            seconds_down_held = 0
        time.sleep(0.1)
                    
    if seconds_down_held >= 2 or seconds_idle >= 15:
        print("                                             ", end="\r")
        print("  Alarm Time Change Cancelled...")
        print ("\n~~~~~~~~~Alarm Time Changer End~~~~~~~\n")
        return 0#exits out of alarm change state if seconds down was held for 2 seconds or if idle for 15 seconds
    
    #Change minute state
    print("                                             ", end="\r")
    print("  Change Minute:", end="\r")
    time.sleep(2) #hold change minute message for 2 seconds
    seconds_up_held = 0
    seconds_down_held = 0
    seconds_idle = 0
    print ("  New Alarm Time = ", alarm_time_temp.TimeString , end="\r")
    
    while seconds_up_held < 2 and seconds_down_held < 2 and seconds_idle < 15:
        if not GPIO.input(alarm_time_down):
            seconds_idle = 0
            while True:
                if GPIO.input(alarm_time_down):
                    alarm_time_temp.SubMinTime(min_increment)
                    print ("  New Alarm Time = ", alarm_time_temp.TimeString , end="\r")
                    break
                else:
                    seconds_down_held = seconds_down_held + 0.1
                    if seconds_down_held > 2:
                        break #This should exit out of the whole alarm change state
                time.sleep(0.1)
        elif not GPIO.input(alarm_time_up):
            seconds_idle = 0
            while True:
                if GPIO.input(alarm_time_up):
                    alarm_time_temp.AddMinTime(min_increment)
                    print ("  New Alarm Time = ", alarm_time_temp.TimeString , end="\r")
                    break
                else:
                    seconds_up_held = seconds_up_held + 0.1
                    if seconds_up_held > 2:
                        break #This should exit out of the whole alarm change state
                time.sleep(0.1)
        else:
            seconds_idle = seconds_idle + 0.1
            seconds_up_held = 0
            seconds_down_held = 0
        time.sleep(0.1)
        
    if seconds_down_held >= 2 or seconds_idle >= 15:
        print("                                             ", end="\r")
        print("  Alarm Time Change Cancelled...")
        print ("\n~~~~~~~~~Alarm Time Changer End~~~~~~~\n")
        return 0 #exits out of alarm change state if seconds down was held for 2 seconds or if idle for 15 seconds

    #Lock in alarm change
    print("                                             ", end="\r")
    print ("  Changing alarm time...", end="\r")
    time.sleep(2)
    alarm_time = alarm_time_temp
    
    return alarm_time #break out of 60 second while loop now that alarm has been changed
