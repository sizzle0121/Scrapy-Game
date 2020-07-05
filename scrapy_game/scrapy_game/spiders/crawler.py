import scrapy
import pandas as pd
import re
import copy
from scrapy_game.items import ScrapyGameItem 

class ScrapyGameCralwer(scrapy.Spider):
    load_table = pd.read_csv('./scrpay_game_input.csv', encoding = 'utf-8')
    name = 'ScrapyGame'
    start_urls = load_table.iloc[:, 1].to_list()
    #['https://arstechnica.com/information-technology/2019/06/apple-moves-mac-pro-production-from-texas-to-china/']
    #['https://303magazine.com/2019/06/italian-speakeasy-sotto-voce-opens-below-jovaninas-broken-italian/']
    #['https://archpaper.com/2019/06/robert-mckinley-shoppable-bungalow-long-island-montauk/']
    #['https://3dprintingindustry.com/news/print-parts-launches-on-demand-additive-manufacturing-service-for-performance-parts-157849/']

    def __init__(self):
        self.social_domains = {'twitter': 'http[s]*://(www\.)?twitter\.com',
                        'linkedin': 'http[s]*://(www\.)?linkedin\.com/in',
                        'facebook': 'http[s]*://(www\.)?facebook\.com',
                        'email': 'mailto:'
                    }
        self.table = pd.read_csv('./scrpay_game_input.csv', encoding = 'utf-8')

    def parse(self, response):
        """DEBUG"""
        print('=============================================')
        #print(response.url)

        """Create Entries for Current Website"""
        Entries = ScrapyGameItem()
        Entries['url'] = response.url
        Entries['contact_info'] = []
        curId = self.table.loc[self.table['url']==response.url, ['id']]
        if curId.empty:
            if str(response.url).find('www.') == -1:
                addWWW = response.url
                addWWW = addWWW[:8] + 'www.' + addWWW[8:]
                curId = self.table.loc[self.table['url']==addWWW, ['id']]
            else:
                rmWWW = response.url
                rmWWW = rmWWW[:8]+rmWWW[12:]
                curId = self.table.loc[self.table['url']==rmWWW, ['id']]
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
        names_author = response.xpath('//a[contains(@href, "author") or contains(@href, "Author")]/text()').getall()
        names_autor = response.xpath('//a[contains(@href, "autor") or contains(@href, "Author")]/text()').getall()
        #print('#######################################')
        #print(names_author)
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

        if FOUND_AUTHOR == False:
            return

        """Find Social Links for Authors"""
        links = response.xpath('//*[contains(@href, "facebook") or contains(@href, "twitter") or contains(@href, linkedin) or contains(@href, "mailto")]/@href').getall()
        if len(links) > 0:    
            for link in links:
                result = self.matchLink(link, cur_domain)
                if result:
                    Entries['contact_info'].append(result)
                    FOUND_CONTACT = True
        

        """Dig One More Page for the Author"""
        headers = {'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36'}
        author_page = response.xpath('//a[contains(@href, "author") or contains(@href, "Author")][contains(text(),\"'+Entries['author_name']+'\")]/@href').get()
        autor_page = response.xpath('//a[contains(@href, "autor") or contains(@href, "Autor")][contains(text(),\"'+Entries['author_name']+'\")]/@href').get()
        if author_page:
            if author_page.find('http') == -1:
                author_page = cur_domain + author_page
            yield scrapy.Request(url=author_page, callback=self.parseAuthorPage, headers=headers, dont_filter=True, cb_kwargs=dict(Entries=Entries, cur_domain=cur_domain))
        elif autor_page:
            if autor_page.find('http') == -1:
                autor_page = cur_domain + autor_page
            yield scrapy.Request(url=autor_page, callback=self.parseAuthorPage, headers=headers, dont_filter=True, cb_kwargs=dict(Entries=Entries, cur_domain=cur_domain))
        else: 
            #print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            yield Entries


    def parseAuthorPage(self, response, Entries, cur_domain):
        #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        links = response.xpath('//*[contains(@href, "facebook") or contains(@href, "twitter") or contains(@href, linkedin) or contains(@href, "mailto")]/@href').getall()
        if len(links) > 0:    
            for link in links:
                result = self.matchLink(link, cur_domain)
                if result:
                    Entries['contact_info'].append(result)
        return Entries


    def matchLink(self, link, cur_domain):
        domain_name = cur_domain.replace('https://', '')
        domain_name = domain_name.replace('.com', '')
        match_twitter = re.search(self.social_domains['twitter']+"/(?!intent|share|"+domain_name+").+", link, re.IGNORECASE)
        match_twitter = match_twitter and (link.find('/status/') == -1)
        match_linkedin = re.search(self.social_domains['linkedin']+"/(?!shareArticle).+", link, re.IGNORECASE)
        match_facebook = re.search(self.social_domains['facebook']+"/(?!share|pages|dialog|notes|"+domain_name+").+", link, re.IGNORECASE)
        match_email = re.search(self.social_domains['email']+"(?!"+domain_name+"|tips|contact).+@.+", link, re.IGNORECASE)
        if match_twitter or match_linkedin or match_facebook or match_email:
            if not match_email:
                return self.domainFilter(link, domain_name)
            else:
                return link
        else:
            return None

    def domainFilter(self, link, domain_name):
        LINK = copy.deepcopy(link)
        com = link.find('.com')
        if link.find('linkedin') == -1:
            link = link[com+5:]
        else:
            link = link[com+8:]
        slash = link.find('/')
        if slash != -1:
            link = link[:slash]
        domain_len = len(domain_name)
        link_len = len(link)
        L = [[0 for i in range(domain_len+1)] for j in range(link_len+1)]
        for i in range(1, link_len+1):
            for j in range(1, domain_len+1):
                if link[i-1].lower() == domain_name[j-1].lower():
                    L[i][j] = L[i-1][j-1] + 1
                else:
                    L[i][j] = max(L[i-1][j], L[i][j-1])
        base = min(domain_len, link_len)
        if (float(L[link_len][domain_len])/float(base)) >= 0.7:
            return None
        return LINK


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

