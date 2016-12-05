# Simple Translation using Python and Lexicons

This code will translate an input file using a dictionary. The input file must be in the CoNLL column format.

senttrans.py will translate on a sentence level using the [Google Translate API](https://cloud.google.com/translate/docs/). 

## Google Translate API Client

The Google Translate API Client can be a little confusing. See [this page](https://developers.google.com/api-client-library/python/apis/translate/v2)
for ideas on how to use the library. You will need an API key, which will cost you money.

Installation:

    $ pip install --upgrade google-api-python-client

[Here's](https://github.com/google/google-api-python-client/tree/master/samples/translate) a useful example.

## Requirements

* [swig-srilm wrapper](https://github.com/desilinguist/swig-srilm/)
* [gensim](https://radimrehurek.com/gensim/) (if you want to use the word vector expansion part)
* Language model created by [SRILM](http://www.speech.sri.com/projects/srilm/).

Here's the simplest possible way to make a language model (<input file> is just a text file):

    $ ngram-count -text <input file> -lm <output file>

See [ngram-count](http://www.speech.sri.com/projects/srilm/manpages/ngram-count.1.html) for more documentation.

## Usage

To translate a file:

   $ python translate.py -i <input file> -o <output file> -s <src lang> -t <target lang>

To translate interactively (from English, to Turkish):

    $ python translate.py -t tur

