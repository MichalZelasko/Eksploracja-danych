import plotly.express as px
import pandas as pd
dictionary = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6, "Sunday": 7}

def visualize_month(m = 10000, filepath = "..\\data\\data_refactored\\uber-raw-data-14.csv", latit = "Lat", longi = "Lon"):
    """Zwizualizowanie rozłożenie zamówień według miesięcy"""
    """Pokazuje m punktów (domyślnie 10000), wybierane są one równomiernie z całego zbioru"""
    df = pd.read_csv(filepath)
    n = len(df) // m
    df = df.iloc[::n, :]
    fig = px.scatter_mapbox(df, lat=latit, lon=longi, color="Month", size="Year",
                      color_continuous_scale=px.colors.cyclical.IceFire, size_max=3, zoom=10,
                      mapbox_style="carto-positron")
    fig.show()

def visualize_week_day(m = 10000, filepath = "..\\data\\data_refactored\\uber-raw-data-14.csv", latit = "Lat", longi = "Lon"):
    """Zwizualizowanie rozłożenie zamówień według dni tygodnia"""
    """Pokazuje m punktów (domyślnie 10000), wybierane są one równomiernie z całego zbioru"""
    df = pd.read_csv(filepath)
    n = len(df) // m
    df = df.iloc[::n, :]
    df.replace({"Day_Name": dictionary})
    fig = px.scatter_mapbox(df, lat=latit, lon=longi, color="Day_Name", size="Year",
                      color_continuous_scale=px.colors.cyclical.IceFire, size_max=3, zoom=10,
                      mapbox_style="carto-positron")
    fig.show()

def visualize_by_time(dest_month, dest_day_name, filepath = "..\\data\\data_refactored\\uber-raw-data-14.csv", m = 10000, latit = "Lat", longi = "Lon"):
    """Zwizualizowanie rozłożenie zamówień według pory dnia"""
    """Pokazuje m punktów (domyślnie 10000), wybierane są one równomiernie z całego zbioru"""
    df = pd.read_csv(filepath)
    if dest_month: df = df[df["Month"] == dest_month]
    if dest_day_name: df = df[df["Day_Name"] == dest_day_name]
    n = len(df) // m
    df = df.iloc[::n, :]
    df.replace({"Day_Name": dictionary})
    fig = px.scatter_mapbox(df, lat=latit, lon=longi, color="Minutes", size="Year",
                      color_continuous_scale=px.colors.cyclical.IceFire, size_max=3, zoom=10,
                      mapbox_style="carto-positron")
    fig.show()

# uber-raw-data-14.csv

## Pickups in each month
visualize_month()

## Pickups per week day
visualize_week_day()

## Pickups for day time

### September Monday
dest_month = 9
dest_day_name = "Monday"

visualize_by_time(dest_month, dest_day_name)

### June Tuesday
dest_month = 6
dest_day_name = "Tuesday"

visualize_by_time(dest_month, dest_day_name)

### July, Saturday 
dest_month = 7
dest_day_name = "Saturday"

visualize_by_time(dest_month, dest_day_name)

### July, Sunday
dest_month = 7
dest_day_name = "Sunday"

visualize_by_time(dest_month, dest_day_name)

# other-Lyft_B02510.csv

## Pickups in each month
visualize_month(filepath = "..\\data\\data_refactored\\other-Lyft_B02510.csv", latit = "start_lat", longi = "start_lng")

## Pickups per week days
visualize_week_day(filepath = "..\\data\\data_refactored\\other-Lyft_B02510.csv", latit = "start_lat", longi = "start_lng")

## Pickups per daytime
### August Monday
dest_month = 8
dest_day_name = "Monday"

visualize_by_time(dest_month, dest_day_name, filepath = "..\\data\\data_refactored\\other-Lyft_B02510.csv", latit = "start_lat", longi = "start_lng")

### August Saturday
dest_month = 8
dest_day_name = "Saturday"

visualize_by_time(dest_month, dest_day_name, filepath = "..\\data\\data_refactored\\other-Lyft_B02510.csv", latit = "start_lat", longi = "start_lng")

### August Sunday
dest_month = 8
dest_day_name = "Sunday"

