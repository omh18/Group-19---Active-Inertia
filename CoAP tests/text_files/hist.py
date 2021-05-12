import os, sys
import numpy as np
import matplotlib.pyplot as plt
import collections
import statistics

f = open("CoAP-London-to-London", "r")

input = f.read()

#Code for parsing files:

#input = input.replace("0.", " 0.")
#print(input)
#cwd = os.path.dirname(os.path.abspath(__file__))

#CoAPFile = os.path.join(cwd,".",f"MQTT-London-to-London")

#input = [s for s in input.split()]

input = [float(s)*1000 for s in input.split()]
#print(input)
#with open(CoAPFile, 'w+') as coap:
#    for t in input:
#        coap.write(t + "\n")

coap = len(input)

f = plt.figure()
ax = f.add_subplot(111)
plt.style.use('ggplot')
plt.hist(input, 100)
plt.xlabel('Difference in ms')
plt.ylabel('Frequency')
plt.title("Broker in London, London-to-London: Time by which CoAP beats MQTT in one-way delay:")
#plt.text(50, 3, '$\mu={:.2f},\ \sigma={:.2f}$'.format(total*1000/counter, statistics.stdev(DelayListms)))
plt.text(0.5, 0.9, '$\mu={:.2f},\ \sigma={:.2f}$'.format(sum(input)/coap, statistics.stdev(input)), ha='center', va='center', transform=ax.transAxes)
plt.grid(True)
#plt.show()
plt.savefig('CoaP-London-to-London-London-Broker.png', bbox_inches = 'tight')


f = open("MQTT-London-to-London", "r")

input = f.read()

input = [float(s)*1000 for s in input.split()]

mqtt = len(input)

f = plt.figure()
ax = f.add_subplot(111)
plt.style.use('ggplot')
plt.hist(input, 20)
plt.xlabel('Difference in ms')
plt.ylabel('Frequency')
plt.title("Broker in London, London-to-London: Time by which MQTT beats CoAP in one-way delay:")
#plt.text(50, 3, '$\mu={:.2f},\ \sigma={:.2f}$'.format(total*1000/counter, statistics.stdev(DelayListms)))
plt.text(0.5, 0.9, '$\mu={:.2f},\ \sigma={:.2f}$'.format(sum(input)/mqtt, statistics.stdev(input)), ha='center', va='center', transform=ax.transAxes)
plt.grid(True)
plt.savefig('MQTT-London-to-London-London-Broker.png', bbox_inches = 'tight')

print(f"MQTT is faster {(mqtt*100)/(mqtt+coap)}% of the time, while CoAP is faster {(coap*100)/(mqtt+coap)}% of the time for London-to-London, with London Broker")
