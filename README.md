# EngineCrawler
EngineCrawler 主要用于抓取国内外一些主流的搜索引擎，搜索返回的url内容，目前支持以下的搜索引擎：
baidu，google，yahoo，ecosia，teoma，360，hotbot，脚本支持直接使用百度或者谷歌的高级搜索语法来进行搜索，谷歌搜索引擎不需要翻墙，抓取的数据是自己搭建的谷歌镜像站。
在使用的时候如果遇到了什么问题，欢迎留言反馈～email:yawen.sir@gmail.com

# Screen
[![asciicast](https://asciinema.org/a/dtDAIIPkRKhArVL6M0yebqIE9.png)](https://asciinema.org/a/dtDAIIPkRKhArVL6M0yebqIE9)
# Usage:
python EngineCrawler.py -e baidu,yahoo -r 'inurl:php?id=1' -p 10 -o
urls.txt
