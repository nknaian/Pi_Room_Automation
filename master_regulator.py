 #!python3
#How I got this setup...
'''
Open command prompt.
Once loaded type sudo idle3 & and press enter on the keyboard.
This will load the Python 3 programming environment called IDLE3 as the
super user which allows you to create a program that affects the GPIO pins.
Once loaded click on file and new window.
'''
#testingz
#NOTE: This script is only meant to be run on my raspberry pi to function with
#      the GPIO setup it has

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
import sys

# local imports
from alarm_funcs import ATime, get_all_alarm_times, pick_random_url_from_file, play_youtube_video, run_script_and_monitor, monitor_alarm_and_place_used_url, change_alarm_manual, run_send_email_and_monitor

'''
............... SETUP ................
'''


#Make sure the GPIO pins are ready
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

temp_sense = 12
heater_off = 5
heater_on = 4
alarm_time_up = 13
alarm_time_down = 26
I_am_here_pin = 6

GPIO.setup(temp_sense, GPIO.IN)
GPIO.setup(I_am_here_pin, GPIO.IN)
GPIO.setup(heater_off, GPIO.OUT)
GPIO.setup(heater_on, GPIO.OUT)
GPIO.setup(alarm_time_up, GPIO.IN)
GPIO.setup(alarm_time_down, GPIO.IN)

'''
...............SANITY CHECKS................
'''


if GPIO.input(temp_sense):
    print("\nTemp above 63 degrees Fahrenheit")
else:
    print("\nTemp below 63 degress Fahrenheit")



'''
...............HELPER FUNCTIONS................
'''



#Define functions turn heater on and turn heater off
def turn_heater_on():
    GPIO.output(heater_on, 1)
    time.sleep(1)
    GPIO.output(heater_on, 0)
    time.sleep(1)

def turn_heater_off():
    GPIO.output(heater_off, 1)
    time.sleep(1)
    GPIO.output(heater_off, 0)
    time.sleep(1)

def Update_heater_state(is_heater_on, current_time):
    if ( not GPIO.input(temp_sense) ) and ( not is_heater_on ):
        turn_heater_on()
        is_heater_on = True
        message = "\nTurned heater on! (At " + current_time + ")"
        print(message)
    elif ( GPIO.input(temp_sense) ) and ( is_heater_on ):
        turn_heater_off()
        is_heater_on = False
        message = "\nTurned heater off! (At " + current_time + ")"
        print(message)
    return is_heater_on


'''
...............CONTROL FUNCTIONS................
'''


#If clock is in wrong time zone...use this: sudo dpkg-reconfigure tzdata
def alarm_func(heater_time, alarm_time, heater_off_time, is_heater_on):
    now = datetime.datetime.now()
    current_time = ATime(now.strftime("%H:%M"))
    while heater_off_time.GreaterThan(current_time):
        #Get current time
        now = datetime.datetime.now()
        current_time = ATime(now.strftime("%H:%M"))

        #If it is alarm time, play alarm
        if current_time.TimeString == alarm_time.TimeString:
            url_line, url, firstName, lastName, email = pick_random_url_from_file()
            browser = play_youtube_video(url)
            wake_up_time, wasFavorited, didFail, additional_feedback = monitor_alarm_and_place_used_url(url_line, url, alarm_time_up, alarm_time_down, browser, firstName, lastName)

            #Create string vresions of booleans:
            str_wasFavorited = str(wasFavorited)
            str_didFail = str(didFail)

            # Append stats file (name, url, wake_up_time, was_favorited)
            with open("/home/pi/Desktop/snoozin_stats", "a") as f:
                write_string = firstName + " " + lastName + ", " + url + ", " + str_didFail + ", " + str_wasFavorited + ", "  + wake_up_time + "\n"
                f.write(write_string)

            #Send email here
            if email != "???":
                print("Sending email")
                run_send_email_and_monitor(["python2", "/home/pi/Desktop/Git_repo/Pi_Room_Automation/gmail/execute_send_email.py", "email", "-v", "SendAlarmNotification", "-e", email, "-n", firstName, "-u", url, "-t", wake_up_time, "-f", str_wasFavorited, "-F", str_didFail, "-a", additional_feedback])
            else:
                print("no email link found")
        is_heater_on = Update_heater_state(is_heater_on, current_time.TimeString)

        time.sleep(45)

    if is_heater_on:
        turn_heater_off()
        is_heater_on = False
        print("\nHeater turned off due to end of interval")


