import csv
from math import *
import tkinter as tk
from tkinter import filedialog, messagebox

#Uses the haversine formula to calculate the distance between two points
def haversine(lat1, lat2, lon1, lon2):
    lat1 = float(lat1)
    lat2 = float(lat2)
    lon1 = float(lon1)
    lon2 = float(lon2)
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dLat = lat2 - lat1
    dLon = lon2 - lon1
    a = sin(dLat/2)**2 + cos(lat1) * cos(lat2) * sin(dLon/2)**2
    c = 2 * asin(sqrt(a))
    r = 3959.87433
    return(c * r)

#Prints Extracted CSV data
def printData(lat, lon, wifiChannel):
    print("Lat: ", lat)
    print("Lon: ", lon)
    print("WiFi Channel: ", wifiChannel)

#Prints Dictionary
def printDict(dict):
    for key, value in dict.items():
        print(f"{key}: {value}\n")

#Calculates the 3 closest points to each point
def calculateClosestPoints(lat, lon, wifiChannel, topThree):
    for i in range(len(lat)):
        distances = []
        for j in range(len(lat)):
            if i != j:
                distance = haversine(lat[i], lat[j], lon[i], lon[j])
                same_channel = wifiChannel[i] == wifiChannel[j]
                distances.append((j, distance, same_channel))
        #sorts based on the distance values
        distances.sort(key=lambda x: x[1])
        topThree[i] = [(lat[index], lon[index], dist, same_channel) for index, dist, same_channel in distances[:3]]
    return None

#Reads from CSV file
def readCSV(filePath):
    fileName = open(filePath, 'r')
    
    file = csv.DictReader(fileName)

    lat = []
    lon = []
    wifiChannel = []
    topThree = {}  

    for col in file:
        lat.append(col['Lat'])
        lon.append(col['Lon'])
        wifiChannel.append(col['WiFi Channel'])
    
    return(lat, lon, wifiChannel, topThree)

#Writes to CSV file
def writeCSV(dict):
    fields = ['Lat1', 'Lon1', 'Distance1', 'Same Channel 1', 
              'Lat2', 'Lon2', 'Distance2', 'Same Channel 2', 
              'Lat3', 'Lon3', 'Distance3', 'Same Channel 3']
    with open('ClosestPoints.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for key, value in dict.items():
            row = []
            for item in value:
                row.extend([item[0], item[1], item[2], item[3]])
            writer.writerow(row)

def importCSV():
    filePath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if filePath:
        global lat, lon, wifiChannel, topThree
        lat, lon, wifiChannel, topThree = readCSV(filePath)
        messagebox.showinfo("Import Successful", "CSV file imported successfully!")

def runCalculation():
    global lat, lon, wifiChannel, topThree
    calculateClosestPoints(lat, lon, wifiChannel, topThree)
    writeCSV(topThree)
    printDict(topThree)
    messagebox.showinfo("Calculation Complete", "Closest points calculated and saved to ClosestPoints.csv!")

# GUI setup
root = tk.Tk()
root.title("CSV Processing GUI")

import_btn = tk.Button(root, text="Import CSV", command=importCSV)
import_btn.pack(pady=10)

calc_btn = tk.Button(root, text="Calculate Closest Points", command=runCalculation)
calc_btn.pack(pady=10)

root.mainloop()


