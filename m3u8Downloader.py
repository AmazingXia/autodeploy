# -*- coding=utf-8 -*-
from tkinter import *
import tkinter.messagebox
from tkinter import ttk
from auto import MyCombobox
from myRequest import fetch
import common

pady = 9
page_size = 8

query_pro_url = f'https://www.baidu.com/app?page_num=1&page_size={page_size}&search_for=all&group=&label=&level=0&owner=&flag=&deleted=0&grey_deploy=false&name='
query_qa_url = f'https://www.baidu.com/remote_variable/qa?page_num=1&page_size={page_size}&search='
query_pmo_url = f'https://www.baidu.com/remote_variable/power?page_num=1&page_size={page_size}&power_id=check_online&search='
query_op_url = f'https://www.baidu.com/remote_variable/power?page_num=1&page_size={page_size}&power_id=deploy_online&search='
query_review_url = f'https://www.baidu.com/remote_variable/power?power_id=review_pass&search='
query_jira_url = f'https://www.baidu.com/remote_variable/jira?search='

def additional_validation_project(url, values):
  def func(_self, search_txt):
    get_url = url + search_txt
    res1 = fetch(get_url)

    if res1:
      list_t = list(set(values +  list(map(lambda item: item['name'], res1['data']))))
      _self['values'] = [i for i in list_t if i[:len(search_txt)] == search_txt]
      # _self['values'] = [i for i in list_t if search_txt in i]
  return func

    
def additional_validation(url, values):
  def func(_self, search_txt):
    get_url = url + search_txt
    res1 = fetch(get_url)
    _self['values'] = list(set(values +  list(map(lambda item: item['label'], res1))))
  return func


