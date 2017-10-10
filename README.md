# Cheap Translation using Python and Lexicons

This code will translate an input file using a dictionary. The input file must be in the CoNLL column format. For 
example, see [eng.conll](eng.conll).


## Requirements

* python 3
* [swig-srilm wrapper](https://github.com/desilinguist/swig-srilm/)
* (Optional) [gensim](https://radimrehurek.com/gensim/) (if you want to use the word vector expansion part)
* (Optional, but recommended) Language model created by [SRILM](http://www.speech.sri.com/projects/srilm/).

Here's the simplest possible way to make a language model (`<input file>` is just a text file):

    $ ngram-count -text <input file> -lm <output file>

See [ngram-count](http://www.speech.sri.com/projects/srilm/manpages/ngram-count.1.html) for more documentation.

## Usage

To translate eng.conll from English (eng) into Turkish (tur):

    $ python translate.py -i eng.conll -o tur.conll -t tur

`eng.conll` is inculded in the repository. `tur.conll` is produced when this is done. Notice that the `-s` argument is not needed, because English is the default source.

To translate interactively (from English, to Turkish):

    $ python translate.py -t tur


There are some config variables in the [utils.py](utils.py). Be sure to set these 
  
 
## Paper
This code was used in the paper: 'Cheap Translation for Cross-Lingual Named Entity Recognition' in EMNLP2017. See [here](http://cogcomp.org/page/publication_view/818) for details.

    
## Lexicons
In the [paper](http://cogcomp.org/page/publication_view/818), we used lexicons from the Masterlex project at University 
of Washington. These are not yet available for public release, but in the meantime, we recommend using the excellent set
of lexicons from Ellie Pavlick et al described in [this paper](http://aclweb.org/anthology/Q14-1007), and available for download [here](https://www.seas.upenn.edu/~epavlick/data.html).

The Pavlick dictionary set is the default setting in [utils.py](utils.py)

## Google Translate API Client

senttrans.py will translate on a sentence level using the [Google Translate API](https://cloud.google.com/translate/docs/). This code is somewhat out of 
date, and may not work any more.  


The Google Translate API Client can be a little confusing. See [this page](https://developers.google.com/api-client-library/python/apis/translate/v2)
for ideas on how to use the library. You will need an API key, which will cost you money.

Installation:

    $ pip install --upgrade google-api-python-client

[Here's](https://github.com/google/google-api-python-client/tree/master/samples/translate) a useful example.
