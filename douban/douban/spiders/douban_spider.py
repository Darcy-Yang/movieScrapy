# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from douban.items import douban
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import string

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
      detail = item.css('.pic a::attr("href")').extract()[0]
      request = scrapy.Request(response.urljoin(detail), callback = self.get_detail)
      yield request
      if response.css('span.next a::attr("href")'):
        next_page = response.css('span.next a::attr("href")').extract()[0]
        next_url = response.urljoin(next_page)
        yield scrapy.Request(next_url, callback = self.parse)

  def get_detail(self, response):
    movie = douban()
    for item in response.css('div#content'):
      movie['director'] = ''
      movie['writer'] = ''
      movie['actor'] = ''
      movie['type'] = ''
      movie['time'] = ''
      movie['run_time'] = ''
      movie['title'] = (item.css('h1 span::text').extract()[0].encode('utf-8')).split(' ')[0]
      movie['time'] = item.css('h1 span::text').extract()[1].encode('utf-8')
      movie['poster'] = item.css('div#mainpic img::attr("src")').extract()[0]
      movie['star'] = item.css('strong.rating_num::text').extract()[0]

      for detail in item.css('span'):
        if (detail.css('::attr("property")').extract()):
          if (detail.css('::attr("property")').extract()[0] == 'v:genre'):
            movie['type'] = movie['type'] + ' ' + detail.css('::text').extract()[0].encode('utf-8')
          if (detail.css('::attr("property")').extract()[0] == 'v:initialReleaseDate'):
            # 取最后一个作为时间和地区的值
            time_and_area = (detail.css('::text').extract()[0].encode('utf-8')).split('(')
            movie['time'] = time_and_area[0]
            movie['area'] = time_and_area[1].split(')')[0]
          if (detail.css('::attr("property")').extract()[0] == 'v:runtime'):
            movie['run_time'] = movie['run_time'] + ' ' + detail.css('::text').extract()[0].encode('utf-8')
          if (detail.css('::attr("property")').extract()[0] == 'v:votes'):
            movie['votes'] = detail.css('::text').extract()[0]
          if (detail.css('::attr("property")').extract()[0] == 'v:summary'):
            summary = (detail.css('::text').extract()[0].encode('utf-8'))
            movie['summary'] = string.strip(summary)

      for index in range(len(response.css('span.attrs'))):
        if (index == 0):
          for detail in (response.css('span.attrs')[index]).css('a'):
            movie['director'] = movie['director'] + ' ' + detail.css('::text').extract()[0].encode('utf-8')
        if (index == 1):
          for detail in (response.css('span.attrs')[index]).css('a'):
            movie['writer'] = movie['writer'] + ' ' + detail.css('::text').extract()[0].encode('utf-8')
        if (index == 2):
          for detail in (response.css('span.attrs')[index]).css('a'):
            movie['actor'] = movie['actor'] + ' ' + detail.css('::text').extract()[0].encode('utf-8')
    yield movie

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
