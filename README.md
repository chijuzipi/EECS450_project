Finding and Analyzing the Web User identifiers of Third-Party Trackers
======================================================================

Usage
-----
```sh
python2 FindIdentifier.py
```
A config file is needed to specify the specific databases and related parameters. By default the config file name is *identifier.cfg*. You can also specify your own config file and run the program using:
```sh
python2 FindIdentifier.py [YourConfigFile]
```
An example of the config file is like this:
```python
[databases]
database1 = httpfox.sqlite
database2 = httpfox.sqlite2

[hosts]
host_list = ['adsonar.com']
excep_list = ['google.com']
# minHost = 
# maxHost = 

[identifiers]
minimum_length = 5
occurance = 0.5
level = 2
```
* The **host_list** will specify the **ONLY** hosts to be included.
* The **excep_list** will specify the hosts to be removed from the analysis.
* The *#* symbol means comment.

Files
-----
* **FindIdentifers.py**: Main file for finding identifiers.
* **SuffixTree.py**: A Unicode-supported generalised suffix tree implementation, forked from (http://www.daimi.au.dk/~mailund/suffix_tree.html).
* **Interface.py**: The interface defined to pass values between pre-processor and identifier finder, and the store format of the identifiers
* **DataHandler.py**: The pre-processor to process the SQLite database crawled from web.

Generalized Suffix Tree
-----------------------
* The Unicode support is implemented using [ICU library](http://site.icu-project.org/). Mostly the unicode is used for a large number of terminators needed for building a generalized suffix tree. According to the number of unicode characters, if the number of strings to process is more than 1.1 million, this method may fail.
* Currently the code has memory issues. The cyclic garbage collectors has not been implemented due to the interwining of the SuffixTree object and Node object stated in *src/suffix_tree_2.1/python_binding.c*. Unless redesigning the whole program, the current work around for multiple suffix tree travarsing and long time running is to divide the work using the *minHost* and *maxHost* parameters in the config file, and then combine the dumped data into one file for analysis.
    
