# pip install pyautogui
import os
import pyautogui
from datetime import datetime,date
import time

def take_screenshots(screenshotPath):
    folder = date.today()
    folderPath = screenshotPath + f'/{folder}'
    # Today folder doesn't exist
    if not os.path.exists(folderPath):
        # Create one
        os.makedirs(folderPath)

    while True:
        now = datetime.now()
        screenshot = pyautogui.screenshot()
        # New day comes
        # Save picture in new folder
        if now.date()!=folder:
            folder = date.today()
            folderPath = screenshotPath + f'/{folder}'
            if not os.path.exists(folderPath):
                os.makedirs(folderPath)

        screenshot.save(f'{folderPath}/{now.strftime("%H-%M-%S")}.png')
        # Wait 1min, then take screenshot again
        time.sleep(60)

# take_screenshots('C:/Users/DELL/OneDrive - VNU-HCMUS/Screenshot')