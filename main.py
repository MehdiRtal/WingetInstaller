import requests
import wget
import zipfile
import os
import argparse
import re
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument("-arm", action="store_true")
parser.add_argument("-arm64", action="store_true")
parser.add_argument("-x86", action="store_true")
parser.add_argument("-x64", action="store_true")
args = parser.parse_args()

def version():
    response = requests.get("https://github.com/microsoft/winget-cli/releases/latest")
    soup = BeautifulSoup(response.text, "lxml")
    return "".join(re.findall(r"\d|[.]", soup.find("h1", class_="d-inline mr-3").text))

url = "https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"

wget.download(url)

root = wget.filename_from_url(url)
filenames = ["winget.exe", "WindowsPackageManager.dll", "resources.pri"]

def extract(arch):
    with zipfile.ZipFile(root) as zip:
        files = zip.namelist()
        for file in files:
            if f"AppInstaller_{arch}.msix" in file:
                zip.extract(file)
    os.remove(root)
    with zipfile.ZipFile(f"AppInstaller_{arch}.msix") as zip:
        for filename in list(set(filenames) & set(zip.namelist())):
            zip.extract(filename)
    os.remove(f"AppInstaller_{arch}.msix")

def compress(version, arch):
    with zipfile.ZipFile(f"winget_{version}_{arch}.zip", mode="w") as zip:
        for file_to_write in filenames:
            zip.write(file_to_write, file_to_write, compress_type=zipfile.ZIP_STORED)
    for filename in filenames:
        os.remove(filename)

if args.arm:
    extract("arm")
    compress(version(), "arm")

if args.arm64:
    extract("arm64")
    compress(version(), "arm64")

if args.x64:
    extract("x64")
    compress(version(), "x64")

if args.x86:
    extract("x86")
    compress(version(), "x86")