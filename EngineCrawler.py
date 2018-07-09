#/usr/bin/env python
#-*- coding:utf-8 -*-
# EngineCrawler v1.0.1

import re
import os
import sys
from time import sleep
import requests
import argparse
from bs4 import BeautifulSoup
from urllib import unquote
from urllib import quote
import multiprocessing
import threading

def parse_args():

    '''命令行解释器'''

    parser = argparse.ArgumentParser(epilog='\tExample: \r\npython ' + sys.argv[0] + " -e baidu,yahoo -r 'inurl:php?id=1' -p 10 -o urls.txt")
    parser._optionals.title = "OPTIONS"
    parser.error = parser_error
    parser.add_argument('-r', '--rule', help="Engine advanced search rules", required=True)
    parser.add_argument('-p', '--page', help="The number of pages returned by the search engine", required=True,type=int)
    parser.add_argument('-e', '--engines', help='Specify a comma-separated list of search engines')
    parser.add_argument('-o', '--output', help='Save the results to text file')
    return parser.parse_args()

def banner():
    print """
 _____             _             ____                    _           
| ____|_ __   __ _(_)_ __   ___ / ___|_ __ __ ___      _| | ___ _ __ 
|  _| | '_ \ / _` | | '_ \ / _ \ |   | '__/ _` \ \ /\ / / |/ _ \ '__|
| |___| | | | (_| | | | | |  __/ |___| | | (_| |\ V  V /| |  __/ |   
|_____|_| |_|\__, |_|_| |_|\___|\____|_|  \__,_| \_/\_/ |_|\___|_|   
             |___/   
                # Coded By Farmsec - @answer
    """

def parser_error(errmsg):
    banner()
    print "Usage: python " + sys.argv[0] + " [Options] use -h for help"
    print "Error: " + errmsg
    sys.exit()

def write_file(filename,results_urls):
    # 将url保存到文件
    print "[*] Saving results to file: %s" % filename
    with open(str(filename), 'at') as f:
        for url in results_urls:
            f.write(url + os.linesep)

class Enumrator_base(object):

    '''最基础的搜索引擎枚举器'''

    def __init__(self,options):
        self.session = requests.Session()
        self.headers = {
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
        }
        self.timeout = 25
        self.search_rules = options.rule
        self.page = options.page
        self.base_url = ''
        self.urls = []

    # 要抓取的网页
    def _get_page(self):
        '''子类应重写这个方法'''
        return

    # 发送http
    def send_request(self):
        '''子类应重写这个方法'''
        return

    # 提取url
    def _extract_url(self,resp):
        '''子类应重写这个方法'''
        return

    # 检查http返回错误
    def _check_response_errors(self,resp):
        '''子类应重写这个方法'''
        return

    # 延时请求以避免被机器人检测
    def _should_sleep(self):
        sleep(2)
        return

class Enumrator_base_threaded(multiprocessing.Process,Enumrator_base):

    '''多进程枚举器'''

    def __init__(self,options,lock=threading.Lock(),q=None):
        Enumrator_base.__init__(self,options)
        multiprocessing.Process.__init__(self)
        self.lock = lock
        self.q = q

    def run(self):
        url_list = self.send_request()  # 实例通过调用start()方法，自动调用run()方法
        for url in url_list:
            self.q.append(url)

class Baidu_enum(Enumrator_base_threaded):

    '''
    百度搜索引擎
    www.baidu.com
    '''

    def __init__(self,options,q=None):
        super(Baidu_enum, self).__init__(options,q=q)
        self.base_url = 'https://www.baidu.com/s?wd={}&pn={}'
        self.q = q

    def _get_page(self):

        '''获取要爬取的网页数量'''

        pages = []
        for pn in range(0,(self.page - 1) * 10,10):
            pages.append(pn)
        return pages

    def send_request(self):
        pages = self._get_page()
        for pn in pages:
            url = self.base_url.format(self.search_rules,pn)
            try:
                response = self.session.get(url,headers=self.headers,timeout=self.timeout)
            except Exception:
                pass
            else:
                self._extract_url(response)
        return self.urls


    def _extract_url(self,resp):

        '''从返回的html中提取url'''

        soup = BeautifulSoup(resp.text, "lxml")
        html_divs = soup.find_all("a", attrs={'data-click': re.compile(r'.'), 'class': None})
        for div in html_divs:
            try:
                response = self.session.get(div['href'], headers=self.headers, timeout=self.timeout)
                if response.status_code == 200:
                    url = response.url
                    self.urls.append(url)
                    print  '[-]Baidu: ' + url
            except Exception:
                pass

