import subprocess
import signal
import os
import time
import shlex

print("Waiting for a gitPullRequest...\n\n")
while True:
    subprocess.Popen("python2 /home/pi/Desktop/Git_repo/Pi_Room_Automation/gmail/execute_email_snoozin.py poll -m GitPullRequest", shell=True)
    time.sleep(2)

