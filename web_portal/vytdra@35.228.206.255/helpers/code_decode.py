import pyzbar.pyzbar as pyzbar
from flask import json

class JsonParse(object):
    def __init__(self, data):
	    self.__dict__ = json.loads(data)

    def decode_jsonify(self):
        return JsonParse(self.data)
        

def decode(image): 
    # Find barcodes and QR codes
    decoded_objects = pyzbar.decode(image)
    
    # Print results
    for obj in decoded_objects:
        print('Type : ', obj.type)
        print('Data : ', obj.data,'\n')

        return obj.data


def code_weekdays(form):
    weekdayList = []
    weekdayList.append(form.monday.data)
    weekdayList.append(form.tuesday.data)
    weekdayList.append(form.wednesday.data)
    weekdayList.append(form.thursday.data)
    weekdayList.append(form.friday.data)
    weekdayList.append(form.saturday.data)
    weekdayList.append(form.sunday.data)

    weekdays = ''
    day = 0

    for weekday in weekdayList:        
        if (weekday):
            weekdays = weekdays + str(day)
        day = day + 1

    return weekdays

def decode_weekdays(weekdays):
    result = ''
    for day in weekdays:
        if (day == '0'):
            result += 'Pr. '
        elif (day == '1'):
            result += 'An. '
        elif (day == '2'):
            result += 'Tr. '
        elif (day == '3'):
            result += 'Kt. '
        elif (day == '4'):
            result += 'Pn. '
        elif (day == '5'):
            result += 'Št. '
        elif (day == '6'):
            result += 'Sk. '
    return result

