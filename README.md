# Facebook Scrapper 

## Usage

### Installation
You will need to install latest version of [Google Chrome](https://www.google.com/chrome/). Moreover, you need to install selenium module as well using

```
pip install selenium
```

**Download ChromeDriver and put it into project dir [Chrome Web Driver](http://chromedriver.chromium.org/downloads).**   

### How to Run
Use `post_scraper.py` to collect the group or page data. 
```
usage: group_scraper.py [-h] [--page PAGES [PAGES ...]] [--group GROUPS [GROUPS ...]][-d DEPTH]
Data Collection
arguments:
  -h, --help            show this help message and exit
  -p, --pages PAGES [PAGES ...]
                        List the pages you want to scrape
                        for recent posts
  
  -g, --groups GROUPS [GROUPS ...]
                        List the groups you want to scrape
                        for recent posts
  
  -d DEPTH, --depth DEPTH
                        How many recent posts you want to gather in
                        multiples of (roughly) 8.
```
Example: ```python post_scraper.py -g groupname -d 20```
____
The output is `posts.csv` inside the script folder.

From `` row column 'Author ID', you can get user profile id.  
There's a file named "input.txt". You can add as many profiles as you want in the following format with each link on a new line:

```
https://www.facebook.com/andrew.ng.96
https://www.facebook.com/user profile id
```

Make sure the link only contains the username or id number at the end and not any other stuff. Make sure its in the format mentioned above.

Note: There are two modes to download Friends Profile Pics and the user's Photos: Large Size and Small Size. You can change the following variables. By default they are set to Small Sized Pics because its really quick while Large Size Mode takes time depending on the number of pictures to download

```
# whether to download the full image or its thumbnail (small size)
# if small size is True then it will be very quick else if its False then it will open each photo to download it
# and it will take much more time
friends_small_size = True
photos_small_size = True
```
----------------------------------------------------------------------------------------------------------------------------------------

## Reference  
https://github.com/harismuneer/Ultimate-Facebook-Scraper   
https://github.com/apurvmishra99/facebook-scraper-selenium   