import requests
import csv
import re
from threading import Thread
import os
import pandas as pd

"""!!! UWAGA !!! ustawić przed uruchomieniem skryptu !!! UWAGA !!!"""
"""Informacja, czy będziemy nadpisywać dane w pliku docelowych"""
do_override = True

class Point :
    """Klasa przechowująca informacje o danym punkcie i pobierająca dane o nim"""
    def __init__(self, name, debug = False) :
        if debug: print("Point:", name)
        self.name = name
        self._name = self.name
        self.response = None
        self.latitude = 0
        self.longitude = 0
        self.error = False
        self.getResponse()
        self.getCoordinates()

    def getResponse(self) :
        """Metoda wysyłająca i odbierająca requesta"""
        try :
            self.response = requests.get('https://nominatim.openstreetmap.org/search?q=' + self.name + '&format=json&viewbox=10.151367187500002,49.90171121726089,27.026367187500004,52.395715477302105')
        except :
            self.error = True

    def getCoordinates(self) :
        """Uzyskiwanie informacji o współrzędnych geograficznych na podstawie odpowiedzi na zapytanie"""
        try :
            self.latitude = self.response.json()[0]['lat']
            self.longitude = self.response.json()[0]['lon']
        except :
            self.error = True
            self.longitude = 0
            self.latitude = 0

    def get_coordinates(self):
        """Metoda do uzyskania odpowiedzi dla nieidealnego sposobu zapisu adresu - podejmuje różne próby jego modyfikacji"""
        if self.error:
            self.name = "New York," + self._name
            self.getResponse()
            self.getCoordinates()
            validate(self)
        if self.error:
            adresses = re.split(",|;|E ", self._name)
            for adress in adresses:
                self.name = "New York," + adress
                self.getResponse()
                self.getCoordinates()
                validate(self)
                if not self.error:
                    break

def find_indexes(filepath):
    """Funckja do uzyskania indeksów kolumn, w których występuje adres"""
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
            
def validate(point):
    """Walidacja poprawności znalezionych współrzędnych, czy mieszczą się w odległości ok 1000km od Nowego Jorku"""
    if point.latitude == None or point.longitude == None:
        point.error = True
    elif abs(float(point.latitude) - 40) > 7.0 or abs(float(point.longitude) + 73) > 7.0:
        point.error, point.latitude, point.longitude = True, None, None
    else:
        point.error = False

def get_point_coordinates(point_adress):
    """Funkcja do znajdowania współrzędnych punktu o niejednoznacznym adresie (analogiczna do metody get_coordinates)"""
    point = Point(point_adress)
    if not point.error:
        validate(point)
        return point
    point = Point("New York," + point_adress)
    if not point.error:
        validate(point)
        return point
    adresses = re.split(",|;|E ", point_adress)
    for adress in adresses:
        point = Point("New York," + adress)
        if not point.error:
            validate(point)
            return point
    validate(point)
    return point

def find_rows_number(filepath):
    """Określanie liczby rzędów w pliku"""
    try:
        with open(filepath) as f:
            n = sum(1 for _ in f)
        return n
    except:
        return 0

def convert_row(row, i, indexes):
    """Funkcja do konwersji całego rzędu danych"""
    converted_row, do_add = [], True
    if i > 0:
        j = 0
        for data in row:
            if j in indexes:
                point = get_point_coordinates(data)
                converted_row.append(point.latitude)
                converted_row.append(point.longitude)
            else:
                converted_row.append(data)
            j += 1
    return converted_row, do_add

def convert_row_with_point(row, i, indexes, point):
    """Funkcja konwertująca zawartość jednego rzędu danych, gdy jest już zadany punkt reprezentujący adres w tym rzędzie"""
    converted_row, do_add = [], True
    if i > 0:
        j = 0
        for data in row:
            if j in indexes:
                converted_row.append(point.latitude)
                converted_row.append(point.longitude)
            else:
                converted_row.append(data)
            j += 1
    return converted_row, do_add

