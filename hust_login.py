import requests
from logging import root as log
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
import json
import re
from base64 import b64encode, b64decode
from io import BytesIO
import pytesseract
from PIL import Image

def decaptcha(img_content):
    log.debug('decaptching...')
    img_list = []
    with Image.open(BytesIO(img_content)) as img_gif:
        for i in range(img_gif.n_frames):
            img_gif.seek(i)
            img_list.append(img_gif.copy().convert('L'))
    width,height = img_list[0].size
    img_merge = Image.new(mode='L',size=(width,height),color=255)
    for pos in [(x,y) for x in range(width) for y in range(height)]:
        if sum([img.getpixel(pos) < 254 for img in img_list]) >= 3:
            img_merge.putpixel(pos,0)
    try:
        captcha_code = pytesseract.image_to_string(img_merge, config='-c tessedit_char_whitelist=0123456789 --psm 6')
    except pytesseract.TesseractNotFoundError:
        raise EnvironmentError('tesseract-ocr is not found or not installed!\n tesseract-ocr未找到或未安装')
    log.debug('captcha_code:{}'.format(captcha_code.strip()))
    # img_merge.save('./src/decaptcha/blended.png')
    return captcha_code

def HustPass(username:str, password:str) -> 'requests.Session': # 以便ide进行类型检查与代码补全
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62'}
    # 建立session
    log.info('setting up session...')
    r = requests.session()
    r.headers.update(headers)
    # 请求网站HTML
    login_html = r.get('https://pass.hust.edu.cn/cas/login')
    # 检查是否需要输入验证码
    captcha_check = re.search('<div class="ide-code-box">(.*)</div>', login_html.text, re.S) is not None # 未取得不使用验证码的网页样本，这个判断可能不符合预期
    if captcha_check:
        # 请求验证码图片
        captcha_img = r.get('https://pass.hust.edu.cn/cas/code', stream=True)
        log.info('captcha detected, trying to decaptcha...')
    # 请求公钥并加密用户名密码
    log.debug('encrypting u/p...')
    pub_key = RSA.import_key(b64decode(json.loads(r.post('https://pass.hust.edu.cn/cas/rsa').text)['publicKey'].strip()))
    cipher = PKCS1_v1_5.new(pub_key)
    encrypted_u = b64encode(cipher.encrypt(username.encode())).decode()
    encrypted_p = b64encode(cipher.encrypt(password.encode())).decode()
    # 定位form
    form = re.search('<form id="loginForm" (.*)</form>', login_html.text, re.S).group(0)# 忽略换行符
    # 抓取ticket
    nonce = re.search('<input type="hidden" id="lt" name="lt" value="(.*)" />', form).group(1)
    # 抓取execution
    execution = re.search('<input type="hidden" name="execution" value="(.*)" />', form).group(1)
    post_params = {
        "rsa": None,
        "ul": encrypted_u,
        "pl": encrypted_p,
        "code": None if not captcha_check else decaptcha(captcha_img.content).strip(),
        "phoneCode": None,
        "lt": nonce,
        "execution": execution,
        "_eventId": "submit"
    }
    log.debug('posting login-form...')
    resp = r.post(
        "https://pass.hust.edu.cn/cas/login", 
        data=post_params,
        headers=headers,
        allow_redirects=False
    )
    try:
        resp.headers['Location']
    except:
        raise Exception("---HustPass Failed---")
    log.info("---HustPass Succeed---")
    return r
