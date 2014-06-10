Finding and Analyzing the Web User identifiers of Third-Party Trackers
======================================================================

Installation
------------
The generalized suffix tree module is written as a C-extension for python, so you need to compile the source code. Here the [distutils](https://docs.python.org/2/extending/building.html) module of python is used to aid for the compilation.
```bash
cd src/suffix_tree-2.1
$PYTHON2_BIN setup.py build
cp build/lib.plat/_suffix_tree.so ..
```
The **lib.plat** actually depends on your system and python version. In ArchLinux x86_64, it is **lib.linux-x86_64-2.7**

Usage
-----
Please use Python 2.x to run the program:
```bash
$PYTHON2_BIN FindIdentifier.py
```
A config file is needed to specify the specific databases and related parameters. By default the config file name is *identifier.cfg*. You can also specify your own config file and run the program using:
```bash
$PYTHON2_BIN FindIdentifier.py YourConfigFile.cfg
```
An example of the config file is like this (For the details of the format and how to parse the file, please refer to [ConfigParser](https://docs.python.org/2/library/configparser.html)):
```ini
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
* The **#** symbol means comment.

The output file is also in the similar format as the input config file. The sections are the hosts that have identifiers found, and for each host there is three name-value pairs: identifiers, keys and requests.
```ini
[myhost.com]
identifiers=[u'hey', u'hi']
keys=[['param_fail', 'param_success'], ['param_fail']]
requests=[[1, 2, 3], [1, 2, 3]]
```

Files
-----
* **FindIdentifers.py**: Main file for finding identifiers.
* **SuffixTree.py**: A Unicode-supported generalised suffix tree implementation, forked from http://www.daimi.au.dk/~mailund/suffix_tree.html.
* **Interface.py**: The interface defined to pass values between pre-processor and identifier finder, and the store format of the identifiers
* **DataHandler.py**: The pre-processor to process the SQLite database crawled from web.
* **FindRootPage.py**
* **IdentifierAnalysis.py**
* **ThirdPartyMeasure.py**

Generalized Suffix Tree
-----------------------

Issues
------
* The Unicode support of the generalized suffix tree is implemented using [ICU library](http://site.icu-project.org/). Mostly the unicode is used for a large number of terminators needed for building a generalized suffix tree. According to the number of unicode characters, if the number of strings to process is more than 1.1 million, this method may fail.
* Currently the code has memory issues. The cyclic garbage collectors has not been implemented due to the interwining of the SuffixTree object and Node object stated in *src/suffix_tree_2.1/python_binding.c*. Unless redesigning the whole program, the current work around for multiple suffix tree travarsing and long time running is to divide the work using the *minHost* and *maxHost* parameters in the config file, and then combine the dumped data into one file for analysis.
    
