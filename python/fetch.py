from urllib import parse
import http.client
import base64
import re
import json

host = '' # fill in your host name or static IP address
port = '80' # change port by your setting
username = '' # fill in your admin. username
password = '' # fill in your password
encodedUsernameAndPassword = base64.b64encode( (username + ':' + password).encode('ascii') ).decode('UTF-8')

def sendHttpRequest( url, path, data, additionalHeaders, method ):

    data = parse.urlencode( data )
    headers = {
	"Content-type": "application/x-www-form-urlencoded",
	"Accept": "text/plain",
    }
    headers.update( additionalHeaders )
    conn = http.client.HTTPConnection( url )
    conn.request( method, path, data, headers )
    response = conn.getresponse()

    return response.read()

sendHttpRequest(
    host + ':' + port,
    '',
    {},
    { 'Authorization': 'Basic ' + encodedUsernameAndPassword, },
    'POST'
)

try:
    sendHttpRequest( host + ':' + port, '/device-map/apply.cgi', {
	    'action_mode': 'refresh_networkmap',
	    'action_script': '',
	    'action_wait': '5',
	    'current_page': 'device-map/clients.asp',
	    'next_page': 'device-map/clients.asp',
	    #'group_id': '',
	    #'flag': '',
	    #'macfilter_rulelist': '',
	    #'macfilter_enable_x': '0',
	}, {
	    'Authorization': 'Basic ' + encodedUsernameAndPassword,
	    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	    'Accept-Encoding': 'gzip, deflate',
	    'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
	    'Authorization': 'Basic YWRtaW46Z29kYmFp',
	    'Cache-Control': 'max-age=0',
	    'Connection': 'keep-alive',
	    'Content-Length': '189',
	    'Content-Type': 'application/x-www-form-urlencoded',
	    'Cookie': 'notification_history=1,0,0,0,0,0,0',
	    'Host': '192.168.1.1',
	    'Origin': 'http://192.168.1.1',
	    'Referer': 'http://192.168.1.1/device-map/clients.asp',
	    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36',
	}, 'POST'
    )
except:
    pass

DHCPHistoryList = re.findall( r'<mac>value=(.*?)<\/mac>\n<hostname>value=(.*?)<\/hostname>',
    sendHttpRequest( host + ':' + port, '/getdhcpLeaseInfo.asp', {}, {
	'Authorization': 'Basic ' + encodedUsernameAndPassword,
	}, 'POST'
    ).decode( 'utf-8' )
)

deviceInfoList = {}
for eachDeviceInfomation in DHCPHistoryList:
    deviceInfoList[ eachDeviceInfomation[0].upper() ] = eachDeviceInfomation[1]

onlineDevicesRes = sendHttpRequest( host + ':' + port, '/update_clients.asp', {}, {
    'Authorization': 'Basic ' + encodedUsernameAndPassword,
    }, 'POST'
).decode( 'utf-8' )

onlineDevicesRaw = re.findall( r'client_list_array = \'(.*)\';', onlineDevicesRes )
onlineDevicesListRaw = re.findall( r'<6>(.*?)>(.*?)>(.*?)>0>0>0', onlineDevicesRaw.pop() )

onlineDevicesList = []
for eachOnlineDevice in onlineDevicesListRaw:
    onlineDevicesList.append( {
	'who': deviceInfoList[ eachOnlineDevice[2] ],
	'ip': eachOnlineDevice[1],
	'MAC': eachOnlineDevice[2],
    } )

sendHttpRequest( host + ':' + port, '/Logout.asp', {}, {
    'Authorization': 'Basic ' + encodedUsernameAndPassword,
    }, 'POST'
)

print( json.dumps( onlineDevicesList ) )
