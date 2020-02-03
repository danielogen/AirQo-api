from google.cloud import bigquery
from datetime import datetime as dt
from datetime import datetime,timedelta
import pandas as pd


def get_channel_hourly_raw_data(channel_id:int):
    channel_id = str(channel_id)
    client = bigquery.Client()
    sql_query = """SELECT  DATETIME_TRUNC(SAFE_CAST(TIMESTAMP(created_at) as DATETIME), HOUR) time, channel_id, ROUND(AVG(SAFE_CAST(field1 as FLOAT64)),2) AS s1_pm2_5,ROUND(AVG(SAFE_CAST(field2 as FLOAT64)),2) AS s1_pm10, 
    ROUND(AVG(SAFE_CAST(field3 as FLOAT64)),2) AS s2_pm2_5,ROUND(AVG(SAFE_CAST(field4 as FLOAT64)),2) AS s2_pm10 FROM `airqo-250220.thingspeak.raw_feeds_pms` WHERE channel_id = {0} GROUP BY channel_id, time ORDER BY time """
    xx = "'" + channel_id + "'"
    sql_query = sql_query.format(xx)
    job_config = bigquery.QueryJobConfig()
    job_config.use_legacy_sql = False
    df = client.query(sql_query, job_config=job_config).to_dataframe()
    return df

def save_cleaned_hourly_data(cleaned_hourly_data):
    client = bigquery.Client()
    dataset_ref = client.dataset('thingspeak','airqo-250220')
    table_ref = dataset_ref.table('hourly_cleaned_feeds_pms')
    table = client.get_table(table_ref)

    rows_to_insert = cleaned_hourly_data
    errors = client.insert_rows(table, rows_to_insert)
    if errors == []:
        return 'Records saved successfully.'
    else:
        return errors

def get_raw_channel_data(channel_id:int):
    channel_id = str(channel_id)
    client = bigquery.Client()
    sql_query = """ 
           
            SELECT SAFE_CAST(TIMESTAMP(created_at) as DATETIME) as time, channel_id,field1 as s1_pm2_5,
            field2 as s1_pm10, field3 as s2_pm2_5, field4 s2_pm10, 
            FROM `airqo-250220.thingspeak.raw_feeds_pms` 
            WHERE channel_id = {0}  AND (SAFE_CAST(TIMESTAMP(created_at) as TIMESTAMP) 
            BETWEEN TIMESTAMP('2020-02-01T11:00:00') AND TIMESTAMP('2020-02-02T11:00:00'))
        """ #new_data_pms - needs to be transformed 
    xx = "'"+ channel_id + "'"
    sql_query = sql_query.format(xx)

    job_config = bigquery.QueryJobConfig()
    job_config.use_legacy_sql = False
     
    df = client.query(sql_query, job_config=job_config).to_dataframe()
    df['time'] =  pd.to_datetime(df['time'])
    df['time'] = df['time']
    df['s1_pm2_5'] = pd.to_numeric(df['s1_pm2_5'],errors='coerce')
    df['channel_id'] = pd.to_numeric(df['channel_id'],errors='coerce')
    df['s1_pm10'] = pd.to_numeric(df['s1_pm10'],errors='coerce')
    df['s2_pm2_5'] = pd.to_numeric(df['s2_pm2_5'],errors='coerce')
    df['s2_pm10'] = pd.to_numeric(df['s2_pm10'],errors='coerce')
    df['s1_s2_average_pm2_5'] = df[['s1_pm2_5', 's2_pm2_5']].mean(axis=1).round(2)
    df['s1_s2_average_pm10'] = df[['s1_pm10', 's2_pm10']].mean(axis=1).round(2)
    time_indexed_data = df.set_index('time')
    final_hourly_data = time_indexed_data.resample('H').mean().round(2) 
    final_data=final_hourly_data.dropna().reset_index()
    
    return final_data



def get_all_static_channels():
    client = bigquery.Client()

    query = """
        SELECT channel_id, latitude, longitude
        FROM `airqo-250220.thingspeak.channel`
        WHERE latitude != 0.0 OR longitude != 0.0
    """
    
    job_config = bigquery.QueryJobConfig()
    job_config.use_legacy_sql = False

    query_job = client.query(
        query,job_config=job_config)

    results = query_job.result()
    static_channels = []

    if results.total_rows >=1:
        for row in results:
            static_channels.append({"channel_id":row.channel_id,"latitude":row.latitude, "longitude":row.longitude})
    return static_channels



