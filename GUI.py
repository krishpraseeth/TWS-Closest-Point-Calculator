import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
import folium
import pandas as pd
import geopandas
import webbrowser
from selenium import webdriver
from PIL import Image
import time
import os
import csv
from math import radians, sin, cos, sqrt, asin
from Cleaner import runCalculation, importCSV, writeCSV, readCSV, calculateClosestPoints, haversine
from MapGenerator import readSiteInfo, readPathInfo, createMap, addSiteMarkers, addPathMarkers, fitMapBounds, openMap, saveMapAsImage


# Application 1: Map Generator
class MapGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Map Generator")
        self.root.configure(bg='#5083a0')
        self.siteFilePath = ""
        self.pathFilePath = ""
        self.site_color = 'red'
        self.path_color = 'black'
        self.create_widgets()

    def create_widgets(self):
        img = tk.PhotoImage(file="logo.png")
        img_label = ttk.Label(self.root, image=img, background='#5083a0')
        img_label.image = img
        img_label.pack(pady=10)

        frame = ttk.Frame(self.root, padding="20", style='TFrame')
        frame.pack(padx=10, pady=10, fill='x', expand=True)

        import_site_btn = ttk.Button(frame, text="Select Site Info File", command=self.select_site_file, style='TButton')
        import_site_btn.pack(pady=10, fill='x')

        import_path_btn = ttk.Button(frame, text="Select Path Info File", command=self.select_path_file, style='TButton')
        import_path_btn.pack(pady=10, fill='x')

        # select_site_color_btn = ttk.Button(frame, text="Select Site Marker Color", command=self.select_site_color, style='TButton')
        # select_site_color_btn.pack(pady=10, fill='x')

        select_path_color_btn = ttk.Button(frame, text="Select Path Dot Color", command=self.select_path_color, style='TButton')
        select_path_color_btn.pack(pady=10, fill='x')

        self.file_label = ttk.Label(frame, text="No files selected", style='TLabel')
        self.file_label.pack(padx=50, pady=10, fill='x')

        # create_map_btn = ttk.Button(frame, text="Create Map", command=self.create_map, style='TButton')
        # create_map_btn.pack(pady=10, fill='x')

        save_image_btn = ttk.Button(frame, text="Save Map as Image", command=self.save_map_as_image, style='TButton')
        save_image_btn.pack(pady=10, fill='x')

    def select_site_file(self):
        self.siteFilePath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if self.siteFilePath:
            self.update_file_label()
            messagebox.showinfo("Selected File", f"Site info file selected: {self.siteFilePath}")

    def select_path_file(self):
        self.pathFilePath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if self.pathFilePath:
            self.update_file_label()
            messagebox.showinfo("Selected File", f"Path info file selected: {self.pathFilePath}")

    def update_file_label(self):
        site_file = self.siteFilePath.split('/')[-1] if self.siteFilePath else "None"
        path_file = self.pathFilePath.split('/')[-1] if self.pathFilePath else "None"
        self.file_label.config(text=f"Site File: {site_file}\n Path File: {path_file}")

    def select_site_color(self):
        color_code = colorchooser.askcolor(title="Choose Site Marker Color")[1]
        if color_code:
            self.site_color = color_code

    def select_path_color(self):
        color_code = colorchooser.askcolor(title="Choose Path Dot Color")[1]
        if color_code:
            self.path_color = color_code

    def create_map(self):
        if not self.siteFilePath or not self.pathFilePath:
            messagebox.showwarning("Warning", "Please select both site info and path info files")
            return

        try:
            geoSiteList, geoSiteDF = readSiteInfo(self.siteFilePath)
            geoPathList, geoPathDF = readPathInfo(self.pathFilePath)

            map = createMap(geoSiteList)
            addSiteMarkers(geoSiteList, geoSiteDF, map, site_color=self.site_color)
            addPathMarkers(geoPathList, map, path_color=self.path_color)
            fitMapBounds(map, geoSiteList, geoPathList)
            openMap(map)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def save_map_as_image(self):
        if not self.siteFilePath or not self.pathFilePath:
            messagebox.showwarning("Warning", "Please select both site info and path info files")
            return

        try:
            geoSiteList, geoSiteDF = readSiteInfo(self.siteFilePath)
            geoPathList, geoPathDF = readPathInfo(self.pathFilePath)

            map = createMap(geoSiteList)
            addSiteMarkers(geoSiteList, geoSiteDF, map, site_color=self.site_color)
            addPathMarkers(geoPathList, map, path_color=self.path_color)
            fitMapBounds(map, geoSiteList, geoPathList)
            saveMapAsImage(map)
            messagebox.showinfo("Save Complete", "Map has been saved as map.png")
        except ValueError as e:
            messagebox.showerror("Error", str(e))


# Application 2: CSV Processing
class CSVProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Processing GUI")
        self.root.configure(bg='#5083a0')
        self.create_widgets()

    def create_widgets(self):
        img = tk.PhotoImage(file="logo.png")
        img_label = ttk.Label(self.root, image=img, background='#5083a0')
        img_label.image = img
        img_label.pack(pady=10)

        frame = ttk.Frame(self.root, padding="20", style='TFrame')
        frame.pack(padx=10, pady=10, fill='x', expand=True)

        import_btn = ttk.Button(frame, text="Import CSV", command=self.importCSV, style='TButton')
        import_btn.pack(pady=10, fill='x')

        self.file_label = ttk.Label(frame, text="No file selected", style='TLabel')
        self.file_label.pack(padx=50, pady=10, fill='x')

        calc_btn = ttk.Button(frame, text="Calculate Closest Points", command=self.runCalculation, style='TButton')
        calc_btn.pack(pady=10, fill='x')

    def importCSV(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                global lat, lon, wifiChannel, topThree
                lat, lon, wifiChannel, topThree = readCSV(file_path)
                if lat and lon and wifiChannel:
                    self.file_label.config(text=f"File: {file_path}")
                    messagebox.showinfo("Import Successful", "CSV file imported successfully!")
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def runCalculation(self):
        global lat, lon, wifiChannel, topThree
        try:
            calculateClosestPoints(lat, lon, wifiChannel, topThree)
            writeCSV(topThree)
        except:
            messagebox.showerror("Calculation Error", "Please input valid data")
        else:
            messagebox.showinfo("Calculation Complete", "Closest points calculated and saved to ClosestPoints.csv!")


# Main Application to switch between Map Generator and CSV Processing
class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Main Application")
        #self.root.geometry("400x300")
        self.root.configure(bg='#5083a0')
        self.create_widgets()

    def create_widgets(self):
        img = tk.PhotoImage(file="logo.png")
        img_label = ttk.Label(self.root, image=img, background='#5083a0')
        img_label.image = img
        img_label.pack(pady=10)

        self.frame = ttk.Frame(self.root, padding="20")
        self.frame.pack(padx=10, pady=10, fill='x', expand=True)

        map_gen_btn = ttk.Button(self.frame, text="Open Map Generator", command=self.open_map_generator, style='TButton')
        map_gen_btn.pack(pady=10, fill='x')

        csv_proc_btn = ttk.Button(self.frame, text="Open CSV Processing", command=self.open_csv_processing, style='TButton')
        csv_proc_btn.pack(pady=10, fill='x')

    def open_map_generator(self):
        new_window = tk.Toplevel(self.root)
        MapGeneratorApp(new_window)

    def open_csv_processing(self):
        new_window = tk.Toplevel(self.root)
        CSVProcessingApp(new_window)


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
