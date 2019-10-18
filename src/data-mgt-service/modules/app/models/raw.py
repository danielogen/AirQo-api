# define the raw schema
class Raw(object):
 
    def __init__(self, time, entry_id, pm2_5, pm10, s2_pm2_5=None, s2_pm10=None, lat=None, long=None, 
    channel_id=None, gps_data=None, pm1=None, voltage=None, uptime=None, RSSI=None, sample_period=None, 
    temp=None, humidity=None, pm2_5_cf_1=None):
        self.time = time
        self.entry_id = entry_id
        self.pm2_5 = pm2_5
        self.pm10 = pm10
        self.s2_pm2_5= s2_pm2_5
        self.s2_pm10 = s2_pm10
        self.lat = lat
        self.channel_id = channel_id
        self.gps_data = gps_data
        self.pm1= pm1
        self.voltage = voltage
        self.uptime = uptime
        self.RSSI = RSSI
        self.sample_period = sample_period
        self.temp = temp
        self.humidity = humidity
        self.pm2_5_cf_1 = pm2_5_cf_1