#importing relevant packages
from google.cloud import bigquery
from google.oauth2 import service_account
import geopandas as gpd
from shapely.ops import cascaded_union
from shapely import wkt
from shapely.geometry import Point
import pandas as pd
import numpy as np
import pickle
from haversine import haversine, Unit
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from haversine import haversine, Unit
import seaborn as sns
import matplotlib.pyplot as plt

def access_bigquery(credentials, project_id):
    return bigquery.Client(credentials= credentials, project=project_id)
    
def kmeans_clustering(data, cluster_number):
    #renaming some columns for better understandability
    data.rename(columns = {'d': 'district', 's': 'subcounty', 'p':'parish', 'pop':'population', 'hhs':'households'}, inplace = True)
    
    #dropping rows with null values
    data.dropna(axis=0, inplace=True)
    data = data.reset_index(drop=True)

    #selecting data to be used for modelling
    X = data[['long', 'lat', 'light_par_tadooba_per_km', 'light_firewood_per_km', 'light_cow_dung_per_km', 'light_grass_per_km', 
    'cook_charc_per_km', 'cook_firewood_per_km', 'cook_dung_per_km', 'cook_grass_per_km', 'waste_burn_per_km', 
    'kitch_outside_built_per_km', 'kitch_make_shift_per_km', 'kitch_open_space_per_km', 'pop_density', 'hhs_density', 
    'pop_per_hhs', 'T123_per_sqkm']]

    #performing standard scaling on input features
    X = StandardScaler().fit_transform(X)
    
    #running the kmeans model
    kmeans = KMeans(n_clusters=cluster_number).fit(X) 
    data['cluster'] = kmeans.fit_predict(X)

    #converting to a Geodataframe
    data['geometry'] = data['geometry'].apply(wkt.loads)
    data = gpd.GeoDataFrame(data, geometry = data['geometry'])

    #shuffling the data and choosing one parish per cluster
    select_data = data.sample(frac=1).reset_index(drop=True)
    select_data= select_data.drop_duplicates('cluster', keep = 'last')

    #generating map with sensor locations
    fig, ax = plt.subplots(figsize=(32, 32))
    chart_title =  'Selecting one sample per cluster' 
    plt.title(chart_title,fontsize=20)
    ax.set_aspect('equal')
    data.plot(column='cluster', ax=ax, legend=True)
    for i, txt in enumerate(data.parish):
        ax.annotate(txt, (data.long[i], data.lat[i]))
    plt.scatter(select_data.long, select_data.lat, s=600, c='k')
    #plt.show()
    fig.savefig(r'Static/initial-sensor-locations.png')

    #generating csv with sensor gps coodinates
    device_locations = select_data[['parish','lat', 'long']]
    #device_csv = device_locations.to_csv(r'device_locations.csv')
    device_json = device_locations.to_json()
    return device_json
    


