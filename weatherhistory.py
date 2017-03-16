import json
import datetime
import urllib2
from datetime import timedelta


#Global Variables

key = '0f08174fce21669a13b9d713238c80ab' #darksky api key

unixDate = '1970-01-01' #date unix time is calculated from
unixDt = datetime.datetime.strptime(unixDate,'%Y-%m-%d')

startDate = '2015-01-01'#first date to retrieve data from
startDt_G = datetime.datetime.strptime(startDate,'%Y-%m-%d')

endDate = '2015-12-31' #last date to retrieve data from
endDt = datetime.datetime.strptime(endDate,'%Y-%m-%d')

unix = str(int((startDt_G - unixDt).total_seconds()))#startdate in Unix format

deltaDates = (endDt-startDt_G).days #number of days between starte date and enddate

outjson = "H://apicall//WeatherHist.json" #path to output .json file

def createJson(outfile):
    #create first json file using first date data
    outfile = outjson
    url = "https://api.darksky.net/forecast/"+key+"/42.3601,-71.0589,"+unix
    response = urllib2.urlopen(url)
    load = json.loads(response.read().decode('utf-8'))
    with open(outfile, 'w') as outfile:
        json.dump(load, outfile)

createJson(outjson)
print "json created"


def updateDict():
    for i in range(deltaDates):
        print i , 'i'
        startDt = startDt_G +timedelta(days=i+1)
        print startDt, 'startDt'
        unix = str(int((startDt - unixDt).total_seconds()))
        url = "https://api.darksky.net/forecast/"+key+"/42.3601,-71.0589,"+unix
        print url, 'url'
        response = urllib2.urlopen(url)
        load = json.loads(response.read().decode('utf-8'))
        print load, 'load'
        with open(outjson , 'r')as f:
            olddict = json.load(f)
            print olddict , 'olddict'
            print type(olddict) , 'type(olddict)'
        olddict.update(load)
        with open(outjson,'w') as f:
            json.dump(olddict, f)
            print 'updated'
                 
updateDict()
       

