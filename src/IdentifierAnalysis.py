import ConfigParser
import FindRootPage
import sys
reload(sys)

sys.setdefaultencoding("utf-8")

if len(sys.argv) != 2:
    print("Please specify the first database!")
    sys.exit(0)

config = ConfigParser.RawConfigParser()
config.read('identifier_user1.cfg')

# numHostTotal = 395
numHostTotal = 822
numTrackHost = len(config.sections())

trackReqArray = []
trackHostMethod = []
referredHostNumber = {}

for host in config.sections():
    trackMethod = 0

    # Get the data from config file
    keys = eval(config.get(host, 'keys'))
    requests = eval(config.get(host, 'requests'))

    # Mark the track method:
    #     - trackMethod = 1: only cookie
    #     - trackMethod = 2: only parameter
    #     - trackMethod = 3: both cookie and parameter
    keysTotal = [y.split('_')[0] for x in keys for y in x]
    if 'cookie' in keysTotal:
        trackMethod += 1
    if 'param' in keysTotal:
        trackMethod += 2
    trackHostMethod.append(trackMethod)

    # Get the number of tracking request for each tracking hosts
    requestTotal = set([y for x in requests for y in x])
    trackReqArray.append([host, len(requestTotal)])

    # Get the root pages for the tracking requests
    rootPageDict = FindRootPage.getRootPage(requestTotal, sys.argv[1])
    referredHostNumber[host] = len(rootPageDict.keys())

hosts, numReq = zip(*trackReqArray)
trackReqTot = sum(numReq)
ratioReq = [x / float(trackReqTot) for x in numReq]

# The portion of third-party host that can track users
trackHost = numTrackHost / float(numHostTotal)
print trackHost

# The pie diagram for the tracked request
trackReqArray = zip(hosts, numReq, ratioReq)
for host, req, ratio in trackReqArray:
    print host, req, ratio

# The pie diagram for the identifier locations
trackMethodArray = [['cookie', len([x for x in trackHostMethod if x == 1])],
                    ['param', len([x for x in trackHostMethod if x == 2])],
                    ['cookie and param', len([x for x in trackHostMethod if x == 3])]]
print trackMethodArray

# The number of referred hosts for each tracking host
for host in referredHostNumber.keys():
    print host, referredHostNumber[host]
