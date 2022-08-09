# __author__ = "seanwlk"
# __copyright__ = "Copyright 2020"
# __license__ = "GPL"
# __description__ = "Wrapper library for managing warface account session"

import requests
import json
import steam.webauth as wa
import steam.steamid as sid
try:
  import steam.util.web as sweb
except ModuleNotFoundError: # Version 1.0 has steam.utils
  import steam.utils.web as sweb
from collections import OrderedDict
from io import StringIO
import lxml.html

class UnsupportedLogin(Exception):
  pass

class MissingSteamLoginData(Exception):
  pass

class WFAccountManager:
  def __init__(self,region,lang="en"):
    """
    - region: russia,west,steam
    - lang: en,fr,cn,es,de,ru
    """
    # Properties
    self.session = requests.Session()
    self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
    self.lang = lang
    self.region = region.lower()
    self.me = {'state': 'guest', 'user_id': None, 'email': '', 'username': '', 'territory': ''}
    self._baseUrl = ""
    # Child Classes
    self.crafting = _CraftingManager(self)
    self.inventory = _InventoryManager(self)
    self.marketplace = _MarketplaceManager(self)
    self.chests = _ChestManager(self)
  def login(self,account=None,password=None,**kwargs):
    def _west(account,password):
      """
      Warface West Login
      Strightforward login. Once called, tries to login with the credentials given.
      Returns: content from /minigames/user/info
      """
      payload = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded',
        'DNT': '1',
        'Cookie': 'amc_lang=en_US;',
        'Host': 'auth-ac.my.games',
        'Origin': 'https://account.my.games',
        'Referer': 'https://account.my.games/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': self.user_agent
      }
      login_data = {
        'login':account,
        'password':password,
        'continue':'https://account.my.games/oauth2/?redirect_uri=https%3A%2F%2Fpc.warface.com%2Fdynamic%2Fauth%2F%3Fo2%3D1&client_id=wf.my.com&response_type=code&signup_method=email%2Cphone&signup_social=mailru%2Cfb%2Cvk%2Cg%2Ctwitch%2Ceg%2Ctw%2Csteam&lang=en_US&gc_id=13.2000076&lang=en_US',
        'failure':'https://account.my.games/oauth2/login/?continue=https%3A%2F%2Faccount.my.games%2Foauth2%2Flogin%2F%3Fcontinue%3Dhttps%253A%252F%252Faccount.my.games%252Foauth2%252F%253Fredirect_uri%253Dhttps%25253A%25252F%25252Fpc.warface.com%25252Fdynamic%25252Fauth%25252F%25253Fo2%25253D1%2526client_id%253Dwf.my.com%2526response_type%253Dcode%2526signup_method%253Demail%25252Cphone%2526signup_social%253Dmailru%25252Cfb%25252Cvk%25252Cg%25252Ctwitch%25252Ceg%25252Ctw%25252Csteam%2526lang%253Den_US%2526gc_id%253D13.2000076%2526lang%253Den_US%26client_id%3Dwf.my.com%26lang%3Den_US%26signup_method%3Demail%252Cphone%26signup_social%3Dmailru%252Cfb%252Cvk%252Cg%252Ctwitch%252Ceg%252Ctw%252Csteam%26gc_id%3D13.2000076&client_id=wf.my.com&lang=en_US&signup_method=email%2Cphone&signup_social=mailru%2Cfb%2Cvk%2Cg%2Ctwitch%2Ceg%2Ctw%2Csteam&gc_id=13.2000076',
        'nosavelogin':'0',
        'g-recaptcha-response': None
      }
      r = self.session.post('https://auth-ac.my.games/sign_in',headers=payload, data=login_data, allow_redirects=False)
      while "location" in r.headers:
        r = self.session.get(r.headers['location'], allow_redirects=False)
      g = r.text
      try:
        _csrfMiddlewareToken = g.split("name=\"csrfmiddlewaretoken\" value=\"")[1].split('"')[0]
        data = {
          'csrfmiddlewaretoken': _csrfMiddlewareToken,
          'response_type': 'code',
          'client_id': 'wf.my.com',
          'redirect_uri': 'https://pc.warface.com/dynamic/auth/?o2=1',
          'scope': '',
          'state': '',
          'hash': 'b4f287b95aa4dbc907ab2880c60012b3',
          'gc_id': None,
          'force': '1'
        }
        payload = {
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
          'Sec-Fetch-Site': 'same-origin',
          'Sec-Fetch-Mode': 'navigate',
          'Sec-Fetch-User': '?1',
          'Sec-Fetch-Dest': 'document',
          'Origin': 'https://account.my.games',
          'Referer': 'https://account.my.games/oauth2/?redirect_uri=https%3A%2F%2Fpc.warface.com%2Fdynamic%2Fauth%2F%3Fo2%3D1&client_id=wf.my.com&response_type=code&signup_method=email%2Cphone&signup_social=mailru%2Cfb%2Cvk%2Cg%2Ctwitch%2Ceg%2Ctw%2Csteam&lang=en_US&gc_id=13.2000076&lang=en_US',
          'Accept-Language': 'en-US,en;q=0.9,it-IT;q=0.8,it;q=0.7',
          'Upgrade-Insecure-Requests': '1',
          'Content-Type': 'application/x-www-form-urlencoded',
          'User-Agent': self.user_agent
        }
        r = self.session.post("https://account.my.games/oauth2/",headers=payload,data=data)
        userInfo = self.session.get('https://pc.warface.com/minigames/user/info').json() # has to be json implicitly. IT will loop if site is down
        self.session.cookies['mg_token'] = userInfo['data']['token']
        self.session.cookies['cur_language'] = self.lang
      except ValueError:
        pass
      userInfo = self.session.get('https://pc.warface.com/minigames/user/info').json()
      self.session.cookies['mg_token'] = userInfo['data']['token']
      self.session.cookies['cur_language'] = self.lang
      self.me = {k: v for k, v in userInfo['data'].items() if k != 'token' and k != 'project'}
      self._baseUrl = "pc.warface.com"
      return userInfo
    def _russia(account,password):
      """
      Warface Ru login
      Has to handle mail ru mailboxes endpoints and the other ones separatly
      """
      domains = ["mail.ru","inbox.ru","list.ru","bk.ru"]
      if account.split("@")[1] in domains:
        g = self.session.post('https://auth-ac.my.games/social/mailru',allow_redirects=True).text
        mailru_state = g.split("%2F&state=")[1].split("'")[0] # This sucks
        payload = {
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
          'Accept-Encoding': 'gzip, deflate, br',
          'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
          'Cache-Control': 'max-age=0',
          'Connection': 'keep-alive',
          'Content-Type': 'application/x-www-form-urlencoded',
          'DNT': '1',
          'Host': 'auth.mail.ru',
          'Origin': 'https://account.mail.ru',
          'Referer': f'https://o2.mail.ru/xlogin?authid=kc6q10mp.x56&client_id=bbddb88d19b84a62aedd1ffbc71af201&force_us=1&from=o2&logo_target=_none&no_biz=1&redirect_uri=https%3A%2F%2Fauth-ac.my.games%2Fsocial%2Fmailru_callback%2F&remind_target=_self&response_type=code&scope=&signup_target=_self&state={mailru_state}',
          'Sec-Fetch-Dest': 'document',
          'Sec-Fetch-Mode': 'navigate',
          'Sec-Fetch-Site': 'same-site',
          'Sec-Fetch-User': '?1',
          'Upgrade-Insecure-Requests': '1',
          'User-Agent': self.user_agent
        }
        act_token = self.session.get("https://account.mail.ru").cookies['act']
        data = {
          'username': account,
          'Login': account,
          'password': password,
          'Password': password,
          'new_auth_form': '1',
          'FromAccount': 'opener=o2&x=login&twoSteps=1&remind_target=_self',
          'act_token': act_token,
          'page': 'https://o2.mail.ru/xlogin?authid=kc6q10mp.x56&client_id=bbddb88d19b84a62aedd1ffbc71af201&force_us=1&from=o2&logo_target=_none&no_biz=1&redirect_uri=https%3A%2F%2Fauth-ac.my.games%2Fsocial%2Fmailru_callback%2F&remind_target=_self&response_type=code&scope=&signup_target=_self',
          'lang': 'en_US'
        }
        r = self.session.post("https://auth.mail.ru/cgi-bin/auth",headers=payload,data=data)
        data = {
          'Page': f'https://o2.mail.ru/login?client_id=bbddb88d19b84a62aedd1ffbc71af201&response_type=code&scope=&redirect_uri=https%3A%2F%2Fauth-ac.my.games%2Fsocial%2Fmailru_callback%2F&state={mailru_state}&no_biz=1',
          'FailPage': f'https://o2.mail.ru/login?client_id=bbddb88d19b84a62aedd1ffbc71af201&response_type=code&scope=&redirect_uri=https%3A%2F%2Fauth-ac.my.games%2Fsocial%2Fmailru_callback%2F&state={mailru_state}&no_biz=1&fail=1',
          'login': account,
          'o2csrf': self.session.cookies['o2csrf'],
          'mode': ''
        }
        payload = {
          'authority': 'o2.mail.ru',
          'method': 'POST',
          'path': '/login',
          'scheme': 'https',
          'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
          'accept-encoding': 'gzip, deflate, br',
          'accept-language': 'en-US,en;q=0.9,it;q=0.8',
          'cache-control': 'max-age=0',
          'content-type': 'application/x-www-form-urlencoded',
          'dnt': '1',
          'origin': 'https://o2.mail.ru',
          'referer': f'https://o2.mail.ru/xlogin?client_id=bbddb88d19b84a62aedd1ffbc71af201&response_type=code&scope=&redirect_uri=https%3A%2F%2Fauth-ac.my.games%2Fsocial%2Fmailru_callback%2F&state={mailru_state}&no_biz=1',
          'sec-fetch-dest': 'document',
          'sec-fetch-mode': 'navigate',
          'sec-fetch-site': 'same-origin',
          'upgrade-insecure-requests': '1',
          'user-agent': self.user_agent
        }
        r = self.session.post('https://o2.mail.ru/login',headers=payload,data=data)
        self.session.get("https://account.my.games/social_back/?continue=https%3A%2F%2Faccount.my.games%2Foauth2%2F%3Fredirect_uri%3Dhttps%253A%252F%252Fru.warface.com%252Fdynamic%252Fauth%252F%253Fo2%253D1%26client_id%3Dru.warface.com%26response_type%3Dcode%26signup_method%3Demail%252Cphone%26signup_social%3Dmailru%252Cfb%252Cvk%252Cg%252Cok%252Ctwitch%252Ctw%26lang%3Dru_RU%26gc_id%3D0.1177&client_id=ru.warface.com&popup=1",headers=payload)
        g = self.session.get("https://account.my.games/profile/userinfo/",allow_redirects=False).text
        _csrfMiddlewareToken = g.split("name=\"csrfmiddlewaretoken\" value=\"")[1].split('"')[0]
        data = {
          'csrfmiddlewaretoken': _csrfMiddlewareToken,
          'response_type': 'code',
          'client_id': 'ru.warface.com',
          'redirect_uri': 'https://ru.warface.com/dynamic/auth/?o2=1',
          'scope': '',
          'state': '',
          'hash': 'be7ced8c2ae834813f503822e744fade',
          'gc_id': '0.1177',
          'force': '1'
        }
        payload = {
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
          'Sec-Fetch-Site': 'same-origin',
          'Sec-Fetch-Mode': 'navigate',
          'Sec-Fetch-User': '?1',
          'Sec-Fetch-Dest': 'document',
          'Origin': 'https://account.my.games',
          'Referer': 'https://account.my.games/oauth2/?redirect_uri=https%3A%2F%2Fru.warface.com%2Fdynamic%2Fauth%2F%3Fo2%3D1&client_id=ru.warface.com&response_type=code&signup_method=email%2Cphone&signup_social=mailru%2Cfb%2Cvk%2Cg%2Cok%2Ctwitch%2Ctw&lang=ru_RU&gc_id=0.1177',
          'Accept-Language': 'en-US,en;q=0.9,it-IT;q=0.8,it;q=0.7',
          'Upgrade-Insecure-Requests': '1',
          'Content-Type': 'application/x-www-form-urlencoded',
          'User-Agent': self.user_agent
        }
        r = self.session.post("https://account.my.games/oauth2/",headers=payload,data=data)
        userInfo = self.session.get('https://ru.warface.com/minigames/user/info').json()
        self.session.cookies['mg_token'] = userInfo['data']['token']
        self.session.cookies['cur_language'] = self.lang
        self.me = {k: v for k, v in userInfo['data'].items() if k != 'token' and k != 'project'}
        self._baseUrl = "ru.warface.com"
        return userInfo
      else:
        # My.Games account on ru site
        payload = {
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
          'Accept-Encoding': 'gzip, deflate, br',
          'Accept-Language': 'en-US,en;q=0.9,it-IT;q=0.8,it;q=0.7',
          'Connection': 'keep-alive',
          'Content-Type': 'application/x-www-form-urlencoded',
          'Cookie':'amc_lang=en_US; ',
          'DNT': '1',
          'Host': 'auth-ac.my.games',
          'Origin': 'https://account.my.games',
          'Sec-Fetch-Dest': 'script',
          'Sec-Fetch-Mode': 'no-cors',
          'Sec-Fetch-Site': 'same-site',
          'Referer': 'https://account.my.games/oauth2/login/?continue=https%3A%2F%2Faccount.my.games%2Foauth2%2F%3Fredirect_uri%3Dhttps%253A%252F%252Fru.warface.com%252Fdynamic%252Fauth%252F%253Fo2%253D1%26client_id%3Dru.warface.com%26response_type%3Dcode%26signup_method%3Demail%252Cphone%26signup_social%3Dmailru%252Cfb%252Cvk%252Cg%252Cok%252Ctwitch%252Ctw%26lang%3Dru_RU%26gc_id%3D0.1177&client_id=ru.warface.com&lang=ru_RU&signup_method=email%2Cphone&signup_social=mailru%2Cfb%2Cvk%2Cg%2Cok%2Ctwitch%2Ctw&gc_id=0.1177',
          'User-Agent': self.user_agent
        }
        login_data = {
          'login':account,
          'password':password,
          'continue':'https://account.my.games/oauth2/?redirect_uri=https%3A%2F%2Fru.warface.com%2Fdynamic%2Fauth%2F%3Fo2%3D1&client_id=ru.warface.com&response_type=code&signup_method=email%2Cphone&signup_social=mailru%2Cfb%2Cvk%2Cg%2Cok%2Ctwitch%2Ctw&lang=ru_RU&gc_id=0.1177',
          'failure':'https://account.my.games/oauth2/login/?continue=https%3A%2F%2Faccount.my.games%2Foauth2%2Flogin%2F%3Fcontinue%3Dhttps%253A%252F%252Faccount.my.games%252Foauth2%252F%253Fredirect_uri%253Dhttps%25253A%25252F%25252Fru.warface.com%25252Fdynamic%25252Fauth%25252F%25253Fo2%25253D1%2526client_id%253Dru.warface.com%2526response_type%253Dcode%2526signup_method%253Demail%25252Cphone%2526signup_social%253Dmailru%25252Cfb%25252Cvk%25252Cg%25252Cok%25252Ctwitch%25252Ctw%2526lang%253Dru_RU%2526gc_id%253D0.1177%26client_id%3Dru.warface.com%26lang%3Dru_RU%26signup_method%3Demail%252Cphone%26signup_social%3Dmailru%252Cfb%252Cvk%252Cg%252Cok%252Ctwitch%252Ctw%26gc_id%3D0.1177&client_id=ru.warface.com&lang=ru_RU&signup_method=email%2Cphone&signup_social=mailru%2Cfb%2Cvk%2Cg%2Cok%2Ctwitch%2Ctw&gc_id=0.1177',
          'nosavelogin':'0',
          'g-recaptcha-response': None
        }
        try:
          r = self.session.post('https://auth-ac.my.games/sign_in',headers=payload,data=login_data, allow_redirects=False)
          while "location" in r.headers:
            r = self.session.get(r.headers['location'], allow_redirects=False)
          g = self.session.get("https://account.my.games/profile/userinfo/",allow_redirects=False).text
          _csrfMiddlewareToken = g.split("name=\"csrfmiddlewaretoken\" value=\"")[1].split('"')[0]
          data = {
            'csrfmiddlewaretoken': _csrfMiddlewareToken,
            'response_type': 'code',
            'client_id': 'ru.warface.com',
            'redirect_uri': 'https://ru.warface.com/dynamic/auth/?o2=1',
            'scope': '',
            'state': '',
            'hash': 'be7ced8c2ae834813f503822e744fade',
            'gc_id': '0.1177',
            'force': '1'
          }
          payload = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Origin': 'https://account.my.games',
            'Referer': 'https://account.my.games/oauth2/?redirect_uri=https%3A%2F%2Fru.warface.com%2Fdynamic%2Fauth%2F%3Fo2%3D1&client_id=ru.warface.com&response_type=code&signup_method=email%2Cphone&signup_social=mailru%2Cfb%2Cvk%2Cg%2Cok%2Ctwitch%2Ctw&lang=ru_RU&gc_id=0.1177',
            'Accept-Language': 'en-US,en;q=0.9,it-IT;q=0.8,it;q=0.7',
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': self.user_agent
          }
          r = self.session.post("https://account.my.games/oauth2/",headers=payload,data=data)
          userInfo = self.session.get('https://ru.warface.com/minigames/user/info').json() # has to be json implicitly. IT will loop if site is down
          self.session.cookies['mg_token'] = userInfo['data']['token']
          self.session.cookies['cur_language'] = self.lang
        except ValueError:
          pass
        self.me = {k: v for k, v in userInfo['data'].items() if k != 'token' and k != 'project'}
        self._baseUrl = "ru.warface.com"
        return userInfo

    if self.region == "west":
      return _west(account,password)
    elif self.region == "steam":
      self._baseUrl = "pc.warface.com"
      return self._steamAuth(account=account,password=password,**kwargs)
    elif self.region == "russia":
      return _russia(account,password)
    else:
      raise UnsupportedLogin

  def _steamSiteLogin(self):
    """
    Final internal function for steam auth that returns the user data
    """
    while True:
      try:
        entrance=self.session.get('https://auth-ac.my.games/social/steam?display=popup&continue=https%3A%2F%2Faccount.my.games%2Fsocial_back%2F%3Fcontinue%3Dhttps%253A%252F%252Faccount.my.games%252Foauth2%252F%253Fredirect_uri%253Dhttps%25253A%25252F%25252Fpc.warface.com%25252Fdynamic%25252Fauth%25252F%25253Fo2%25253D1%2526client_id%253Dwf.my.com%2526response_type%253Dcode%2526signup_method%253Demail%252Cphone%2526signup_social%253Dmailru%25252Cfb%25252Cvk%25252Cg%25252Cok%25252Ctwitch%25252Ctw%25252Cps%25252Cxbox%25252Csteam%2526lang%253Den_US%26client_id%3Dwf.my.com%26popup%3D1&failure=https%3A%2F%2Faccount.my.games%2Fsocial_back%2F%3Fsoc_error%3D1%26continue%3Dhttps%253A%252F%252Faccount.my.games%252Foauth2%252Flogin%252F%253Fcontinue%253Dhttps%25253A%25252F%25252Faccount.my.games%25252Foauth2%25252Flogin%25252F%25253Fcontinue%25253Dhttps%2525253A%2525252F%2525252Faccount.my.games%2525252Foauth2%2525252F%2525253Fredirect_uri%2525253Dhttps%252525253A%252525252F%252525252Fpc.warface.com%252525252Fdynamic%252525252Fauth%252525252F%252525253Fo2%252525253D1%25252526client_id%2525253Dwf.my.com%25252526response_type%2525253Dcode%25252526signup_method%2525253Demail%2525252Cphone%25252526signup_social%2525253Dmailru%252525252Cfb%252525252Cvk%252525252Cg%252525252Cok%252525252Ctwitch%252525252Ctw%252525252Cps%252525252Cxbox%252525252Csteam%25252526lang%2525253Den_US%252526client_id%25253Dwf.my.com%252526lang%25253Den_US%252526signup_method%25253Demail%2525252Cphone%252526signup_social%25253Dmailru%2525252Cfb%2525252Cvk%2525252Cg%2525252Cok%2525252Ctwitch%2525252Ctw%2525252Cps%2525252Cxbox%2525252Csteam%2526amp%253Bclient_id%253Dwf.my.com%2526amp%253Blang%253Den_US%2526amp%253Bsignup_method%253Demail%25252Cphone%2526amp%253Bsignup_social%253Dmailru%25252Cfb%25252Cvk%25252Cg%25252Cok%25252Ctwitch%25252Ctw%25252Cps%25252Cxbox%25252Csteam')
        openid_login={}
        html = StringIO(entrance.content.decode())
        tree = lxml.html.parse(html)
        root = tree.getroot()
        for form in root.xpath('//form[@name="loginForm"]'):
          for field in form.getchildren():
            if 'name' in field.keys():
              openid_login[field.get('name')]=field.get('value')
        self.session.headers.update({'referer': entrance.url})
        steam_redir=self.session.post('https://steamcommunity.com/openid/login', data=openid_login)
        self.session.get('https://auth-ac.my.games/sdc?from=https%3A%2F%2Faccount.my.games%2Foauth2%2F%3Fredirect_uri%3Dhttps%253A%252F%252Fpc.warface.com%252Fdynamic%252Fauth%252F%253Fo2%253D1%26client_id%3Dwf.my.com%26response_type%3Dcode%26signup_method%3Demail%2Cphone%26signup_social%3Dmailru%252Cfb%252Cvk%252Cg%252Cok%252Ctwitch%252Ctw%252Cps%252Cxbox%252Csteam%26lang%3Den_US%26signup%3D1')
        g = self.session.get("https://account.my.games/profile/userinfo/",allow_redirects=False).text
        _csrfMiddlewareToken = g.split("name=\"csrfmiddlewaretoken\" value=\"")[1].split('"')[0]
        data = {
          'csrfmiddlewaretoken': _csrfMiddlewareToken,
          'response_type': 'code',
          'client_id': 'wf.my.com',
          'redirect_uri': 'https://pc.warface.com/dynamic/auth/?o2=1',
          'scope': '',
          'state': '',
          'hash': 'b4f287b95aa4dbc907ab2880c60012b3',
          'gc_id': None,
          'force': '1'
        }
        payload = {
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
          'Sec-Fetch-Site': 'same-origin',
          'Sec-Fetch-Mode': 'navigate',
          'Sec-Fetch-User': '?1',
          'Sec-Fetch-Dest': 'document',
          'Origin': 'https://account.my.games',
          'Referer': 'https://account.my.games/oauth2/?redirect_uri=https%3A%2F%2Fru.warface.com%2Fdynamic%2Fauth%2F%3Fo2%3D1&client_id=ru.warface.com&response_type=code&signup_method=email%2Cphone&signup_social=mailru%2Cfb%2Cvk%2Cg%2Cok%2Ctwitch%2Ctw&lang=ru_RU&gc_id=0.1177',
          'Accept-Language': 'en-US,en;q=0.9,it-IT;q=0.8,it;q=0.7',
          'Upgrade-Insecure-Requests': '1',
          'Content-Type': 'application/x-www-form-urlencoded',
          'User-Agent': self.user_agent
        }
        r = self.session.post("https://account.my.games/oauth2/",headers=payload,data=data)
        userInfo = self.session.get('https://pc.warface.com/minigames/user/info').json()
        self.session.cookies['mg_token'] = userInfo['data']['token']
        self.session.cookies['cur_language'] = self.lang
      except:
        continue
      break
    if hasattr(self ,"steamUser"): # return generated oauth2 keys to user
      steamData = {
        'steamID' : self.steamUser.steam_id.as_64,
        'auth_token' : self.steamUser.oauth_token,
        'steamguard_token' : self.steamUser.session.cookies.get_dict()[f"steamMachineAuth{self.steamUser.steam_id.as_64}"]
      }
      userInfo['steam'] = steamData
    self.me = {k: v for k, v in userInfo['data'].items() if k != 'token' and k != 'project'}
    return userInfo
  def _steamAuth(self,account=None,password=None,steamID=None,auth_token=None,steamguard_token=None):
    """
    Aliased internal function for steam auth. If used with plain username and password
    returns dict with a status request for 2FA when required. Use <>.postSteam2FA() after
    Possible statuses:
    0 - No 2FA required - Plain login, you can now use session
    1 - Captcha required - Post the captcha code
    2 - Email code required - Post the code received on the email
    3 - Steamguard 2FA required - Post the 2FA code from steamguard
    """
    if account and password:
      if not 'sessionid' in self.session.cookies.get_dict():
        self.steamUser = wa.MobileWebAuth(account, password)
        try:
          self.steamUser.login()
          self.session.cookies.update(self.steamUser.session.cookies)
          self._steamSiteLogin()
          return {"status" : 0, "message" : "No 2FA required. Check user session"}
        except wa.CaptchaRequired:
          self.twofaType = "captcha"
          return {"status" : 1, "message" : "Captcha Required", "url" : self.steamUser.captcha_url} # User must .postSteam2FA(code)
        except wa.EmailCodeRequired:
          self.twofaType = "email"
          return {"status" : 2, "message" : "Email code Required"} # User must .postSteam2FA(code)
        except wa.TwoFactorCodeRequired:
          self.twofaType = "steamguard"
          return {"status" : 3, "message" : "Steamguard 2FA Required"} # User must .postSteam2FA(code)
    elif steamID and auth_token and steamguard_token:
      steamid = sid.SteamID(steamID)
      try:
        response = self.session.post('https://api.steampowered.com/IMobileAuthService/GetWGToken/v1/', data={'access_token': auth_token}).json()['response']
      except:
        return self._steamSiteLogin()
      if not 'token' in response or not 'token_secure' in response:
        return False
      cookies = {
        'steamLogin': f"{steamid}||{response['token']}",
        'steamLoginSecure': f"{steamid}||{response['token_secure']}",
        f'steamMachineAuth{steamid}': steamguard_token,
        'sessionid': sweb.generate_session_id()
      }
      jar = requests.cookies.RequestsCookieJar()
      for cookie in cookies:
        jar.set(cookie, cookies[cookie], domain='steamcommunity.com', path='/')
      self.session.cookies.update(jar)
      return self._steamSiteLogin()
    else:
      raise MissingSteamLoginData

  def postSteam2FA(self,code):
    """
    Function for steam users that have 2FA on.
    You have to use this after you do <>.login() and post the code
    """
    if self.twofaType == "captcha":
      self.steamUser.login(captcha=code)
    elif self.twofaType == "email":
      self.steamUser.login(email_code=code)
    elif self.twofaType == "steamguard":
      self.steamUser.login(twofactor_code=code)
    self.session.cookies.update(self.steamUser.session.cookies)
    return self._steamSiteLogin()

  def _refreshMGToken(self):
    """
    Internal method that resets the MG token from /minigames/user/info to cookies
    """
    userInfo = self.session.get(f'https://{self._baseUrl}/minigames/user/info').json()
    self.session.cookies['mg_token'] = userInfo['data']['token']
  def get(self,url,headers=None,data=None,isJson=True):
    """
    Method that allows custom links to bet HTTP GET with user session
    It's possible to add headers , data and get html page instead of json by default
    In the url given, the string $baseurl$ will be replaced with the current instance _baseUrl
    """
    if isJson:
      return self.session.get(url.replace("$baseurl$",self._baseUrl),headers=headers,data=data).json()
    return self.session.get(url.replace("$baseurl$",self._baseUrl),headers=headers,data=data).text
  def post(self,url, headers=None, data=None, isJson: bool = True):
    """
    Method that allows custom links to bet HTTP POST with user session
    It's possible to add headers , data and get html page instead of json by default
    In the url given, the string $baseurl$ will be replaced with the current instance _baseUrl
    """
    if isJson:
      return self.session.post(url.replace("$baseurl$",self._baseUrl),headers=headers,data=data).json()
    return self.session.post(url.replace("$baseurl$",self._baseUrl),headers=headers,data=data).text
  def user(self):
    """
    Get live data from /minigames/user/info instead of cached .me property
    """
    return self.session.get(f'https://{self._baseUrl}/minigames/user/info').json()

