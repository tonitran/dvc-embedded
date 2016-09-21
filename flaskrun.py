from sensor import *
from flask import Flask
from flask_cors import CORS, cross_origin

# Flask setup
app = Flask(__name__)
CORS(app) #Run with server enabled CORS

# GET call for door
@app.route("/door")
@cross_origin()
def doorIsOpen():
    doorStateDict = getDoorState()
    return convertToJSON(doorStateDict)

# Get all data on a certain day
@app.route('/logs/<string:year>/<string:month>/<string:day>')
@cross_origin()
def getLogOn(year, month, day):
    #Make the query
    query = 'select * from history where DATE(timeStamp) = "%s-%s-%s"' % (year,month,day) #TODO UNSAFE
    returnList = accessDB('SELECT',query,())
    print(query)
    print(len(returnList))
    #Construct the list for the json encoder.
    listToEncode = []
    for tuple in returnList:
        jsonDict = {'timeStamp': tuple[0], 'isOpen': tuple[1]}
        listToEncode.append(jsonDict)
    #Encode the JSON
    return convertToJSON(listToEncode)

# Get a range of data from ISO time to ISO time
@app.route('/logs')
@cross_origin()
def getLogRange():
    lowerBound = request.args.get('from')
    upperBound = request.args.get('to')
    query = 'select * from history where timeStamp >= ? and timeStamp < ?'
    returnList = accessDB('SELECT',query,(lowerBound,upperBound))
    #Construct the list for the json encoder.
    listToEncode = []
    for tuple in returnList:
        jsonDict = {'timeStamp': tuple[0], 'isOpen': tuple[1]}
        listToEncode.append(jsonDict)
    #Encode the JSON
    return convertToJSON(listToEncode)

# (Helper) Converts a dict or list to JSON
def convertToJSON(item):
    json_data = json.dumps(item, sort_keys=True, separators=(',', ':'))
    return json_data