class Google_enum(Enumrator_base_threaded):

    '''
    谷歌搜索引擎
    answer.run
    谷歌在国内被墙掉了，抓取镜像站的数据
    '''
    def __init__(self,options,q=None):
        super(Google_enum,self).__init__(options,q=q)
        self.base_url = 'http://google.answer.run/search?q={}&start={}'
        self.headers = {
            'Host':'google.answer.run',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
            'Upgrade-Insecure-Requests':'1',
        }
        self.q = q

    def _get_page(self):

        pages = []
        for pn in range(0,(self.page -1 ) * 10,10):
            pages.append(pn)
        return pages

    def send_request(self):
        pages = self._get_page()
        for pn in pages:
            url = self.base_url.format(self.search_rules,pn)
            try:
                response = self.session.get(url,headers=self.headers,timeout=self.timeout)
                self._should_sleep()
            except Exception:
                pass
            else:
                self._extract_url(response)
        return self.urls

    def _extract_url(self,resp):
        soup = BeautifulSoup(resp.text, "lxml")
        cite_tages = soup.select("h3 a")
        for cite_tage in cite_tages:
            url = cite_tage['href']
            if url.startswith('http') or url.startswith('https'):
                self.urls.append(url)
                print '[-]Google: ' + url
            else:
                pass

    def _check_response_errors(self,resp):
        if 'Our systems have detected unusual traffic' in resp:
            print '[!] Error Google probably now is blocking our requests'
            print '[~] Finished now the Google Enumeration ......'
            return False
        return True

class Yahoo_enum(Enumrator_base_threaded):

    '''
    雅虎搜索引擎
    search.yahoo.com
    '''

    def __init__(self,options,q=None):
        super(Yahoo_enum, self).__init__(options,q=q)
        self.base_url = 'https://search.yahoo.com/search?p={}&b={}'
        self.q = q

    def _get_page(self):

        pages = []
        for pn in range(0,(self.page - 1) * 10,10):
            pages.append(pn)
        return pages

    def send_request(self):
        pages = self._get_page()
        for pn in pages:
            url = self.base_url.format(self.search_rules, pn+1)
            try:
                response = self.session.get(url,headers=self.headers,timeout=self.timeout)
            except Exception:
                pass
            else:
                self._extract_url(response)
        return self.urls

    def _extract_url(self, resp):
        '''
        雅虎搜索返回的url结果：
        yahoo_encryption_url = '
        http://r.search.yahoo.com/_ylt=AwrgDaPBKfdaMjAAwOBXNyoA;_ylu=X3oDMTByb2lvbXVuBGNvbG8DZ3ExBHBvcwMxBHZ0aWQDBHNlYwNzcg--/RV=2/RE=1526176322/RO=10/RU=
        http://berkeleyrecycling.org/page.php?id=1
        /RK=2/RS=6rTzLqNgZrFS8Kb4ivPrFbBBuFs-'
        '''
        soup = BeautifulSoup(resp.text, "lxml")
        try:
            a_tags = soup.find_all("a", " ac-algo fz-l ac-21th lh-24")
            for a_tag in a_tags:
                yahoo_encryption_url = a_tag['href']
                yahoo_decrypt_url = unquote(yahoo_encryption_url)   # 解码
                split_url = yahoo_decrypt_url.split('http://')
                if len(split_url) == 1:
                    result_https_url = 'https://' + split_url[0].split('https://')[1].split('/R')[0] # 获取返回https协议的url
                    self.urls.append(result_https_url)
                    print '[-]Yahoo: ' + result_https_url
                else:
                    result_http_url = 'http://' + split_url[2].split('/R')[0] # 获取返回http协议的url
                    print '[-]Yahoo: ' + result_http_url
                    self.urls.append(result_http_url)
        except Exception:
            pass

class Qihu360_enum(Enumrator_base_threaded):

    '''
    360搜索引擎
    www.so.com
    '''

    def __init__(self,options,q=None):
        super(Qihu360_enum,self).__init__(options,q=q)
        self.headers = {
            'Host': 'www.so.com',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
        }
        self.base_url = 'https://www.so.com/s?q={}&pn={}'
        self.q = q

    def _get_page(self):
        pages = []
        for pn in range(0,self.page,1):
            pages.append(pn)
        return pages

    def send_request(self):
        pages = self._get_page()
        for pn in pages:
            url = self.base_url.format(self.search_rules,pn)
            try:
                response = self.session.get(url, headers=self.headers, timeout=self.timeout)
            except Exception:
                pass
            else:
                self._extract_url(response)
        return self.urls

    def _extract_url(self,resp):
        soup = BeautifulSoup(resp.text, 'lxml')
        h3_tags = soup.find_all('h3', "res-title")
        for h3_tag in h3_tags:
            for a_tag in h3_tag:
                try:
                    data_url = a_tag['data-url']
                    print '[-]360: ' + data_url
                    self.urls.append(data_url)
                except TypeError:
                    pass
                except KeyError:
                   # = = 捕获了一个异常调试代码的时候发现还有一个......
                    try:
                        href_url = a_tag['href']
                        print '[-]360: ' + a_tag['href']  # 现在可以打印获取a_tag['href']中的数据了
                        self.urls.append(href_url)
                    except KeyError:
                        pass

