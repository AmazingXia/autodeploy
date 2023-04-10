from myRequest import fetch
import json, sys
from jiraModel import checkJira
from sendinfo import task, cancel_task

m3 = None

statusMap = {
  0: '',
  1: '等待中',
  2: '成功',
  3: '失败',
  4: '进行中',
}

appInfo = {
  'rebuild': True,
  'projectName': '',
  'review': '',
  'branch': '',
  'jira': '',
  'env': '',
  'qa': '',
  'pmo': '',
  'op': '',
  'id': '',
  'pipeline_id': '',
  'pipelineHistoryId': '',
  'currUserName': '',
  'currUserPhone': '',
  'QAphone': '',
  'deployLink': '',
}
Webhook = 'https://oapi.dingtalk.com/robot/send?access_token=XXX'
hasSendQaDing = False
hasSendPmoDing = False
hasSendOPDing = False

def sendNotice(phone, user):
  global appInfo
  if (not len(phone)):
    return

  text = ' '.join(list(map(lambda item: f"@{item}", phone))) 
  temp = '部署阿里云' if (appInfo['env'] == 'dev') else '上线'

  data = {
    'msgtype': 'markdown',
    'markdown': {
      'title': '流水线链接',
      'text': f"{text}  {appInfo['currUserName']}申请{temp}   [链接]({appInfo['deployLink']})",
    },
    'at': {
      'atMobiles': phone,
      'isAtAll': False,
    },
  }

  url = Webhook
  dingRes = fetch(url, method = 'post', data=data, host=None)
  
  if (dingRes['errcode'] == 0):
    m3.alert('已在钉钉通知===>')
    print('已在钉钉通知===>', )
  else:
    m3.alert(f'dingRes===>{dingRes}')
    print('dingRes===>', dingRes)

  methodSelect(f"申请{temp} \n {appInfo['deployLink']}", user)
  

# 部署测试环境
def deployTest(variables, from_stage_history_id, pipeline_name):
  data_test = {
    'app_id': appInfo['id'],
    'app_name': appInfo['projectName'],
    'from_stage_history_id': from_stage_history_id,
    'pipeline_history_id': appInfo['pipelineHistoryId'],
    'pipeline_id': appInfo['pipeline_id'],
    'pipeline_name': pipeline_name,
    'retry': False,
    'variables': variables
  }
  m3.alert("自动部署测试环境")
  fetch('https://www.baidu.com/run_pipeline/from_stage', method='post', data = data_test)


# 提交测试
def checkInTest (variables, from_stage_history_id, pipeline_name):
  checkRes = fetch(f"https://www.baidu.com/remote_variable/qa?search={appInfo['qa']}")
  # checkRes = list(filter(lambda item: item['label'] == appInfo['qa'], checkRes))
  if (len(checkRes) != 1):
    m3.alert(f'搜索到的QA===>{checkRes}')
    raise Exception('请输入准确的QA名称')
  variables[0]['value'] = json.dumps(checkRes[0], ensure_ascii=False, sort_keys=True)

  appInfo['QAphone'] = (json.loads(checkRes[0]['value'].replace('\\', '')))['phone']
  appInfo['qa'] = checkRes[0]['label']

  data_check = {
    'app_id': appInfo['id'],
    'app_name': appInfo['projectName'],
    'from_stage_history_id': from_stage_history_id,
    'pipeline_history_id': appInfo['pipelineHistoryId'],
    'pipeline_id': appInfo['pipeline_id'],
    'pipeline_name': pipeline_name,
    'retry': False,
    'variables': variables
  }
  m3.alert("自动提交测试")
  fetch('https://www.baidu.com/run_pipeline/from_stage', method='post', data = data_check)


