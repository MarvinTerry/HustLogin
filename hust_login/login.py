import json
import re
from base64 import b64decode, b64encode
from html import unescape
from logging import root as log

import requests
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from .decaptcha import decaptcha


LOGIN_URL = 'https://pass.hust.edu.cn/cas/login'
RSA_URL = 'https://pass.hust.edu.cn/cas/rsa'
CAPTCHA_URL = 'https://pass.hust.edu.cn/cas/code'
MAX_LOGIN_ATTEMPTS = 3


def _extract_hidden_value(html: str, name: str) -> str:
    match = re.search(
        rf'<input[^>]*name="{re.escape(name)}"[^>]*value="([^"]*)"',
        html
    )
    if match is None:
        raise ValueError('HUSTPASS: LOGIN FORM CHANGED, MISSING {}'.format(name))
    return match.group(1)


def _captcha_required(html: str) -> bool:
    return 'id="codeImage"' in html or 'id="code"' in html


def _load_public_key(session: requests.Session) -> RSA.RsaKey:
    public_key = json.loads(session.post(RSA_URL).text)['publicKey']
    try:
        return RSA.import_key(b64decode(public_key))
    except (ValueError, TypeError):
        return RSA.import_key(public_key)


def _extract_error_message(html: str) -> str:
    match = re.search(r'<span id="errormsghide">(.*?)</span>', html, re.S)
    if match is None:
        return ''
    return unescape(re.sub(r'<[^>]+>', '', match.group(1))).strip()


def HustLogin(username:str, password:str, headers:dict=None) -> requests.Session:# 以便ide进行类型检查与代码补全
    '''
    PARAMETERS:\n
    username -- Username of pass.hust.edu.cn  e.g. U2022XXXXX\n
    password -- Password of pass.hust.edu.cn\n
    headers  -- Headers you want to use, optional
    '''
    # 输入类型检查
    if not isinstance(username, str) or not isinstance(password, str):
        raise TypeError('HUSTPASS: CHECK YOUR UID AND PWD TYPE')
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62'}
    else:
        if not isinstance(headers, dict):
            raise TypeError('HUSTPASS: CHECK YOUR HEADERS TYPE')
    # 输入有效检查
    if len(username)==0 or len(password)==0:
        raise ValueError('HUSTPASS: YOUR UID OR PWD IS EMPTY')
    try:
        headers['User-Agent']
    except:
        raise ValueError('HUSTPASS: YOUR HEADERS DO NOT INCLUDE UA')
    # 建立session
    log.info('setting up session...')
    r = requests.session()
    r.headers.update(headers)
    for attempt in range(1, MAX_LOGIN_ATTEMPTS + 1):
        login_html = r.get(LOGIN_URL)
        nonce = _extract_hidden_value(login_html.text, 'lt')
        execution = _extract_hidden_value(login_html.text, 'execution')

        captcha_code = ''
        if _captcha_required(login_html.text):
            captcha_img = r.get(CAPTCHA_URL, stream=True)
            log.info('captcha detected, trying to decaptcha...')
            captcha_code = decaptcha(captcha_img.content).strip()

        log.debug('encrypting u/p...')
        cipher = PKCS1_v1_5.new(_load_public_key(r))
        encrypted_u = b64encode(cipher.encrypt(username.encode())).decode()
        encrypted_p = b64encode(cipher.encrypt(password.encode())).decode()

        post_params = {
            "ua": '',
            "visitorId": '',
            "rsa": '',
            "ul": encrypted_u,
            "pl": encrypted_p,
            "code": captcha_code,
            "phoneCode": '',
            "lt": nonce,
            "execution": execution,
            "_eventId": "submit"
        }
        log.debug('posting login-form...')
        resp = r.post(LOGIN_URL, data=post_params, allow_redirects=False)
        if 'Location' in resp.headers:
            log.info("---HustPass Succeed---")
            log.debug('Thank you for using hust_login')
            return r

        error_message = _extract_error_message(resp.text)
        if '验证码' in error_message and attempt < MAX_LOGIN_ATTEMPTS:
            log.warning('captcha rejected, retrying login...')
            continue
        raise ConnectionRefusedError(
            error_message if error_message else '---HustPass Failed---'
        )

    raise ConnectionRefusedError('---HustPass Failed---')

def CheckLoginStatu(session:requests.Session) -> bool:
    '''
    Check login statu\n
    Return False if is not logged in
    '''
    ret = session.get('https://one.hust.edu.cn')
    if ret.status_code != 200:
        log.warning('HUSTPASS: check login failed, code:{}'.format(ret.status_code))
        return False
    return True
