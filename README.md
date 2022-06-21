# WingetDownloader

WingetDownloader is a simple script which lets you have winget without having access to Microsoft Store, App Installer or even PowerShell. It downloads winget from the official repo and extracts it.

## Installation
# Method 1
First clone the repo, extract it, then install python and run:

    pip install wget requests bs4 lxml 
    python WingetDownloader -arch
    
Replace `arch` with your disired system architecture.

#Method 2
Fork the repo then go to github actions and build the script by choosing your desired `arch` in the settings.
