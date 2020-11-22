# Using the pihole-stats display
[e-Ink display I used](https://www.waveshare.com/product/displays/e-paper/epaper-3/1.54inch-e-paper-module-b.htm)

## Install requirements
`sudo apt install git`  
`git pull https://github.com/scul/pihole-stats.git`  
`cd pihole-stats`  
`chmod u+x install.sh`  
`./install.sh`  
This will create the log file and path, as well as installing and activating the systemd service and timer files to refresh the display.  

`pip3 install -r requirements.txt`  
Installs the python requirements

## Enable SPI
`sudo raspi-config`  > `3 Interface Options` > `4P SPI`

You'll probably need to reboot now to ensure SPI access.

# Run the program
`./epaper_small.py`