import re
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup


'''
Optional settings:

The program allows you to define two central settings below:

    STOPFILES = let's you determine which file names to block when reading a directory.
    CACHE_RAW_IN_OBJECT = let's you determine whether each ProQuestResult will contain an instance variable (_raw) that contains the raw HTML from each of the files. Turned off to save memory but turn on if you, for some reason, need to read the HTML from each of the files.

'''

STOPFILES = ['.DS_Store']
CACHE_RAW_IN_OBJECT = False



class ProQuestResult(object):
    '''
    Reads individual HTML files with ProQuest search results and provides a list of dicts (ProQuestResults.results) and DataFrame object (ProQuestResults.df) with all the details for the search results.
    
    Provide the script with a file variable to set it up: ProQuestResult(file). File needs to be a string or a PosixPath (see pathlib's documentation if need be).
    
    You can also access the search query as a string: ProQuestResults.query.
    
    If you request len(ProQuestResults.results) for the object, it will return the number of search results in the file.
    
    Note: Accessing the instance variable results and df will both generate them to order. That means that the script, depending on the number of search results in each file, can take some time to run.
    '''
    
    
    def __init__(self, file = None):
        if file is None or (not isinstance(file, str) and not isinstance(file, Path)): raise RuntimeError(f"File ({file}) must be a string value (or a PosixPath) containing a path to a ProQuest search result file.")
        
        self.file = Path(file)
        self._raw = None
        
        if not self.file.is_file(): raise RuntimeError(f"The provided file ({file}) needs to be a readable file.")
        
        with open(file) as f:
            if CACHE_RAW_IN_OBJECT:
                self._raw = f.read()
                soup = BeautifulSoup(self._raw,'lxml')
            else:
                raw = f.read()
                soup = BeautifulSoup(raw,'lxml')
                
        self.query = soup.find("textarea", {"id": "searchTerm"}).text.lstrip()
        self._all_results = soup.find_all("li", {"class": "resultItem"})
        self._results = None
        self._df = None
    
    
    def __len__(self):
        return(len(self._all_results))
    
    
    def __repr__(self):
        return(f"ProQuestResult('{self.file})'")

    
    @property
    def results(self):
        if self._results is None: self._results = self._process_all_results()
        return(self._results)
    
    
    @property
    def df(self):
        if self._df is None:
            if self._results is None: self._results = self._process_all_results()
            
            if self._results is None:
                self._df = None
            else:
                self._df = pd.DataFrame.from_dict(self._results)
        return(self._df)
    
    
    def _process_all_results(self):
        ''' Internal function to provide a list of dictionaries with all the search results found in the instance BeautifulSoup object _all_results. '''
        
        def test_regex(metadata):
            ''' Nested function to generate a dictionary of information from regex parsed metadata about a specific article. '''
            pattern = re.compile('(.+) \((.+)\); (.+) Vol. (.+), Iss. (.+),\s+\((.+)\): (.+).')
            result = pattern.search(metadata)
            if result is not None:
                return({
                    'publication': result[1],
                    'vol': result[4],
                    'issue': result[5],
                    'date': result[6],
                    'pages': result[7]
                })
            else:
                #print("Could not decode metadata:",metadata)
                return({
                    'publication': None,
                    'vol': None,
                    'issue': None,
                    'date': None,
                    'pages': None
                })

        _ = []
        for r in self._all_results:
            # get title
            if r.find("a", {"class": "previewTitle"}) is not None:
                title = r.find("a", {"class": "previewTitle"}).text
            else:
                title = None

            # get fulltext link
            if r.find("a", {"class": "format_fulltext"}) is not None:
                link_details = r.find("a", {"class": "format_fulltext"})
                link_details = link_details['href']
                link_details = link_details.split("/")
                fulltext_link = "/"+link_details[3]+"/"+link_details[4]+"/"+link_details[5]+"/"+link_details[6]+"/"+link_details[7]+"/"+link_details[8]
            else:
                fulltext_link = None

            # get pdf link
            if r.find("a", {"class": "format_pdf"}) is not None:
                link_details = r.find("a", {"class": "format_pdf"})
                link_details = link_details['href']
                link_details = link_details.split("/")
                fulltext_pdf = "/"+link_details[3]+"/"+link_details[4]+"/"+link_details[5]+"/"+link_details[6]+"/"+link_details[7]+"/"+link_details[8]
            else:
                fulltext_pdf = None

            #get all metadata
            if r.find_all("span", {"class": "titleAuthorETC"}) is not None:
                metadata = r.find_all("span", {"class": "titleAuthorETC"})
                if(len(metadata) == 1):
                    author = None
                    metadata = metadata[0].text.replace(u'\xa0', u' ')
                    info = test_regex(metadata)
                elif(len(metadata) == 2):
                    author = metadata[0].text.strip()
                    metadata = metadata[1].text.replace(u'\xa0', u' ')
                    info = test_regex(metadata)
            else:
                info = {
                    'publication': None,
                    'issue': None,
                    'vol': None,
                    'date': None,
                    'pages': None
                }
                
            _.append({
                'author': author,
                'publication': info['publication'],
                'full_date': info['date'],
                'vol': info['vol'],
                'issue': info['issue'],
                'title': str(title),
                'pages': info['pages'],
                'link_details': str(fulltext_link),
                'link_pdf': str(fulltext_pdf),
                'ad': " ad " in title.lower() or title[0:2].lower() == "ad" # not a great way to check this, so data points here need to be taken with a grain of salt.
            })
        
        return(_)
    

