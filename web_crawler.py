# import necessary libraries
import requests
from bs4 import BeautifulSoup
import json, re, os

# build the web crawler object
class WebCrawler:

    # create three variables: start_url, max_depth, list of visited urls
    def __init__(self, start_url, max_depth=2):
        self.start_url = start_url
        self.max_depth = max_depth
        self.visited = set()

    # create a function to make sure that the primary url is valid
    def is_successful(self):

        try:
            response = requests.get(self.start_url) # request the page info 
            response.raise_for_status() # raises exception when not a 2xx response
            if response.status_code == 200: # check if the status code is 200, a.k.a successful
                return True
            
            else: # if not, print the error with the status code
                print(f"The crawling could not being becasue of unsuccessful request with the status code of {response.status_code}.")

        except requests.HTTPError as e: # if HTTPS Error occured, print the error message
            print(f"HTTP Error occurred: {e}")

        except Exception as e: # if any other error occured, print the error message
            print(f"An error occurred: {e}")
    
    # create a function to get the links
    def process_page(self, url, depth):

        # apply depth threshold
        if depth > self.max_depth or url in self.visited:
            return set(), '' # return emppty set and string

        self.visited.add(url) # add the visited url to the list
        links = set() # create a set to store the collected links
        content = '' # create a variable to store the content extracted

        try:
            r = requests.get(url, timeout=5) # request the content of a url
            r.raise_for_status() # check if the request status is successful
            soup = BeautifulSoup(r.text, 'html.parser') # parse the content of the collected html
            
            # Extract the links links
            anchors = soup.find_all('a') # find all the anchors

            for anchor in anchors: # merge the anchor with the starting url
                link = requests.compat.urljoin(url, anchor.get('href')) # get the link and join it with the starting url
                links.add(link) # add the link to the previously created set
            
            # Extract the content from the url
            content = ' '.join([par.text for par in soup.find_all('p')]) # get all the text
            content =  re.sub(r'[\n\r\t]', '', content) # remove the sequence characters

        except requests.RequestException: # if the request encounters an error, pass
            pass

        return links, content # return the set of the collected links and the contet of the current url

    # crawl the web within the depth determined
    def crawl(self):
        
        if self.is_successful(): # check if the requesting the starting url info is valid to continue crawling
            
            urls_content = {} # create a dictionary to store the links as keys and contents as values
            urls_to_crawl = {self.start_url} # start crawling from the initial url

            # crawl the web within the depth determined
            for depth in range(self.max_depth + 1):

                new_urls = set() # create a set to store the internal new urls

                for url in urls_to_crawl:  # crawl through the urls

                    if url not in self.visited: # check and make sure that the url is not crawled before
                        links, content = self.process_page(url, depth) # return the links and content of the crawled url
                        urls_content[url] = content # add the url as a key and content as a value to the disctionary created previously
                        new_urls.update(links) # add the internal links to the previously created set

                urls_to_crawl = new_urls # change the urls to crawl list to crawl through the internal links

            # create a folder to store the crawled websites
            current_dir = os.getcwd() # get the current working directory
            folder_dir = os.path.join(current_dir,'crawled_websites') # create a folder inside the current directory

            if not os.isdir(folder_dir): # check if the folder already exists
                os.makedirs(folder_dir) # if not, create the folder directory

            filename = re.sub(r'\W+', '_', self.start_url) + '_crawling_results.json' # format the filename to modify unsupported characters
           
            # save the results as a json file in the local directory
            with open(os.path.join(folder_dir,filename), 'w', encoding='utf-8') as file:
                json.dump(urls_content, file, ensure_ascii=False, indent=10) # ensure to keep the unicode characters and indent to make it more readable

            return urls_content # return the disctionary storing all urls and their content