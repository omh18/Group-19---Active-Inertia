import datetime
import logging
import datetime, time
import os, sys
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from uuid import uuid4
import asyncio

import aiocoap.resource as resource
from aiocoap import *

class TimeMeasurement():
    def __init__(self):
        self.timeMQTT = None
        self.timeCoAP = None
        
    def timeNow(self):
        return time.time()
    
    def receivedMQTT(self):
        self.timeMQTT = self.timeNow()
        
        if self.timeCoAP != None:
            print(f"CoAP packet arrived first by {abs(self.timeMQTT-self.timeCoAP)}s")
            self.timeMQTT = None
            self.timeCoAP = None
        
    def receivedCoAP(self):
        self.timeCoAP = self.timeNow()
        
        if self.timeMQTT != None:
            print(f"MQTT packet arrived first by {abs(self.timeMQTT-self.timeCoAP)}s")
            self.timeMQTT = None
            self.timeCoAP = None

timer = TimeMeasurement()

class BlockResource(resource.Resource):
    timer.receivedCoAP()
    """Example resource which supports the GET and PUT methods. It sends large
    responses, which trigger blockwise transfer."""

    def __init__(self):
        super().__init__()
        self.set_content(b"This is the resource's default content. It is padded "\
                b"with numbers to be large enough to trigger blockwise "\
                b"transfer.\n")

    def set_content(self, content):
        self.content = content
        while len(self.content) <= 1024:
            self.content = self.content + b"0123456789\n"

    async def render_get(self, request):
        return Message(payload=self.content)

    async def render_put(self, request):
        print('PUT payload: %s' % request.payload)
        self.set_content(request.payload)
        return Message(code=codes.CHANGED, payload=self.content)

class SeparateLargeResource(resource.Resource):
    timer.receivedCoAP()
    """Example resource which supports the GET method. It uses asyncio.sleep to
    simulate a long-running operation, and thus forces the protocol to send
    empty ACK first. """

    def get_link_description(self):
        # Publish additional data in .well-known/core
        return dict(**super().get_link_description(), title="A large resource")

    async def render_get(self, request):
        await asyncio.sleep(3)

        payload = "Three rings for the elven kings under the sky, seven rings "\
                "for dwarven lords in their halls of stone, nine rings for "\
                "mortal men doomed to die, one ring for the dark lord on his "\
                "dark throne.".encode('ascii')
        return Message(payload=payload)

class TimeResource(resource.ObservableResource):
    timer.receivedCoAP()
    """Example resource that can be observed. The `notify` method keeps
    scheduling itself, and calles `update_state` to trigger sending
    notifications."""

    def __init__(self):
        super().__init__()

        self.handle = None

    def notify(self):
        self.updated_state()
        self.reschedule()

    def reschedule(self):
        self.handle = asyncio.get_event_loop().call_later(5, self.notify)

    def update_observation_count(self, count):
        if count and self.handle is None:
            print("Starting the clock")
            self.reschedule()
        if count == 0 and self.handle:
            print("Stopping the clock")
            self.handle.cancel()
            self.handle = None

    async def render_get(self, request):
        payload = datetime.datetime.now().\
                strftime("%Y-%m-%d %H:%M").encode('ascii')
        return Message(payload=payload)

class WhoAmI(resource.Resource):
    timer.receivedCoAP()
    async def render_get(self, request):
        text = ["Used protocol: %s." % request.remote.scheme]

        text.append("Request came from %s." % request.remote.hostinfo)
        text.append("The server address used %s." % request.remote.hostinfo_local)

        claims = list(request.remote.authenticated_claims)
        if claims:
            text.append("Authenticated claims of the client: %s." % ", ".join(repr(c) for c in claims))
        else:
            text.append("No claims authenticated.")

        return Message(content_format=0,
                payload="\n".join(text).encode('utf8'))


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


def customCallback(client, userdata, message):
    if message.payload.decode("utf-8") == "test":
        timer.receivedMQTT()
        print("Callback called!")
    else: pass

# Connect and subscribe to AWS IoT
try:
    myAWSIoTMQTTClient.connect(1000)
    myAWSIoTMQTTClient.subscribe(topic, qos, customCallback)
except:
    print("Could not connect to AWS MQTT broker")
    raise SystemExit

def main():
    # Resource tree creation
    root = resource.Site()

    root.add_resource(['.well-known', 'core'],
            resource.WKCResource(root.get_resources_as_linkheader))
    root.add_resource(['time'], TimeResource())
    root.add_resource(['other', 'block'], BlockResource())
    root.add_resource(['other', 'separate'], SeparateLargeResource())
    root.add_resource(['whoami'], WhoAmI())

    context = Context.create_server_context(root)

    asyncio.Task(context)
    print("ready to receive")

    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
