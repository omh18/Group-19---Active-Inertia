import asyncio
import datetime, time
import os, sys
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from uuid import uuid4

from aiocoap import *

startTime = None

def customCallback(client, userdata, message):
    msg = message.payload.decode("utf-8")
    timeDiffCoAP = now() - startTime
    print(f"MQTT responded in {float(timeDiffCoAP.total_seconds())}")

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

def now():
    return datetime.datetime.now()


async def main():
    protocol = await Context.create_client_context()
    
    msg = "test"
        
    request = Message(code=GET, uri=f'coap://{sys.argv[1]}:5683/time')
    
    myAWSIoTMQTTClient.publish(topic, msg, qos)
    startTime = now()

    try:
        response = await protocol.request(request).response
        timeDiffCoAP = now() - startTime
        print(f"CoAP responded in {float(timeDiffCoAP.total_seconds())}")
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    # else:
    #     print('Result: %s\n%r'%(response.code, response.payload))

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    time.sleep(2)