import subprocess
import time

p1 = subprocess.Popen(["xdotool", "getmouselocation", "--shell"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

out, err = p1.communicate()

initial_x_line = out.rsplit("\n", 10)[0]
initial_y_line = out.rsplit("\n", 10)[1]

timeElapsed = 0
while True:
    p2 = subprocess.Popen(["xdotool", "getmouselocation", "--shell"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out, err = p2.communicate()

    current_x_line = out.rsplit("\n", 10)[0]
    current_y_line = out.rsplit("\n", 10)[1]

    if current_x_line != initial_x_line:
        break
    if current_y_line != initial_y_line:
        break

    timeElapsed += 1
    time.sleep(1)

print "\nTime elapsed = " + str(timeElapsed) + "\n"
