import os
import subprocess

def compile_resources():
    os.makedirs("fonts", exist_ok=True)
    
    subprocess.run(["pyrcc5", "resources.qrc", "-o", "resources_rc.py"])
    
    print("Resources compiled successfully!")

if __name__ == "__main__":
    compile_resources() 