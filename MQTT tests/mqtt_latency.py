from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time, datetime
import os
from uuid import uuid4

#lazy coding but works lol
class TimeCalculator:
    def __init__ (self):
        #time of msg dispatch for each index so messages arriving before eachother dont get mixed up
        self.timeStarts = {}

        # stores time differences for all messages
        self.timeDeltas = {}

        self.timeDeltasList = None

    def endOfMessages(self):
        self.timeDeltasList = list(self.timeDeltas.values())

    def timeNow(self):
        return datetime.datetime.now()
    
    def startT(self, i):
        self.timeStarts[i] = self.timeNow()
    
    def finishT(self, i):
        timeDiff = self.timeNow() - self.timeStarts[i]
        self.timeDeltas[i] = float(timeDiff.total_seconds())
    
    def getTimeDelta(self, i):
        return self.timeDeltas[i]
    
    def getReceivedMessages(self):
        return len(self.timeDeltas)
    
    def calcAvg (self):
        return sum(self.timeDeltasList) / len(self.timeDeltas)
    
    def calcMax (self):
        return max(self.timeDeltasList)
    
    def calcMin (self):
        return min(self.timeDeltasList)
    
    def calcOver10(self):
        return len([x for x in self.timeDeltasList if x >= 0.01])
    
    def calcOver20(self):
        return len([x for x in self.timeDeltasList if x >= 0.02])
        

timeCalc = TimeCalculator()

# Custom MQTT message callback
def customCallback(client, userdata, message):
    msg = message.payload.decode("utf-8")
    timeCalc.finishT(msg)
    
    print(f"Received a new message: {message.payload}. from topic: {message.topic}. Time taken: {timeCalc.getTimeDelta(msg)}")


cwd = os.path.dirname(__file__)

qos = 0
host = "a3ccusvtjpdwda-ats.iot.eu-west-2.amazonaws.com"
rootCAPath = f"{cwd}\certs\Amazon-root-CA-1.pem"
certificatePath = f"{cwd}\certs\device.pem.crt"
privateKeyPath = f"{cwd}\certs\private.pem.key"
port = 8883
useWebsocket = False #todo: Test speed when True
clientId = "test-" + str(uuid4())
topic = "topic_1" #args.topic


# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.NOTSET)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)


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
myAWSIoTMQTTClient.connect(1000)
myAWSIoTMQTTClient.subscribe(topic, qos, customCallback)
time.sleep(1)


# publish to topic
messages = [f"Hello world {x}" for x in range(10)]
# messages = range(1,10)
for m in messages:
    msg = f"{m}"

    timeCalc.startT(msg)
    myAWSIoTMQTTClient.publish(topic, msg, qos)

    time.sleep(0.1)

#to ensure all messages are received
time.sleep(1)

timeCalc.endOfMessages()
print(f"Messages received: {timeCalc.getReceivedMessages()}")
print(f"Average time: {timeCalc.calcAvg()} seconds")
print(f"Max time: {timeCalc.calcMax()} seconds")
print(f"Min time: {timeCalc.calcMin()} seconds")
print(f"Over 10ms: {timeCalc.calcOver10()} occurrences")
print(f"Over 20ms: {timeCalc.calcOver20()} occurrences")