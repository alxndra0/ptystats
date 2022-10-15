import os
import sys
import time
from dotenv import load_dotenv
import json
from graphqlclient import GraphQLClient

import upsetfactorfinder

load_dotenv()
STARTGGTOKEN = os.getenv('STARTGG_TOKEN')
ggApiVersion = 'alpha'

gql = GraphQLClient('https://api.start.gg/gql/' + ggApiVersion)
gql.inject_token('Bearer ' + STARTGGTOKEN)

#Event id from start.gg for testing "779346" is red river riot 9
event_id = sys.argv[1]
hashtag = sys.argv[2]
textFileName = f'{event_id}_upset_thread.txt'
if len(sys.argv) >= 4:
    textFileName = sys.argv[3]

print(textFileName)

def upsetFactor(winSeed, loseSeed):
    LowerTopXthseed = upsetfactorfinder.topX(upsetfactorfinder.placement(winSeed))
    HigherTopXthseed = upsetfactorfinder.topX(upsetfactorfinder.placement(loseSeed))

    return upsetfactorfinder.seedplacing(LowerTopXthseed) - upsetfactorfinder.seedplacing(HigherTopXthseed)

def parseScore(gqlScore, winName, losName):
    if gqlScore == 'DQ':
        return 'DQ'
    a = gqlScore[gqlScore.find(winName) + len(winName) + 1]
    b = gqlScore[gqlScore.find(losName) + len(losName) + 1]
    return f'{a}-{b}'

universal_perPage = 100

#TODO: MAKE FILTER AS A PARAM
def queryEvent(id, pageNum, perPage):
    return gql.execute('''
query TournamentQuery($page: Int!, $eventID:ID, $perPage: Int!) {
		event(id: $eventID){
    	sets(perPage: $perPage, page: $page) {
      	pageInfo {
      	  total
      	  totalPages
      	  page
      	  perPage
      	}
        nodes {
          id
          winnerId
          fullRoundText
          state
          displayScore
          slots {
            slotIndex
            entrant {
              id
              name
              initialSeedNum
            }
          }
        }
    }
  	}
	}
    ''',
    {
        "page": pageNum,
        "eventID": event_id,
        "perPage": perPage
    })


tourney_ongoing = True
#Set of set id's to make sure no duplicates
checkSet = set()

event = json.loads(queryEvent(event_id, 1, universal_perPage))
#total amount of sets in the event
totalPages = event["data"]["event"]["sets"]["pageInfo"]["totalPages"]
totalSets = event["data"]["event"]["sets"]["pageInfo"]["total"]
#####
print(f'Total sets to check = {totalSets}')
print(f'Total pages to check = {totalPages}')
numChecks = 0

scriptStartTime = time.localtime()
print(f'Auto upset script starting at {time.strftime("%H:%M:%S", scriptStartTime)}')

while tourney_ongoing:
    print(f'Beginning check {numChecks + 1}')
    for page in range(totalPages):
        print(f'PAGE {page+1}')
        event = json.loads(queryEvent(event_id, page+1, universal_perPage))
        nodes = event["data"]["event"]["sets"]["nodes"]
        for currSet in nodes:
            if currSet["id"] not in checkSet and currSet["state"] == 3:
                checkSet.add(currSet["id"])
                upset = 0
                setWinnerID = currSet["winnerId"]
                winnerSeed = 0
                winnerName = ''
                loserSeed = 0
                loserName = ''
                for slot in currSet["slots"]:
                    if slot["entrant"]["id"] == setWinnerID:
                        winnerSeed = slot["entrant"]["initialSeedNum"]
                        winnerName = slot["entrant"]["name"]
                    else:
                        loserSeed = slot["entrant"]["initialSeedNum"]
                        loserName = slot["entrant"]["name"]
                upset = upsetFactor(winnerSeed, loserSeed)
                if upset > 0:
                    print('Upset found:')
                    #begin tweet format
                    bracketside = ''
                    if "Win" in currSet["fullRoundText"]:
                        bracketside = '🔵W'
                    elif "Los" in currSet["fullRoundText"]:
                        bracketside = '🔴L'
                    elif "Grand" in currSet["fullRoundText"]:
                        if "Reset" in currSet["fullRoundText"]:
                            bracketside = "Grands Reset"
                        else:
                            bracketside = "Grand Finals"
                    
                    tweetText = f'{bracketside} {winnerName} {parseScore(currSet["displayScore"], winnerName, loserName)} {loserName} upset factor: {upset} {hashtag}'

                    print(tweetText + '\n')

                    #Writing upset to file
                    twFile = open(textFileName, 'a', encoding='UTF-8')
                    twFile.write(tweetText + '\n')
                    twFile.close()
    numChecks += 1
    print(f'So far checked {len(checkSet)} sets')
    # if len(checkSet) >= totalSets:
    #     tourney_ongoing = False
    #     t = time.localtime()
    #     print(f'All sets are complete. Stopping script at {time.strftime("%H:%M:%S", t)}')
    #     break
    t = time.localtime()
    print(f'Sleeping for 5 minutes starting at {time.strftime("%H:%M:%S", t)}. Script started at {time.strftime("%H:%M:%S", scriptStartTime)}')
    time.sleep(300)
tourney_ongoing = False