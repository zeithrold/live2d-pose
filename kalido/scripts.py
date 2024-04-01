from zipfile import ZipFile
from argparse import ArgumentParser
from pathlib import Path
import urllib.request
import urllib.parse
import io

cubism_url = "https://cubism.live2d.com/sdk-web/bin/CubismSdkForWeb-5-r.1.zip"
dir_name = "CubismSdkForWeb-5-r.1"

arg_parser = ArgumentParser()
arg_parser.add_argument("action")

args = arg_parser.parse_args()

def check_dir_exists():
    # Check is external directory exists
    path = Path("external")
    if not path.exists():
        path.mkdir()
        print("External directory created")
    else:
        print("External directory already exists")

if args.action == "download":
    check_dir_exists()
    target_path = Path("external") / "cubism-sdk"
    if target_path.exists():
        print("external/cubism-sdk already exists, deleting...")
        target_path.rmdir()
    print("Downloading Cubism SDK...")
    # Download the Cubism SDK
    with urllib.request.urlopen(cubism_url) as res:
        print("Extracting Cubism SDK...")
        with ZipFile(io.BytesIO(res.read())) as zip_file:
            zip_file.extractall(Path("external"))
    (Path("external") / dir_name).rename(target_path)
    print("Cubism SDK downloaded and extracted to external/cubism-sdk")
elif args.action == "check":
    check_dir_exists()
    target_path = Path("external") / "cubism-sdk" / "Core" / "live2dcubismcore.min.js"
    if target_path.exists():
        print("Cubism SDK is already downloaded")
    else:
        print("Cubism SDK is not downloaded")
        exit(1)
        


