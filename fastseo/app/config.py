from dotenv import load_dotenv
import os


class Config(object):
    DATAFORSEO_LOGIN = os.environ.get('DATAFORSEO_LOGIN') or '123analyticsacc@gmail.com'
    DATAFORSEO_PASSWORD = os.environ.get('DATAFORSEO_LOGIN') or 'XdlFY3OvrsLzVuSI'
    DOMAIN = os.environ.get("DOMAIN") or 'c04f7b28b681.ngrok.io'
