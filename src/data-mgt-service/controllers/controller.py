from flask import Blueprint, request, jsonify
import logging
import datamanagement.datamanagement as dm
import datetime as dt

_logger = logging.getLogger(__name__)

data_management_app = Blueprint('data_management_app', __name__)

@data_management_app.route('/api/v1/coordinates', methods=['GET'])
def get_coordinates():
    if request.method == 'GET':
        all_coordinates = dm.get_all_coordinates()
        _logger.info(all_coordinates)
        return jsonify({'coordinates': all_coordinates})
       
        
@data_management_app.route('/health', methods=['GET'])
def health():
    if request.method == 'GET':
        _logger.info('health status OK')
        return 'ok'

@data_management_app.route('/api/v1/predict/', methods=['POST'])
def predict_avgs():
    if request.method == 'POST':
        json_data = request.get_json()
        if not json_data:
               return {'message': 'No input data provided'}, 400
        _logger.info(f'Inputs: {json_data}')
        input_data, errors = validate_inputs(input_data=json_data)

        if not errors:        
            entered_latitude = json_data["latitude"]
            entered_longitude  = json_data["longitude"]
            enter_time = json_data["selected_datetime"]

            channel_id_with_specified_coordinates = dm.get_channel_id(entered_latitude,entered_longitude)
            print("channel id :", channel_id_with_specified_coordinates)
            if channel_id_with_specified_coordinates == 0:
                channel_id_with_specified_coordinates = get_closest_channel(entered_latitude,entered_longitude)
                print("channel id closest", channel_id_with_specified_coordinates)
                print("type of data", type(channel_id_with_specified_coordinates))

            entered_chan = channel_id_with_specified_coordinates
            entered_time = dt.datetime.strptime(enter_time,"%Y-%m-%d %H:%M")

            print('type of latitude:', type(entered_latitude))

            if entered_chan != "Channel Id Not available":
                formatted_results = make_prediction_using_averages(entered_chan, entered_time, 
                    entered_latitude,entered_longitude)              

                return jsonify({'formatted_results': formatted_results})
            else:
                 return jsonify({'errors': 'location predictions are not available currently.'}), 404
        else:
            _logger.info(f'errors: {errors}')
            return jsonify({'inputs': json_data,'errors': errors }), 400
       
        
        
        

        