class M3u8Downloader:
  def __init__(self, **keyWords):
    self.root = Tk()
    self.root.wm_attributes('-topmost',1)
    self.title = "XX平台自动部署"
    self.version = "0.0.3"
    self.m3 = {}

    tabControl = ttk.Notebook(self.root)
    tab1 = ttk.Frame(tabControl)
    tab2 = ttk.Frame(tabControl) 
    tabControl.add(tab1, text='构建')
    tabControl.add(tab2, text='配置')
    tabControl.grid(row = 0, sticky = W, padx=3, pady = 6)


    self.auth = ""
    self.root.title("%s-%s" % (self.title, self.version))
    
    # 设置
    # self.frm = LabelFrame(self.root, text="设置")
    self.frm = LabelFrame(tab1, text="设置")
    self.frm.grid(row = 0, sticky = W + E + S + N, padx=10)
    
    
    self.setform = LabelFrame(tab2, text="设置")
    self.setform.grid(row = 0, sticky = W + N + E)
    self.varMethod = StringVar()
    self.varMethod.set(keyWords.get('method', 'auto'))
    Label(self.setform, text="发送钉钉消息方式:", font=("Lucida Grande", 11)).grid(row = 0, column = 0, sticky = W)
    self.rb1 = Radiobutton(self.setform, text='自动发送', variable=self.varMethod, value='auto', font=("Lucida Grande", 11))
    # self.rb2 = Radiobutton(self.setform, text='询问', variable=self.varMethod, value='inquiry', font=("Lucida Grande", 11))
    self.rb3 = Radiobutton(self.setform, text='关闭', variable=self.varMethod, value='close', font=("Lucida Grande", 11))
    self.rb1.grid(row = 0, column = 1, sticky = W, pady=0)
    # self.rb2.grid(row = 0, column = 2, sticky = W, pady=0)
    self.rb3.grid(row = 0, column = 1, sticky = E, pady=0)
    
    
    self.varDelay = StringVar()
    self.varDelay.set(keyWords['delay'])
    Label(self.setform, text="延时时间:", font=("Lucida Grande", 11)).grid(row = 1, column = 0, sticky = W)
    Entry(self.setform, width=26, textvariable=self.varDelay).grid(row = 1, column = 1, sticky = W, pady=pady)
    Label(self.setform, text="单位(秒)", font=("Lucida Grande", 11)).grid(row = 1, column = 2, sticky = W)
    
    
    self.varProName = StringVar()
    self.varProName.set(keyWords['projectName'])
    Label(self.frm, text="项目名称:", font=("Lucida Grande", 11)).grid(row = 0, column = 0, sticky = W)
    # self.project_name = Entry(self.frm, width=26, textvariable=self.varProName)
    self.project_name = MyCombobox(self.frm, width=26, textvariable=self.varProName, key_word = 'projectNameTuple', values = keyWords['projectNameTuple'], additional_validation = additional_validation_project(query_pro_url, keyWords['projectNameTuple']))
    self.project_name.grid(row = 0, column = 1, sticky = W, pady=pady)
    self.project_name.set(keyWords['projectName'])

    self.varBranchName = StringVar()
    self.varBranchName.set(keyWords['branch'])
    Label(self.frm, text="分支:", font=("Lucida Grande", 11)).grid(row = 1, column = 0, sticky = W)
    # self.branch_instance = Entry(self.frm, width=26, textvariable=self.varBranchName)
    self.branch_instance = MyCombobox(self.frm, width=26, textvariable=self.varBranchName, key_word = 'branchTuple', values = keyWords['branchTuple'])
    self.branch_instance.set(keyWords['branch'])
    self.branch_instance.grid(row = 1, column = 1, sticky = W, pady=pady)


    self.varJiraName = StringVar()
    self.varJiraName.set(keyWords['jira'])
    Label(self.frm, text="JIRA:", font=("Lucida Grande", 11)).grid(row = 2, column = 0, sticky = W)
    # self.jira_instance = Entry(self.frm, width=26, textvariable=self.varJiraName)
    self.jira_instance = MyCombobox(self.frm, width=26, textvariable=self.varJiraName, key_word = 'jiraTuple', values = keyWords['jiraTuple'])
    self.jira_instance.set(keyWords['jira'])
    self.jira_instance.grid(row = 2, column = 1, sticky = W, pady=pady)
    
    self.varQaName = StringVar()
    self.varQaName.set(keyWords['qa'])
    Label(self.frm, text="QA:", font=("Lucida Grande", 11)).grid(row = 3, column = 0, sticky = W)
    # self.qa_instance = Entry(self.frm, width=26,  textvariable=self.varQaName)
    self.qa_instance = MyCombobox(self.frm, width=26, textvariable=self.varQaName, key_word = 'qaTuple', values = keyWords['qaTuple'], additional_validation = additional_validation(query_qa_url, keyWords['qaTuple']))
    self.qa_instance.set(keyWords['qa'])
    self.qa_instance.grid(row = 3, column = 1, sticky = W, pady=pady)


    self.varReview = StringVar()
    self.varReview.set(keyWords['review'])
    Label(self.frm, text="代码审核:", font=("Lucida Grande", 11)).grid(row = 4, column = 0, sticky = W)
    # self.review_instance = Entry(self.frm, width=26,  textvariable=self.varReview) 
    self.review_instance = MyCombobox(self.frm, width=26, textvariable=self.varReview, key_word = 'reviewTuple', values = keyWords['reviewTuple'],  additional_validation = additional_validation(query_review_url, keyWords['reviewTuple']))
    self.review_instance.set(keyWords['review'])
    self.review_instance.grid(row = 4, column = 1, sticky = W, pady=pady)
    
    self.varEnv = StringVar()
    self.varEnv.set(keyWords.get('env', ''))
    Label(self.frm, text="部署环境:", font=("Lucida Grande", 11)).grid(row = 5, column = 0, sticky = W)
    self.rb1 = Radiobutton(self.frm, text='阿里云', variable=self.varEnv, value='dev', font=("Lucida Grande", 11))
    self.rb2 = Radiobutton(self.frm, text='线上', variable=self.varEnv, value='online', font=("Lucida Grande", 11))
    self.rb1.grid(row = 5, column = 1, sticky = W, pady=0)
    self.rb2.grid(row = 5, column = 1, sticky = E, pady=pady)

    def xFunc(event):
      history = common.config.get('history', {})
      project_name = self.project_name.get()
      if (project_name in history):
        self.branch_instance.delete(0, END)
        self.branch_instance['value'] = history[project_name]['branch']
        self.branch_instance.current(0)

        self.jira_instance.delete(0, END)
        self.jira_instance['value'] = history[project_name]['jira']
        self.jira_instance.current(0)

        self.qa_instance.delete(0, END)
        self.qa_instance['value'] = history[project_name]['qa']
        self.qa_instance.current(0)

        self.review_instance.delete(0, END)
        self.review_instance['value'] = history[project_name]['review']
        self.review_instance.current(0)

    self.project_name.bind("<<ComboboxSelected>>", xFunc)
    
    self.button_start = Button(self.frm, text="开始运行", width=8, height=3, font=("Lucida Grande", 11))
    self.button_start.place(anchor=E, relx=1, rely=0.15)
    self.button_exit = Button(self.frm, text="构建上次", width = 8, height=3,font=("Lucida Grande", 11))
    self.button_exit.place(anchor=E, relx=1, rely=0.45, )
    self.button_stop = Button(self.frm, text="停止", width = 8, height=3,font=("Lucida Grande", 11))
    self.button_stop.place(anchor=E, relx=1, rely=0.75, )
    
    
    if (keyWords['env'] == 'online'):
      self.varPmoName = StringVar()
      self.varPmoName.set(keyWords['pmo'])
      self.pmo_lable = Label(self.frm, text="PMO:", font=("Lucida Grande", 11))
      self.pmo_lable.grid(row = 6, column = 0, sticky = W)
      # self.pmo_instance = Entry(self.frm, width=26, textvariable=self.varPmoName)
      self.pmo_instance = MyCombobox(self.frm, width=26, textvariable=self.varPmoName, key_word = 'pmoTuple', values = keyWords['pmoTuple'], additional_validation = additional_validation(query_pmo_url, keyWords['pmoTuple']))
      self.pmo_instance.set(keyWords['pmo'])
      self.pmo_instance.grid(row = 6, column = 1, sticky = W, pady=pady)
      
      
      self.varOpName = StringVar()
      self.varOpName.set(keyWords['op'])
      self.op_lable = Label(self.frm, text="运维:", font=("Lucida Grande", 11))
      self.op_lable.grid(row = 7, column = 0, sticky = W)
      # self.op_instance = Entry(self.frm, width=26, textvariable=self.varOpName)
      self.op_instance = MyCombobox(self.frm, width=26, textvariable=self.varOpName, key_word = 'opTuple', values = keyWords['opTuple'], additional_validation = additional_validation(query_op_url, keyWords['opTuple']))
      self.op_instance.set(keyWords['op'])
      self.op_instance.grid(row = 7, column = 1, sticky = W, pady=pady)
    
    # 消息
    # self.message_frm = LabelFrame(self.root, text="消息", )
    self.message_frm = LabelFrame(tab1, text="消息", )
    self.message_frm.grid(row = 1, columnspan=1, padx=10, pady=10, sticky = S + N)

    self.scrollbar = Scrollbar(self.message_frm)
    self.scrollbar.pack(side='right', fill='y')
    self.message_v = StringVar()
    self.message_s = ""
    self.message_v.set(self.message_s)

    # self.message = Text(self.message_frm, width=59, height=22)
    self.message = Text(self.message_frm, width=59, height=19)
    # self.message = Text(self.message_frm)
    self.message.insert('insert', self.message_s)
    self.message.pack(side='bottom', fill='both', expand=1)
    # 以下两行代码绑定text和scrollbar
    self.scrollbar.config(command=self.message.yview)
    self.message.config(yscrollcommand=self.scrollbar.set)
    self.message.config(state=DISABLED)
    # print('dir(self.root)===>', dir(self.root))
    # print('self.size===>', self.root.size())
    # print('winfo_rooty===>', self.root.winfo_rooty())
    # print('winfo_screenwidth===>', self.root.winfo_screenwidth())
    # print('winfo_screenwidth===>', self.root.winfo_screenwidth())
    # print('winfo_width===>', self.root.winfo_width())
    # print('winfo_width===>', self.root.winfo_height())
    ws, hs = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
    self.root.geometry("+%d+%d" % (-ws * 3, -hs * 3))
    self.root.resizable(0, 0)

  def alert(self, m):
    if m:
      self.message.config(state=NORMAL)
      self.message.insert(END, m + "\n")
      # 确保scrollbar在底部
      self.message.see(END)
      self.message.config(state=DISABLED)
    self.root.update()

  def clear_alert(self):
    self.message.config(state=NORMAL)
    self.message.delete('1.0', 'end')
    self.message.config(state=DISABLED)
    self.root.update()

  def update_size(self):
    w = self.root.winfo_width()
    h = self.root.winfo_height()
    ws, hs = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
    self.root.geometry("+%d+%d" % ((ws - w - 20), (hs / 2) - (h / 2)))

  # askquestion
  # askokcancel
  # askyesno
  # askretrycancel
  def show_info(self, m, method = 'showinfo'):
    method = getattr(tkinter.messagebox, method)
    res = method(self.title,  m)
    return res
    

  def remove_label(self, **keyWords):
    env = keyWords['env']
    if (env == 'dev'):
      if (hasattr(self, 'pmo_lable')):
        self.pmo_lable.destroy()
        self.pmo_instance.destroy()
        self.op_lable.destroy()
        self.op_instance.destroy()
        del self.pmo_lable
        del self.pmo_instance
        del self.op_instance
        
    elif (env == 'online'):
      
      if (not hasattr(self, 'pmo_lable')):
        self.pmo_lable = Label(self.frm, text="PMO:", font=("Lucida Grande", 11))
        self.pmo_lable.grid(row = 6, column = 0, sticky = W)
        self.varPmoName = StringVar()
        self.varPmoName.set(keyWords['pmo'])
        # self.pmo_instance = Entry(self.frm, width=26, textvariable=self.varPmoName)
        self.pmo_instance = MyCombobox(self.frm, width=26, textvariable=self.varPmoName, key_word = 'pmoTuple', values = keyWords['pmoTuple'], additional_validation = additional_validation(query_pmo_url, keyWords['pmoTuple']))
        self.pmo_instance.set(keyWords['pmo'])
        self.pmo_instance.grid(row = 6, column = 1, sticky = W, pady=pady)

        self.varOpName = StringVar()
        self.varOpName.set(keyWords['op'])
        self.op_lable = Label(self.frm, text="运维:", font=("Lucida Grande", 11))
        self.op_lable.grid(row = 7, column = 0, sticky = W)
        # self.op_instance = Entry(self.frm, width=26, textvariable=self.varOpName)
        self.op_instance = MyCombobox(self.frm, width=26, textvariable=self.varOpName, key_word = 'opTuple', values = keyWords['opTuple'], additional_validation = additional_validation(query_op_url, keyWords['opTuple']))
        self.op_instance.set(keyWords['op'])
        self.op_instance.grid(row = 7, column = 1, sticky = W, pady=pady)

        self.root.update()


# https://www.jb51.net/article/190379.htm?tdsourcetag=s_pcqq_aiomsg
# 我们使用上述的方法得到的位置和宽高，其实是tk初始化时的一个值。
# 因此在初始化的时候默认都是1，如果需要获取准确的位置和大小信息 此时我们调用update方法，刷新win窗口。