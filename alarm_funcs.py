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
    heater_time = ATime(alarm_time.TimeString, "sub", 2, "hour")
    heater_off_time = ATime(alarm_time.TimeString, "add", 45, "min")
    return heater_time, heater_off_time

def pick_random_url_from_file():
    # Pick random url
    with open("/home/pi/Desktop/Random_urls") as f:
        urls = f.readlines()
    random.seed()
    rand_url_index = random.randint(0, len(urls) - 1)
    url_line = urls[rand_url_index]
    if ", " in url_line:
        url = url_line.split(", ")[0]
        nameAndEmail = url_line.split(", ")[1]
        numSpaces = nameAndEmail.count(" ")
        email = nameAndEmail.split(" ", 6)[numSpaces]
        lastName = nameAndEmail.split(" ", 6)[numSpaces - 1]

        # First name will be all words in between comma and last name
        firstName = ""
        for i in range(0, numSpaces - 1):
            firstName += nameAndEmail.split(" ", 6)[i]
            if i == numSpaces - 2:
                pass
            else:
                firstName += " "

    else:
        url = url_line
        firstName = "???"
        lastName = "???"
        email = "???"

    # Delete url_line from "Random_url"
    iterator = 0
    with open("/home/pi/Desktop/Random_urls", "w") as f_source:
        for i in range(0, len(urls)):
            if i == rand_url_index:
                pass
            else:
                f_source.write(urls[i])

    return url_line, url, firstName, lastName, email

def play_youtube_video(url):
    subprocess.Popen("amixer cset numid=3 1", shell=True)
    subprocess.Popen("amixer cset numid=1 50%", shell=True) # Set volume to 0 to start

    # Open instance of firefox and maximize window
    browser = webdriver.Firefox()
    browser.maximize_window()

    # retrieve password:
    with open("/home/pi/Desktop/password", "r") as f:
        password = f.readline()

    # log in to youtube so I can watch 18+ videos
    browser.get('https://accounts.google.com/ServiceLogin?continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Fhl%3Den%26feature%3Dcomment%26app%3Ddesktop%26next%3D%252Fall_comments%253Fv%253DLAr6oAKieHk%26action_handle_signin%3Dtrue&uilel=3&service=youtube&passive=true&hl=en')
    browser.find_element_by_id('Email').send_keys('snoozinforabruisin@gmail.com')
    browser.find_element_by_id('next').click()
    browser.find_element_by_id('Passwd').send_keys(password)
    browser.find_element_by_id('signIn').click()

    browser.get(url)
    time.sleep(5) # Give url a few seconds to open
    subprocess.Popen("amixer cset numid=1 95%", shell=True) # Set volume to high end

    return browser

def run_send_email_and_monitor(scriptWithArgs):
    try:
        out = subprocess.check_output(scriptWithArgs, stderr=subprocess.STDOUT, timeout = 60)
    except subprocess.TimeoutExpired as error:
        str_error = str(error)
        print("\n" + str_error + "\n")
    else:
        str_out = str(out)
        if str_out != "b\'\'":
            print(out)


def run_script_and_monitor(scriptWithArgs): #This function takes the script with args as a list, just as it would be typed in terminal...use to relay standard error and output (will not work for execute_send_email)
    try:
        out = subprocess.check_output(scriptWithArgs, stderr=subprocess.STDOUT, timeout = 60)
    except subprocess.TimeoutExpired as error:
        str_error = str(error)
        print("\n" + str_error + "\n")
    else:
        str_out = str(out)
        if str_out != "b\'\'":
            print(out)


def monitor_alarm_and_place_used_url(url_line, url, alarm_time_up, alarm_time_down, browser, firstName, lastName): # This function takes 5 min at the most
    elapsed_alarm_time = 0
    wake_up_time = 1000 #just making it a number much greater than 300
    wasFavorited = False
    didFail = False

    # Get the initial mouse location for comparison later
    p1 = subprocess.Popen(["xdotool", "getmouselocation", "--shell"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out, err = p1.communicate()
    initial_x_line = out.split(b'\n', 10)[0]
    initial_y_line = out.split(b'\n', 10)[1]

    while True:

        # Get the current mouse position
        p2 = subprocess.Popen(["xdotool", "getmouselocation", "--shell"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        out, err = p2.communicate()
        current_x_line = out.split(b'\n', 10)[0]
        current_y_line = out.split(b'\n', 10)[1]

        if elapsed_alarm_time > 300: # When mic circuit created use that instead of timing to figure if an alarm isn't being played
            wake_up_time = elapsed_alarm_time
            didFail = True
            break

        elif (current_x_line != initial_x_line) and (wake_up_time > elapsed_alarm_time):
            wake_up_time = elapsed_alarm_time
            subprocess.Popen("amixer cset numid=1 86%", shell=True) # Set volume to 50%
            break

        elif (current_y_line != initial_y_line) and (wake_up_time > elapsed_alarm_time):
            wake_up_time = elapsed_alarm_time
            subprocess.Popen("amixer cset numid=1 86%", shell=True) # Set volume to 50%
            break

        elapsed_alarm_time += 1
        time.sleep(1)

    if didFail:
        # Alarm didn't work...I didn't get up
        print("\nAlarm placed in FailedVideos :/\n")
        with open("/home/pi/Desktop/FailedVideos", "a") as f:
            f.write(url_line)
        subprocess.Popen("omxplayer -o local /home/pi/Desktop/staring_at_the_sun.mp3", shell=True) #the default really should be an annoying alarm...figure that out...

    else: # only give favoriting option if video didn't fail
        wake_up_time = str(wake_up_time) + " seconds"

        print("\n\nAlaram brought to you this morning by ", firstName, lastName, "\n\n")

        # Enter additional feedback on the video if you have any
        inputString = "\n\nDo you have any additional feedback for " + firstName + " on the video?\n\n"
        additional_feedback = input(inputString)

        print("\nWould you like to favorite the video?\n")
        while True:
            if not GPIO.input(alarm_time_up):
                # Alarm was favorited
                print("\nAlarm Placed in FavoritedVideos!\n")
                wasFavorited = True
                with open("/home/pi/Desktop/FavoritedVideos", "a") as f:
                    f.write(url_line)
                break

            elif not GPIO.input(alarm_time_down):
                # Alarm worked, not a favorite though
                print("\nAlarm Placed in PlayedVideos\n")
                with open("/home/pi/Desktop/PlayedVideos", "a") as f:
                    f.write(url_line)
                break

    browser.close() # Now that you set your like for the video, close it

    return wake_up_time, wasFavorited, didFail, additional_feedback

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
