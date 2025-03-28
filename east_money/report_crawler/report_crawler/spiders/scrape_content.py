import scrapy
import json
import datetime
class ReportContentSpider(scrapy.Spider):
    name = 'report_content_spider'
    # 定义初始URL
    report_url_prev = "https://data.eastmoney.com/report/zw_strategy.jshtml?encodeUrl="
    
    # 自定义设置
    custom_settings = {
        'FEEDS': {
            f'output_{datetime.datetime.now().strftime("%Y%m%d")}.json': {
                'format': 'json',
                'encoding': 'utf8',
                'store_empty': False,
                'indent': 4,
            },
        }
    }
    
    def start_requests(self):
        #读取文件 report_list.json
        with open('report_list.json', 'r', encoding='utf-8') as file:
            report_list = json.load(file)
        
        for report in report_list:
            url = self.report_url_prev + report['encodeUrl']
            # 发送POST请求
            yield scrapy.Request(
                url=url,
                method='GET',
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                },
                meta=report,
                callback=self.parse
            )
            
            #break
    
    def parse(self, response):
        #使用css selector 进行内容抽取
        content = response.css('div#ctx-content').get()
        yield {
            'content': content
        } | response.meta

# settings.py 文件中的推荐配置
BOT_NAME = 'report_crawler'

SPIDER_MODULES = ['your_project.spiders']
NEWSPIDER_MODULE = 'your_project.spiders'

# 遵守robots.txt规则
ROBOTSTXT_OBEY = False

# 配置默认请求头
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

# 下载延迟
DOWNLOAD_DELAY = 2

# 并发请求数
CONCURRENT_REQUESTS = 16