from utils import *
from collections import defaultdict
from itertools import product
import gzip
import codecs


def dictname(target):
    """ This uses the naming convention from Ellie Pavlick's
    mechanical turk dictionaries.

    :param target: target language code (2 or 3 letters)
    """
    if USEMASTERLEX:
        return LEXICONPATH + "{0}-eng.masterlex.txt.gz".format(target)
    elif USEPAVLICK:
        return LEXICONPATH + "/dict.{}".format(target)


def readlexicon(fname):
    """ Reads files from Katrin Kirchhoff/Mark H-J lexicons
    """
    f2e = defaultdict(set)
    e2f = defaultdict(set)

    logger.info("Reading " + fname)
    if USEMASTERLEX:
        with gzip.open(fname, "rb") as f:
            lines = f.readlines()
    elif USEPAVLICK:
        with open(fname, "r") as f:
            lines = f.readlines()

        # some lines have multiple definitions in them.
        # expand these to multiple lines
        newlines = []
        for line in lines:
            sline = line.strip().split("\t")
            for eng in sline[1:]:
                newlines.append(sline[0] + "\t" + eng)
        lines = newlines

    pairs = defaultdict(int)

    for line in lines:
        sline = line.strip().split("\t")

        if USEMASTERLEX:
            f = sline[0]
            e = sline[5]
        elif USEPAVLICK:
            f = sline[0]
            e = sline[1]

        pairs[(e, f)] += 1
        pairs[(e.lower(), f.lower())] += 1
        
        ewords = e.split()
        fwords = f.split()
        for ew, fw in product(ewords, fwords):
            pairs[(ew, fw)] += 1
            pairs[(ew.lower(), fw.lower())] += 1

        f2e[f].add(e)
        f2e[f.lower()].add(e)
        
        e2f[e].add(f)
        e2f[e.lower()].add(f)

    logger.info("Num e keys: {0}.".format(len(e2f)))
    numentries = sum(map(len, list(e2f.values())))
    logger.info("Num entries: {0}".format(numentries))
    logger.info("Avg keys per entry: {0}".format(float(numentries) / len(e2f)))
    
    return e2f, f2e, pairs


def getlexiconmapping(source, target):
    dct = defaultdict(lambda: defaultdict(float))
    
    if source == "eng":
        e2f, f2e, pairs = readlexicon(dictname(target))

        # normalize the dictionary with scores.
        for k in list(e2f.keys()):

            scores = [(w, pairs[(k,w)]) for w in e2f[k]]

            t1 = float(sum([p[1] for p in scores]))
            t1 = max(0.1, t1)
            nscores = sorted([(p[0], p[1] / t1) for p in scores], key=lambda p: p[1])

            for p in nscores:
                dct[k][p[0]] += p[1]
            
        return dct, f2e

    if target == "eng":
        e2f, f2e, pairs = readlexicon(dictname(source))
        
        # normalize the dictionary with scores.
        for k in list(f2e.keys()):
            
            # vive la difference (VLD): pair is reversed.
            scores = [(w, pairs[(w,k)]) for w in f2e[k]]
            t1 = float(sum([p[1] for p in scores]))
            t1 = max(0.1, t1)
            nscores = sorted([(p[0], p[1] / t1) for p in scores], key=lambda p: p[1])

            for p in nscores:
                dct[k][p[0]] += p[1]

        return dct, e2f
    
    l1dict, l1rev, pairs1 = readlexicon(dictname(source))
    l2dict, l2rev, pairs2 = readlexicon(dictname(target))

    # these are all english keys
    l1set = set(l1dict.keys())
    l2set = set(l2dict.keys())
    
    inter = l1set.intersection(l2set)
    print("Size of intersection:", len(inter))

    for s in inter:
        # l1dict[s] is a set. Just get scores for each element of the set. 
        scores1 = [(w, pairs1[(s,w)]) for w in l1dict[s]]
        scores2 = [(w, pairs2[(s,w)]) for w in l2dict[s]]
        
        t1 = float(sum([p[1] for p in scores1]))
        t2 = float(sum([p[1] for p in scores2]))

        # to avoid division by 0
        t1 = max(0.1, t1)
        t2 = max(0.1, t2)
        
        nscores1 = sorted([(p[0], p[1] / t1) for p in scores1], key=lambda p: p[1])
        nscores2 = sorted([(p[0], p[1] / t2) for p in scores2], key=lambda p: p[1])

        for p1,p2 in product(nscores1, nscores2):            
            dct[p1[0]][p2[0]] += p1[1] * p2[1]

    return dct, None


def getFAfile(lang):
    """ This creates a file for fast_align training """
    dct = readlexicon(dictname(lang))

    out = codecs.open("text.eng-"+lang, "w", "utf8")
    
    for key in dct:
        vals = dct[key]
        for val in vals:
            out.write(key.lower() + " ||| " + val.lower() + "\n")

    out.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="")

    parser.add_argument("--source", "-s", help="Source language code (3 letter)")
    parser.add_argument("--target", "-t", help="Target language code (3 letter)")
    
    args = parser.parse_args()
        
    dct, f2e = getlexiconmapping(args.source, args.target)