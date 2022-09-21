import os
import sys
from dotenv import load_dotenv
import json
from graphqlclient import GraphQLClient

load_dotenv()
STARTGGTOKEN = os.getenv('STARTGG_TOKEN')
ggApiVersion = 'alpha'

gql = GraphQLClient('https://api.start.gg/gql/' + ggApiVersion)
gql.inject_token('Bearer ' + STARTGGTOKEN)

tourneyslug = sys.argv[1]

getTourneyBySlug = gql.execute('''
query TournamentInfo($slug: String!) {
        tournament(slug: $slug) {
           name
          events {
            name
            id
          }
        }
    }
    ''',
    {
        "slug": tourneyslug
    })
tourney = json.loads(getTourneyBySlug)

print(f'{tourney["data"]["tournament"]["name"]} Events and IDs')
for event in tourney["data"]["tournament"]["events"]:
    print(f'{event["name"]}: {event["id"]}')
