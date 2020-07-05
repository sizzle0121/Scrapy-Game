# Scrapy Game
-------------------------------------------
Data Engineering Challenge of SparkAmplify


## Environment
* Scrapy 2.2.0
* Python 3.5
* Pandas 1.0.3


## Run
In the directory which includes ```scrapy.cfg```	
> scrapy crawl ScrapyGame	
> // the output file will be ```output.csv```


## About the Task
1. Please write a program to scrap the authors' name and their contact info(email, social media)
2. The links will include some noise

### Input File
200 rows of (id, url) in ```scrpay_game_input.csv```

### Output File
rows of (id, url, author\_name, contact\_info)


## Methods
### About Extracting Authors' name
* In the very first version, I tried to extract authors' name by looking all tags whose __class name contains '[Aa]uthor'__; however, the text extracted by this way is very messy, since there are more tags containing the class name '[Aa]uthor' than I thought. In addition, it's not easy for us to locate the personal page (under the same domain name, not social media) of the author in this way.

* Then I came up with seeing if __href attributes contain '[Aa]uthor(s)?' in the link__ to locate authors' name. It turned out that almost 80% authors' name can be extracted by this methods. In the later versions of codes, I added more regular expressions to identify __whether the text is a human name__ more accurately.

* The above method can already extract nearly __87%__ authors' name from all given urls. To further improve it, I also checked if __rel attributes__ contain '[Aa]uthor(s)?'. By doing so plus adding some regular expressions for specific cases, now we can scrap __over 94%__ authors' name from the given urls. The rest of links are either noise (redirect to pages without news and authors) or the pages whose html tags do not contain any feature for us to locate the author name (we can parse it, but the method will be too specific, only for those pages)	

### About Extracting Contact Info
* The approach is to first extracted all social media links and email addresses, then start to __filter irrelevant links and addresses__.

* How to filter? I set up regular expressions to exclude the shared links, quoted links, and the social media of the website itself. However, some social media of the website itself are not exactly named by the domain name. Therefore, I further filtered them by finding __the length of the longest common subsequence__ of the domain name and the id of the social media, then calculate __the length / min(domain name, id of the social media)__. If the ratio >= 70%(threshold), the social media is highly possible for the website itself, thus, we can filter it out.

* The contact info may present on the __personal page__ of the author. Hence, I also request to the personal page and do the above things. The contact info in the output file contains all the possible contacts of the author by this way of extracting and filtering.

## If I have more time...
* I will create a classifier (can be done by using GCP) to identify if the input text is a human name to extract authors' name in a more accurately also more generally way (no need to set up many regular expressions for different conditions and specific cases).

* I will create a identifier to identify if the contact info matches the author (extract the exact contacts), if no match, then use google-api-puthon-client to search for the author's social media and identify the searching result again.
