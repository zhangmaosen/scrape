import scrapy
import json

class ReportSpider(scrapy.Spider):
    name = 'report_spider'
    # 定义初始URL
    report_list_url = "https://reportapi.eastmoney.com/report/list2"
    
    # POST请求的payload
    payload = {
        "beginTime": "2023-03-25",
        "endTime": "2025-03-25",
        "industryCode": "*",
        "ratingChange": None,
        "rating": None,
        "orgCode": None,
        "code": "*",
        "rcode": "",
        "pageSize": 50,
        "pageNo":1
    }
    
    def start_requests(self):
        # 发送POST请求
        yield scrapy.Request(
            url=self.report_list_url,
            method='POST',
            body=json.dumps(self.payload),
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            callback=self.parse
        )
    
    def parse(self, response):
        # 将响应转换为JSON
        data = json.loads(response.text)
        total_page = data.get('TotalPage', 1)
        page_no = data.get('pageNo', 1)
        # 处理数据
        for item in data.get('data', []):
            yield item
        
        # 如果需要分页处理（假设有分页）
        total_page = data.get('TotalPage', 1)
        page_no = data.get('pageNo', 1)
        total_count = data.get('TotalCount', 0)
        current_count = len(data.get('data', []))
        if page_no < total_page:
            # 修改payload中的page参数进行翻页
            # 注意：具体分页参数需要根据API实际情况调整
            self.payload['pageNo'] = self.payload.get('pageNo', 0) + 1
            yield scrapy.Request(
                url=self.report_list_url,
                method='POST',
                body=json.dumps(self.payload),
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                },
                callback=self.parse
            )

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