def master_regulator():
    # constants:
    min_increment = 5
    hour_increment = 1

    # initial states
    alarm_time = ATime("07:00")
    I_am_here = True
    is_heater_on = False
    remote_heater_request = False
    heater_on_remotely = False
    heater_off_remotely = False
    alarm_on = True
    sent_success = False

    turn_heater_off() #in case heater was left on after program terminated
    time.sleep(1)

    #Testing alarm_func: (comment out block during normal operation)
    '''
    now = datetime.datetime.now()
    current_time = ATime(now.strftime("%H:%M"))
    heater_time = ATime(current_time.TimeString)
    alarm_time = ATime(heater_time.TimeString, "add", 1, "min")
    heater_off_time = ATime(alarm_time.TimeString, "add", 5, "min")
    alarm_func(heater_time, alarm_time, heater_off_time, is_heater_on)
    '''#end alarm_func testing

    #Derive other alarm times
    heater_time, heater_off_time = get_all_alarm_times(alarm_time)

    print ("\nAlarm is set for", alarm_time.TimeString)
    print ("Heater will turn on at", heater_time.TimeString)
    print ("Heater will turn off at", heater_off_time.TimeString)

    # part of testing being done a few lines below:
    now = datetime.datetime.now()
    prev_time = ATime(now.strftime("%H:%M"))

    while True:

        ###### Input and alarm time checks (Every minute) ######


        #Get current time
        now = datetime.datetime.now()
        current_time = ATime(now.strftime("%H:%M"))

        #Test print to track when we come back from a long time since the last loop
        prev_plus_one = ATime(prev_time.TimeString, "add", 1, "min")
        prev_plus_two = ATime(prev_time.TimeString, "add", 2, "min")
        if (prev_plus_one.TimeString == current_time.TimeString) or (prev_plus_two.TimeString == current_time.TimeString) :
            print(current_time.TimeString)
        else:
            print("Re-entering the while loop at ", current_time.TimeString)
        prev_time = current_time # Set prev equal to current for next time

        #Decide whether it is alarm time and what to do with heater
        one_min_late = ATime(heater_time.TimeString, "add", 1, "min")
        if (current_time.TimeString == heater_time.TimeString or current_time.TimeString == one_min_late.TimeString) and alarm_on :
            alarm_func(heater_time, alarm_time, heater_off_time, is_heater_on)
            is_heater_on = False
        elif remote_heater_request:
            if heater_on_remotely and not is_heater_on:
                turn_heater_on()
                is_heater_on = True
                print("\nHeater turned on per remote request\n")
            elif heater_off_remotely and is_heater_on:
                turn_heater_off()
                is_heater_on = False
                heater_off_remotely = False
                heater_on_remotely = False
                print("\nHeater turned off per remote request\n")
            else:
                print("\nHeater already in this state!\n")
            remote_heater_request = False   # The request has been fufilled

        elif I_am_here or heater_on_remotely:
            is_heater_on = Update_heater_state(is_heater_on, current_time.TimeString)
            if not is_heater_on and heater_on_remotely: # Once heater is turned off after a remote request,
                heater_on_remotely = False              # keep it off (unless someone is here)
                # send emali to user saying that room is now warm
        elif not I_am_here and is_heater_on:
            turn_heater_off()
            is_heater_on = False
            print("\nHeater turned off because I am not here")

        #Check for new urls from gmail
        run_script_and_monitor(["python2", "/home/pi/Desktop/Git_repo/Pi_Room_Automation/gmail/execute_email_snoozin.py", "poll", "-m", "AddUrls"])


        #Check for new alarm requests from gmail
        run_script_and_monitor(["python2", "/home/pi/Desktop/Git_repo/Pi_Room_Automation/gmail/execute_email_snoozin.py", "poll", "-m", "AlarmRequest"])

        with open("/home/pi/Desktop/Git_repo/Pi_Room_Automation/gmail/alarm_state_buffer", "r") as f_read:
            text_state = f_read.readlines()
            if text_state == ['On\n']:
                alarm_on = True
                print("Alarm turned on per remote request")
                with open("/home/pi/Desktop/Git_repo/Pi_Room_Automation/gmail/alarm_state_buffer", "w") as f_write:
                    f_write.write("")
            elif text_state == ['Off\n']:
                alarm_on = False
                print("Alarm turned off per remote request")
                with open("/home/pi/Desktop/Git_repo/Pi_Room_Automation/gmail/alarm_state_buffer", "w") as f_write:
                    f_write.write("")
            else:
                pass
            # Then you should send an email back to the sender with the
            # result (can store text of email in the text buffer)

        #Check for new heater requests from gmail
        run_script_and_monitor(["python2", "/home/pi/Desktop/Git_repo/Pi_Room_Automation/gmail/execute_email_snoozin.py", "poll", "-m", "HeaterRequest"])

        with open("/home/pi/Desktop/Git_repo/Pi_Room_Automation/gmail/heater_state_buffer", "r") as f_read:
            text_state = f_read.readlines()
            if text_state == ['On\n']:
                remote_heater_request = True
                heater_on_remotely = True
                with open("/home/pi/Desktop/Git_repo/Pi_Room_Automation/gmail/heater_state_buffer", "w") as f_write:
                    f_write.write("")
            elif text_state == ['Off\n']:
                remote_heater_request = True
                heater_off_remotely = True
                with open("/home/pi/Desktop/Git_repo/Pi_Room_Automation/gmail/heater_state_buffer", "w") as f_write:
                    f_write.write("")
            else:
                pass
            # Then you should send an email back to the sender with the
            # result (can store text of email in the text buffer). Maybe give
            # a prediction of how long it will take to get to get warm based
            # on the mornings heat up time


        ####### Input checks (Every second) ######


        seconds_up_held = 0
        seconds = 0
        while seconds < 60:
            #Get if alarm is being changed
            if not GPIO.input(alarm_time_up):
                seconds_up_held = seconds_up_held + 1
                if seconds_up_held > 2:
                    new_alarm_time = change_alarm_manual(alarm_time, alarm_time_up, alarm_time_down, hour_increment, min_increment)
                    if new_alarm_time == 0: #Don't change alarm time if 0 was returned
                        pass
                    else:
                        alarm_time = new_alarm_time
                        heater_time, heater_off_time = get_all_alarm_times(alarm_time) #update other times
                        print("                                             ", end="\r")
                        print ("  Alarm is now set 4", alarm_time.TimeString)
                        print ("  Heater will turn on at", heater_time.TimeString)
                        print ("  Heater will turn off at", heater_off_time.TimeString)
                        print ("\n~~~~~~~~~Alarm Time Changer End~~~~~~~\n")
                    break
            else:
                seconds_up_held = 0

            #Get whether I am here
            if (not GPIO.input(I_am_here_pin)) and heater_off_remotely == False:
                I_am_here = True
            elif  GPIO.input(I_am_here_pin):
                I_am_here = False
                heater_off_remotely = False # Now that user is here we can disregard the remote request

            seconds = seconds + 1
            time.sleep(1)


'''
...............MAIN BLOCK................
'''
# Parse arguments (this currently isn't doing anything)
parser = argparse.ArgumentParser(description='parse arges')
parser.add_argument('-p', dest="process",
                    help='pass in the callers proccess id')

args = parser.parse_args

while True:
try:
        master_regulator()
    except Exception as error:
        str_error = str(error)
        print("In master_regulator an error was found:\n" + str_error + "\n")
