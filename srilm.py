# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.8
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.





from sys import version_info
if version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_srilm', [dirname(__file__)])
        except ImportError:
            import _srilm
            return _srilm
        if fp is not None:
            try:
                _mod = imp.load_module('_srilm', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _srilm = swig_import_helper()
    del swig_import_helper
else:
    import _srilm
del version_info
try:
    _swig_property = property
except NameError:
    pass  # Python < 2.2 doesn't have 'property'.


def _swig_setattr_nondynamic(self, class_type, name, value, static=1):
    if (name == "thisown"):
        return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'SwigPyObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name, None)
    if method:
        return method(self, value)
    if (not static):
        if _newclass:
            object.__setattr__(self, name, value)
        else:
            self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)


def _swig_setattr(self, class_type, name, value):
    return _swig_setattr_nondynamic(self, class_type, name, value, 0)


def _swig_getattr_nondynamic(self, class_type, name, static=1):
    if (name == "thisown"):
        return self.this.own()
    method = class_type.__swig_getmethods__.get(name, None)
    if method:
        return method(self)
    if (not static):
        return object.__getattr__(self, name)
    else:
        raise AttributeError(name)

def _swig_getattr(self, class_type, name):
    return _swig_getattr_nondynamic(self, class_type, name, 0)


def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except Exception:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

try:
    _object = object
    _newclass = 1
except AttributeError:
    class _object:
        pass
    _newclass = 0



def initLM(order):
    return _srilm.initLM(order)
initLM = _srilm.initLM

def deleteLM(ngram):
    return _srilm.deleteLM(ngram)
deleteLM = _srilm.deleteLM

def getIndexForWord(s):
    return _srilm.getIndexForWord(s)
getIndexForWord = _srilm.getIndexForWord

def getWordForIndex(i):
    return _srilm.getWordForIndex(i)
getWordForIndex = _srilm.getWordForIndex

def readLM(ngram, filename):
    return _srilm.readLM(ngram, filename)
readLM = _srilm.readLM

def getWordProb(ngram, word, context):
    return _srilm.getWordProb(ngram, word, context)
getWordProb = _srilm.getWordProb

def getNgramProb(ngram, ngramstr, order):
    return _srilm.getNgramProb(ngram, ngramstr, order)
getNgramProb = _srilm.getNgramProb

def getUnigramProb(ngram, word):
    return _srilm.getUnigramProb(ngram, word)
getUnigramProb = _srilm.getUnigramProb

def getBigramProb(ngram, ngramstr):
    return _srilm.getBigramProb(ngram, ngramstr)
getBigramProb = _srilm.getBigramProb

def getTrigramProb(ngram, ngramstr):
    return _srilm.getTrigramProb(ngram, ngramstr)
getTrigramProb = _srilm.getTrigramProb

def getSentenceProb(ngram, sentence, length):
    return _srilm.getSentenceProb(ngram, sentence, length)
getSentenceProb = _srilm.getSentenceProb

def getSentencePpl(ngram, sentence, length):
    return _srilm.getSentencePpl(ngram, sentence, length)
getSentencePpl = _srilm.getSentencePpl

def numOOVs(ngram, sentence, length):
    return _srilm.numOOVs(ngram, sentence, length)
numOOVs = _srilm.numOOVs

def corpusStats(ngram, filename, stats):
    return _srilm.corpusStats(ngram, filename, stats)
corpusStats = _srilm.corpusStats

def getCorpusProb(ngram, filename):
    return _srilm.getCorpusProb(ngram, filename)
getCorpusProb = _srilm.getCorpusProb

def getCorpusPpl(ngram, filename):
    return _srilm.getCorpusPpl(ngram, filename)
getCorpusPpl = _srilm.getCorpusPpl

def howManyNgrams(ngram, order):
    return _srilm.howManyNgrams(ngram, order)
howManyNgrams = _srilm.howManyNgrams
# This file is compatible with both classic and new-style classes.