visualize_by_time(dest_month, dest_day_name, filepath = "..\\data\\data_refactored\\other-Lyft_B02510.csv", latit = "start_lat", longi = "start_lng")

### September Wednesday
dest_month = 9
dest_day_name = "Wednesday"

visualize_by_time(dest_month, dest_day_name, filepath = "..\\data\\data_refactored\\other-Lyft_B02510.csv", latit = "start_lat", longi = "start_lng")

### September Friday
dest_month = 9
dest_day_name = "Friday"

visualize_by_time(dest_month, dest_day_name, filepath = "..\\data\\data_refactored\\other-Lyft_B02510.csv", latit = "start_lat", longi = "start_lng")

### September Saturday
dest_month = 9
dest_day_name = "Friday"

visualize_by_time(dest_month, dest_day_name, filepath = "..\\data\\data_refactored\\other-Lyft_B02510.csv", latit = "start_lat", longi = "start_lng")

# other-Federal_02216.csv

## Pickups in each month

### Pickup points
df = pd.read_csv("..\\data\\converted\\other-Federal_02216.csv")
df["Month"] = df["Month"] - 6
fig = px.scatter_mapbox(df, lat="PU_Address_latitude", lon="PU_Address_longitude", color="Month", size="Year",
                  color_continuous_scale=px.colors.cyclical.IceFire, size_max=5, zoom=10,
                  mapbox_style="carto-positron")
fig.show()

### Dropout points
df = pd.read_csv("..\\data\\converted\\other-Federal_02216.csv")
df["Month"] = df["Month"] - 6
fig = px.scatter_mapbox(df, lat="DO_Address_latitude", lon="DO_Address_longitude", color="Month", size="Year",
                  color_continuous_scale=px.colors.cyclical.IceFire, size_max=5, zoom=10,
                  mapbox_style="carto-positron")
fig.show()


## Pickups in each week day

### Pickup points
df = pd.read_csv("..\\data\\converted\\other-Federal_02216.csv")
dictionary = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6, "Sunday": 7}
df.replace({"Day_Name": dictionary})
fig = px.scatter_mapbox(df, lat="PU_Address_latitude", lon="PU_Address_longitude", color="Day_Name", size="Year",
                  color_continuous_scale=px.colors.cyclical.IceFire, size_max=5, zoom=10,
                  mapbox_style="carto-positron")
fig.show()

### Dropout points
df = pd.read_csv("..\\data\\converted\\other-Federal_02216.csv")
dictionary = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6, "Sunday": 7}
df.replace({"Day_Name": dictionary})
fig = px.scatter_mapbox(df, lat="DO_Address_latitude", lon="DO_Address_longitude", color="Day_Name", size="Year",
                  color_continuous_scale=px.colors.cyclical.IceFire, size_max=5, zoom=10,
                  mapbox_style="carto-positron")
fig.show()

## Pickups in each day time
dest_month = None
dest_day_name = None

### Pickup points
df = pd.read_csv("..\\data\\converted\\other-Federal_02216.csv")
if dest_month: df = df[df["Month"] == dest_month]
if dest_day_name: df = df[df["Day_Name"] == dest_day_name]
dictionary = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6, "Sunday": 7}
df.replace({"Day_Name": dictionary})
fig = px.scatter_mapbox(df, lat="PU_Address_latitude", lon="PU_Address_longitude", color="Minutes", size="Year",
                  color_continuous_scale=px.colors.cyclical.IceFire, size_max=5, zoom=10,
                  mapbox_style="carto-positron")
fig.show()

### Dropout points
df = pd.read_csv("..\\data\\converted\\other-Federal_02216.csv")
if dest_month: df = df[df["Month"] == dest_month]
if dest_day_name: df = df[df["Day_Name"] == dest_day_name]
dictionary = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6, "Sunday": 7}
df.replace({"Day_Name": dictionary})
fig = px.scatter_mapbox(df, lat="DO_Address_latitude", lon="DO_Address_longitude", color="Minutes", size="Year",
                  color_continuous_scale=px.colors.cyclical.IceFire, size_max=5, zoom=10,
                  mapbox_style="carto-positron")
fig.show()