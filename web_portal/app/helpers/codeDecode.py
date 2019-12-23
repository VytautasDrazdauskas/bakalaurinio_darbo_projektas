import pyzbar.pyzbar as pyzbar

def decode(image): 
    # Find barcodes and QR codes
    decodedObjects = pyzbar.decode(image)
    
    # Print results
    for obj in decodedObjects:
        print('Type : ', obj.type)
        print('Data : ', obj.data,'\n')

        return obj.data
