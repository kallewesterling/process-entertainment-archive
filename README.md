# process-entertainment-archive
A python script to traverse through HTML files with ProQuest results to generate an easily navigable CSV file (and Pandas DataFrame).

# Instructions for use
On line 36-39, define your settings:

``search_result_directory`` should be set to the folder that contains the HTML files with search results from ProQuest's Entertainment Archive (automatically set to **search_results**).

``stopfiles`` is a list containing the files you would like to _not_ include in the creation of the CSV file (for instance, Mac OS X's really annoying **.DS_Store** file).

``savefile_csv`` should be set to the name of your results file. (automatically set to **results.csv**; but note that the script automatically adds the current date and time on line 127).

``remove_duplicates`` should be set to **True** if you want the script to automatically remove any duplicate entries at the end of processing.
