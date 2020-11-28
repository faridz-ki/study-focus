from platform import system
from subprocess import check_output, STARTUPINFO, STARTF_USESHOWWINDOW
from pathlib import Path
import re, os

system_type = system()

if system_type == "Windows":
    import wmi
    manager = wmi.WMI()
elif system_type == "Linux":
    import psutil
else:
    exit("Not a Usable Platform")


def GetProcesses():
    names = []
    if system_type == "Windows":
        for process in manager.Win32_Process():
            names.append(process.Name)
    elif system_type == "Linux":
        for process in psutil.process_iter():
            names.append(process.name().split("/")[0])
    names = list(set(names))
    return names


def GetPrograms():
    names = []
    if system_type == "Windows":
        links = list(Path("C:/ProgramData/Microsoft/Windows/Start Menu").rglob("*.lnk"))
        links += list(Path("C:/Users/" + os.getenv("USERNAME") + "/AppData/Roaming/Microsoft/Windows/Start Menu/Programs").rglob("*.lnk"))
        links = [str(link) for link in links]
        startupinfo = STARTUPINFO()
        startupinfo.dwFlags |= STARTF_USESHOWWINDOW
        for link in links:
            if not re.search(",", link) and not re.search("\(", link):
                double_slashed = link.replace("\\", "\\\\")
                cargs = ["wmic", "path", "win32_shortcutfile", "where", "name=\"{0}\"".format(double_slashed), "get", "target", "/value"]
                filename = list(filter(None, check_output(cargs, startupinfo=startupinfo).splitlines()))[0]
                print(filename)
                if filename != b"Target=":
                    names.append(filename.split(b"\\")[-1].decode("utf-8"))
    elif system_type == "Linux":
        for program in check_output(["/bin/bash", "-c", "compgen -c"]).splitlines():
            temp = program.decode('utf-8')
            if re.search("[a-zA-Z]", temp):
                names.append(temp)
    names = list(set(names))
    names.sort()
    return names

print(GetPrograms())
