import network
import socket
import time
import machine

ssid = '[INSERT WIFI NAME HERE]'
password = '[INSERT WIFI PASSWORD HERE]'
broadcast = "192.168.1.255" #broadcast address for sending magic packet. you can calculate it by using this website https://remotemonitoringsystems.ca/broadcast.php
mac_addr = [0x00,0x00,0x00,0x00, 0x00, 0x00] #mac address for your ethernet. you can find it using ipconfig /all on windows.
username = b'admin' #username on subhan.work

server_ip = '95.179.200.243' #ip address of subhan.work (don't change this)


def blink(interval):
    """ 
    Blink the LED on the Raspberry Pi Pico for a specified interval.

    Args:
        interval (float): the interval in seconds for which to blink the LED
    """
    led = machine.Pin("LED", machine.Pin.OUT)
    led.on()
    time.sleep(interval)
    led.off()
    time.sleep(interval)
    return

def send_wake():
    """
    Send a wake on lan packet to the specified mac address.

    Args:
        none

    Returns:
        none

    """
    msg = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
    magic = msg+(mac_addr*16)
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.sendto(bytes(magic),(broadcast,9))
    time.sleep(1)
    soc.close()



#blink the led for half a second
blink(.5)

#connect to the wifi specified
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

print("connecting....")

#try connecting to the wifi for up to 10 seconds
wlan.connect(ssid, password)
for _ in range(20):  # Try for up to 10 seconds
    if wlan.isconnected():
        print("connected!!")
        #blink the led for half a second
        blink(.5)
        break
    time.sleep(0.5)
else:
    print("Failed to connect to Wi-Fi")

#check if we are connected to the wifi
if wlan.isconnected():
    #create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect((server_ip , 6000))
    #blink the led for a quarter of a second
    blink(.25)

    try:
        #send the username to the server
        sock.send(username)
    except:
        print("error sending username!!!")

    #while we are connected to the wifi, keep listening for commands from the server
    while wlan.isconnected():
        try:
            #try to receive a command from the server
            data = sock.recv(1024).decode('utf-8')
            if data == "wake":
                #if the command is "wake", send a wake on lan packet
                print("RECIEVED WAKE COMMAND!!")
                #blink the led for an eighth of a second
                blink(.125)
                send_wake()
        except OSError:
            pass
        
        #if no command was received, send a keep_alive packet to the server
        #this is to keep the connection alive
        #blink the led for an eighth of a second
        blink(.125)
        print("sending keep_alive packet, no data came")
        try:
            sock.send(b'keep_alive')
            print("sent")
        except:
            print("error sending keep_alive packet")