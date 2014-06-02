import ConfigParser
import sys
reload(sys)

sys.setdefaultencoding("utf-8")

config = ConfigParser.RawConfigParser()
config.read('identifier_user1.cfg')

numHostTotal = 1000
numTrackHost = len(config.sections())
trackReqArray = []
trackHostMethod = []
for host in config.sections():
    trackMethod = 0
    keys = eval(config.get(host, 'keys'))
    requests = eval(config.get(host, 'requests'))

    keysTotal = [y.split('_')[0] for x in keys for y in x]
    if 'cookie' in keysTotal:
        trackMethod += 1
    if 'param' in keysTotal:
        trackMethod += 2
    trackHostMethod.append(trackMethod)

    requestTotal = [y for x in requests for y in x]
    trackReqArray.append([host, len(set(requestTotal))])

hosts, numReq = zip(*trackReqArray)
trackReqTot = sum(numReq)
ratioReq = [x / float(trackReqTot) for x in numReq]

# The portion of third-party host that can track users
trackHost = numTrackHost / float(numHostTotal)
# The pie diagram for the tracked request
trackReqArray = zip(hosts, numReq, ratioReq)
# The pie diagram for the identifier locations
trackMethodArray = [['cookie', len([x for x in trackHostMethod if x == 1])],
                    ['param', len([x for x in trackHostMethod if x == 2])],
                    ['cookie and param', len([x for x in trackHostMethod if x == 3])]]
