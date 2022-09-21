import os
import sys
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

def upsetFactor(winSeed, loseSeed):
    LowerTopXthseed = upsetfactorfinder.topX(upsetfactorfinder.placement(winSeed))
    HigherTopXthseed = upsetfactorfinder.topX(upsetfactorfinder.placement(loseSeed))

    return upsetfactorfinder.seedplacing(LowerTopXthseed) - upsetfactorfinder.seedplacing(HigherTopXthseed)

def parseScore(gqlScore, winName, losName):
    a = gqlScore[gqlScore.find(winName) + len(winName) + 1]
    b = gqlScore[gqlScore.find(losName) + len(losName) + 1]
    return f'{a}-{b}'

def queryEvent(id, pageNum):
    return gql.execute('''
query TournamentQuery($page: Int!, $eventID:ID) {
		event(id: $eventID){
    	sets(perPage: 1, page: $page) {
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
        "eventID": event_id
    })

#For loop that goes through each set.
# If set is completed, determine upset factor.
#   If greater than 0, format and send tweet.
#   Also mark the set as checked to avoid duplicate tweets.

tourney_ongoing = True
currPage = 1
#Set of set id's to make sure no duplicates
checkSet = set()

event = json.loads(queryEvent(event_id, currPage))
#total amount of sets in the event
totalSets = event["data"]["event"]["sets"]["pageInfo"]["total"]


while tourney_ongoing:
    for i in range(totalSets):
        event = json.loads(queryEvent(event_id, i+1))
        currSet = event["data"]["event"]["sets"]["nodes"][0]
        if currSet["id"] not in checkSet:
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
                
                # tweetText = f'{bracketside} {currSet["displayScore"]} upset factor: {upset} {hashtag}'
                tweetText = f'{bracketside} {winnerName} {parseScore(currSet["displayScore"], winnerName, loserName)} {loserName} upset factor: {upset} {hashtag}'
                print(tweetText)
    tourney_ongoing = False