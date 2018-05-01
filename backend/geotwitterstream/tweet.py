'''
file: Tweet.py
author: Giovanni Macciocu
date: Tue May  1 07:13:30 2018
'''

class TweetCoord(object):
    def __init__(self, latitude_longitude_a=(40, -74), latitude_longitude_b=(41, -73)):
        '''
        latitude_longitude_a --- (latitude, longitude) pair A of bounding box
        latitude_longitude_b --- (latitude, longitude) pair B of bounding box
        '''
        self._latitude_longitude_a = latitude_longitude_a
        self._latitude_longitude_b = latitude_longitude_b

    @property
    def latitude_longitude_a(self):
        return self._latitude_longitude_a

    @property
    def latitude_longitude_b(self):
        return self._latitude_longitude_b

    @latitude_longitude_a.setter
    def latitude_longitude_a(self, val):
        self._latitude_longitude_a = val

    @latitude_longitude_b.setter
    def latitude_longitude_b(self, val):
        self._latitude_longitude_b = val

    def __str__(self):
        return '%s,%s,%s,%s' % (self._latitude_longitude_a[1], self._latitude_longitude_a[0],
                self._latitude_longitude_b[1], self._latitude_longitude_b[0])


class TweetMessage(object):
    def __init__(self, tweet):
        self._tweet = tweet

    def __str__(self):
        for key in self._tweet:
            print('%s: %s' % (key, self._tweet[key]))

    def userinfo(self):
        txt = ''
        if 'user' not in self._tweet:
            txt = 'user-info: not available'
        else:
            if 'name' in self._tweet['user']:
                txt += '%s' % (self._tweet['user']['name'])
            if 'id' in self._tweet['user']:
                txt += ' (%s)' % (self._tweet['user']['description'])
            if 'description' in self._tweet['user']:
                txt += ' - %s' % (self._tweet['user']['description'])
        return txt

    def message(self):
        txt = ''
        if 'text' not in self._tweet:
            txt = 'message-text: not available'
        else:
            txt = self._tweet['text']
        return txt

    def locationinfo(self):
        txt = ''
        if 'place' not in self._tweet:
            txt = 'location-info: not available'
        else:
            if 'country' in self._tweet['place']:
               txt = self._tweet['place']['country']
            if 'country_code' in self._tweet['place']:
                txt += ' (%s)' % (self._tweet['place']['country_code'])
            if 'full_name' in self._tweet['place']:
                txt += ' - %s' % (self._tweet['place']['full_name'])
        return txt

    def locationcoord(self):
        txt = 'coordinates (latitude,longitude): '
        coordinates_available = False
        if 'bounding_box' in self._tweet['place']:
            if 'coordinates' in self._tweet['place']['bounding_box']:
                coordinates_available = True
                # 3d list [[[longitude, latitude], [longitude, latitude] ...]]
                bounding_box_coord = self._tweet['place']['bounding_box']['coordinates']
                for location in bounding_box_coord:
                    for longitude_latitude in location:
                        txt += ('  (%s, %s)' % (longitude_latitude[1], longitude_latitude[0]))
        if not coordinates_available:
            txt += 'not available'
        return txt
