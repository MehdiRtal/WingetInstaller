import requests
import wget
import zipfile
import os
import argparse
import re
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument("arch", nargs="?", default=False)
parser.add_argument("-artifact", action="store_false")
args = parser.parse_args()

download_link = "https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
root_filename = wget.filename_from_url(download_link)
filenames_to_extract = ["winget.exe", "WindowsPackageManager.dll", "resources.pri"]

def version():
    response = requests.get("https://github.com/microsoft/winget-cli/releases/latest")
    soup = BeautifulSoup(response.text, "lxml")
    return "".join(re.findall(r"\d|[.]", soup.find("h1", class_="d-inline mr-3").text))

def extract(arch):
    with zipfile.ZipFile(root_filename) as zip:
        files = zip.namelist()
        for file in files:
            if f"AppInstaller_{arch}.msix" in file:
                zip.extract(file)
    os.remove(root_filename)
    with zipfile.ZipFile(f"AppInstaller_{arch}.msix") as zip:
        for filename in list(set(filenames_to_extract) & set(zip.namelist())):
            zip.extract(filename)
    os.remove(f"AppInstaller_{arch}.msix")

def compress(version, arch):
    with zipfile.ZipFile(f"winget_{version}_{arch}.zip", mode="w") as zip:
        for file_to_write in filenames_to_extract:
            zip.write(file_to_write, file_to_write, compress_type=zipfile.ZIP_STORED)
    for filename in filenames_to_extract:
        os.remove(filename)

def deploy(arch):
    extract(arch)
    if args.artifact:
        compress(version(), arch)
    if not args.artifact:
        with open(os.getenv("GITHUB_ENV"), "a") as f:
            f.write(f"version={version()}")

if __name__ == "__main__":
    if os.path.exists(root_filename):
        os.remove(root_filename)
    wget.download(download_link)
    if args.arch:
        deploy(args.arch)