def get_point(row, i, indexes):
    """Stworzenie punktu dla danego rzędu"""
    if i > 0:
        j = 0
        for data in row:
            if j in indexes:
                point = Point(data)
            j += 1
    return point

def convert_csv_file(sourcepath, destpath, from_row, to_row, override = do_override):
    """Normalna, synchroniczna konwersja jendego pliku .csv"""
    """from_row - numer wiersza od które zaczynamy konwersję"""
    """to_row - numer wiersza, na których zatrzymuejmy konwersję"""
    """overrride - flaga reprezentująca informację nadpisujemy stary plik wynikowy"""
    converted_rows = []
    n, dest_n, max_n = find_rows_number(sourcepath), find_rows_number(destpath), to_row         
    indexes, converted_row = find_indexes(sourcepath)
    converted_rows.append(converted_row)
    if override:  from_row = dest_n
    with open(sourcepath) as csvfile:
        rows, i, do_add = csv.reader(csvfile, delimiter=',', quotechar='\"'), 0, True
        for row in rows:
            if i == max_n: 
                break
            if i > from_row:
                converted_row, do_add = convert_row(row, i, indexes)
                if do_add: converted_rows.append(converted_row)
            i += 1
            print(sourcepath, 100.0 * (i + 1) / min(n+1, max_n+1), "%")
    write_to_csv_file(destpath, converted_rows, do_override)

def create_for_csv_file(sourcepath, destpath, from_row, to_row, override = do_override):
    """Funckja, która najpierw tworzy wszystkie punkty, o które chcemy zapytać, a następnie odpytuje o nie Open Street Map, na koniec następuje konwersja danych"""
    points, converted_rows = [], []
    n, dest_n, max_n = find_rows_number(sourcepath), find_rows_number(destpath), to_row         
    indexes, converted_row = find_indexes(sourcepath)
    converted_rows.append(converted_row)
    if override: from_row = dest_n
    with open(sourcepath) as csvfile:
        rows, i, do_add = csv.reader(csvfile, delimiter=',', quotechar='\"'), 0, True
        for row in rows:
            if i == max_n: 
                break
            if i > from_row:
                points.append(get_point(row, i, indexes))
            i += 1
    ########Mamy wszystkie punkty, o które chcemy pytać, zapytanie polega na uruchomieniu point.get_coordinates()########
    # TODO
    #####################################################################################################################
    for point in points:
        point.get_coordinates()
    idx = 0
    with open(sourcepath) as csvfile:
        rows, i, do_add = csv.reader(csvfile, delimiter=',', quotechar='\"'), 0, True
        for row in rows:
            if i == max_n: 
                break
            if i > from_row:
                converted_row, do_add = convert_row_with_point(row, i, indexes, points[idx])
                if do_add: 
                    converted_rows.append(converted_row)
                    idx += 1
            i += 1
    write_to_csv_file(destpath, converted_rows, do_override)

def create_for_csv_file_pandas(sourcepath, destpath, from_row, to_row, override = do_override):
    """Funckja, która najpierw tworzy wszystkie punkty, o które chcemy zapytać, a następnie odpytuje o nie Open Street Map, na koniec następuje konwersja danych"""
    """!!! UWAGA !!! Funkcja nadaje się wyłącznie do nadpisywania danych znajdujących sie w pliku docelowym !!! UWAGA !!!"""
    df, points = pd.read_csv(sourcepath), []
    dest_n, max_n = find_rows_number(destpath), to_row         
    indexes, _ = find_indexes(sourcepath)
    name = df.columns[indexes[0]]
    if not override: from_row = dest_n
    print(df[name].values[from_row:max_n])
    for adres in df[name].values[from_row:max_n]:
        points.append(Point(adres))
    ########Mamy wszystkie punkty, o które chcemy pytać, zapytanie polega na uruchomieniu point.get_coordinates()########
    # TODO
    #####################################################################################################################
    for point in points:
        point.get_coordinates()
    longitudes = [0] * len(df.index)
    latitudes = [0] * len(df.index)
    for i in range(from_row, max_n):
        longitudes[i] = points[i-from_row].longitude
        latitudes[i] = points[i-from_row].latitude
    df[name+"_longitude"] = longitudes
    df[name+"_latitude"] = latitudes
    df[from_row:max_n].to_csv(destpath)


