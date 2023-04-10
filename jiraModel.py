# -*- coding:'utf-8' -*-
from pathlib import Path
import os, stat, shutil, time, subprocess, sys
import tempfile
import common
out_temp = tempfile.SpooledTemporaryFile(max_size=100*1000)
fileno = out_temp.fileno()

# stdout 是 none的时候  说明命令行运行出错,  输出在stderr上  stdout此时是None
# stdout 指向文件流的时候  无法通过stdout.read() 获取输出
# 

PWD = os.getcwd()

def checkJira(git_url = '', branch=''):
  if (branch == 'master'):
    return False
  try: 
    print('0===>', 0)
    print('PWD===>', PWD)
    if (not Path("./.deploy_temp").exists()):
      os.mkdir('./.deploy_temp')
    # os.chdir('./.deploy_temp')
    cwd = os.path.join(os.path.dirname(sys.argv[0]), './.deploy_temp')
    print('1===>', 1)
    gitRes = subprocess.Popen('git init', bufsize=1024, shell=False, stdout=fileno, stderr=fileno, cwd=cwd)
    gitRes.wait()
    print('2===>', 2)
    print('cwd===>', cwd)
    # common.alert(f"cwd===>{cwd}")
    
    print('3===>', 3)
    # common.alert(f"3===>3")
    print('4===>', 4)
    # common.alert(f"4===>4")
    # git remote add -f -t master -t dev -m master origin ssh://git@gitlab.didapinche.com:9122/web/web-passengerh5.git
    addRes = subprocess.Popen(f"git remote add -f -t master -t {branch} -m master origin {git_url}", bufsize=1024, shell=False, stdout=fileno, stderr=fileno, cwd=cwd)
    # addRes = subprocess.Popen(f"git remote add origin {git_url}", bufsize=1024, shell=False, stdout=fileno, stderr=fileno, cwd=cwd)
    addRes.wait()

    # print('git remote add origin===>', addRes.stdout.read())
    # print('5===>', 5)
    # common.alert(f"5===>5")

    # updateRes = subprocess.Popen(['git', 'remote', 'update', '-p'], bufsize=1024, shell=False, stdout=fileno, stderr=fileno, cwd=cwd)
    # updateRes.wait()
    # print('git remote update===>', updateRes.stdout.read().decode())
    # common.alert(f"git remote update===>{addRes.stdout.read().decode()}")

    # remRes= subprocess.Popen('git remote -v', bufsize=1024, shell=False, stdout=fileno, stderr=fileno, cwd=cwd)
    # remRes.wait()

    # print('git remote -v===>', remRes.stdout.read().decode())
    # common.alert(f"git remote -v===>{remRes.stdout.read().decode()}")
    # print('6===>', 6)
    # common.alert(f"6===>6")

    # git log remotes/origin/master ^remotes/origin/dev
    obj = subprocess.Popen(["git", "log", "remotes/origin/master", f"^remotes/origin/{branch}"],bufsize=1024, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    # obj = subprocess.Popen("git", "log", "remotes/origin/master", f"^remotes/origin/{branch}", bufsize=1024, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    obj.wait()
    print('7===>', 7)
    # common.alert(f"7===>7")
    # temp = obj.decode()
    temp = str(obj.stdout.read(), 'UTF-8')
    print('temp===>', temp)
    # common.alert(f"8===>8")
    # print('obj.stdout.read()===>',str(temp, 'UTF-8'))
    isLast = bool(len(temp))
    print('isLast===>', isLast)
    if (isLast):
      common.alert(f"落后于master, 自动合并中···")
      return mergeMaster(git_url, branch)
    else:
      common.alert(f"分支是否落后==> False")
      clear_folder()
      return False
          
    # common.alert(f"落后于master===>{isLast}")
  except subprocess.CalledProcessError as e:
    print('subprocess.CalledProcessError===>', e.output.decode())
    common.alert(f"checkBranch===> {e.output.decode()}")
  except Exception as result:
    print(result)
    common.alert(f'checkBranch===>{result}')
  finally:
    pass

def mergeMaster(git_url = '', branch=''):
  cwd = os.path.join(os.path.dirname(sys.argv[0]), './.deploy_temp')
  try:
    subprocess.Popen(f"git checkout -b {branch} origin/{branch}", bufsize=1024, shell=False, stdout=fileno, stderr=fileno, cwd=cwd).wait()
    
    mergeobj = subprocess.Popen(["git", "merge", "origin/master"], bufsize=1024, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd)
    mergeobj.wait()
    temp =  str(mergeobj.stdout.read(), 'UTF-8')
    print('mergeobj.stdout.read()===>', temp)
    
    if 'CONFLICT' in temp:
      common.show_info(f'存在冲突 请手动合并',)
      return True
    
    pushobj = subprocess.Popen(f"git push origin {branch}",bufsize=1024, shell=False, stdout=fileno, stderr=fileno, cwd=cwd)
    pushobj.wait()
    return False
  except subprocess.CalledProcessError as e:
    print('subprocess.CalledProcessError===>', e.output.decode())
    common.alert(f"error===> {e.output.decode()}")
    return True
    
  except Exception as result:
    print(result)
    common.alert(f'mergeMaster===>{result}')
    return True
  finally:
    clear_folder()

def clear_folder():
  os.chdir(PWD)
  if (Path("./.deploy_temp").exists()):
    print('123===>', 123)
    def readonly_handler(func, path, execinfo):
      os.chmod(path, stat.S_IWRITE)
      func(path)
    shutil.rmtree('./.deploy_temp', onerror=readonly_handler)



#  git remote show origin
# https://python3-cookbook.readthedocs.io/zh_CN/latest/c13/p06_executing_external_command_and_get_its_output.html