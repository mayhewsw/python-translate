#!/usr/bin/python
#  -*- coding: utf-8 -*-
import codecs,os,re
import HTMLParser
from collections import defaultdict
import string, math
from srilm import *
from utils import *


class Translator:

    def __init__(self, method, source, target):
        self.method = method
        self.source = source
        self.target = target
        self.lm = None

        self.load_dictionary()
        self.load_lm()
        
        
    def load_dictionary(self):
        if self.method == "google":
            #import googletrans
            #self.dct = googletrans.getgooglemapping(fname, self.source, self.target)
            print "Doesn't work right now..."
        elif self.method == "lexicon":
            import lexicons        
            self.dct,_ = lexicons.getlexiconmapping(self.source, self.target)

            #print "HACKING DICTIONARY WITH UN/US TOKENIZATION!"
            #self.dct["U.N."] = defaultdict(float)
            #self.dct["U.N."]["U . N ."] += 1
            #self.dct["U.S."] = defaultdict(float)
            #self.dct["U.S."]["U . S ."] += 1

        else:
            print "Mapping needs to be lexicon or google, is:", self.method
            self.dct = None


    def load_lm(self):
        # read the LM    
        self.lm = initLM(5)
        tgt2 = langmap[self.target]
        LMPATH="/shared/corpora/ner/lorelei/"+tgt2+"/"+tgt2+"-lm.txt"

        if os.path.exists(LMPATH):
            logger.info("Reading " + LMPATH)
            readLM(self.lm, LMPATH)
            logger.info("done reading.")
        else:
            logger.info("No LM today")


    def translate(self, lines):

        outlines = []
        missing = 0
        total = 0
        missedwords = defaultdict(int)
        h = HTMLParser.HTMLParser()

        # this is a set of words to be ignored when counting translation failures
        ignores = list(string.punctuation)
        ignores.extend(map(str, range(2050)))
        ignores.append("-DOCSTART-")
        ignores.append("--")

        # with word translations in hand, run over file again and translate each word
        # if Google translation is not available for a word, it returns that word.
        # confusing b/c it is possible that the translation is the exact word.    
        i = 0
        progress = 0
        window = 4
        while True:
            currprog = i / float(len(lines))
            if currprog > progress+0.1:
                logger.info(currprog)
                progress = currprog

            # Stopping condition!
            if i >= len(lines):
                break

            # open a window after position i, but stop if encounter a break.
            words = []
            tags = set()
            for line in lines[i:i+window]:
                wd = getword(line)
                tag = gettag(line)
                if wd is None:
                    break

                words.append(wd)
                tags.add(tag)

            # allow that no words will be found (empty line)
            if len(words) == 0:
                outlines.append("\n")
                i += 1
                continue

            # the current line.
            sline = lines[i].split("\t")

            # if the line has an empty word, fill it with something.
            if len(sline) > 5 and sline[5] == "":
                sline[5] = "x"

            addlines = []

            # start with the full number of words, and remove words as necessary
            found = False
            for jj in range(len(words), 0, -1):
                srcwords = words[:jj]
                srcphrase = " ".join(srcwords)
                
                hit = srcphrase in self.dct

                # try lower case
                if not hit:
                    hit = srcphrase.lower() in self.dct
                    if hit:
                        srcphrase = srcphrase.lower()                
                
                if not hit:
                    srcexpand = englishexpand(srcphrase)
                    #srcexpand = uzbekexpand(srcphrase)
                    for w in srcexpand:
                        if w in self.dct:
                            #print w, "in dct!"
                            srcphrase = w
                            hit = srcphrase in self.dct
                            break
                
                # Don't translate PER/ORG
                #if "B-PER" in tags or "I-PER" in tags:
                #    hit = False
                    
                if hit:
                    #logger.debug(srcphrase)

                    # these are now also associated with a score.
                    opts = self.dct[srcphrase]

                    # ngram decides how far back we will go
                    ngram = min(3, len(outlines))
                    context = []
                    for rev in range(-ngram, 0, 1):
                        c = getword(outlines[rev])
                        if c is None:
                            context = []
                        else:
                            context.append(c)

                    #print srcphrase
                    newopts = dict(opts)
                    # select the best option using LM
                    if self.lm:
                        for opt in newopts:
                            score = newopts[opt] + 0.0000001
                            if len(opt.split()) == 0:
                                continue
                            text = " ".join(context + [opt.split()[0]]).encode("utf8")
                            lmscore = getNgramProb(self.lm, text, len(context)+1)
                            newopts[opt] = lmscore + math.log(score)
                            #print opt, lmscore, score
                            #newopts[opt] = math.log(score)
                            #newopts[opt] = random.random()

                    best = max(newopts.items(), key=lambda p: p[1])
                    w = best[0]

                    logger.debug(u"{0} : {1} ({2})".format(srcphrase, best[0], best[1]))

                    w = h.unescape(w)

                    # if last word is an empty line capitalize this word.
                    if len(outlines) > 0  and getword(outlines[-1]) == None:
                        w = w.capitalize()
                    
                    transwords = w.split()

                    # this allows us to transfer exact lines from source
                    kk = 0
                    for wind,word in enumerate(transwords):
                        line = lines[i + kk]
                        newsline = line.split("\t")
                        newsline[5] = word

                        if wind > 0 and len(srcwords) == 1 and lines[i][0] == "B":
                            _,tag = newsline[0].split("-")
                            newsline[0] = "I-" + tag

                        addlines.append("\t".join(newsline))

                        if kk < len(srcwords) - 1:
                            kk+=1 

                    i += jj                

                    found = True
                    break

            # word not in dict. srcphrase has just 1 token
            if not found:
                # check if lexicon doesn't contain element
                #removes = ["the", "said", "was", "has", "been", "were", "'s", "are"]
                removes = []
                if srcphrase in removes:
                    pass

                
                res = re.search('(\W+)', srcphrase)
                if res is not None:
                    groups = res.groups()
                else:
                    groups = []

                # Don't want this special punctuation trick!!!
                if len(groups) > 0 and False:

                    # if there is a tag.
                    tag = sline[0]

                    g = groups[0]
                    ssp = srcphrase.split(g)

                    for chunk in ssp:
                        sline[0] = tag
                        sline[5] = chunk
                        if len(chunk) > 0:
                            addlines.append("\t".join(sline))

                        if tag[0] == "B":
                            tag = "I" + tag[1:]
                        
                        sline[0] = tag
                        sline[5] = g
                        addlines.append("\t".join(sline))
                        
                    # because we added too many...
                    addlines.pop()

                    missing += 1
                    
                else:
                    #logger.debug("skip: {0}".format(srcphrase))
                    addlines.append("\t".join(sline))
                    if srcphrase not in ignores:
                        missing += 1
                        missedwords[srcphrase] += 1
                i += 1

            total += 1

            for line in addlines:
                outlines.append(line) 

        coverage = (total - missing) / float(total)    
        logger.info("translated {0} of the corpus".format(coverage))

        if len(missedwords) > 0:
            logger.debug("Most popular missed words:")
            #for w,s in sorted(missedwords.items(), key=lambda p: p[1], reverse=True)[:10]:
            #    logger.debug("{0} : {1}".format(w,s))
            
        return outlines
        
            
    def translate_file(self, fname, outfname, format="conll"):
        """ This actually does the translation, given a word mapping."""

        if format == "conll":
            lines = readconll(fname)
        elif format == "plaintext":
            lines = readplaintext(fname)
        else:
            print "Format not known: " + format
            exit()

        # everything is done in conll format. That is... one word per line. 
        outlines = self.translate(lines)
        
            
        print "Writing to:", outfname
        if format == "conll":
            writeconll(outfname, outlines)
        elif format == "plaintext":
            writeplaintext(outfname, outlines)
        else:
            print "Unknown format: " + format
    

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Translate a CoNLL file")

    parser.add_argument("--input", "-i",help="Input file name (fifth word of each row is translated)")
    parser.add_argument("--output", "-o",help="Output file. Format: origword  transword")
    parser.add_argument("--method",help="Either google, or lexicon", choices=["lexicon", "google"], default="lexicon")
    parser.add_argument("--source","-s", help="Source language code (3 letter)", default="eng")
    parser.add_argument("--target","-t", help="Target language code (3 letter)", required=True)
    parser.add_argument("--format","-f", help="Format of input file", choices=["conll", "plaintext"], default="conll")

    
    args = parser.parse_args()

    tt = Translator(args.method, args.source, args.target)
    
    if args.input and args.output:
        tt.translate_file(args.input, args.output, args.format)
    else:
        print "Interactively translating from",args.source,"to", args.target
        srctext = ""
        while srctext not in ["q", "exit", "Q"]:
            srctext = raw_input(args.source + ">> ")
            if srctext == "":
                continue
            
            lines = plaintexttolines(srctext)
            print args.target + ": " + linestoplaintext(tt.translate(lines))[0].strip()
