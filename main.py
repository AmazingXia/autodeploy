# -*- coding=utf-8 -*-
import os, json, stat, shutil
from pathlib import Path
import m3u8Downloader
from deploy import deploy
from jiraModel import clear_folder
from  threading import Thread
from auth import getCookie
import sys
import codecs
import common

# mac
# sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

m3 = None


def myAsync(fun):
  def wrapper(*args, **kwargs):
    print('fun===>', fun)
    thr = Thread(target = fun, args=args, kwargs=kwargs)
    thr.setDaemon(True)
    thr.start()
  return wrapper


def stop():
  m3.alert('停止中······')
  common.config['stop'] = True


# 设置排序模式
def order_type(env = ''):
  global m3
  common.config['env'] = env
  m3.remove_label(**common.config)


@myAsync
def start(rebuild = False):
  global m3
  config = common.config
  m3.clear_alert()


  # m3.alert(f'sys.argv===>{sys.argv}')
  # m3.alert(f'os.getcwd()===>{os.getcwd()}')
  # m3.alert(f'os.path.dirname(os.path.realpath(sys.argv[0]))===>{os.path.dirname(os.path.realpath(sys.argv[0]))}')


  # try:
  #   with open(os.path.join(os.path.dirname(sys.argv[0]), 'deploy.json'), 'r', encoding='utf-8') as file:
  #     config = json.loads(file.read())
  #     m3.alert(f"config==>{config}")
  # except Exception as resaon:
  #   print('resaon===>', resaon)
  #   m3.alert(f"esaon===>{resaon}")
  
  try:
    config['projectName'] = m3.varProName.get().strip()
    config['review'] = m3.varReview.get().strip()
    config['branch'] = m3.varBranchName.get().strip()
    config['jira'] = m3.varJiraName.get().strip()
    config['qa'] = m3.varQaName.get().strip()
    config['env'] = m3.varEnv.get().strip()
    config['method'] = m3.varMethod.get().strip()
    config['delay'] = m3.varDelay.get().strip()
    config['rebuild'] = rebuild
    config['stop'] = False


    if (config['projectName'] not in config['projectNameTuple'] and config['projectName']):
      config['projectNameTuple'].insert(0, config['projectName'])

    if (config['branch']  not in config['branchTuple'] and config['branch']):
      config['branchTuple'].insert(0, config['branch'])

    if (config['jira']  not in config['jiraTuple'] and config['jira']):
      config['jiraTuple'].insert(0, config['jira'])

    if (config['qa']  not in config['qaTuple'] and config['qa']):
      config['qaTuple'].insert(0, config['qa'])

    if (config['review']  not in config['reviewTuple'] and config['review']):
      config['reviewTuple'].insert(0, config['review'])

    if (config['branch']  not in m3.branch_instance['values'] and config['branch']):
      m3.branch_instance['values'] = [config['branch'], ] + list(m3.branch_instance['values'])

    if (config['jira']  not in m3.jira_instance['values'] and config['jira']):
      m3.jira_instance['values'] = [config['jira'], ] + list(m3.jira_instance['values'])

      

    if (hasattr(m3, 'varPmoName') and hasattr(m3, 'varOpName') and hasattr(m3, 'pmo_instance')):
      if (config['pmo']  not in config['pmoTuple']):
        config['pmoTuple'].insert(0, config['pmo'])

      if (config['op']  not in m3.op_instance['values']):
        config['opTuple'].insert(0, config['op'])

      config['pmo'] = m3.varPmoName.get().strip()
      config['op'] = m3.varOpName.get().strip()

    history = config.get('history', {})

    if (config['projectName'] not in history and config['projectName']):
      history[config['projectName']] = {
        'pmo': [],
        'op': [],
        'qa': [],
        'jira': [],
        'branch': [],
        'review': [],
        'env': [],
      }

    print('history===>', history[config['projectName']], )
      
    if (config['pmo'] in history[config['projectName']]['pmo']):
      history[config['projectName']]['pmo'].remove(config['pmo'])  
    if (config['op'] in history[config['projectName']]['op']):
      history[config['projectName']]['op'].remove(config['op'])  
    if (config['jira'] in history[config['projectName']]['jira']):
      history[config['projectName']]['jira'].remove(config['jira'])  
    if (config['branch'] in history[config['projectName']]['branch']):
      history[config['projectName']]['branch'].remove(config['branch'])  
    if (config['review'] in history[config['projectName']]['review']):
      history[config['projectName']]['review'].remove(config['review'])  
    if (config['op'] in history[config['projectName']]['op']):
      history[config['projectName']]['op'].remove(config['op'])  
    if (config['env'] in history[config['projectName']]['env']):
      history[config['projectName']]['env'].remove(config['env'])  
    if (config['qa'] in history[config['projectName']]['qa']):
      history[config['projectName']]['qa'].remove(config['qa'])

    history[config['projectName']]['pmo'].insert(0, config['pmo'])
    history[config['projectName']]['op'].insert(0, config['op'])
    history[config['projectName']]['jira'].insert(0, config['jira'])
    history[config['projectName']]['branch'].insert(0, config['branch'])
    history[config['projectName']]['review'].insert(0, config['review'])
    history[config['projectName']]['op'].insert(0, config['op'])
    history[config['projectName']]['env'].insert(0, config['env'])
    history[config['projectName']]['qa'].insert(0, config['qa'])

    m3.alert('开始执行')
    # print('project_name===>',  m3.project_name['values'])
    print('开始执行config===>\n', config)
    # m3.alert(f"config===>{config}")

    common.save_config()
  except Exception as resaon:
    m3.alert(f'报错信息===>{resaon}')
    print('main.py 153 Exception===>', resaon)
  else:
    deploy(m3, config)
    # sys.exit(0)
    # m3.show_info("任务执行中，请勿重复开启任务")


def after_draw():
  m3.update_size()
  # 绑定点击事件
  m3.rb1.bind("<Button-1>", lambda x: order_type('dev'))
  m3.rb2.bind("<Button-1>", lambda x: order_type('online'))
  m3.button_start.bind("<Button-1>", lambda x: start(True))
  m3.button_exit.bind("<Button-1>", lambda x: start(False))
  m3.button_stop.bind("<Button-1>", lambda x: stop())
  # m3.button_stop.bind("<Button-1>", lambda x: m3.show_info('shi?', 'askyesno'))
  # 手动加入消息队列-
  # 校验是否可以获取最新的cookie
  if(not getCookie('www.baidu.com')):
    m3.show_info('请先使用Chrome浏览器登录XX平台, 20秒后再运行')
    sys.exit(0)
  m3.root.update()


def run():
  global m3
  print('common.config===>', common.config)
  clear_folder()
  m3 = m3u8Downloader.M3u8Downloader(**common.config)
  common.modify(m3)
  m3.root.update()
  m3.root.after(1, after_draw)
  m3.root.mainloop()

if __name__ == "__main__":
  common.init_config()
  run()