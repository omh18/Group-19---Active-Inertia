import os, sys
import numpy as np
import matplotlib.pyplot as plt
import collections
import statistics

f = open("05-11 13:10 CoAP newcastle-london-newcastle.txt", "r")

input = f.read()

#Code for reparsing files:

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
plt.title("Broker in London, London-to-Newcastle: Time by which CoAP beats MQTT in one-way delay:")
#plt.text(50, 3, '$\mu={:.2f},\ \sigma={:.2f}$'.format(total*1000/counter, statistics.stdev(DelayListms)))
plt.text(0.5, 0.9, '$\mu={:.2f},\ \sigma={:.2f}$'.format(sum(input)*1000/coap, statistics.stdev(input)), ha='center', va='center', transform=ax.transAxes)
plt.grid(True)
#plt.show()
plt.savefig('CoaP-Newcastle-to-London-London-Broker.png', bbox_inches = 'tight')


f = open("05-11 13:10 MQTT newcastle-london-newcastle.txt", "r")

input = f.read()

input = [float(s)*1000 for s in input.split()]

mqtt = len(input)

f = plt.figure()
ax = f.add_subplot(111)
plt.style.use('ggplot')
plt.hist(input, 20)
plt.xlabel('Difference in ms')
plt.ylabel('Frequency')
plt.title("Broker in London, London-to-Newcastle: Time by which MQTT beats CoAP in one-way delay:")
#plt.text(50, 3, '$\mu={:.2f},\ \sigma={:.2f}$'.format(total*1000/counter, statistics.stdev(DelayListms)))
plt.text(0.5, 0.9, '$\mu={:.2f},\ \sigma={:.2f}$'.format(sum(input)*1000/mqtt, statistics.stdev(input)), ha='center', va='center', transform=ax.transAxes)
plt.grid(True)
plt.savefig('MQTT-Newcastle-to-London-London-Broker.png', bbox_inches = 'tight')

print(f"MQTT is faster {(mqtt*100)/(mqtt+coap)}% of the time, while CoAP is faster {(coap*100)/(mqtt+coap)}% of the time for Newcastle-to-London, with London Broker")
