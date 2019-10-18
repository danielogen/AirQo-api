# define the processed collection schema
class Processed(object):
 
    def __init__(self, time, pm2_5, pm10, s2_pm2_5=None, s2_pm10=None, lat=None, long=None, 
    channel_id=None, pm1=None, voltage=None, temp=None, humidity=None):
        self.time = time
        self.pm2_5 = pm2_5
        self.pm10 = pm10
        self.s2_pm2_5= s2_pm2_5
        self.s2_pm10 = s2_pm10
        self.lat = lat
        self.channel_id = channel_id
        self.pm1= pm1
        self.voltage = voltage
        self.temp = temp
        self.humidity = humidity