PTYSTATS Auto Upset thread formatter thing
Works for double elimination bracket events only

REQUIRES START.GG API TOKEN
for more information visit https://developer.start.gg/docs/intro/

place token in ".env" file in same directory as auto.py
the line should read:
STARTGG_TOKEN=<your-token>

TO RETRIEVE EVENT ID:
$ python eventIDtool.py <tournament-slug>

<tournament-slug> is the part of the start.gg URL after /tournament/

example:
https://www.start.gg/tournament/low-tide-city-2022/
                        (Don't forget the quotes)
$ python eventIDtool.py "low-tide-city-2022"

Low Tide City 2022 Events and IDs
Slap City 2v2: 675609
Smash Bros Ultimate Squad Strike: 622429    
Smash Bros. Ultimate 2v2: 622421
Melee Low Tier 1v1: 622430
Melee 2v2: 622420
Smash 64 2v2: 625238
Rivals of Aether 2v2: 664648
Rivals of Aether Workshop Tournament: 664647
Smash Bros. Ultimate 1v1: 622416
Melee 1v1: 622417
Splatoon 2 4v4: 664616
Smash 64 1v1: 622419
Slap City 1v1: 675608
Rivals of Aether 1v1: 664645

To start auto script for an event:
$ python auto.py <event-id> <hashtag> <textfile-name>

in the absence of <textfile-name>, upsets will be written to "<event-id>_upset_thread.txt"

example:

$ python auto.py 662417 "#lowtidemeleesinglesupsets" "ltc.txt"

The script will check all sets for event marked as completed and calculate any upsets.
Upsets with upset factor > 0 will be formatted, then written both to output and text file.
Every 5 minutes, the script will check again.
CTRL+C to forcibly exit. Restarting the script WILL DUPLICATE upset entries.