class ProQuestResults(object):
    '''
    Flexible class that reads any number of individual HTML files with ProQuest search results and provides a list of dicts (ProQuestResults.results) and DataFrame object (ProQuestResults.df) with all the details for the search results.
    
    Provide the script with a list of file names as strings or PosixPaths or a directory as a string or PosixPath or a number of directories provided as a list of strings or PosixPaths to set it up:
        ProQuestResult(files = ['list', 'of', 'paths', 'to', 'files'])
        ProQuestResult(directory = 'the path of a directory')
        ProQuestResult(directory = ['the path of a directory', 'the path of another directory'])
    
    Note: Accessing the instance variable results and df will both generate them to order. That means that the script, depending on the number of search results in each file, can take some time to run.
    '''
    
    
    def __init__(self, files=None, directory=None):

        # First, let's sort out the files and directory information and generate a files instance variable (self.files) that contains a list of all the Path objects
        if files is None and directory is not None:
            if isinstance(directory, str) or isinstance(directory, Path):
                # directory is a string or a Path
                directory = Path(directory)
                files = [x for x in Path(directory).iterdir() if x.is_file() and x.name not in STOPFILES]
                
            elif isinstance(directory, list) and (all(isinstance(x, str) for x in directory) or all(isinstance(x, Path) for x in directory)):
                # directory is a list of strings or paths
                directory = [Path(x) for x in directory]
                files = []
                for _dir in directory:
                    files.extend([x for x in Path(_dir).iterdir() if x.is_file() and x.name not in STOPFILES])
            elif isinstance(directory, list) and not (all(isinstance(x, str) for x in directory) or all(isinstance(x, Path) for x in directory)):
                raise RuntimeError("Cannot interpret list of directories. Make sure that the list contains only strings or PosixPath objects.")
            else:
                raise RuntimeError("Cannot interpret list of directories. Make sure that the list contains only strings or PosixPath objects.")
        elif files is not None:
            if isinstance(files, list) and directory is None and all(isinstance(x, str) for x in files) or all(isinstance(x, Path) for x in files):
                pass # we have files and no directory, so all is good
            
        
        self.files = [Path(x) for x in files]
        self.directory = directory # make sure we can access this later
        self._results = None
        self._df = None
        self._query_to_files = None
        self._files_to_query = None
    
    
    def __len__(self):
        if self._results is None: self._results = self._process_all_results()
        return(len(self._results))
    
    
    def __repr__(self):
        return(f"ProQuestResult('{self.file})'")
    
    
    @property
    def results(self):
        if self._results is None: self._results = self._process_all_results()
        return(self._results)

    
    @property
    def df(self):
        if self._df is None:
            if self._results is None: self._results = self._process_all_results()
            if self._results is None:
                self._df = None
            else:
                self._df = pd.DataFrame.from_dict(self._results)
        return(self._df)
    
    
    def _process_all_results(self):
        ''' Internal function to create a list of results from each of the files, consolidated into one single list which is returned to the caller. '''
        _ = []
        for file in self.files:
            results = ProQuestResult(file).results
            _.extend(results)
        return(_)
    
    
    @property
    def query_to_files(self):
        if self._query_to_files is None: self._query_to_files = self._setup_query_to_files()
        return(self._query_to_files)
    
    
    @property
    def files_to_query(self):
        if self._files_to_query is None: self._files_to_query = self._setup_files_to_query()
        return(self._files_to_query)
    
    
    def _setup_query_to_files(self):
        _ = {}
        for file in self.files:
            query = ProQuestResult(file).query
            if query not in _: _[query] = []
            _[query].append(file)
        return(_)
    
    def _setup_files_to_query(self):
        _ = {}
        for file in self.files:
            query = ProQuestResult(file).query
            if file not in _: _[file] = query # technically, we don't have to test for this condition here but better safe than sorry.
        return(_)