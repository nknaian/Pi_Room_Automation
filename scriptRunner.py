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
script_running = True
gitPull_script_running = False


# Run master regulator in terminal
proc1 = subprocess.Popen(["lxterminal -e python3 /home/pi/Desktop/Git_repo/Pi_Room_Automation/master_regulator.py"], shell=True, preexec_fn=os.setsid)

try:
    time.sleep(2)
    while True:
                               
        if not GPIO.input(toggle_script):
            
            if script_running:
                #Kill master_regulator
                os.killpg(os.getpgid(proc1.pid), signal.SIGTERM)
                script_running = False

                #Run the gitpull loop
                proc2 = subprocess.Popen(["lxterminal -e python /home/pi/Desktop/Git_repo/Pi_Room_Automation/gitPullLoop.py"], shell=True, preexec_fn=os.setsid)
                gitPull_script_running = True
                
            elif gitPull_script_running:
                #Stop running gitpull loop
                os.killpg(os.getpgid(proc2.pid), signal.SIGTERM)
                gitPull_script_running = False

                #Run master regulator again
                proc1 = subprocess.Popen(["lxterminal -e python3 /home/pi/Desktop/Git_repo/Pi_Room_Automation/master_regulator.py"], shell=True, preexec_fn=os.setsid)
                script_running = True
                
            else:
                raise ControlFlowException(78, script_running, gitPull_script_running)
                
                
        time.sleep(2)

    ### End Script Loop ###

except ControlFlowException as error:
    print(error)
    
except BaseException as error:
    error_message = 'An exception occurred: {}'.format(error)
    print(error_message)
