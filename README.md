# EngineCrawler
EngineCrawler 主要用于抓取国内外一些主流的搜索引擎搜索返回的url内容，目前支持以下的搜索引擎：
baidu，google，yahoo，ecosia，teoma，360，hotbot，脚本支持直接使用百度或者谷歌的高级搜索语法来进行搜索，谷歌搜索引擎不需要翻墙，抓取的数据是自己搭建的谷歌镜像站。

# Screen
[![asciicast](https://asciinema.org/a/rDfqOd2nvM3mmnMnz64rX6Q7U.png)](https://asciinema.org/a/rDfqOd2nvM3mmnMnz64rX6Q7U)

# Usage:
python EngineCrawler.py -e baidu,yahoo -r 'inurl:php?id=1' -p 10 -o
urls.txt
