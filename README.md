# Stability_Dimensions

## Overview
![alt text](https://github.com/kyleButler9/Stability_Dimensions//back.png?raw=true)
![alt text](https://github.com/kyleButler9/Stability_Dimensions//front.png?raw=true)
![alt text](https://github.com/kyleButler9/Stability_Dimensions//survey.png?raw=true)

## Initialization

Navigate in powershell to the parent directory of this repo and then,
after installing the Requirements.txt file via

    pip3 install -r Stability_Dimensions/Requirements.txt

initialize the database schema of the database specified in the .ini file stored
in the panels/psql subdirectory and run

    python Stability_Dimensions/panels/psql/Initialize_Database.py

## Running

To view the app directly from a Bokeh server, from the parent directory and
execute the command:

    bokeh serve --show Stability_Dimensions
or

    bokeh serve --port 5432 --allow-websocket-origin=192.168.0.1:5432 --show Stability_Dimensions

Where 192.168.0.1 is your IPv4 address and 5432 is your port. Note that to share
on LAN, you must open an inbound rule on the your firewall at that port.

It is advised that you run this in a virtualenv environment, save this repo
in the Scripts folder in the environment created by virtualenv, and execute the
above commands from the Scripts folder.
