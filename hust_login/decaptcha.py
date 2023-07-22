from io import BytesIO
import pytesseract
from logging import root as log
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
        log.fatal('tesseract is not installed !!', exc_info=True)
        raise EnvironmentError('USE sudo apt install tesseract-ocr OR go to https://tesseract-ocr.github.io/tessdoc/Downloads.html')
    log.debug('captcha_code:{}'.format(captcha_code.strip()))
    # img_merge.save('./src/decaptcha/blended.png')
    return captcha_code
