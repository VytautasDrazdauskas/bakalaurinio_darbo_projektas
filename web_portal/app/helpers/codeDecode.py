import pyzbar.pyzbar as pyzbar

def decode(image): 
    # Find barcodes and QR codes
    decodedObjects = pyzbar.decode(image)
    
    # Print results
    for obj in decodedObjects:
        print('Type : ', obj.type)
        print('Data : ', obj.data,'\n')

        return obj.data


def codeWeekdays(form):
    weekdayList = []
    weekdayList.append(form.monday.data)
    weekdayList.append(form.tuesday.data)
    weekdayList.append(form.wednesday.data)
    weekdayList.append(form.thursday.data)
    weekdayList.append(form.friday.data)
    weekdayList.append(form.saturday.data)
    weekdayList.append(form.sunday.data)

    weekdays = ''
    day = 1

    for weekday in weekdayList:        
        if (weekday):
            weekdays = weekdays + str(day)
        day = day + 1

    return weekdays

def decodeWeekdaysLt(weekdays):
    result = ''
    for day in weekdays:
        if (day == '1'):
            result += 'Pr. '
        elif (day == '2'):
            result += 'An. '
        elif (day == '3'):
            result += 'Tr. '
        elif (day == '4'):
            result += 'Kt. '
        elif (day == '5'):
            result += 'Pn. '
        elif (day == '6'):
            result += 'Št. '
        elif (day == '7'):
            result += 'Sk. '
    return result
