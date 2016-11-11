#!/usr/bin/python
#  -*- coding: utf-8 -*-
import codecs,os
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
            self.dct = lexicons.getlexiconmapping(self.source, self.target)
        else:
            print "Mapping needs to be lexicon or google, is:", self.method
            self.dct = None

    def load_lm(self):
        # read the LM    
        self.lm = initLM(5)
        tgt2 = langmap[self.target]
        LMPATH="/shared/corpora/ner/lorelei/"+tgt2+"/"+tgt2+"-lm.txt"

        if os.path.exists(LMPATH):
            print "Reading ", LMPATH    
            readLM(self.lm, LMPATH)
            print "done reading."
        else:
            print "No LM today"

                    

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
                print currprog
                progress = currprog

            # Stopping condition!
            if i >= len(lines):
                break

            # open a window after position i, but stop if encounter a break.
            words = []
            for line in lines[i:i+window]:
                wd = getword(line)
                if wd is None:
                    break

                words.append(wd)        

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
                srcphrase = " ".join(srcwords).lower()

                hit = srcphrase in self.dct

                if not hit:
                    srcexpand = englishexpand(srcphrase)
                    #srcexpand = uzbekexpand(srcphrase)
                    for w in srcexpand:
                        if w in self.dct:
                            #print w, "in dct!"
                            srcphrase = w
                            hit = srcphrase in self.dct
                            break

                # Don't translate PER names.
                #if jj == 1 and "PER" in sline[0]:
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
                    #print "best:", best[0], best[1]
                    #print

                    #logger.debug(w + ", " + best[1])

                    w = h.unescape(w)

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

            # word not in dict.
            if not found:
                # check if lexicon doesn't contain element
                removes = ["the", "said", "was", "has", "been", "were", "'s", "are"]
                if srcphrase in removes:
                    pass
                else:
                    addlines.append("\t".join(sline))
                    if srcphrase not in ignores:
                        missing += 1
                        missedwords[srcphrase] += 1
                i += 1

            total += 1

            for line in addlines:
                outlines.append(line) 

        coverage = (total - missing) / float(total)    
        print "translated", coverage, "of the corpus."

        print "Most popular missed words:"
        for w,s in sorted(missedwords.items(), key=lambda p: p[1], reverse=True)[:10]:
            print w," : ",s
            
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
        outlines = translate(lines)
        
            
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
        srctext = raw_input(args.source + ">> ")
        lines = plaintexttolines(srctext)
        print tt.translate(lines)
