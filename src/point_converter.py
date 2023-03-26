import requests
import csv
import re
from threading import Thread
import os
import time

class Measurements:
    def __init__(self):
        self.s = 0
        self.s_max = 0

class Point :
    def __init__(self, name, debug = False) :
        if debug: print("Point:", name)
        self.name = name
        self.response = None
        self.latitude = 0
        self.longitude = 0
        self.error = False
        self.getResponse()
        self.getCoordinates()

    def getResponse(self) :
        try :
            self.response = requests.get('https://nominatim.openstreetmap.org/search?q=' + self.name + '&format=json&viewbox=10.151367187500002,49.90171121726089,27.026367187500004,52.395715477302105')
        except :
            self.error = True

    def getCoordinates(self) :
        if not self.error :
            try :
                self.latitude = self.response.json()[0]['lat']
                self.longitude = self.response.json()[0]['lon']
            except :
                self.error = True
        if float(self.latitude) > 45.0 or float(self.latitude) < 35.0 or float(self.longitude) > -67.5 or float(self.longitude) < -77.5: self.error = True

def find_indexes(filepath):
    with open(filepath) as csvfile:
        rows = csv.reader(csvfile, delimiter=',', quotechar='\"')
        i, index, indexes = 0, 0, []
        for row in rows:
            converted_row = []
            if i == 0:
                for name in row:
                    if "address" in name.lower() or "adress" in name.lower() or "PuFrom" in name or "Base Name" in name:
                        indexes.append(index)
                        converted_row.append(name + "_latitude")
                        converted_row.append(name + "_longitude")
                    else:
                        converted_row.append(name)
                    index += 1
                return indexes, converted_row

def get_point_coordinates(point_adress):
    point = Point(point_adress)
    if not point.error:
        return point
    point = Point("New York," + point_adress)
    if not point.error:
        return point
    adresses = re.split(",|;", point_adress)
    for adress in adresses:
        point = Point("New York," + adress)
        if not point.error:
            return point
    return point

def find_rows_number(filepath):
    with open(filepath) as f:
        n = sum(1 for _ in f)
    return n

def convert_row(row, i, indexes):
    converted_row, do_add = [], True
    if i > 0:
        j = 0
        for data in row:
            if j in indexes:
                point = get_point_coordinates(data)
                if point.error:
                    do_add = False
                else:
                    converted_row.append(point.latitude)
                    converted_row.append(point.longitude)
            else:
                converted_row.append(data)
            j += 1
    return converted_row, do_add

def convert_csv_file(measurement, sourcepath, destpath, ):
    converted_rows = []
    n, max_n = find_rows_number(sourcepath), 10
    if not ("uber" in sourcepath or "Lyft" in sourcepath): 
        if "Federal" in sourcepath:
            measurement.s += (3 * n)
        else:    
            measurement.s += n
    if not ("uber" in sourcepath or "Lyft" in sourcepath): 
        if "Federal" in sourcepath:
            measurement.s_max += (3 * min(n, max_n+1))
        else:    
            measurement.s_max += min(n, max_n+1)            
    indexes, converted_row = find_indexes(sourcepath)
    converted_rows.append(converted_row)
    with open(sourcepath) as csvfile:
        rows = csv.reader(csvfile, delimiter=',', quotechar='\"')
        i, do_add = 0, True
        for row in rows:
            if i == max_n: break
            converted_row, do_add = convert_row(row, i, indexes)
            i += 1
            if do_add: converted_rows.append(converted_row)
            print(sourcepath, 100.0 * (i + 1) / min(n, max_n+1), "%")
    write_to_csv_file(destpath, converted_rows)

def convert_files(measurement, filenames, sourcepath = "..\\data\\archive\\", destpath = "..\\data\\converted\\"):
    threads = []
    for filename in filenames:
        threads.append(Thread(target=convert_csv_file, args=[measurement, sourcepath + filename, destpath + filename]))
        threads[-1].start()
    for thread in threads:
        thread.join()

def list_directory(dirpath):
    return os.listdir(dirpath)

def convert_all_files_in_directory(measurement, sourcepath = "..\\data\\data_refactored\\", destpath = "..\\data\\converted\\"):
    filenames = list_directory(sourcepath)
    convert_files(measurement, filenames, sourcepath = sourcepath, destpath = destpath)

def write_to_csv_file(filepath, rows):
    print("Writing to csv file:", filepath)
    with open(filepath, 'w', newline='') as file:
        writer = csv.writer(file)
        for row in rows:
            writer.writerow(row)

if __name__ == "__main__":
    # point = Point("New York, LOVE CORP CAR INC")
    # print(point.latitude, point.longitude)

    # convert_csv_file("..\\data\\archive\\other-Federal_02216.csv")

    # convert_files(["other-American_B01362.csv", "other-Carmel_B00256.csv", "other-Federal_02216.csv", "other-Dial7_B00887"])

    measurement = Measurements()
    t = time.time()
    convert_all_files_in_directory(measurement)
    print(100.0 * measurement.s_max / measurement.s, "%")
    print("Measured time:", time.time() - t)
    print("Expected time:", (time.time() - t) * measurement.s / measurement.s_max)

