Finding and Analyzing the Web User identifiers of Third-Party Trackers
======================================================================

Usage
----------
```
python2 FindIdentifier.py
```
A config file is needed to specify the specific databases and related parameters. An example is like this:
```
[databases]
database1 = httpfox.sqlite
database2 = httpfox.sqlite2

[hosts]
host_list = ['adsonar.com']
excep_list = ['google.com']

[identifiers]
minimum_length = 5
occurance = 0.5
level = 2
```
* The **host_list** will specify the **ONLY** hosts to be included.
* The **excep_list** will specify the hosts to be removed from the analysis.

Files
-----
* **FindIdentifers.py**: Main file for finding identifiers.
* **SuffixTree.py**: A Unicode-supported generalised suffix tree implementation, forked from http://www.daimi.au.dk/~mailund/suffix_tree.html.
* **Interface.py**: The interface defined to pass values between pre-processor and identifier finder, and the store format of the identifiers
* **DataHandler.py**: The pre-processor to process the SQLite database crawled from web.

Suffix Tree
-----------
    
