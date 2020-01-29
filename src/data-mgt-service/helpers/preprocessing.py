import pandas as pd
import datamanagement.datamanagement as dm
from datetime import datetime as dt


def preprocessing(data:pd.DataFrame):

    df = client.query(sql_query, job_config=job_config).to_dataframe()
    df['time'] =  pd.to_datetime(df['time'])
    df['time'] = df['time']
    df['s1_pm2_5'] = pd.to_numeric(df['s1_pm2_5'],errors='coerce')
    df['channel_id'] = pd.to_numeric(df['channel_id'],errors='coerce')
    df['s1_pm10'] = pd.to_numeric(df['s1_pm10'],errors='coerce')
    df['s2_pm2_5'] = pd.to_numeric(df['s2_pm2_5'],errors='coerce')
    df['s2_pm10'] = pd.to_numeric(df['s2_pm10'],errors='coerce')
    time_indexed_data = df.set_index('time')
    final_hourly_data = data.resample('H').mean().round(2) 
    return time_indexed_data
   
    #dropping rows with null values
    final_data=final_hourly_data.dropna()
   
    return final_data

def generate_hourly_observations_for_all_static_devices():
    """
        calculates the hourly observations for all the static channels.
    """
    all_channel_observations=[]
    specified_locations = dm.get_all_static_channels()

    if specified_locations[0:2]:
        for i in range(0, len(specified_locations)):
            channel_id = specified_locations[i].get('channel_id')
            latitude = specified_locations[i].get('latitude')
            longitude = specified_locations[i].get('longitude')
            created_at = dt.now()
            results = dm.get_raw_channel_data(channel_id)
            for j in range(len(results)) : 
                s1_pm2_5= results.loc[j, "s1_pm2_5"]
                s1_pm10= results.loc[j, "s1_pm10"]
                s2_pm2_5= results.loc[j, "s2_pm2_5"]
                s2_pm10= results.loc[j, "s2_pm10"] 
                time = results.loc[j, "time"]
                temperature = None
                humidity = None
                voltage = None
                observations_tuple = (channel_id, s1_pm2_5, s1_pm10,
                 s2_pm2_5, s2_pm10, temperature, humidity, latitude,
                  longitude, voltage, created_at, time)
            all_channel_observations.append(observations_tuple)

        dm.save_cleaned_hourly__data(all_channel_observations)
            
    return all_channel_observations


if __name__ == '__main__':
    
    print('main')
    values_saved = generate_hourly_observations_for_all_static_devices()
    print(values_saved)
    print('completed saving')
    
    