# 提交上线
def submitOnline(variables, from_stage_history_id, pipeline_name):
  powerRes = fetch(f"https://www.baidu.com/remote_variable/power?power_id=check_online&search={appInfo['pmo']}")
  deployRes = fetch(f"https://www.baidu.com/remote_variable/power?power_id=deploy_online&search={appInfo['op']}")

  variables[0]['value'] = json.dumps(powerRes[0], ensure_ascii=False, sort_keys=True)
  variables[1]['value'] = json.dumps(deployRes[0], ensure_ascii=False, sort_keys=True)

  appInfo['PMOphone'] = (json.loads(powerRes[0]['value'].replace('\\', '')))['phone']
  appInfo['OPphone'] = (json.loads(deployRes[0]['value'].replace('\\', '')))['phone']

  data_online = {
    'app_id': appInfo['id'],
    'app_name': appInfo['projectName'],
    'from_stage_history_id': from_stage_history_id,
    'pipeline_history_id': appInfo['pipelineHistoryId'],
    'pipeline_id': appInfo['pipeline_id'],
    'pipeline_name': pipeline_name,
    'retry': False,
    'variables': variables
  }
  m3.alert("自动提交上线")
  fetch("https://www.baidu.com/run_pipeline/from_stage", method='post', data=data_online)


# 提交代码审核
def submitCodeReview(variables, from_stage_history_id, pipeline_name):
  codeRes = fetch(f"https://www.baidu.com/remote_variable/power?power_id=review_pass&search={appInfo['review']}")
  variables[0]['value'] = json.dumps(codeRes[0], ensure_ascii=False, sort_keys=True)

  data_code = {
    'app_id': appInfo['id'],
    'app_name': appInfo['projectName'],
    'from_stage_history_id': from_stage_history_id,
    'pipeline_history_id': appInfo['pipelineHistoryId'],
    'pipeline_id': appInfo['pipeline_id'],
    'pipeline_name': pipeline_name,
    'retry': False,
    'variables': variables
  }
  fetch("https://www.baidu.com/run_pipeline/from_stage", method='post', data=data_code)


# 合并分支到master
def mergeMaster(variables, from_stage_history_id, pipeline_name):
  data_merge = {
    'app_id': appInfo['id'],
    'app_name': appInfo['projectName'],
    'from_stage_history_id': from_stage_history_id,
    'pipeline_history_id': appInfo['pipelineHistoryId'],
    'pipeline_id': appInfo['pipeline_id'],
    'pipeline_name': pipeline_name,
    'retry': False,
  }
  fetch("https://www.baidu.com/run_pipeline/from_stage", method='post', data=data_merge)


def methodSelect(info, ding_user):
  global appInfo
  if (appInfo['method'] == 'close'):
    return
  if appInfo['method'] == 'auto':
    task(info, ding_user, int(appInfo['delay']))

