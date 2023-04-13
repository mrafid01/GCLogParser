# GC Log Parser

## Running
run.bat on windows (might have to run on administrator for the first time when installing requirements)
run.sh on linux/wsl

## Env
If not deploying, just leave as is
else:
- make a .env at root with app and api links
- make change index.js APP_URL

## Troubleshooting
- If python doesn't exist, try creating a symlink between python and a current python version (example is 3.10):
'''sh
sudo ln -s /usr/bin/python3.10 /usr/bin/python
'''