from flask import Flask, request, jsonify, render_template
from google.cloud import bigquery
from google.oauth2 import service_account
import models

app = Flask(__name__, static_folder="static")

@app.route('/')
def home():
    return render_template('index.html')
    
@app.route('/map', methods=['POST'])
def cluster():
    #city = request.form.get("city") 
    #cluster_number = request.form.get("device_number")
    cluster_number = 40

    #credentials to access GCP
    credentials = service_account.Credentials.from_service_account_file('C:/Users/Lillian/AirQo-d982995f6dd8.json')
    project_id = 'airqo-250220'
    bqclient = models.access_bigquery(credentials, project_id)
    
    #downloading geo_census data from bigquery and converting it to a dataframe
    query_string = "SELECT * FROM `airqo-250220.thingspeak.geo_census`"
    bqdata = bqclient.query(query_string).result()
    data = bqdata.to_dataframe()

    #running clustering model
    #models.kmeans_clustering(data, cluster_number)
    #return render_template('sensor_map.html')
    return models.kmeans_clustering(data, cluster_number)
    
if __name__ == "__main__":
    app.run(debug=True)