class _CraftingManager:
  def __init__(self, accountManager):
    self.accountManager = accountManager
  def crates(self):
    """
    Method that returns list of user crafting chests
    """
    return self.accountManager.get(f'https://{self.accountManager._baseUrl}/minigames/craft/api/user-info')['data']['user_chests']
  def startCrate(self, chest_id):
    """
    Method that starts the crafting crate opening
    """
    return self.accountManager.post(f'https://{self.accountManager._baseUrl}/minigames/craft/api/start',data={'chest_id':int(chest_id)})
  def openCrate(self, chest_id):
    """
    Method that collects items from an opened crate
    """
    return self.accountManager.post(f'https://{self.accountManager._baseUrl}/minigames/craft/api/open',data={'chest_id':int(chest_id),'paid':0})
  def resources(self):
    """
    Method that returns list of user crafting resources
    """
    return self.accountManager.get(f'https://{self.accountManager._baseUrl}/minigames/craft/api/user-info')['data']['user_resources']
  def slotCount(self):
    """
    Method that returns the amount of crafting slots the user has
    """
    return self.accountManager.get(f'https://{self.accountManager._baseUrl}/minigames/craft/api/user-info')['data']['user_slots_count']

class _InventoryManager:
  def __init__(self, accountManager):
    self.accountManager = accountManager
  def list(self):
    """
    Method that returns list of user inventory items from battlepass services
    """
    return self.accountManager.get(f'https://{self.accountManager._baseUrl}/minigames/inventory/api/list')['data']['inventory']
  def chars(self):
    """
    Method that returns list of user in-game characters to which you can transfer items
    Useful for <>.inventory.transfer() method
    """
    return self.accountManager.get(f'https://{self.accountManager._baseUrl}/minigames/inventory/api/list')['data']['chars']
  def transfer(self, server, item_id, amount=1, notification=False):
    """
    Method that allows the user to transfer items from the battlepass invetory to the game
    Takes as arguments the server shardID and item ID available from <>.inventory.list()
    By default the amount is set to 1 and item will be transferred without in-game notification
    """
    data = {
      'shardId': server,
      'count': amount,
      'itemId': item_id,
      'is_notice' : 1 if notification else 0
    }
    return self.accountManager.post(f'https://{self.accountManager._baseUrl}/minigames/inventory/api/pass-to-game',data=data)
  def lootDogToken(self):
    """
    Method that returns lootdog token
    Probably for future use. Currenlty is blank.
    """
    return self.accountManager.get(f'https://{self.accountManager._baseUrl}/minigames/inventory/api/list')['data']['lootdog_token']

