
from math import log, modf, ceil

def placement(n):
    if n < 5:
        #print(n)
        return n
        
    if "1" in bin(n)[4:]:
        pass
    else:
        n -=1
    lenbin = len(bin(n))
    cleaned = bin(n)[:4]+"0"*(lenbin-4)
    #print(cleaned)
    n = int(cleaned,2)
    n += 1
    #print(n)
    return n

def topX(n):
    if n < 5:
        #print(n)
        return n
    n -=1
    #helper = "0b"+ bin(n)[3:]
    helper = int(log(n,2)) - 1
    j = n + 2**helper #int(helper,2)
    #print(j)
    return j

def seedplacing(topx):
    
    if topx < 5:
        return topx
    j = log(topx,2)
    mfj = modf(j)
    sp =int( mfj[1] * 2 + ceil(mfj[0]))
    
    return sp

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
        

