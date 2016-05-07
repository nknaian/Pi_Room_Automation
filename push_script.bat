ECHO Hello World
git add -A
set /p commit_message="Enter commit message: " 
git commit -m commit_message
git push
PAUSE