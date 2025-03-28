import json
from scrapy.exceptions import DropItem

class RotatingJsonPipeline:
    def __init__(self):
        self.item_count = 0  # 计数器
        self.file = None  # 当前文件句柄
        self.file_index = 0  # 文件序号
        self.max_items = 10000  # 每文件最大 Item 数
        self.base_filename = 'output'  # 基础文件名
    
    def open_spider(self, spider):
        # 爬虫开始时打开第一个文件
        self._open_new_file()
    
    def _open_new_file(self):
        # 关闭当前文件（如果存在）
        if self.file:
            self.file.close()
        # 打开新文件
        filename = f"{self.base_filename}_{self.file_index}.json"
        self.file = open(filename, 'w', encoding='utf-8')
        self.file.write('[\n')  # JSON 数组开始
        self.item_count = 0  # 重置计数器
        self.file_index += 1  # 文件序号递增
    
    def process_item(self, item, spider):
        # 转换为字典（如果 item 是 Scrapy Item 对象）
        item_dict = dict(item)
        
        # 检查是否需要轮转文件
        if self.item_count >= self.max_items:
            # 写入结束符并换新文件
            self.file.write('\n]')
            self._open_new_file()
        
        # 写入当前 Item
        if self.item_count > 0:
            self.file.write(',\n')  # 前一个 Item 后加逗号
        line = json.dumps(item_dict, ensure_ascii=False)
        self.file.write(line)
        self.item_count += 1
        
        return item
    
    def close_spider(self, spider):
        # 爬虫结束时关闭文件
        if self.file:
            self.file.write('\n]')  # JSON 数组结束
            self.file.close()