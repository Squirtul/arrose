Welcome to Arrose!

This full guide will help you prepare Arrose software onto your own Raspberry Pi!

You must have both:
- Raspberry Pi 4 (with reasonably sized MicroSD)
- Waveshare 2.4" LCD Module (with 8 leads)


Your LCD will have a terminal for 8 leads. They are labelled. Connect each to the corresponding pin on your Raspberry Pi:

VCC > Pin 2   
GND > Pin 6     
DIN > Pin 19 
CLK > Pin 23    
CS > Pin 24     
DC > Pin 22
RST > Pin 13
BL > Pin 12

To find the numbers of each pin, see https://www.raspberrypi-spy.co.uk/wp-content/uploads/2012/06/Raspberry-Pi-GPIO-Header-with-Photo.png


Insert the MicroSD into your computer. Use the Raspberry Pi Imager to flash Pi OS 64-bit onto the SD (https://www.raspberrypi.com/software/)
Set (and remember) a hostname, username and password. Add your WiFi SSID (name) and password, so the Pi can connect to to the internet
Make sure you ENABLE SSH with password auth!

Insert the MicroSD into the Pi and power it on.

Use your router's admin page to find the IP address of your Pi. Alternatively, plug a keyboard and monitor into the Pi and run "hostname -I" to get its IP.

From your PC, run the file "installer.bat" and follow steps!


And that's it! Set your airport and have fun =)


If your WiFi goes down and the Pi cannot reconnect:
- Check status with "nmcli device status"
- Manually connect with "sudo nmcli device wifi connect [ssid] password [password]"
- Make it connect automatically in the future with "sudo nmcli connection modify "SSID" connection.autoconnect yes"