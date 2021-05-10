import asyncio
import datetime, time
import os, sys
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from uuid import uuid4

from aiocoap import *

class Times:
    def timeNow(self):
        return datetime.datetime.now()
    
    def __init__(self):
        self.sendMQTTTime = None
        self.sendCoAPTime = None
                
    def sendMQTT(self):
        self.sendMQTTTime = self.timeNow()
        
    def sendCoAP(self):
        self.sendCoAPTime = self.timeNow()
        
    def recvMQTT(self):
        print(f"MQTT packet received in {float((self.timeNow()-self.sendMQTTTime).total_seconds())}s")
        
    def recvCoAP(self):
        print(f"CoAP packet received in {float((self.timeNow()-self.sendCoAPTime).total_seconds())}s")
        
timer = Times()

def customCallback(client, userdata, message):
    timer.recvMQTT()

cwd = os.path.dirname(os.path.abspath(__file__))

qos = 0
host = "a3ccusvtjpdwda-ats.iot.eu-west-2.amazonaws.com"
rootCAPath = os.path.join(cwd,"certs","Amazon-root-CA-1.pem")
privateKeyPath = os.path.join(cwd,"certs","private.pem.key")
certificatePath = os.path.join(cwd,"certs","device.pem.crt")
port = 8883
clientId = "test-" + str(uuid4())
topic = "topic_1"

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureEndpoint(host, port)
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
try:
    myAWSIoTMQTTClient.connect(1000)
    myAWSIoTMQTTClient.subscribe(topic, qos, customCallback)
except:
    print("Could not connect to AWS MQTT broker")
    raise SystemExit



async def main():
    protocol = await Context.create_client_context()
    
    msg = "test"
        
    request = Message(code=GET, uri=f'coap://{sys.argv[1]}:5683/time')
    timer.sendCoAP()
    
    myAWSIoTMQTTClient.publish(topic, msg, qos)
    timer.sendMQTT()

    try:
        response = await protocol.request(request).response
        timer.recvCoAP()
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    time.sleep(2)