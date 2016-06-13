import RPi.GPIO as GPIO
import subprocess
import signal
import os
import time

### Custom Exceptions ###

class ControlFlowException(Exception):
    def __init__(self, lineNumber, script, gitPullScript):
        Exception.__init__(self, "A ControlFlowException occured in scriptRunner.py at line {0}. script = {1}, gitPullScript = {2}".format(lineNumber, script, gitPullScript))
        self.lineNumber = lineNumber
        self.script = script
        self.gitPullScript = gitPullScript

### End Custom Exceptions ###


### Function Definitions ###

def writeToTextpad(proc, text, writeType):
    with open("/home/pi/Desktop/scriptOutput", writeType) as f:
        f.write(text)
    os.system("sudo killall leafpad") # close window and reopen so we can see updates
    proc = subprocess.Popen("leafpad /home/pi/Desktop/scriptOutput", shell=True)


### End Function Definitions ###


### Pin Setup ###

#Make sure the GPIO pins are ready
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

toggle_script = 17

GPIO.setup(toggle_script, GPIO.IN)

### End Pin Setup ###



### Script Loop ###

#Open scriptOutput text file
proc1_3 = subprocess.Popen("leafpad /home/pi/Desktop/scriptOutput", shell=True)
time.sleep(1)


script_running = True
gitPull_script_running = False
error_encountered = False
error_message_shown = False

writeToTextpad(proc1_3, "", "w") # clear the scriptOutput notepad

# Run master regulator to start
proc2 = subprocess.Popen(["python3", "-u", "/home/pi/Desktop/Git_repo/Pi_Room_Automation/master_regulator.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, preexec_fn=os.setsid)

try:
    #proc1 = subprocess.Popen("lxterminal -e sudo idle3 &", shell=True)
    time.sleep(2)
    while True:
        
        if (proc2.poll() is not None) and (script_running == True):
            error_encountered = True
            out, err = proc2.communicate()
            subprocess.check_output(["python2", "/home/pi/Desktop/Git_repo/Pi_Room_Automation/gmail/execute_send_email.py", "email", "-v", "SendErrorMessage", "-b", err])

            os.system("sudo killall leafpad")
            script_running = False
            
        elif (proc2.poll() is None) and script_running:
            output= proc2.stdout.read()
            writeToTextpad(proc1_3, output, "a")
        
        else:
            if (not gitPull_script_running) and (not error_encountered):
                raise ControlFlowException(76, script_running, gitPull_script_running)
            elif error_encountered and not error_message_shown:
                writeToTextpad(proc1_3, "\nAn error was encountered...check email for error message", "a")
                error_message_shown = True
            else:
                pass
                               
        if not GPIO.input(toggle_script):
            os.system("sudo killall leafpad")
            
            if script_running:
                #Kill master_regulator
                os.killpg(os.getpgid(proc2.pid), signal.SIGTERM)
                os.system("sudo killall leafpad")
                script_running = False

                #Run the gitpull loop
                proc3 = subprocess.Popen(["lxterminal -e python /home/pi/Desktop/Git_repo/Pi_Room_Automation/gitPullLoop.py"], shell=True, preexec_fn=os.setsid) #maybe try setting stdin equal to what you want it to run
                gitPull_script_running = True
                
            elif gitPull_script_running:
                #Stop running gitpull loop
                os.killpg(os.getpgid(proc3.pid), signal.SIGTERM)
                gitPull_script_running = False

                #Run master regulator again
                proc2 = subprocess.Popen(["python3", "-u", "/home/pi/Desktop/Git_repo/Pi_Room_Automation/master_regulator.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, preexec_fn=os.setsid)
                writeToTextpad(proc1_3, "", "w") # clear the scriptOutput notepad
                script_running = True
                
            else:
                #Run the gitpull loop (This is the case that master_regulator errored out)
                proc3 = subprocess.Popen(["lxterminal -e python /home/pi/Desktop/Git_repo/Pi_Room_Automation/gitPullLoop.py"], shell=True, preexec_fn=os.setsid) 
                gitPull_script_running = True
                error_encountered = False #reset the error flags to false...it's being handled
                error_message_shown = False
                
                
        time.sleep(2)

    ### End Script Loop ###

except ControlFlowException as error:
    writeToTextpad(proc1_3, "\n" + str(error), "a")
    
except BaseException as error:
    error_message = 'An exception occurred: {}'.format(error)
    writeToTextpad(proc1_3, error_message, "a")
