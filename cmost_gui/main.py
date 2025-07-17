import subprocess
from pathlib import Path


def main():
    print("welcome to use Cmost_gui，press exit to exit")
    process = subprocess.Popen(["streamlit", "run", str(Path(__file__).parent / "combine.py"), "--theme.base", "light"])
    while True:
        c = input()
        if c=="exit":
            process.terminate()
            print("programe exit")
            break


if __name__ == "__main__":
    main()