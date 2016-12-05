from googleapiclient.discovery import build
import shelve
import codecs
import utils

API_KEY = utils.getapikey()

def getgooglemapping(fname, source, target):
    """
    Given a filename and a source and target languages, this will gather words
    from the the fifth column of each tab-sep row in fname and create a word
    mapping from source to target. Note that if Google cannot find a translation,
    then it will simply return the word as is. 
    
    Language codes are Google two letter codes (en, uz, tr, de, etc.)

    Results are stored in python shelves.
    """

    service = build('translate', 'v2',developerKey=API_KEY)
    
    memo = shelve.open("shelves/translatedict-" + source + "-" + target + ".shelf")

    with codecs.open(fname, "r", "utf-8") as f:
        lines = f.readlines()        

    words = []
    chars = 0
    
    for line in lines:            
        sline = line.split("\t")
        if len(sline) > 5:
            srcword = sline[5].encode("utf8").strip()
            if srcword not in memo:
                words.append(srcword.decode("utf8"))
                chars += len(srcword)

    price = 20 / 1000000.
    cost = price * chars
                
    print "It will cost",cost,"to run this script."
    c = ""
    if cost == 0.0:
        print "zero cost, so running automatically..."
        c = "y"
    while c not in ["y", "n"]:
        c = raw_input("Continue? (y/n)  ")
        if c == "y":
            break
        elif c == "n":
            exit()
        else:
            print "please enter y or n"

    # gather a list of words to be translated.
    for i in range(0, len(words), 20):
        iwords = words[i:i+75]
        print "size of request:",len(iwords)
        try:
            response = service.translations().list(source=source,target=target, q=iwords).execute()
            if len(response["translations"]) > 0:
                translations = response["translations"]
                for w,t in zip(iwords,translations):
                    tword = t["translatedText"]
                    # memo can only take strings...
                    memo[w.encode("utf8")] = tword
            else:
                print "WHAAAAT"

        except Exception as e:
            print "Whoops... exception"
            print e
            import traceback
            traceback.print_exc()
            

    ret = dict(memo)
    memo.close()
    return ret

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Get Google mapping")

    parser.add_argument("fname",help="Input file name (fifth word of each row is translated)")
    parser.add_argument("source",help="Source language code (2 letter)")
    parser.add_argument("target",help="Target language code (2 letter)")

    args = parser.parse_args()
    
    dct = getgooglemapping(args.fname,args.source, args.target)
    print dct
