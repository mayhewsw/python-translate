from apiclient.discovery import build
import codecs
import html.parser
import shelve
from collections import defaultdict
import string
from utils import *

# NICE TRY INTERNET
API_KEY = getapikey()

def translatefile(fname, outfname, source, target, format="conll"):
    """
    Given a filename, an outfname, and a source and target languages, this will translate
    the first word of each tab-sep row in fname from source to target and write to outfname. Language codes are Google
    two letter codes (en, uz, tr, de, etc.)
    """

    outlines = []
    service = build('translate', 'v2',developerKey=API_KEY)

    h = html.parser.HTMLParser()
    
    if format == "conll":
        lines = readconll(fname)
    elif format == "plaintext":
        lines = readplaintext(fname)
    else:
        print("Format not known: " + format)
        exit()

        
    memo = shelve.open("shelves/sents-" + source + "-" + target + ".shelf")
        
    sents = []
    sent = ""

    # gather all sentences
    for line in lines:            
        sline = line.split("\t")
        if len(sline) > 5:
            srcword = str(sline[5]).strip()
            sep = " "
            #if srcword in ["'s","n't","'ve"]:
            #    sep = ""
            sent += sep + srcword
            
        else:
            sent = sent.strip()
            sents.append(sent)
            sent = ""

            #if len(sents) > 10:
            #break
            
    chars = 0
    trans = []
    for sent in sents:
        if sent not in memo:
            trans.append(sent)
            chars += len(sent)

    price = 20 / 1000000.
    cost = price * chars
                
    print("It will cost",cost,"to run this script.")
    c = ""
    if cost == 0.0:
        print("zero cost, so running automatically...")
        c = "y"
    while c not in ["y", "n"]:
        c = input("Continue? (y/n)  ")
        if c == "y":
            break
        elif c == "n":
            exit()
        else:
            print("please enter y or n")

    outsents = []
    # gather a list of words to be translated.
    for i in range(0, len(trans), 20):
        isents = trans[i:i+50]
        print("size of request:",len(isents))
        try:
            response = service.translations().list(source=source,target=target, q=isents).execute()
            if len(response["translations"]) > 0:
                translations = response["translations"]
                for w,t in zip(isents,translations):
                    tsent = t["translatedText"]
                    memo[w] = tsent
                    #outsents.append(tsent)
            else:
                print("WHAAAAT")

        except Exception as e:
            print("Whoops... exception")
            print(e)

    outlines = []

    # these will be written to a file for fast_align to use.
    parlines = []
    
    for sent in sents:        
        outsent = memo[sent]

        # fix outsent?
        # try some simple tokenization.
        outsent = h.unescape(outsent)

        tokens = []
        for word in outsent.split():
            while len(word) > 0 and word[0] in string.punctuation:
                tokens.append(word[0])
                word = word[1:]

            if len(word) == 0:
                continue

            after = []
            while len(word) > 0 and word[-1] in string.punctuation:
                after.insert(0, word[-1])
                word = word[:-1]

            tokens.append(word)
            tokens.extend(after)

        outsent = " ".join(tokens)
        
        parlines.append(sent + " ||| " + outsent + "\n")
        
        #out.write(line);
        ssent = outsent.split()
        for w in ssent:
            w = h.unescape(w)

            if w.endswith("."):
                outlines.append("O\t0\t0\tx\tx\t" + w[:-1] + "\tx\tx\t0\n")
                outlines.append("O\t0\t0\tx\tx\t.\tx\tx\t0\n")
            else:
                outlines.append("O\t0\t0\tx\tx\t" + w + "\tx\tx\t0\n")
                   
        outlines.append("\n")

    with codecs.open("text.en-" + target, "w", "utf8") as out:
        print("Writing to: text.en-" + target) 
        for line in parlines:
            out.write(line)

    print("Writing to:", outfname)
    if format == "conll":
        writeconll(outfname, outlines)
    elif format == "plaintext":
        writeplaintext(outfname, outlines)
    else:
        print("Unknown format: " + format)

    memo.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="")

    parser.add_argument("--input", "-i",help="Input file name (fifth word of each row is translated)", required=True)
    parser.add_argument("--output", "-o",help="Output file.", required=True)
    parser.add_argument("--source","-s", help="Source language code (2 letter)", default="en")
    parser.add_argument("--target","-t", help="Target language code (2 letter)", required=True)
    parser.add_argument("--format","-f", help="Format of input file", choices=["conll", "plaintext"], default="conll")
    
    args = parser.parse_args()
    
    translatefile(args.input, args.output, args.source, args.target, args.format)
    
