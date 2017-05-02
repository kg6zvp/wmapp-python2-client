#!/usr/bin/python2

# Source: http://gitlab.wmapp.mccollum.enterprises/wmapp/python2-client

import json
import requests
import getpass
import socket

protocol = "http"
server = "auth.wmapp.mccollum.enterprises"

authBaseUrl = protocol+"://"+server+"/api"
tokenBaseUrl = authBaseUrl+"/token"
usersBaseUrl = authBaseUrl+"/users"

loginUrl = tokenBaseUrl+"/getToken"
logoutUrl = tokenBaseUrl+"/invalidateToken"
listUrl = tokenBaseUrl+"/listTokens"
renewUrl = tokenBaseUrl+"/renewToken"
invalidationSubscriptionUrl = tokenBaseUrl+"/subscribeToInvalidation"
tokenValidUrl = tokenBaseUrl+"/tokenValid"

tokenSignature=""
tokenString=""

def readTokens():
    try:
	with open('token.json', 'r') as tf:
	    global tokenString
	    tokenString = tf.read()
	with open('sigb64.txt', 'r') as sf:
	    global tokenSignature
	    tokenSignature = sf.read()
	return True
    except IOError as e:
	return False

def getToken(username, password, deviceName):
    hrs = {'Content-Type': 'application/json'}
    loginObject = {'username': username, 'password': password, 'devicename': deviceName}
    return requests.post(url=loginUrl, data=json.dumps(loginObject), headers=hrs)

def invalidateToken(delToken, token, sigb64):
    hrs = {'Content-Type': 'application/json'}
    hrs['Token'] = token
    hrs['TokenSignature'] = sigb64
    return requests.delete(url=logoutUrl+'/'+str(delToken['tokenId']), headers=hrs)

def listTokens(token, sigb64):
    hrs = {'Content-Type': 'application/json'}
    hrs['Token'] = token
    hrs['TokenSignature'] = sigb64
    return requests.get(url=listUrl, headers=hrs)

def renewToken(token, sigb64):
    hrs = {'Content-Type': 'application/json'}
    hrs['Token'] = token
    hrs['TokenSignature'] = sigb64
    return requests.get(url=renewUrl, headers=hrs)

def subscribeToInvalidation(invalidationSubscription, token, sigb64):
    hrs = {'Content-Type': 'application/json'}
    hrs['Token'] = token
    hrs['TokenSignature'] = sigb64
    return requests.post(url=invalidationSubscriptionUrl, headers=hrs)

"""
" Check whether the token is valid against the token validation API endpoint
"""
def isValidToken(token, sigb64):
    hrs = {'Content-Type': 'application/json'}
    hrs['Token'] = token
    hrs['TokenSignature'] = sigb64
    return requests.get(url=tokenValidUrl, headers=hrs)

"""
" Check your response against an API endpoint (primarily for testing, but may be good for production)
" @param httpResponse: response object from python-requests library to check
" @param expectedResponse: numeric response code expected
" @failureMessage String description of what action failed
"
" @return boolean: whether the code was verified or not
"""
def checkCode(httpResponse, expectedResponse, failureMessage):
    if httpResponse.status_code != expectedResponse:
	print "\tFailed to "+failureMessage
	print "\t"+str(httpResponse.status_code)
	print "\t"+httpResponse.content
	return False
    return True

def getTokenString():
    global tokenString
    return tokenString

def getSignature():
    global tokenSignature
    return tokenSignature

def persistTokens():
    with open('token.json', 'w') as tf:
	tf.write(getTokenString())
    with open('sigb64.txt', 'w') as sf:
	sf.write(getSignature())

def wmLogin(username, password, deviceName):
    validCreds = getToken(username, password, deviceName)
    if not checkCode(validCreds, 200, "login"):
	return False
    global tokenString
    tokenString = validCreds.content
    global tokenSignature
    tokenSignature = validCreds.headers['TokenSignature']
    persistTokens()
    return True

def promptLogin():
    username = raw_input("Username: ")
    passwd = getpass.getpass()
    return wmLogin(username, passwd, socket.gethostname())

def loadCredentials(prompt=True):
    if readTokens():
	return True
    if prompt:
	return promptLogin()
    return False

"""
Sample code:

  Login:
    print "Performing login..."
    wmLogin('erichtofen', 'oneStupidLongTestPassword23571113', 'validDevice')
"""