def generate_hourly_observations_for_all_static_devices():
    """
        calculates the hourly observations for all the static channels.
    """
    specified_locations = get_all_static_channels()
    empty_channels=[]
    #675991
    #listed_channels =[] 

    if specified_locations:
        for i in range(0, len(specified_locations)):
            all_channel_observations=[]
            channel_id = int(specified_locations[i].get('channel_id'))
            #print(type(channel_id))
            latitude = float(specified_locations[i].get('latitude'))
            #print(type(latitude))
            longitude = float(specified_locations[i].get('longitude'))
            #print(type(longitude))
            created_at = dt.now()

            #if channel_id not in listed_channels:

            results = get_raw_channel_data(channel_id)
                
            print(results.head())
                #results.to_csv('sample.csv')
            if not results.empty:
                for j in range(len(results)) : 
                    s1_pm2_5= float(results.loc[j, "s1_pm2_5"])
                    s1_pm10= float(results.loc[j, "s1_pm10"])
                    s2_pm2_5= float(results.loc[j, "s2_pm2_5"])
                    s2_pm10= float(results.loc[j, "s2_pm10"])
                    time = pd.to_datetime(results.loc[j, "time"])
                    s1_s2_average_pm2_5 = float(results.loc[j, "s1_s2_average_pm2_5"])
                    s1_s2_average_pm10 = float(results.loc[j, "s1_s2_average_pm10"])
                        #print(type(time))
                    observations_tuple = (channel_id, s1_pm2_5, s1_pm10,
                         s2_pm2_5, s2_pm10, latitude,
                          longitude, created_at, time, s1_s2_average_pm2_5, s1_s2_average_pm10)
                    all_channel_observations.append(observations_tuple)

                print('calling saving method')
                resultxx =save_cleaned_hourly__data(all_channel_observations)
                print(resultxx)
                print('ending saving method')
                
            else:
                empty_channels.append(channel_id)
        

        print(all_channel_observations)
        print('empty channels')
        print(empty_channels)
            
    return all_channel_observations

def function_to_execute(data, context):
    action = base64.b64decode(data['data']).decode('utf-8') 
    client = bigquery.Client()   
    if (action == "download!"):
        channel_ids_query = "SELECT channel_id, latitude, longitude FROM `airqo-250220.thingspeak.channel` WHERE latitude != 0.0 OR longitude != 0.0"
        channel_df = client.query(channel_ids_query).result().to_dataframe()
        
        #channel_id_list = channel_df['channel_id'].tolist()
        
        for index, row in channel_df.iterrows():
            channel_id = int(row['channel_id'])
            latitude  = float(row['latitude'])
            longitude = float(row['longitude'])
            results = get_raw_channel_data(channel_id)
            all_channel_observations=[]
    
            if not results.empty:
                for j in range(len(results)) :
                    channel_id = int(results.loc[j, "channel_id"])
                    s1_pm2_5= float(results.loc[j, "s1_pm2_5"])
                    s1_pm10= float(results.loc[j, "s1_pm10"])
                    s2_pm2_5= float(results.loc[j, "s2_pm2_5"])
                    s2_pm10= float(results.loc[j, "s2_pm10"])
                    time = pd.to_datetime(results.loc[j, "time"])
                    print('type of time: ', type(time))
                    print(type(time)) 
                    latitude= latitude
                    longitude = longitude
                    created_at = dt.now()
                    s1_s2_average_pm2_5 = float(results.loc[j, "s1_s2_average_pm2_5"])
                    s1_s2_average_pm10 = float(results.loc[j, "s1_s2_average_pm10"])

                    observations_tuple = (channel_id, s1_pm2_5, s1_pm10, s2_pm2_5, s2_pm10, latitude, longitude, created_at, time, s1_s2_average_pm2_5, s1_s2_average_pm10)
                    all_channel_observations.append(observations_tuple)

                save_cleaned_hourly_data(all_channel_observations)
                
            else:
                pass
            




if __name__ == '__main__':
    
    print('main')   
    
    #values_saved  =generate_hourly_observations_for_all_static_devicesx('action','xxxx')
    values_saved = function_to_execute('action', 'dxxxx')
    print(values_saved)
    #results = get_all_static_channels()
    #print(len(results))
    #print(results)
    #for i in range(0, len(results)):
        #print(results[i])
    print('completed saving')