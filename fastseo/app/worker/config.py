from dotenv import load_dotenv
import os

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    DATAFORSEO_LOGIN = os.environ.get('DATAFORSEO_LOGIN') or '123analyticsacc@gmail.com'
    DATAFORSEO_PASSWORD = os.environ.get('DATAFORSEO_LOGIN') or 'XdlFY3OvrsLzVuSI'