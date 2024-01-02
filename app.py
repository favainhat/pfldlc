from flask import Flask, send_from_directory, make_response, request
import ssl
import base64
import time
import datetime
import io
import hashlib
import hmac
import struct
from Crypto.Cipher import AES

# Constants.
DIR_P01 = 'p01'

app = Flask(__name__)

# ----------------------------------------------------------------------------------------------------------------------
#helper function
#from https://github.com/kinnay/NintendoClients
def b64decode(text):
	text = text.replace(".", "+").replace("-", "/").replace("*", "=")
	return base64.b64decode(text)

def b64encode(text):
	# Convert to bytes if necessary
	if isinstance(text, str):
		text = text.encode()
	text = base64.b64encode(text).decode()
	return text.replace("+", ".").replace("/", "-").replace("=", "*")

def dictToQuery(d):
  query = ''
  idx = 0
  for key in d.keys():
    if idx != 0:
        query += '&'
    query += str(key) + '=' + str(d[key])
    idx +=1
  return query

# ----------------------------------------------------------------------------------------------------------------------
# DLC file routes.
#https://npdl.cdn.nintendowifi.net
@app.route(f'/p01/<path:path>', methods=['GET'])
def serve_dlc_file(path):
    return send_from_directory(DIR_P01, path)

# ----------------------------------------------------------------------------------------------------------------------
# 3ds NASC server
#https://nasc.nintendowifi.net/ac
def nasc_response():
    resp_dict ={}
    try:
        req = request.form.to_dict()
        action  = b64decode(req['action']).decode()
        print(action)
        if action =="LOGIN":
            titleid = b64decode(req['titleid']).decode()
            gameid = b64decode(req['gameid']).decode()
            resp_dict['locator'] = b64encode('0.0.0.0:0') #It varies depending on the gameid.
            resp_dict['retry'] = b64encode('0')
            resp_dict['returncd'] = b64encode('001')
            resp_dict['token'] = b64encode('notActualToken') #Temp value
            resp_dict['datetime'] = b64encode(str(datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")))
        elif action =="SVCLOC":
            userid = b64decode(req['userid']).decode()
            resp_dict['retry'] = b64encode('0')
            resp_dict['returncd'] = b64encode('007')
            resp_dict['servicetoken'] = b64encode(userid) #Real server contains more information include userid and freind code and current time with encryption. We currently only need userid.
            resp_dict['statusdata'] = b64encode('Y')
            resp_dict['svchost'] = b64encode('n/a')
            resp_dict['datetime'] = b64encode(str(datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")))
        else:
            raise ValueError('Unknown action.')
        resp = dictToQuery(resp_dict)
        response = make_response(resp)
        response.headers['Content-Type'] = 'text/plain;charset=ISO-8859-1'
        return response
    except Exception as e:
        resp_dict ={};
        resp_dict['retry'] = b64encode('1')
        resp_dict['returncd'] = b64encode('109')
        resp_dict['datetime'] = b64encode(str(datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")))
        resp = dictToQuery(resp_dict)
        response = make_response(resp)
        response.headers['Content-Type'] = 'text/plain;charset=ISO-8859-1'
        return response
    
@app.route('/ac',methods=['POST'])
def nasc_ac():
    return nasc_response()


#http://conntest.nintendowifi.net/
@app.route('/', methods=['GET'])
def conn_test():
    response = send_from_directory("conntest", 'test.html')
    response.headers['X-Organization'] = 'Nintendo'
    response.headers['Content-type'] = 'text/html'
    return response

    
if __name__ == '__main__':
    app.run()
