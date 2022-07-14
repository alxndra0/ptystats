
from math import log, modf, ceil

'''
welcome to the pty stats program
i use this program for tournaments to calculate upset factors for tournaments as they happen
it works in a few steps

THIS ONLY WORKS FOR DOUBLE ELIMINATION TOURNAMENTS!! a different version would have to be made for single elim or triple elim

it takes a seeding
and converts that to an expected placing
which it then converts to a top X finish (e.g. top 32 finish or top 8 finish)
which it then converts to the final projected loser's round you're expected to finish at
        top 1 -> 1st round
        top 2 -> 2nd round
        top 3 -> 3rd round
        top 4 -> 4th round
        top 6 -> 5th round
        top 8 -> 6th round
        top 12 -> 7th round
        top 16 -> 8th round
        top 24 -> 9th round
        top 32 -> 10th round
        top 48 -> 11th round
        so on and so forth

then you do winner's round number - loser's round number to get upset factor
e.g.    51 seed beats 11 seed
        51 -> 49th place -> top 64 -> fplr 12
        11 -> 9th place -> top 12 -> fplr 7
        12 - 7 = upset factor 5

you may wonder "why go from seeding to placing to round? why not just go seeding to round?"
        a: it's just easier that way. i've thought about ways to go from seeding to round 
        in one step but they usually involve sneakly going to the placement first because 
        it's a nice way to normalize the seeding


'''




def placement(n): #convert a seeding to the expected placement 
    if n < 5:     #e.g. 40 seed is expected to place 33rd
        return n        
    if "1" in bin(n)[4:]:
        pass
    else:
        n -=1
    lenbin = len(bin(n))
    cleaned = bin(n)[:4]+"0"*(lenbin-4)    
    n = int(cleaned,2)
    n += 1    
    return n

def topX(n): #convert an expected placement to the "round of X" number
    if n < 5:# e.g. expected to place 33rd means round of / top 48 finish        
        return n
    n -=1
    helper = int(log(n,2)) - 1
    j = n + 2**helper 
    return j

def seedplacing(topx): # convert a round of / top X finish to a final projected loser's round 
                       # e.g. top 48 finish is an FPLR of 11 (log2(48) = 5.589, so 5*2 +1 = 11)
    if topx < 5:
        return topx
    j = log(topx,2)
    mfj = modf(j)
    sp =int( mfj[1] * 2 + ceil(mfj[0]))
    
    return sp

def seedingtoseedplace(seed): #function that does the three above functions to convert
    seedplacing(topX(placement(seed))) # a seeding to a final projected losers round in one step

def upsetfactor(winnerseed,loserseed):  #function takes two seeds as input and 
    wsp = seedingtoseedplace(winnerseed)#returns the upset factor if the first one beat the second one
    lsp = seedingtoseedplace(loserseed)
    ufactor = wsp-lsp 
    return ufactor

if __name__ == "main":
    f = open("seeding.csv")      
    seedlist = f.readlines()
    f.close()
    seeddictionary = {}
    for seeding in seedlist:
        s = seeding.split(",")
        seeddictionary.update({s[11].strip('"'):int(s[4])}) 

    print(seeddictionary)



    tournamentname = "Get Smashed at Tin Roof"

    while(True):
        try:
            winner = input("gamertag of winning player:\n")
            loser = input("gamertag of losing player:\n")
            winningseed = seeddictionary[winner]
            print("found winning gamer!")
            losingseed = seeddictionary[loser]
            print("found losing gamer")
            
            print("surprise margin finder:")
            print("winning seed: {}".format(winningseed))
            print("lower seed: {}".format(losingseed))
            if (winningseed > losingseed):
                LowerTopXthseed = topX(placement(winningseed))
                HigherTopXthseed = topX(placement(losingseed))

                surprisemargin = seedplacing(LowerTopXthseed) - seedplacing(HigherTopXthseed)
                if (surprisemargin > 0):
                    bracketside = int(input("W(inners) or L(osers):\n"))
                    bracketside = "🔵W" if bracketside else "🔴L"
                    setcount = input("Set count? :\n")
                    SM = "surprise margin of : {}".format(surprisemargin)
                    tweet = "{} {} {} {}, {} @ {}".format(bracketside,winner,setcount,loser,SM,tournamentname)
                    print (tweet)
                    writer = open("upsetsTR.txt", "a", encoding="utf-8")
                    writer.write(tweet)
                    writer.write("\n")
                    writer.close()
                else:
                    print("upset factor 0")
            else:
                print("no upset")
        except KeyError:
            print("one or more gamertags not found! please try again")
        