def deploy(app, config = {}):
  global m3
  global appInfo
  global hasSendQaDing
  global hasSendPmoDing
  global hasSendOPDing

  hasSendQaDing = False
  hasSendPmoDing = False
  hasSendOPDing = False
  appInfo.update(config)
  m3 = app

  try:
    checkRes = fetch(f"https://www.baidu.com/remote_variable/qa?search={appInfo['qa']}")
    
    # checkRes = list(filter(lambda item: item['label'] == appInfo['qa'], checkRes))
    if (len(checkRes) != 1):
      m3.alert('请输入准确的QA姓名')
      m3.alert(f'搜索到的QA===>{checkRes}')
      raise Exception('请输入准确的QA姓名')
    appInfo['QAphone'] = (json.loads(checkRes[0]['value'].replace('\\', '')))['phone']
    appInfo['qa'] = checkRes[0]['label']



    userRes = fetch(url = 'https://www.baidu.com/api/tethys/v2/login/user')
    appInfo['currUserPhone'] = userRes['user']['phone']
    appInfo['currUserName'] = userRes['user']['name']


    res1 = fetch(f"https://www.baidu.com/app?page_num=1&page_size=10&name={appInfo['projectName']}&search_for=all&group=&label=&level=0&owner=&flag=&deleted=0&grey_deploy=false")
    res1['data'] = list(filter(lambda item: item['name'] == appInfo['projectName'], res1['data']))
    if (len(res1['data']) != 1):
      print('请输入准确的项目名称===>', )
      m3.alert('请输入准确的项目名称')
      m3.alert(f"搜索到的项目===>{res1['data']}")
      raise Exception('请输入准确的项目名称')
    else :
      appInfo['id'] = res1['data'][0]['id']
      appInfo['git_url'] = res1['data'][0]['git_url']
      appInfo['projectName'] = res1['data'][0]['name']

    m3.alert(f'检测分支是否落后·····')
    
    isLast = checkJira(git_url = appInfo['git_url'], branch = appInfo['branch'])
    if (isLast):
      m3.alert(f'已停止运行===>')
      return

      # 查询jira信息
    res2 = fetch(f"https://www.baidu.com/remote_variable/jira?search={appInfo['jira']}")
    # print('res2[0]===>', res2[0]['value'])
    jiraStatus = json.loads(res2[0]['value'].replace('\\', ''))
    m3.alert(f"JIRA状态===>{jiraStatus['status']}")
    if (jiraStatus['status'] != 'Resolved'):
      raise Exception('JIRA不是Resolved状态')
    appInfo['jiraName'] = res2[0]['label']


    # 获取流水线ID
    lineRes = fetch(f"https://www.baidu.com/pipeline?app_id={appInfo['id']}")
    appInfo['pipeline_id'] = lineRes[0]['id']

    if (appInfo['pipeline_id'] == ''):
      raise Exception('流水线ID不存在')

    data1 = {
      'branch': appInfo['branch'],
      'jira': json.dumps(res2[0], ensure_ascii=False),
      'pipeline_id': appInfo['pipeline_id'],
      'release_time': "",
    }

    # 
    if (appInfo['rebuild']):
      res3 = fetch('https://www.baidu.com/run_pipeline', method='post', data = data1)
      # print('创建流水线===>', res3)
      m3.alert('创建流水线')

    # 获取流水线最新的一次部署
    pipelineRes = fetch(f"https://www.baidu.com/pipeline_history_latest?pipeline_id={appInfo['pipeline_id']}")
    appInfo['pipelineHistoryId'] = pipelineRes['id']
    appInfo['deployLink'] = f"https://www.baidu.com/page/application/{appInfo['id']}/{appInfo['projectName']}/pipelines/{appInfo['pipeline_id']}?tabIndex=0&pipelineHistoryId={appInfo['pipelineHistoryId']}"

    def queryStatus(version = ''):
      global appInfo
      global hasSendQaDing
      global hasSendPmoDing
      global hasSendOPDing
      statusRes = fetch(f"https://www.baidu.com/run_pipeline/status?version={version}&pipeline_history_id={appInfo['pipelineHistoryId']}")

      lineStatus = statusRes['pipeline_history']['status'] #当前流水线状态   4进行中  0
      stage_histories = statusRes['pipeline_history']['stage_histories']

      if (len([item for item in stage_histories if (item['status'] == 3 and item['task_histories'][0]['name'] != '合并分支到master')])):
        print('当前流水线运行失败,重新构建中········')
        m3.alert("当前流水线运行失败,重新构建中····")
        res = m3.show_info('当前流水线运行失败,重新构建中', 'askretrycancel')
        if (res):
          appInfo['rebuild'] = True
          deploy(m3, config)
        return

      tempList = list(filter(lambda item: item['status'] != 2, stage_histories))

      if (len(tempList)):
        currStep = tempList[0]
      else:
        m3.alert("当前流水线以构建完成")
        return

      variables = currStep['task_histories'][0]['input_variables'] if 'input_variables' in currStep['task_histories'][0] else {}
      txt = statusMap.get(currStep['status'], '等待中')
      print(f"{currStep['name']}===>{txt}")
      m3.alert(f"{currStep['name']}===>{txt}")

      # 提交代码审核
      if ((lineStatus == 0 and currStep['name'] == '提交代码审核')):
        submitCodeReview(variables, currStep['id'], statusRes['pipeline_history']['pipeline_name'])

      # system_task_id
      #部署测试
      if (lineStatus == 0 and (currStep['permission'] == 'deploy_test' or (currStep['name'].find('部署') != -1  and currStep['name'].find('测试') != -1))):
        deployTest(variables, currStep['id'], statusRes['pipeline_history']['pipeline_name'])

      # 提交测试
      if (lineStatus == 0 and currStep['name'] == '提交测试'):
        checkInTest(variables, currStep['id'], statusRes['pipeline_history']['pipeline_name'])

      # 部署到阿里云
      if (lineStatus == 0 and currStep['permission'] == 'deploy_aliyun'):
        #通知QA
        if (not hasSendQaDing):
          hasSendQaDing = True
          sendNotice([appInfo['QAphone']], appInfo['qa'])
        # m3.alert(f"提示{appInfo['qa']}部署{appInfo['projectName']}")
        # m3.show_info(f"提示{appInfo['qa']}部署")
        # threading.Timer(30, m3.show_info(f"提示{appInfo['qa']}部署"), (30,)).start()
        
      # 测试通过
      if (lineStatus == 0 and (currStep['permission'] == 'test_pass' or currStep['name'] == '测试通过')):
        if (appInfo['env'] == 'dev'):
          print('部署阿里云成功===>', )
          m3.alert("部署阿里云成功")
          m3.alert("部署完成")
          m3.show_info('部署阿里云成功')
          cancel_task()
          return

      #提交上线 提示PMO审核通过
      if (lineStatus == 0 and currStep['name'] == '提交上线'):
        submitOnline(variables, currStep['id'], statusRes['pipeline_history']['pipeline_name'])
        
        if (not hasSendPmoDing):
          hasSendPmoDing = True

          if (not appInfo['PMOphone']):
            powerRes = fetch(f"https://www.baidu.com/remote_variable/power?power_id=check_online&search={appInfo['pmo']}")
            appInfo['PMOphone'] = (json.loads(powerRes[0]['value'].replace('\\', '')))['phone']

          sendNotice([appInfo['PMOphone']], appInfo['pmo'])

      #提示运维部署
      if (lineStatus == 0 and currStep['task_histories'] == 'deploy_online' or (currStep['name'].find('部署') != -1  and currStep['name'].find('线上') != -1)):
        cancel_task()
        if (not hasSendOPDing):
          hasSendOPDing = True

          if (not appInfo['OPphone']):
            deployRes = fetch(f"https://www.baidu.com/remote_variable/power?power_id=deploy_online&search={appInfo['op']}")
            appInfo['OPphone'] = (json.loads(deployRes[0]['value'].replace('\\', '')))['phone']
          
          sendNotice([appInfo['OPphone'], appInfo['currUserPhone']], appInfo['op'])

      if (lineStatus == 0 and currStep['task_histories'][0]['name'] == '合并分支到master'):
        cancel_task()
        print('部署线上成功===>')
        m3.alert("部署线上成功")
        m3.show_info('部署线上成功')
        mergeMaster(variables, currStep['id'], statusRes['pipeline_history']['pipeline_name'])
        if (currStep['status'] == 3):
          m3.alert("合并分支到master失败")
        return


      if (config.get('stop', False)):
        m3.alert('已停止===')
        print('已停止===>', )
        cancel_task()
        return 
      return queryStatus(statusRes['version'])

    # print(appInfo)
    queryStatus()

  except TypeError as e:
    m3.show_info('请先使用Chrome浏览器登录XX平台, 20秒后再运行')
    m3.alert(f'请登录XX平台')
    m3.alert(f'已停止运行===>')
  except Exception as result:
    print('Exception result===>', result)
    m3.alert(f'报错信息===>{result}')
    m3.alert(f'已停止运行===>')