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

This relies on the [swig-srilm wrapper](https://github.com/desilinguist/swig-srilm/)

## Usage

To translate a file:

    $ ./translate.py 

To translate interactively (from English, to Turkish):

    $ ./translate.py -t tur

