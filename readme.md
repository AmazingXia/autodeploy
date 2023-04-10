# 此项目只用于交流学习, 切勿用于其他用途

### 获取浏览器存于磁盘中的cookie并解密

### 打开钉钉给指定用户发送消息(mac不支持)

### 使用ttk搭建面板


安装依赖
 win32crypt  cryptography requests

https://www.pianshen.com/article/55691274750/



pipenv shell

pip list

pipenv install

pyinstaller  -F -w  main.py

win32crypt  cryptography requests

#### mac
pyinstaller --windowed --onefile --clean --noconfirm main.py
pyinstaller --clean --noconfirm --windowed --onefile main.spec

#### win
-F参数表示覆盖打包，这样在打包时，不管我们打包几次，都是最新的，这个记住就行，固定命令。
pyinstaller  -F -w  -p
pyinstaller -F -w-i wind.ico setup.py
Pyinstaller -F setup.py 打包exe
Pyinstaller -F -w setup.py 不带控制台的打包
Pyinstaller -F -i xx.ico setup.py 打包指定exe图标打包
pyinstaller  -F -w  main.py

#### -F：打包后只生成单个exe格式文件；
#### -D：默认选项，创建一个目录，包含exe文件以及大量依赖文件；
#### -c：默认选项，使用控制台(就是类似cmd的黑框)；
#### -w：不使用控制台；
#### -p：添加搜索路径，让其找到对应的库；
#### -i：改变生成程序的icon图标。