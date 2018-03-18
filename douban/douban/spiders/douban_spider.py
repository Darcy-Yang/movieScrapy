# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from douban.items import douban
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class DoubanSpider(Spider):
  name = 'douban'
  allowed_domains = ['movie.douban.com']
  start_urls = [  
      "https://movie.douban.com/top250" 
  ]

  def parse(self, response):
    # filename = response.url.split('/')[-2]
    # open(filename, 'wb').write(response.body)
    movie = douban()
    for item in response.css('div.item'):
      movie['order'] = item.css('.pic em::text').extract()
      movie['title'] = item.css('.title::text').extract()[0].encode('utf-8')
      movie['img_src'] = item.css('img::attr("src")').extract()[0]
      info = item.css('.bd p::text').extract()[0].encode('utf-8')
      movie['info'] = info.lstrip().rstrip()
      movie['movietype'] = item.css('.bd p').extract()[0].split('<br>')[1].split('</p>')[0].lstrip().rstrip()
      movie['star'] = item.css('.rating_num::text').extract()
      movie['votes'] = item.css('.star span:nth-child(4)::text').extract()[0].encode('utf-8')
      # print movie['info'].lstrip().rstrip()
      if item.css('.inq::text'):
        movie['quote'] = item.css('.inq::text').extract()[0].encode('utf-8')
      else:
        movie['quote'] = ''
      yield movie
    if response.css('span.next a::attr("href")'):
      next_page = response.css('span.next a::attr("href")').extract()[0]
      next_url = response.urljoin(next_page)
      yield scrapy.Request(next_url, callback = self.parse)

class MtimeSpider(Spider):
  name = 'mtime'
  allowed_domains = ['www.mtime.com']
  start_urls = [
    "http://www.mtime.com/top/movie/top100/"
  ]
  
  def parse(self, response):
    chromedriver = "/Applications/Google Chrome.app/Contents/MacOS/chromedriver"
    opener = webdriver.Chrome(chromedriver)
    
    poster = douban()
    for item in response.css('h2.px14'):
      images_url = item.css('a::attr("href")').extract()[0] + 'posters_and_images/'
      poster['title'] = item.css('a::text').extract()[0].encode('utf-8')
      opener.get(images_url)
      poster['poster_url'] = opener.execute_script("return imageList[0].stagepicture[0].officialstageimage[0].img_1000")
      yield poster
    for num in range(2, 11):
      next_url = 'http://www.mtime.com/top/movie/top100/index-' + str(num) + '.html'
      yield scrapy.Request(next_url, callback = self.parse)

class MovieFM(Spider):
  name = 'moviefm'
  allowed_domains = 'dianying.fm'
  start_urls = [
    'http://dianying.fm/collection/'
  ]

  def parse(self, response):
    fm = douban()
    for item in response.css('li'):
      if item.css('.fm-co-cover'):
        fm['album_link'] = 'dianying.fm' + item.css('.fm-co-cover a::attr("href")').extract()[0]
        fm['album_img_url'] = item.css('.fm-co-cover a img::attr("src")').extract()[0]
        fm['title'] = item.css('.fm-co-desc div a::text').extract()[0].encode('utf-8')
        fm['info'] = item.css('.fm-co-desc div:nth-child(3)::text').extract()[0]
        yield fm
      else: 
        pass  
