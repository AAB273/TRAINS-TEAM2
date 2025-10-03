import tkinter as tk
import pandas as pd

from tkinter import ttk
from PIL import Image, ImageTk
from Track_Blocks import Block

df = pd.read_excel("Track Data.xlsx", sheet_name="Green Line")
qf = pd.read_excel("Track Sample Data.xlsx", sheet_name="Train Data")
pf = pd.read_excel("Track Sample Data.xlsx", sheet_name="Track Data")

########################################################################################################################

#INPUTS/OUTPUTS

commanded_speed = []
commanded_authority = []
switch_positions = [] # 0 if Switch is facing left; 1 if Switch is facing right
light_states = [] # 00 if light is red, 01 if light is yellow, 10 is green, 11 is super green
block_occupancy = [] # 0 if Block is not occupied; 1 if Block is occupied

blocks = []
#track_config (sent as file?)
#use block class for: grade, elevation, length, speed limit, track heater, beacon
track_direction = [] # 0 if track is facing left or up; 1 if track is facing right or down
railway_crossing = [] # 0 if crossing is inactive; 1 if crossing is active
heaters_work = [] # 0 of heater does not work; 1 if heater does work

# locations of Infastructure given by which track block they are located in
switch_locations = []
light_location = [] #figure out where to get location of lights
railway_location = []
station_location = []

environmental_temp: float

failure_modes = [] # 0 if no failure occurs; 1 if failure occurs
track_circuit_fail: bool
railway_crossing_fail: bool
power_fail: bool

ticket_sales = []
passengers_boarding = []
passengers_disembarking = []
train_occupancy = []
active_trains = []


########################################################################################################################

#DATA EXTRACTION FROM EXCEL 

for i, row in enumerate(df.iterrows(), start=1):
    _, data = row
    b = Block(
        grade=data["Block Grade (%)"],
        elevation=data["ELEVATION (M)"],
        length=data["Block Length (m)"],
        speed_limit=data["Speed Limit (Km/Hr)"]
    )
    b.block_number = i
    blocks.append(b)

    # Read Infrastructure column
    infra = str(data["Infrastructure"]).strip()

    if "SWITCH" in infra:
        switch_locations.append(i)

    if "RAILWAY" in infra:
        railway_location.append(i)

    if "STATION" in infra:
        # Split once at "STATION" and take what's after it
        parts = infra.split("STATION", 1)

        station_name = None
        if len(parts) > 1:
            # After "STATION", break into fields separated by semicolons
            fields = [f.strip() for f in parts[1].split(";") if f.strip()]
            if fields:
                station_name = fields[0]  # first token is the station name

        # Fallback if no name was found
        if not station_name:
            station_name = f"Station_{i}"

        station_location.append((i, station_name))


for j, row in enumerate(qf.iterrows(), start=1):
    _, data = row
    active_trains.append(data["Train ID"])
    commanded_speed.append(data["Commanded Speed"])
    commanded_authority.append(data["Commanded Authority"])
    train_occupancy.append(data["Train Occupancy"])


for k, row in enumerate(pf.iterrows(), start=1):
    _, data = row

    b = Block(
        track_heater=data["Track Heater"],
        beacon=data["Beacon"]
    )
    b.block_number = k
    blocks.append(b)

    if "Default Environmental Temp" in pf.columns:
        environmental_temp = pf["Default Environmental Temp"].dropna().iloc[0]
    else:
        environmental_temp = None

    switch_positions.append(data["Switch Positions"])
    light_states.append(data["Light States"])
    block_occupancy.append(["Block Occupancy"])
    track_direction.append(data["Track Direction"])
    railway_crossing.append(data["Railway Crossing"])
    heaters_work.append(data["Heater Works"])
    light_location.append(data["Light Locations"])
    failure_modes.append(data["Failures"])
    ticket_sales.append(data["Ticket Sales"])
    passengers_boarding.append(data["Passengers Boarding"])
    passengers_disembarking.append(data["Passengers Disembarking"])


##########################################################################################################################

#TEST CODE/UI

for b in blocks:
    print(f"Block {b.block_number}: Grade: {b.grade}, Elevation: {b.elevation}, Length: {b.length}, Speed Limit: {b.speed_limit}, Heater: {b.track_heater}")


##################################################################################################################################

#LOAD DATA

def load_data():
    """
    Package data from UI_Test into a dictionary for the UI.
    """
    return {
        "blocks": blocks,
        "active_trains": active_trains,
        "commanded_speed": commanded_speed,
        "commanded_authority": commanded_authority,
        "train_occupancy": train_occupancy,
        "switch_positions": switch_positions,
        "light_states": light_states,
        "block_occupancy": block_occupancy,
        "track_direction": track_direction,
        "railway_crossing": railway_crossing,
        "heaters_work": heaters_work,
        "switch_locations": switch_locations,
        "light_location": light_location,
        "railway_location": railway_location,
        "station_location": station_location,
        "environmental_temp": environmental_temp if 'environmental_temp' in globals() else None,
        "failure_modes": failure_modes,
        "ticket_sales": ticket_sales,
        "passengers_boarding": passengers_boarding,
        "passengers_disembarking": passengers_disembarking,
    }