class _MarketplaceManager:
  def __init__(self, accountManager):
    self.accountManager = accountManager
  def list(self):
    """
    Method that returns the list of items in the marketplace
    """
    return self.accountManager.get(f'https://{self.accountManager._baseUrl}/minigames/marketplace/api/all')['data']
  def buy(self, entity_id, cost, type):
    """
    Method that allows to buy items from marketplace
    Arguments are available in <>.marketplace.list()
    """
    data = {
      'entity_id': entity_id,
      'cost': cost,
      'type' : type
    }
    return self.accountManager.post(f'https://{self.accountManager._baseUrl}/minigames/marketplace/api/buy',data=data)
  def sell(self,item_id,cost):
    """
    Method that allows to sell in the marketplace
    Arguments are available in <>.inventory.list()
    """
    data = {
      'item_id': item_id,
      'cost': cost
    }
    return self.accountManager.post(f'https://{self.accountManager._baseUrl}/minigames/inventory/api/sale',data=data)
  def myOffers(self):
    """
    Method that returns the list of items that the user is currently selling
    """
    return self.accountManager.get(f'https://{self.accountManager._baseUrl}/minigames/marketplace/api/user-items')['data']
  def history(self):
    """
    Method that returns the selling/buying history of the user
    """
    return self.accountManager.get(f'https://{self.accountManager._baseUrl}/minigames/marketplace/api/history')['data']


class _ChestManager:
  def __init__(self, accountManager):
    self.accountManager = accountManager
  def list(self):
    """
    Method that returns the list of chests available for the user
    """
    return self.accountManager.get(f'https://{self.accountManager._baseUrl}/minigames/chest_boxes/api/get-chests')['data']
  def keys(self):
    """
    Method that returns the dict of key chests owned by the user
    """
    keys = {}
    r = self.accountManager.get(f'https://{self.accountManager._baseUrl}/minigames/chest_boxes/api/get-chests')['data']
    for chest in r:
      if 'key' in r[chest]:
        keys[r[chest]['id']] = r[chest]['key']['count']
    return keys
  def open(self, chest_id):
    """
    Method that opens user chests given the chest_id and returns the content of it
    """
    return self.accountManager.post(f'https://{self.accountManager._baseUrl}/minigames/chest_boxes/api/open-chest',data={'id':chest_id})
