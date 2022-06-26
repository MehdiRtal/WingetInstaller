import requests
import wget
import zipfile
import os
import argparse
import re
from bs4 import BeautifulSoup
.
parser = argparse.ArgumentParser()
parser.add_argument("architecture", nargs="?", default="x64")
parser.add_argument("-portable", action="store_false")
parser.add_argument("-compress", action="store_true")
parser.add_argument("-artifact", action="store_true")
args = parser.parse_args()

files = ["winget.exe", "WindowsPackageManager.dll", "resources.pri"]
DLLs = ["concrt140.dll", "msvcp140.dll", "vcruntime140.dll", "vcruntime140_1.dll"]

def version():
    response = requests.get("https://github.com/microsoft/winget-cli/releases/latest")
    soup = BeautifulSoup(response.text, "lxml")
    return "".join(re.findall(r"\d|[.]", soup.find("h1", class_="d-inline mr-3").text))

def download():
    wget.download("https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle", bar=None)
    for DLL in DLLs:
        wget.download(f"https://github.com/MehdiRtal/WingetInstaller/raw/main/DLLs/{DLL}", bar=None)

def extract(arch):
    with zipfile.ZipFile("Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle") as zip:
        for file in zip.namelist():
            if file == f"AppInstaller_{arch}.msix":
                zip.extract(file)
    with zipfile.ZipFile(f"AppInstaller_{arch}.msix") as zip:
        for file in list(set(files) & set(zip.namelist())):
            zip.extract(file)
    os.remove("Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle")
    os.remove(f"AppInstaller_{arch}.msix")

def compress(version, arch):
    with zipfile.ZipFile(f"winget_{version}_{arch}.zip", mode="w") as zip:
        for file in files + DLLs:
            zip.write(file, file, compress_type=zipfile.ZIP_STORED)
            os.remove(file)  

def install():
    for file in files + DLLs:
        os.system(fr"cmd /c xcopy {file} C:\Windows\System32 /c /q /y")
        os.remove(file)

def deploy(arch):
    download()
    extract(arch)
    if args.compress:
        compress(version(), arch)
    if args.portable:
        install()
    if args.artifact:
        with open(os.getenv("GITHUB_ENV"), "a") as f:
            f.write(f"version={version()}")

if __name__ == "__main__":
    deploy(args.architecture)
