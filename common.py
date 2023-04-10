# -*- coding:'utf-8' -*-
import os, json, stat, shutil, sys

m3 = None
config = {
  'projectName': '',
  'branch': '',
  'jira': '',
  'env': '',
  'qa': '',
  'review': '',
  'pmo': '',
  'op': '',
  'stop': False,
  'rebuild': True,
  'projectNameTuple': [],
  'qaTuple': [],
  'branchTuple': [],
  'jiraTuple': [],
  'reviewTuple': [],
  'pmoTuple': [],
  'opTuple': [],
  'history': {},
  'method': 'auto',
  'delay': '120'
}

def modify(b):
  global m3
  m3=b
  print('common m3===>', m3)


def alert(m):
  global m3
  if m3:
    m3.alert(m)

def show_info(m, method = 'showinfo'):
  global m3
  if m3:
    res = m3.show_info(m, method)
    print(f'{method}===>{res}')
    return res
  return None


def init_config():
  try:
    with open(os.path.join(os.path.dirname(sys.argv[0]), 'deploy.json'), 'r', encoding='utf-8') as file:
      tempconfig = json.loads(file.read())
      config.update(tempconfig)
  except Exception as resaon:
    print('resaon===>', resaon)


def save_config():
  with open(os.path.join(os.path.dirname(sys.argv[0]), 'deploy.json'), 'w') as file:
    file.write(json.dumps(config, indent=2))