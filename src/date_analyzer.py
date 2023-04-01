import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

"""Stałe pomocnicze"""
month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
month_length = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
week_day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def analyze_dataframe(filename, sourcepath = "..\\data\\data_refactored\\"):
    """Odczyt danych z pliku, selekcja kolumn, uruchomienie analizy"""
    filepath = sourcepath+filename
    df = pd.read_csv(filepath)
    year = df["Year"]
    month = df["Month"]
    day = df["Day"]
    day_name = df["Day_Name"]
    minutes = df["Minutes"]
    draw_month_chart(filename, month, year[0])
    draw_week_day_charts(filename, day_name, month, year[0])
    draw_time_charts(filename, minutes, month, day_name, year[0])
    draw_day_chart(filename, day, month, year[0])

def validate_data_barplot(counts):
    """Sprawdzenie czy dane dla barplot nie są puste"""
    return sum(counts) > 0  

def validate_data_histogram(data):
    """Sprawdzenie czy dane dla histogramu nie są puste"""
    return len(data) > 0  

def print_analyzing_dataframe(unique, counts):
    """Wydrukowanie na ekran zawartości dataframe'u o zadanych etykietach i jednym rzędzie danych"""
    counts_dict, s = {}, sum(counts)
    for i in range(len(counts)):
        counts_dict[unique[i]] = [counts[i] / s]
    dataframe = pd.DataFrame(data=counts_dict, columns=unique)
    print(dataframe)
    return dataframe

def draw_month_chart(filename, month, year = 2014):
    """Wizualizacji danych odnośnie intensywności wykorzystania ubera w poszczególnych miesiącach"""
    names, pickup_number = month_names, [0] * 12
    unique, counts = np.unique(month, return_counts=True)
    for u, c in zip(unique, counts): pickup_number[u-1] = c
    if validate_data_barplot(pickup_number):
        print_analyzing_dataframe(month_names, pickup_number)
        plt.bar(np.arange(12), pickup_number)
        plt.figure(figsize=(16, 16), dpi=80)
        plt.xticks(np.arange(12), names)
        plt.title(f"Pick up number per month\n{filename}\nyear = {year}")
        plt.xlabel("Month")
        plt.ylabel("Pick up number")
        plt.show()

def draw_week_day_chart(filename, day_name, extra_info = ""):
    """Wizualizacji danych odnośnie intensywności wykorzystania ubera w poszczególnych dniach tygodnia"""
    names, pickup_number = week_day_names, [0] * 7
    unique, counts = np.unique(day_name, return_counts=True)
    for u, c in zip(unique, counts): pickup_number[names.index(u)] = c
    if validate_data_barplot(pickup_number):
        dataframe = print_analyzing_dataframe(week_day_names, pickup_number)
        plt.bar(np.arange(7), pickup_number)
        plt.figure(figsize=(16, 16), dpi=80)
        plt.xticks(np.arange(7), names)
        plt.title(f"Pick up number per week day {extra_info}\n{filename}")
        plt.xlabel("Week day")
        plt.ylabel("Pick up number")
        plt.show()
        return dataframe
    else:
        return pd.DataFrame(data=np.zeros(shape = (1, 7)), columns=week_day_names)    

def draw_week_day_charts(filename, day_name, month, year = 2014):
    """Wizualizacji danych odnośnie intensywności wykorzystania ubera w poszczególnych dniach tygodnia"""
    """Dla różnych przedziałach czasowych: cały rok, każdy miesią z osobna"""
    draw_week_day_chart(filename, day_name)
    dataframes = []
    for i in range(1, 13):
        dataframe = draw_week_day_chart(filename, day_name[month == i], extra_info=f"for {month_names[i - 1]}\nyear = {year}")
        dataframes.append(dataframe)
    print(pd.concat(dataframes))    

def draw_time_chart(filename, time, extra_info = ""):
    """Wizualizacja intensywności wykorzystania ubera w zależności od pory dnia"""
    if validate_data_histogram(time):
        plt.hist(time, bins = 96)
        plt.figure(figsize=(16, 16), dpi=80)
        plt.title(f"Pick up number per day time {extra_info}\n{filename}")
        plt.xlim((0, 1440))
        plt.xlabel("Time")
        plt.ylabel("Pick up intensity")
        plt.show()

def draw_time_charts(filename, time, month, day, year = 2014):
    """Wizualizacja intensywności wykorzystania ubera w zależności od pory dnia"""
    """Dla całego roku, różnych dni tygodnia i różnych miesięcy"""
    draw_time_chart(filename, time)
    for d in range(0, 7):
        draw_time_chart(filename, time[day == week_day_names[d]], f"for {week_day_names[d]}\nyear = {year}")
    for m in range(1, 13):
        time_selected = time[month == m]
        day_selected = day[month == m]
        draw_time_chart(filename, time_selected, f"for {month_names[m - 1]}\nyear = {year}")
        for d in range(0, 7):
            draw_time_chart(filename, time_selected[day_selected == week_day_names[d]], f"for {week_day_names[d]} in {month_names[m - 1]}\nyear = {year}")

def draw_day_chart(filename, day, month, year = 2014):
    """Wizualizacja intensywności wykorzystania ubera w zależności od dnia miesiąca"""
    """Osobno dla każdego z miesięcy"""
    for m in range(1, 13):
        day_selected = day[month == m]
        if validate_data_histogram(day_selected):
            plt.hist(day_selected, bins=month_length[m - 1])
            plt.figure(figsize=(16, 16), dpi=80)
            plt.title(f"Pick up number per day in {month_names[m - 1]}\n{filename}\nyear = {year}")
            plt.xlim((0, month_length[m - 1]))
            plt.xlabel("Day")
            plt.ylabel("Pick up intensity")
            plt.show()

if __name__ == "__main__":
    analyze_dataframe("uber-raw-data-15.csv")