def convert_files(filenames, sourcepath = "..\\data\\data_refactored\\", destpath = "..\\data\\converted\\", from_row = 0, to_row = 1000000):
    """Funkcja tworząca osobne wątki dla konwersji każdego z plików"""
    threads = []
    for filename in filenames:
        threads.append(Thread(target=convert_csv_file, args=[sourcepath + filename, destpath + filename, from_row, to_row]))
        threads[-1].start()
    for thread in threads:
        thread.join()

def list_directory(dirpath):
    """Funkja pomocnicza zwracająca zawartość katalogu"""
    return os.listdir(dirpath)

def convert_all_files_in_directory(sourcepath = "..\\data\\data_refactored\\", destpath = "..\\data\\converted\\"):
    """Funkcja konwertuje wszystkie pliki w katalogu, UWAGA nie sprawdza, czy plik ma rozrzerzenie .csv"""
    filenames = list_directory(sourcepath)
    convert_files(filenames, sourcepath = sourcepath, destpath = destpath)

def write_to_csv_file(filepath, rows, override):
    """Funkcja do zapisu danych odczytanych z plików od pliku o rozszerzeniu .csv"""
    print("Writing to csv file:", filepath)
    n = find_rows_number(filepath)
    if not override and n > 0:
        with open(filepath, 'a', newline='') as file:
            writer = csv.writer(file)
            for row in rows[1:]:
                writer.writerow(row)
    else:
        with open(filepath, 'w', newline='') as file:
            writer = csv.writer(file)
            for row in rows:
                writer.writerow(row) 

def preprocess(filepath = "..\\data\\data_refactored\\other-Dial7_B00887.csv"):
    """Funkcja pomocnicza, zastosowana do preprocesingu danych z pliku other-Dial7_B00887.csv w celu połączenia kolumn reprezentujących adres w jedną"""
    preprocessed_rows = []
    with open(filepath) as csvfile:
        rows = csv.reader(csvfile, delimiter=',', quotechar='\"')
        for row in rows:
            new_row = []
            new_row.extend(row[0:3])
            new_row.append(str(row[3])+" "+str(row[4])+" "+str(row[5]))
            new_row.extend(row[6:])
            preprocessed_rows.append(new_row)
    with open(filepath[:-4]+"_preprocesses"+filepath[-4:], 'w', newline='') as file:
        writer = csv.writer(file)
        for row in preprocessed_rows:
            writer.writerow(row) 


if __name__ == "__main__":
    """Test Open Street Map"""
    # point = Point("New York, LOVE CORP CAR INC")
    # print(point.latitude, point.longitude)

    """Konwersja pojedynczego pliku"""
    # convert_csv_file(measurement, "..\\data\\data_refactored\other-Federal_02216.csv", "..\\data\\converted\\other-Federal_02216.csv")
    
    """Konwersja wielu plików"""
    # convert_files(["other-American_B01362.csv", "other-Carmel_B00256.csv", "other-Dial7_B00887_preprocesses.csv"], from_row=0, to_row=10)
    
    """Test konwersji z wyszczególnieniem listy punktów"""
    # create_for_csv_file("..\\data\\data_refactored\other-American_B01362.csv", "..\\data\\converted\\other-American_B01362.csv", from_row=0, to_row=10, override = do_override)
    
    """Test konwersji z wyszczególnieniem listy punktów z wykorzystaniem biblioteki pandas"""
    create_for_csv_file_pandas("..\\data\\data_refactored\other-American_B01362.csv", "..\\data\\converted\\other-American_B01362.csv", from_row=0, to_row=10, override = do_override)

    """Preprocessing plików"""
    # preprocess()

    """Konwersja wszystkich plików w katalogu"""
    # convert_all_files_in_directory(measurement)

