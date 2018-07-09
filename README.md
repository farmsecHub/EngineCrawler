# EngineCrawler
EngineCrawler主要用于抓取国内外一些主流的搜索引擎搜索返回的url内容
目前支持以下的搜索引擎：
baidu，google，yahoo，ecosia，teoma，360，hotbot
可以直接使用百度或者谷歌的高级搜索语法来进行搜索，谷歌搜索引擎无需翻墙，抓取的数据是自己搭建的谷歌镜像站。

# Usage:
python EngineCrawler.py -e baidu,yahoo -r 'inurl:php?id=1' -p 10 -o
urls.txt
