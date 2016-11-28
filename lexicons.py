from utils import *
from collections import defaultdict
from itertools import product
import gzip,codecs

def readlexicon(target):
    """ Reads files from Katrin Kirchhoff/Mark H-J lexicons

    :param target: target language code (3 letters)
    """
    fname = LEXICONPATH + "{0}-eng.masterlex.txt.gz".format(target)
    f2e = defaultdict(set)
    e2f = defaultdict(set)

    logger.info("Reading " + fname)
    with gzip.open(fname, "rb") as f:
        lines = f.readlines()

    pairs = defaultdict(int)

    for line in lines:
        sline = line.split("\t")
        f = sline[0].decode("utf8")        
        e = sline[5].decode("utf8")

        pairs[(e,f)] += 1
        pairs[(e.lower(),f.lower())] += 1
        
        ewords = e.split()
        fwords = f.split()
        for ew,fw in product(ewords,fwords):
            pairs[(ew,fw)] += 1
            pairs[(ew.lower(),fw.lower())] += 1

        f2e[f].add(e)
        e2f[e].add(f)
        e2f[e.lower()].add(f)

        # TODO: what about f.lower()?

    #print "Num f keys:", len(f2e)
    logger.info("Num e keys: {0}.".format(len(e2f)))
    numentries = sum(map(len, e2f.values()))
    logger.info("Num entries: {0}".format(numentries))
    logger.info("Avg keys per entry: {0}".format(float(numentries) / len(e2f)))
    
    # also read Wikipedia title mapping.
    #p = "/shared/preprocessed/ctsai12/multilingual/wikidump/ta/titles.enta.align"
    #p = "/shared/corpora/ner/gazetteers/tl_pair/org"
    #print "USING", p
    #with codecs.open(p, "r", "utf8") as f:
    #    for line in f:
            #eng,tam = line.replace("title_", "").replace("_", " ").split(" ||| ")
    #        eng,tgl = line.split("\t")
    #        e2f[eng].add(tgl)
            
    return e2f,f2e,pairs

def getlexiconmapping(source, target):
    dct = defaultdict(lambda: defaultdict(float))
    
    if source == "eng":
        e2f,f2e,pairs = readlexicon(target)

        # normalize the dictionary with scores.
        for k in e2f.keys():

            scores = [(w, pairs[(k,w)]) for w in e2f[k]]

            t1 = float(sum(map(lambda p: p[1], scores)))
            t1 = max(0.1, t1)
            nscores = sorted(map(lambda p: (p[0], p[1] / t1), scores), key=lambda p: p[1])

            for p in nscores:
                dct[k][p[0]] += p[1]
            
        return dct,f2e

    if target == "eng":
        raise Exception("eng as target is not supported")
    
    l1dict,l1rev,pairs1 = readlexicon(source)
    l2dict,l2rev,pairs2 = readlexicon(target)

    # these are all english keys
    l1set = set(l1dict.keys())
    l2set = set(l2dict.keys())
    
    inter = l1set.intersection(l2set)
    print "Size of intersection:", len(inter)
    
    #import ipdb; ipdb.set_trace()

    for s in inter:
        # l1dict[s] is a set. Just get scores for each element of the set. 
        scores1 = [(w, pairs1[(s,w)]) for w in l1dict[s]]
        scores2 = [(w, pairs2[(s,w)]) for w in l2dict[s]]
        
        t1 = float(sum(map(lambda p: p[1], scores1)))
        t2 = float(sum(map(lambda p: p[1], scores2)))

        # to avoid division by 0
        t1 = max(0.1, t1)
        t2 = max(0.1, t2)
        
        nscores1 = sorted(map(lambda p: (p[0], p[1] / t1), scores1), key=lambda p: p[1])
        nscores2 = sorted(map(lambda p: (p[0], p[1] / t2), scores2), key=lambda p: p[1])

        #print nscores1
        #print nscores2
        #print
        
        for p1,p2 in product(nscores1, nscores2):            
            #dct[p1[0]].append((p2[0], p1[1] * p2[1]))
            dct[p1[0]][p2[0]] += p1[1] * p2[1]

    return dct,None


def getFAfile(lang):
    dct = readlexicon(lang)

    out = codecs.open("text.eng-"+lang, "w", "utf8")
    
    for key in dct:
        vals = dct[key]
        for val in vals:
            out.write(key.lower() + " ||| " + val.lower() + "\n")

    out.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="")

    parser.add_argument("source",help="")
    parser.add_argument("target",help="")
    
    args = parser.parse_args()
        
    #getFAfile(args.target)
    dct,f2e = getlexiconmapping(args.source, args.target)

    for p in dct["spectacle"]:
        print p
        print f2e[p]
        print
