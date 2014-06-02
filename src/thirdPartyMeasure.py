from FindIdentifier import *
import ConfigParser


config = ConfigParser.RawConfigParser()
config.read('identifier.cfg')
database1 = config.get('databases', 'database1')
database2 = config.get('databases', 'database2')
level = config.getint('identifiers', 'level')
try:
    hostList = eval(config.get('hosts', 'host_list'))
except:
    hostList = None

try:
    excepList = eval(config.get('hosts', 'excep_list'))
except:
    excepList = None

print("Generating the available host list.....")
stringArrayDict1, stringArrayDict2, candidateHostList = generateHostList(database1, database2,
                                                                         hostList = hostList,
                                                                         excepList = excepList)
f = open('thirdParty.output', 'w')
for host in candidateHostList:
    keys, sequences, reqIds = stringArrayDict1[host]
    f.write(host + '\t' + str(len(set(reqIds))) + '\n')

f.close()
