git status
PAUSE
git add -A
set /p commit_message=Enter commit message (with quotations):
git commit -m %commit_message%"
git push
python gmail\execute_send_email.py email -v GitPullRequest
PAUSE
