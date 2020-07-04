import scrapy
import pandas as pd
import re
import copy
from scrapy_game.items import ScrapyGameItem 

class ScrapyGameCralwer(scrapy.Spider):
    load_table = pd.read_csv('./scrpay_game_input.csv', encoding = 'utf-8')
    name = 'ScrapyGame'
    start_urls = load_table.iloc[:, 1].to_list()

    def __init__(self):
        self.domains = {'twitter': 'http[s]*://[w]*\.twitter\.com',
                        'linkedin': 'http[s]*://[w]*\.linkedin\.com/in',
                        'facebook': 'http[s]*://[w]*\.facebook\.com'
                    }
        self.table = pd.read_csv('./scrpay_game_input.csv', encoding = 'utf-8')

    def parse(self, response):
        """Create Entries for Current Website"""
        Entries = ScrapyGameItem()
        Entries['url'] = response.url
        Entries['contact_info'] = []
        curId = self.table.loc[self.table['url']==response.url, ['id']]
        if curId.empty:
            addWWW = response.url
            addWWW = addWWW[:8] + 'www.' + addWWW[8:]
            curId = self.table.loc[self.table['url']==addWWW, ['id']]
        if not curId.empty:
            curId = curId.values[0][0]
            Entries['Id'] = curId

        """Initialize Boolean Values for Tasks"""
        FOUND_AUTHOR = False
        FOUND_CONTACT = False

        """Match Possible Tags"""
        #author_tags = re.findall("class=\"[^<>]*[Aa]uthor[^<>]*\"", str(response.body))
        #publishBy_tags = re.findall("class=\"[^<>]*[Pp]ublish[^<>]*\"", str(response.body))
    
        """Find from author_tags"""
        #for author_tag in author_tags:
        #    author_tag = author_tag.split("\"")
        #    author_tag = author_tag[1]
        #    author_tag = author_tag.replace(' ', '.')

        "Possible URLs for Authors"
        cur_domain, cur_domain_www = self.getCurrentDomain(str(response.url))
        author_url = cur_domain+'.*[Aa]uthor.*'
        author_url_www = cur_domain_www+'.*[Aa]uthor.*'
        
        """Find From Author href Tag"""
        names_author = response.xpath('//a[contains(@href, "author")]/text()').getall()
        names_autor = response.xpath('//a[contains(@href, "autor")]/text()').getall()
        #print('#######################################')
        #print(names)
        if len(names_author) > 0:
            for name in names_author:
                if self.is_valid(name):
                    Entries['author_name'] = name
                    FOUND_AUTHOR = True
                    break
        elif len(names_autor) > 0:
            for name in names_autor:
                if self.is_valid(name):
                    Entries['author_name'] = name
                    FOUND_AUTHOR = True
                    break
        
        return Entries


    def is_valid(self, name):
        if not re.search('^[a-zA-Záéíóúýàèìòùâêîôûäëïöüÿ]+[.]*([- ]+[a-zA-Záéíóúýàèìòùâêîôûäëïöüÿ]+[.]*){1,2}$', name):
            return False
        by = re.search('^[Bb]y[ ]*$', name)
        publish = re.search('.*[Pp]ublish.*', name)
        post = re.search('.*[Pp]ost.*', name)
        written = re.search('.*[Ww]ritten.*', name)
        sign = re.search('[Ss]ign [Uu]p|[Ii]n', name)
        subscribe = re.search('subscribe.*', name, re.IGNORECASE)
        getStart = re.search('get start.*', name, re.IGNORECASE)
        pro = re.search('^[Pp]ro[ ]*$', name)
        return not by and not publish and not post and not written and not sign and not subscribe and not getStart and not pro


    def getCurrentDomain(self, current_url):
        idx = current_url.find('.com')
        idx += 4
        current_url = current_url[:idx]
        current_url_www = copy.deepcopy(current_url)
        if current_url.find('www.') == -1:
            current_url_www = current_url[:8]+'www.'+current_url[8:]
        else:
            current_url = current_url.replace('www.', '')
        return current_url, current_url_www