class Ecosia_enum(Enumrator_base_threaded):

    '''
    Ecosia搜索引擎
    www.ecosia.org
    '''

    def __init__(self,options,q=None):
        super(Ecosia_enum,self).__init__(options,q=q)
        self.headers = {
            'Host':'www.ecosia.org',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
        }
        self.base_url = 'https://www.ecosia.org/search?p={}&q={}'
        self.search_rules = quote(self.search_rules)  # 将传入搜索引擎的参数进行url编码以避免被机器人检测
        self.q = q

    def _get_page(self):
        pages = []
        for pn in range(0,self.page,1):
            pages.append(pn)
        return pages

    def send_request(self):
        pages = self._get_page()
        for pn in pages:
            url = self.base_url.format(pn,self.search_rules)
            try:
                response = self.session.get(url, headers=self.headers, timeout=self.timeout)
            except Exception:
                pass
            else:
                self._extract_url(response)
        return self.urls

    def _extract_url(self,resp):
        soup = BeautifulSoup(resp.text, "lxml")
        a_tags = soup.find_all('a', 'result-url js-result-url')
        for a_tag in a_tags:
            url = a_tag['href']
            self.urls.append(url)
            print '[-]Ecosia: ' + url

class Teoma_enum(Enumrator_base_threaded):

    '''
    Teoma搜索引擎

    '''

    def __init__(self,options,q=None):
        super(Teoma_enum,self).__init__(options,q=q)
        self.headers = {
            'Host':'www.teoma.com',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
        }
        self.base_url = 'http://www.teoma.com/web?q={}&page={}'
        self.q =q

    def _get_page(self):
        pages = []
        for pn in range(1,self.page,1):
            pages.append(pn)
        return pages

    def send_request(self):
        pages = self._get_page()
        for pn in pages:
            url = self.base_url.format(self.search_rules,pn)
            try:
                response = self.session.get(url, headers=self.headers, timeout=self.timeout)
            except Exception:
                pass
            else:
                self._extract_url(response)
        return self.urls

    def _extract_url(self,resp):
        soup = BeautifulSoup(resp.text, "lxml")
        cite_tags = soup.find_all('cite', 'algo-display-url')
        for cite_tag in cite_tags:
            url = cite_tag.get_text()
            self.urls.append(url)
            print '[-]Teoma: ' + cite_tag.get_text()


class Hotbot_enum(Enumrator_base_threaded):

    '''
    hotbot 搜索引擎
    www.hotbot.com
    '''

    def __init__(self,options,q=None):
        super(Hotbot_enum, self).__init__(options,q=q)
        self.base_url = 'https://www.hotbot.com/web?q={}&offset={}'
        self.headers = {
            'Host':'www.hotbot.com',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
            'Upgrade-Insecure-Requests':'1',
        }
        self.q = q

    def _get_page(self):
        pages = []
        for pn in range(0,(self.page-1)*10,10):
            pages.append(pn)
        return pages

    def send_request(self):
        pages = self._get_page()
        for pn in pages:
            url = self.base_url.format(self.search_rules,pn)
            try:
                response = self.session.get(url, headers=self.headers, timeout=self.timeout)
            except Exception:
                pass
            else:
                self._extract_url(response)
        return self.urls

    def _extract_url(self,resp):
        soup = BeautifulSoup(resp.text, "lxml")
        div_tags = soup.find_all('div', 'site-title')
        for div_tag in div_tags:
            for a_tag in div_tag:
                url = a_tag['href']
                self.urls.append(url)
                print '[-]Hotbot: ' + url

def main(args_options):

    engines = args_options.engines
    output = args_options.output

    urls_queue = multiprocessing.Manager().list() # url队列

    # 搜索引擎索引
    supported_engines = {
        'baidu': Baidu_enum,
        'google': Google_enum,
        'yahoo': Yahoo_enum,
        'ecosia':Ecosia_enum,
        'teoma':Teoma_enum,
        '360':Qihu360_enum,
        'hotbot':Hotbot_enum,
    }
    chosen_enums = []

    if engines is None:
        # 默认选择所有搜索引擎
        chosen_enums = [
            Baidu_enum,
            Yahoo_enum,
            Ecosia_enum,
            Teoma_enum,
            Qihu360_enum,
            Google_enum,
            Hotbot_enum
        ]
    else:
        engines = engines.split(',')
        for engine in engines:
            if engine.lower() in supported_engines:
                chosen_enums.append(supported_engines[engine.lower()])   # 选择搜索引擎

    enums = [enum(args_options,q=urls_queue) for enum in chosen_enums]  # 列表生成式生成搜索引擎类的实例

    for enum in enums:
        enum.start()  # 启动搜索引擎爬取url
    for enum in enums:
        enum.join()

    urls = set(urls_queue)   #set对url去重
    write_file(output,urls)


if __name__ == '__main__':
    args = parse_args()
    main(args)