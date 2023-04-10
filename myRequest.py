# -*- coding=utf-8 -*-
import requests
from auth import getCookie

Authorization=''
timeout=100 # 100秒后超时 

def fetch(url, method = 'get', params = {}, data = {}, host = 'www.baidu.com', token = ''):
  global Authorization
  if (not Authorization):
    Authorization = getCookie('www.baidu.com')
    if (not Authorization):
      raise Exception('Authorization不存在, 请登录XX平台20秒后再次尝试')

  try:
    headers = {
      'authorization': f'Bearer {Authorization}',
      'Authorization': f'Bearer {Authorization}',
      'cookie': f'Authorization={Authorization}',
      # 'x-acs-dingtalk-access-token': token,
      # 'Host': 'www.baidu.com',
      'content-type': 'application/json',
      'Accept-Language': 'zh-CN,zh;q=0.8',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
      # 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
    }


    res = requests.request(method, url=url.strip(), params= params, json=data, headers=headers, timeout=timeout)
    # print('res.status_code===>', res.status_code)
    # print('res.text===>', res.text)
    if res.status_code == 200:
      return res.json() if (res.text) else None
    else:
      if res.status_code == 401:
        Authorization = ''
      print('请求报错 res===>', res.text, '\n\r', url, '\n\r', data)
      raise Exception(f"请求报错 res===>{res.text}\n\rurl==> {url}\n\rdata===>{data}")
  except Exception as e:
    print('e===>', e)
    raise Exception(e)
