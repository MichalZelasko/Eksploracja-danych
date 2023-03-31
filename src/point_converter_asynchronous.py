import requests
import csv
import re
import time
import aiohttp
import asyncio

class Measurements:
    def __init__(self):
        self.s = 0
        self.s_max = 0

class Point :
    def __init__(self, names, debug = False) :
        if debug: print("Point:", names)
        self.names = names
        self.response = None
        self.latitude = 0
        self.longitude = 0
        self.error = False
        self.urls = []
        self.responses = []
        self.getURLs()
        # self.getResponse()
        # self.getCoordinates()

    def getURLs(self) :
        for name in self.names:
            self.urls.append('https://nominatim.openstreetmap.org/search?q=' + name + '&format=json&viewbox=10.151367187500002,49.90171121726089,27.026367187500004,52.395715477302105')

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

def get_point(point_adress):
    adresses = []
    adresses.append(point_adress)
    adresses.append("New York," + point_adress)
    point_adresses = re.split(",|;", point_adress)
    for adress in point_adresses:
        adresses.append("New York," + adress)
    point = Point(adresses)
    return point

def find_rows_number(filepath):
    with open(filepath) as f:
        n = sum(1 for _ in f)
    return n

def next_point(row, i, indexes):
    if i > 0:
        j = 0
        for data in row:
            if j in indexes:
                point = get_point(data)
                return point
            j += 1


def create_points(row, i, indexes):
    points = []
    if i > 0:
        j = 0
        for data in row:
            if j in indexes:
                points.append(next_point(data, i, indexes))
            j += 1
    return points

async def make_requests(points):
    current = 0
    async with aiohttp.ClientSession() as session:
        for point in points:
            for url in point.urls:
                async with session.get(url) as resp:
                    current += 1
                    print(current)
                    response = await resp.json()
                    point.responses.append(response)

async def get_coordinates(session, url):
    async with session.get(url) as resp:
        try:
            response = await resp.json()
        except:
            print(f"incorrect response for {url}")
            response = "error"
        return response

async def make_requests_gathered(points):
    async with aiohttp.ClientSession() as session:

        tasks = []
        for point in points:
            for url in point.urls:
                print(url)
                tasks.append(asyncio.ensure_future(get_coordinates(session, url)))

        responses = await asyncio.gather(*tasks)
        print(len(responses))

def make_requests_synchronous(points):
    for point in points:
        for url in point.urls:
            requests.get(url)


def convert_csv_file(sourcepath, destpath):
    converted_rows, points = [], []
    n, max_n = find_rows_number(sourcepath), 3          
    indexes, converted_row = find_indexes(sourcepath)
    converted_rows.append(converted_row)
    with open(sourcepath) as csvfile:
        rows = csv.reader(csvfile, delimiter=',', quotechar='\"')
        i = 0
        for row in rows:
            if i == max_n: break
            points.extend(create_points(row, i, indexes))
            i += 1
    asyncio.run(make_requests_gathered(points))
    # make_requests_synchronous(points)
    for point in points:
        print(len(point.responses))
    # write_to_csv_file(destpath, converted_rows)

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
    convert_csv_file("..\\data\\archive\\other-Federal_02216.csv", None)
    print("Measured time:", time.time() - t)