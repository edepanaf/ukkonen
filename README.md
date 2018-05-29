# ukkonen
Three Python implementations of the algorithm of Ukkonen from 'On-line construction of suffix trees', Algorithmica.
Builds the suffix tree of a given string.

The first implementation 'faithful_ukkonen' works only for string written in lower-case letters.
It is a faithful line by line implementation of the algorithm presented in the paper.
It is NOT practical.

The second implementation 'abstract_ukkonen' works on any alphabet and slightly differs from the original.
The relevant structures are abstracted as objects.
It has been improved by Olivier Buob and has ploting options.

The third implementation 'short_ukkonen' is way shorter (50 effective code lines) but readable.
