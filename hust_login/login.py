import requests
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
import json
import re
from base64 import b64encode, b64decode
from .decaptcha import decaptcha


def HustPass(username, password):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62'}
    # 建立session
    print('setting up session...')
    r = requests.session()
    r.headers.update(headers)
    # 请求网站HTML
    login_html = r.get('https://pass.hust.edu.cn/cas/login')
    # 请求验证码图片
    captcha_img = r.get('https://pass.hust.edu.cn/cas/code', stream=True)
    # 请求公钥并加密用户名密码
    print('encrypting u/p...')
    pub_key = RSA.import_key(b64decode(json.loads(
        r.post('https://pass.hust.edu.cn/cas/rsa').text)['publicKey']))
    cipher = PKCS1_v1_5.new(pub_key)
    encrypted_u = b64encode(cipher.encrypt(username.encode())).decode()
    encrypted_p = b64encode(cipher.encrypt(password.encode())).decode()
    # 抓取ticket
    nonce = re.search(
        '<input type="hidden" id="lt" name="lt" value="(.*)" />', login_html.text).group(1)
    execution = re.search(
        '<input type="hidden" name="execution" value="(.*)" />', login_html.text).group(1)
    post_params = {
        "rsa": None,
        "ul": encrypted_u,
        "pl": encrypted_p,
        "code": decaptcha(captcha_img.content),
        "phoneCode": None,
        "lt": nonce,
        "execution": execution,
        "_eventId": "submit"
    }
    print('posting login-form...')
    resp = r.post(
        "https://pass.hust.edu.cn/cas/login",
        data=post_params,
        allow_redirects=False
    )
    try:
        resp.headers['Location']
        print("---HustPass Succeed---")
        return r
    except:
        raise Exception("Error: ---HustPass Failed---")
