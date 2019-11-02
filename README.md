# Process ProQuest Entertainment Archive files

A python script to traverse through HTML files with ProQuest results to generate an easily navigable CSV file (and Pandas DataFrame).


## How to Install

This package requires you to install two other packages for it to run: `pandas` and `BeautifulSoup`. Install them by running these two commands in your command line:

```sh
pip install pandas`
```

```sh
pip install beautifulsoup4`
```


## Set Up the Program

The program allows you to define two optional settings. Open `ProQuestResult.py` and find the two lines that contain the two variables `STOPFILES` and `CACHE_RAW_IN_OBJECT`.

`STOPFILES` needs to be a list of strings. It determines which file names the program will block when reading a directory. By default it is set to only include one element, Mac OS X's annoyingly present .DS_Store files:
```python STOPFILES = ['.DS_Store']```

`CACHE_RAW_IN_OBJECT` needs to be a boolean. It determines whether each ProQuestResult will contain an instance variable (`ProQuestResult._raw`) that contains the raw HTML from each of the files. By default, this variable is set to `False` in order to save memory. Switch to `True` if you for some reason need to be able to access the HTML from your search result file.


## How to Run

Drop the `ProQuestResult.py` file into your project folder. Then run `from ProQuestResult import *` in your project, whether it is a Python file or a Jupyter Notebook.

You have two options when creating an object containing your search results: `ProQuestResult` (1) and `ProQuestResults` (2). The subtle difference is in the plural.


### (1) ProQuestResult

If you have one individual HTML files with ProQuest search results, this is the object you want to invoke. It provides a list of dictionaries (`ProQuestResults.results`) and a DataFrame object (`ProQuestResults.df`) with all the details for the search results.


#### Setting up the object

To set up an object, simply provide it with a file variable to set it up: 

`parsed_results = ProQuestResult(file = './my_search_results/the_file_with_results.html')`

The `file` parameter should be a string but can also be a PosixPath (see pathlib's documentation for reference).


#### Accessing search results

Once the object has been set up, you can easily access the search results as a list of dictionaries:

`print(parsed_results.results)`

If you'd rather see the search results as a pandas DataFrame, you can do so by calling:

`parsed_results.df`

This also provides an easy way to export the DataFrame to a CSV, by calling:

`parsed_results.df.to_csv('xxx.csv')` **<-- I need to look into whether this actually works**

*Note: Accessing the instance variables `results` and `df` will both generate them to order. That means that the script, depending on the number of search results in each file, can take some time to run.*

The object also gives you easy access to the search query as a string:

`print(parsed_results.query)`

If you request `len()` for the object, it will return the number of search results in the file:

`len(parsed_results)`


### (2) ProQuestResults

If you have a directory or a list of files containing search results from ProQuest and you want to collect all of them in one object, you can do so by calling `ProQuestResults` instead of the examples above.


#### Setting up the object

The program is flexible and can ingest a number of variations through the two variables it accepts: `files` or `directory`.

**`files`** needs to be provided as a list of file names as strings (or PosixPaths). For example:

`ProQuestResult(files = ['./first_file.html', './second_file.html', './third_file.html', './fourth_file.html'])`

**`directory`** can be provided as either (1) a string (or a PosixPath) with a path to a directory containing the search result files you want to work with, or (2) a list of strings (or PosixPaths) that refer to any number of directories containing search result files.

For example, if you work with a single directory (1 above), you would call:

`parsed_results = ProQuestResults(directory = './my_search_results/')`

If you have a number of directories you need to summarize in one object (see 2 above), you would call the same object but set it up with a list of directories:

`parsed_results = ProQuestResults(directory = ['./my_first_search_result_directory/', './my_second_search_result_directory/'])`


#### Accessing search results

Once the object has been set up, you can easily access the search results in the same manner as the examples under `ProQuestResult` above:

To access all the search results as a list of dictionaries: `print(parsed_results.results)`

To access all the search results as a DataFrame: `parsed_results.df`

*Note: As is the case with `ProQuestResult`, accessing the instance variable `results` and `df` will both generate them to order. That means that the script, depending on the number of search results in each file, can take some time to run.*


## Future features

Note that since the `ProQuestResults` object is set up by numerous files, currently the `ProQuestResults` object cannot provide the search queries. In a future version, it will be able to provide the search query for each file (through requesting `ProQuestResults.files_to_queries`) and each file that contains each search query (through requesting `ProQuestResults.queries_to_files`).