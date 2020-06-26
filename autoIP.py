import random
import requests
from fake_useragent import UserAgent       # 随机User-Agent
from retrying import retry         # 重试下载
import lxml.html			# 用来解析网页

class ReptileIp(object):
    def __init__(self,init_url):
        __ua = UserAgent()
        self.init_url = init_url       # 网页地址
        self.headers = {'User-Agent':__ua.random}

    # 下载重试
    @retry(stop_max_attempt_number = 3) 	# 这个装饰器就是用来重试下载的 重试3次
    def download_html(self,url_str,data,method,proxies):
        if method == 'POST':  			# 判断请求方式
            result = requests.post(url_str,data=data,headers=self.headers,proxies=proxies)
        else:
            result = requests.get(url_str,headers=self.headers,timeout = 3,proxies=proxies)
        assert result.status_code == 200      # 断言，状态码不等于200说明失败了，重试下载
        return result.content    		# 返回网页HTML，字节流

    #下载内容
    def download_url(self,url_str,data=None,method = 'GET',proxies = {}):
     # 这里要捕获异常，请求网页出现错误在这里可以捕获到
        try:
            #  调用上面的写好的 重试下载download_html（）
            result = self.download_html(url_str,data,method,proxies)
        except Exception as e:
            print(e)
            result = None
        return result

    # 提取信息
    def filter_html(self,content):
        html = lxml.html.fromstring(content)
        data_host = html.xpath('//table/tr/td[last()-8]/text()')    # ip
        data_port = html.xpath('//table/tr/td[last()-7]/text()')    # 端口号
        data_http = html.xpath('//table/tr/td[last()-4]/text()')    # http/https
        proxies = [] 	  # 存放拼接好的ip地址
        for num in range(len(data_http)):
            http = data_http[num]
            host = data_host[num]      # ip  60.216.101.46
            port = data_port[num]	 # 端口号 59351
            https = http + '://' + host + ':' + port		# 拼接
            proxies.append(https)		# 添加进list
        return proxies

    def run(self):
        url_str = self.init_url		# url，
        # 下载链接
        html_content = self.download_url(url_str)		# 调用上面的下载
        # 提取ip		得到的是列表，转成字符串用！分割每个ip，方便后续读取解析
        proxies_list = '!'.join(self.filter_html(html_content))		# 调用上面的提取ip
        with open('ip.txt','w+') as fp:			# 保存进txt文件
            fp.write(proxies_list)

    # 校验ip
    def verify_ip(self):
        with open('ip.txt','r') as fp:		# 读取文件里的ip
            proxies_list = fp.read()
        proxies_list = proxies_list.split('!')	# 还记得存的是字符串，用！切割成列表
        p_list = random.sample(proxies_list,4)   	# 因为里面有100个ip校验起来比较慢，所以随机抽取4个，进行校验
        invalid_ip = []		# 存放失效的ip
        for url in p_list:
            proxies = {'http': url}
            # 这里通过访问百度的页面进行校验
            req = requests.get('https://www.baidu.com', headers=self.headers, proxies=proxies)
            if req.status_code == 200:	# 状态码是200，说明此ip能用
                continue
            else:
                invalid_ip.append(url)    	# 否则，存进要删除的列表中
        for i in invalid_ip:
            proxies_list.remove(i)		# 删除失效的ip
        return {'http': random.choice(proxies_list)}		# 随机返回一个能用的ip

if __name__ == '__main__':
    ip = ReptileIp('https://www.xicidaili.com/nn/2')
    # 获取   run()执行一次就可以了，
    ip.run()
    # 校验,并取1个ip
    print(ip.verify_ip())   #
