# -*- coding:'utf-8' -*-
import time,traceback,sqlite3,os,json,base64,sys

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.hashes import SHA1
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def decryptString(key,data):
    iv = data[3:15]
    cipherbytes = data[15:]
    aesgcm=AESGCM(key)
    plainbytes=aesgcm.decrypt(iv, cipherbytes, None)
    plaintext=plainbytes.decode('utf-8')
    return plaintext

def getKey():
    LocalState = ''
    if (os.path.exists(os.environ['LOCALAPPDATA']+r"\Google\Chrome\User Data\Local State")):
      LocalState  = os.environ['LOCALAPPDATA']+r"\Google\Chrome\User Data\Local State"
    elif (os.path.exists(os.environ['LOCALAPPDATA']+r"\Google\Chrome Dev\User Data\Local State")):
      LocalState  = os.environ['LOCALAPPDATA']+r"\Google\Chrome Dev\User Data\Local State"
    else:
      raise Exception('没有找到Cookie文件, 请使用正式版Chrome浏览器或者开发版Chrome浏览器!')

    with open(LocalState, 'r', encoding='utf-8') as f:
        base64_encrypted_key = json.load(f)['os_crypt']['encrypted_key']

    from win32crypt import CryptUnprotectData
    encrypted_key_with_header=base64.b64decode(base64_encrypted_key)
    encrypted_key=encrypted_key_with_header[5:] 
    key = CryptUnprotectData(encrypted_key,None,None,None,0)[1]
    # mykey = base64.b64encode(key)
    return key


def getChromeCookie(hostsUrl):
    cookiepath = ''
    if (os.path.exists(os.environ['LOCALAPPDATA']+r"\Google\Chrome\User Data\Default\Cookies")):
      cookiepath  = os.environ['LOCALAPPDATA']+r"\Google\Chrome\User Data\Default\Cookies"
    elif (os.path.exists(os.environ['LOCALAPPDATA']+r"\Google\Chrome\User Data\Default\Network\Cookies")):
      cookiepath  = os.environ['LOCALAPPDATA']+r"\Google\Chrome\User Data\Default\Network\Cookies"
    elif (os.path.exists(os.environ['LOCALAPPDATA']+r"\Google\Chrome Dev\User Data\Default\Cookies")):
      cookiepath  = os.environ['LOCALAPPDATA']+r"\Google\Chrome Dev\User Data\Default\Cookies"
    else: 
      raise Exception('没有找到Cookie文件, 请使用正式版Chrome浏览器或者开发版Chrome浏览器!')

    sql = f"select name,encrypted_value from cookies where host_key = '{hostsUrl}'"
  
    try:
        conn = sqlite3.connect(cookiepath)
        conn.text_factory =  bytes 
        res=conn.execute(sql).fetchall()
        conn.close()
    except Exception as e:
        print(e)
    key = getKey()
    
    if res: 
      return f'{decryptString(key, res.pop()[1])}' 
    else: return ''
    # cookieList.append( f'{str(row[0],encoding = "utf-8")}={decryptString(key, row[1])}')
    # row = res.pop()
    # return f'{decryptString(key, row[1])}'


def clean(decrypted: bytes) -> str:
    last = decrypted[-1]
    if isinstance(last, int):
        return decrypted[:-last].decode("utf8")
    return decrypted[: -ord(last)].decode("utf8")


def chrome_decrypt(encrypted_value: bytes, key: bytes, init_vector: bytes):
  encrypted_value = encrypted_value[3:]
  cipher = Cipher(algorithm=AES(key), mode=CBC(init_vector), backend=default_backend())
  decryptor = cipher.decryptor()
  decrypted = decryptor.update(encrypted_value) + decryptor.finalize()
  return clean(decrypted)

def chrome_cookies(url: str, browser: str = "Chrome",):
    import keyring

    file_path = ''
    if (os.path.exists(os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/Cookies'))):
      file_path  = os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/Cookies')
    elif (os.path.exists(os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/Network/Cookies'))):
      file_path  = os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/Network/Cookies')
    elif (os.path.exists(os.path.expanduser('~/Library/Application Support/Chromium/Default/Cookies'))):
      file_path  = os.path.expanduser('~/Library/Application Support/Chromium/Default/Cookies')
    elif (os.path.exists(os.path.expanduser('~/Library/Application Support/Google/Chrome Dev/Default/Cookies'))):
      file_path  = os.path.expanduser('~/Library/Application Support/Google/Chrome Dev/Default/Cookies')
    else:
      raise Exception('没有找到Cookie文件, 请使用正式版Chrome浏览器或者开发版Chrome浏览器!')

    config = {
        "my_pass": keyring.get_password(
            "{} Safe Storage".format(browser), browser
        ),
        "iterations": 1003,
        "cookie_file": file_path,
        "init_vector": b" " * 16,
        "length": 16,
        "salt": b"saltysalt"
    }
    
    if isinstance(config["my_pass"], str):
      config["my_pass"] = config["my_pass"].encode("utf8")

    kdf = PBKDF2HMAC(
        algorithm=SHA1(),
        backend=default_backend(),
        iterations=config["iterations"],
        length=config["length"],
        salt=config["salt"],
    )
    enc_key = kdf.derive(config["my_pass"])

    
    try:
        conn = sqlite3.connect(config["cookie_file"])
    except sqlite3.OperationalError:
        print("Unable to connect to cookie_file at: {}\n".format(config["cookie_file"]))
        raise

    sql = ("select name, encrypted_value from cookies where host_key like ?")

    cookies = ''

    for item in conn.execute(sql, (url,)).fetchall():
        cookies = chrome_decrypt(item[1], key=enc_key, init_vector=config["init_vector"])

    conn.rollback()

    return cookies


def getCookie(url):
  # mac环境
  if sys.platform == "darwin":
    return chrome_cookies(url)
  # windows系统
  elif sys.platform == 'win32':
    return getChromeCookie(url)

obj = {
  "Authorization": getCookie('www.baidu.com'),
}
print(json.dumps(obj))