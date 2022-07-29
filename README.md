# Graphiccino
Graphiccino (spelled like "Capuccino") is, currenlty, a plotting tool to view ArduPilot logs.
It is similar to Mission Planner, but further development is towards plotting data from other log formats and data/table sources.


# pip requirements
dearpygui==1.6.1
polars==0.13.25
pymavlink
pyinstaller


# To build the exe
pyinstaller --noconfirm --onedir --windowed --name "Graphiccino"  "D:/ArduPlotter/GUI.py"
