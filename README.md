# WFAccountManager

Simple class that allows the usage of Warface account with a session that takes care of the login and offers useful methods.

## Requirements
- `steam` library
- `lxml` library
- Python >= 3.6

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install wfaccountmanager.

```bash
pip install wfaccountmanager
pip install -U git+https://github.com/seanwlk/wfaccountmanager # Live updated library
```

## Usage

Upon object declaration you have to specify the region you will use tha account from. At the current time the only one supported are `west`,`steam`,`russia`.
Then you can login with the credentials. You can also specify `lang` parameter which by default is `en`.

```python
from wfaccountmanager import WFAccountManager

wf = WFAccountManager("west")
wf.login(account,password)
```
### Methods

- <>.login()

This method has different behaviour if you are using steam instead of west or russia.
```python
# For west and russia
wf.login(account,password) # Returns content from /minigames/user/info
# Example output:
{
"state": "Success",
"data": {
    "state": "auth",
    "user_id": 9999999,
    "email": "foo@bar.com",
    "username": "foobar",
    "token": "ioeqwinj5409i23490jkljfdslj2",
    "project": "wf",
    "territory": "pc"
    }
}
```
Steam `login()` method will return a status code requiring you to put a 2FA code. Here's how to:
```python
myLogin = wf.login("foobar","bestSniperEU") # Steam account
# {"status" : 0, "message" : "No 2FA required. Check user session"} this will happen to users with no security setup
# {"status" : 1, "message" : "Captcha Required", "url" : "capthca URL to resolve"}
# {"status" : 2, "message" : "Email code Required"}
# {"status" : 3, "message" : "Steamguard 2FA Required"}

wf.postSteam2FA("ASB1G") # Setting the 2FA gotten on the app, via mail or captcha
# returns /minigames/user/info
```

When using steam with the `login()` method the returned data will contain a `steam` key with inside the `steamID` the `auth_token` and `steamguard_token` which will allow you to login in a future session without user and password but by passing those parameters only.
Note that if the Oauth2 keys are expired, the method will implicitly return an empty session.
```python
wf.login(steamID="Your Steam OPENID",auth_token=token,steamguard_token=steamguard)
```
- <>.user()

Returns the live data from /minigames/user/info useful to check if session expired for some reason.
```python
wf.user() # Returns content from /minigames/user/info
# Example output:
{
"state": "Success",
"data": {
    "state": "auth",
    "user_id": 9999999,
    "email": "foo@bar.com",
    "username": "foobar",
    "token": "ioeqwinj5409i23490jkljfdslj2",
    "project": "wf",
    "territory": "pc"
    }
}
```
- <>.get(url,headers=None,data=None,isJson=True)

With this you can HTTP GET custom URLs using the Warface session. You can pass headers and data which by default are not set.
Furthermore you can return the output as plain text if you set `isJson=False` which is true by default.
This method also includes a hidden shortcut that allows you to pass an URL string contraining `$baseurl$` and it will replace it with the actual instance baseUrl
```python
wf.get("https://pc.warface.com/minigames/battlepass/task/all")
wf.get("https://$baseurl$/minigames/battlepass/task/all")
wf.get("https://pc.warface.com/en/profile/", isJson=False)
```
- <>.post(url,headers=None,data=None,isJson=True)

With this you can HTTP POST custom URLs using the Warface session. You can pass headers and data which by default are not set.
Furthermore you can return the output as plain text if you set `isJson=False` which is true by default.
This method also includes a hidden shortcut that allows you to pass an URL string contraining `$baseurl$` and it will replace it with the actual instance baseUrl
```python
wf.post("https://pc.warface.com/minigames/battlepass/box/open")
wf.post("https://$baseurl$/minigames/battlepass/box/open")
```

## Managers
With version 0.0.3 the service manager sub classes were introduced. This is a cleaner way of using the library and it allows the user to call specific methods for a particular service instead of having way too many methods on the main class.

### <>.myitems
My Items manager that allows you to see the available game items for you to transfer and the available game profiles
- <>.myitems.profiles

Static attribute that gives you the available profiles and shardIds for your account (Only available if `<>.myitems.getUserProfiles()` was called at least once during runtime, else returns an empty list)
```python
# Example output
[
  {
    "username": "foobar",
    "level": 93,
    "shard": "EU",
    "shardId": 1,
    "profileId": "11111"
  },
  {
    "username": "foofoo",
    "level": 70,
    "shard": "EU",
    "shardId": 1,
    "profileId": "2323232323"
  }
]
```
- <>.myitems.getUserProfiles()

Returns the same as the static attribute that gives you the available profiles and refreshes its cache
```python
# Example output
[
  {
    "username": "foobar",
    "level": 93,
    "shard": "EU",
    "shardId": 1,
    "profileId": "11111"
  },
  {
    "username": "foofoo",
    "level": 70,
    "shard": "EU",
    "shardId": 1,
    "profileId": "2323232323"
  }
]
```
- <>.myitems.list()

Returns the list of items you have available for transfer
```python
# Example output, may differ based on item type but the base schema stays the same
[
  {
    "cartid":"1639063",
    "uid":"14345042",
    "itemid":"1545",
    "itemcount":"1",
    "last_update":"1499935454",
    "promoid":"156",
    "tid":"0",
    "iteminfo":{
      "id":1545,
      "title":"Walther P99",
      "itemid":"pt31_shop",
      "count":"1",
      "duration":"7",
      "duration_type":"day",
      "consumable":"0",
      "permanent":"0",
      "regular":"",
      "priority":"",
      "tag":"",
      "type":"item",
      "limit":"0"
    }
  },
  {
    "cartid":"1659295",
    "uid":"14345042",
    "itemid":"1557",
    "itemcount":"1",
    "last_update":"1499935454",
    "promoid":"156",
    "tid":"0",
    "iteminfo":{
      "id":1557,
      "title":"Warlord Boots",
      "itemid":"shared_shoes_09",
      "count":"1",
      "duration":"7",
      "duration_type":"day",
      "consumable":"0",
      "permanent":"0",
      "regular":"",
      "priority":"",
      "tag":"",
      "type":"item",
      "limit":"0"
    }
  },
  ...
}
```
- <>.myitems.history()

Returns the list of items you transferred in-game
```python
# Example output
[
  {
    "cartid":"29002997",
    "promoid":"313",
    "uid":"9999999",
    "itemid":"8447",
    "itemcount":"1",
    "shardid":"1",
    "status":100,
    "last_update":"1634142775",
    "details":"",
    "charid":"23232323",
    "send_status":"OK",
    "send_ts":"1639218962",
    "promo_name":"Promo \"Origins\"",
    "iteminfo":{
      "title":"Armageddon Engineer Helmet",
      "itemid":"engineer_helmet_armagedon",
      "count":1,
      "duration":15,
      "duration_type":"day",
      "consumable":0,
      "permanent":0,
      "regular":0,
      "type":"item",
      "title_fr":"Casque Armageddon pour Ingénieur",
      "title_de":"Ingenieurshelm Armageddon",
      "title_pl":"Hełm inżyniera Armageddon",
      "title_es":"Casco de ingeniero Armagedón",
      "title_tr":"Kıyamet Mühendis Miğferi",
      "title_pt":"Capacete de Engenheiro Armagedom",
      "title_ko":"아마게돈 엔지니어 헬멧",
      "title_cn":"末日工程师头盔",
      "title_jp":"エンジニアヘルメット「アルマゲドン」",
      "id":8447
    },
    "charname":"foobar"
  },
  {
    "cartid":"28471329",
    "promoid":"2",
    "uid":"9999999",
    "itemid":"7613",
    "itemcount":"1",
    "shardid":"1",
    "status":100,
    "last_update":"1626084624",
    "details":"",
    "charid":"11111",
    "send_status":"OK",
    "send_ts":"1628322603",
    "promo_name":"Support service",
    "iteminfo":{
      "id":7613,
      "title":"Achievement Fan of Discord",
      "title_fr":"Réalisation Fan de Discord",
      "title_de":"Leistung Discord-Fan",
      "title_pl":"Osiągnięcie Fan Discordu",
      "title_es":"Achievement Fan of Discord",
      "title_tr":"Achievement Fan of Discord",
      "title_pt":"Conquista Fã do Discord",
      "title_cn":"Achievement Fan of Discord",
      "title_jp":"@ru_discord_mark_01",
      "gold":"",
      "goldeu":"",
      "goldtur":"",
      "icon_url":"",
      "itemid":"unlock_ru_discord_mark_01",
      "price":"",
      "item_css_class":"",
      "type":"item",
      "count":"1",
      "duration":"0",
      "duration_type":"",
      "consumable":"0",
      "permanent":"0",
      "regular":"1",
      "priority":"",
      "tag":"",
      "sale":"",
      "limit":"0"
    },
    "charname":"foohoo"
  },
  ...
}
```
- <>.myitems.transferItem(cartId, profileId, shardId, sendNotification = True)

Allows you to transfer items that are listed in the `<>.myitems.list()` result. All the parameters are mandatory except the notifications, you can choose if send them in-game or not.
```python
# Example output
{
  "result":1,
  "msg":"Sent to the selected server: Absolute AT308"
}
```
### <>.inventory
Battlepass inventory management class that implements the needed methods.
- <>.inventory.list()

Native API that returns the content of the user battlepass inventory.
```python
wf.inventory.list() # Returns content from /minigames/inventory/api/list ['data']['inventory']
```
- <>.inventory.chars()

Native API that returns list of user in-game characters to which you can transfer items. Useful for <>.inventory.transfer() method
```python
wf.inventory.chars() # Returns content from /minigames/craft/api/user-info ['data']['chars']
```
- <>.inventory.transfer(server, item_id, amount=1, notification=False)

Method that allows the user to transfer items from the battlepass invetory to the game. Takes as arguments the server shardID (available from `<>.inventory.chars()`) and item ID (available from `<>.inventory.list()`). By default the amount is set to 1 and item will be transferred without in-game notification.
```python
wf.inventory.transfer(1,6025) # Transfers 1 temporary golden scar H to server 1 which in my case it's EU
```
- <>.inventory.lootDogToken()

Method that returns lootdog token. Probably for future use. Currenlty is blank.
```python
wf.inventory.lootDogToken()
```
### <>.crafting
- <>.crafting.crates()

Returns the list of user crafting crates either awaiting to be opened or to be opened/collected.
```python
wf.crafting.crates()
# Example output
[
    {
    "id": 48653619,
    "type": "silver",
    "state": "awaiting",
    "ended_at": -756216
    },
    {
    "id": 48654021,
    "type": "platinum",
    "state": "awaiting",
    "ended_at": -698615
    },
    {
    "id": 48654439,
    "type": "silver",
    "state": "awaiting",
    "ended_at": -756215
    },
    {
    "id": 48657667,
    "type": "silver",
    "state": "awaiting",
    "ended_at": -756215
    }
]
```
- <>.crafting.startCrate(crate_id)

Method that starts the crafting crate opening
```python
wf.crafting.startCrate(982645)
```
- <>.crafting.openCrate(crate_id)

Method that collects items from an opened crate
```python
wf.crafting.openCrate(982645)
# Example output
{"data":{"resource":{"level":1,"amount":30}},"state":"Success"}
```
- <>.crafting.resources()

Method that returns list of user crafting resources
```python
wf.crafting.resources()
# Example output
[
{
"level": 1,
"amount": 14714
},
{
"level": 2,
"amount": 23913
},
{
"level": 3,
"amount": 10776
},
{
"level": 4,
"amount": 666
},
{
"level": 5,
"amount": 121
}
]
```
- <>.crafting.slotCount()

Method that returns the amount of crafting slots the user has
```python
wf.crafting.slotCount()
# Example output
8
```
### <>.marketplace
- <>.marketplace.list()

Method that returns the list of items in the marketplace
```python
wf.marketplace.list()
```
- <>.marketplace.buy(entity_id, cost, type)

Method that allows to buy items from marketplace. Arguments are available in <>.marketplace.list()
Most items have type = "inventory
```python
wf.marketplace.buy(612, 40, "inventory")
```
- <>.marketplace.sell(item_id, cost, type)

Method that allows to sell in the marketplace. Arguments are available in <>.inventory.list()
```python
wf.marketplace.sell(612, 40)
```
- <>.marketplace.myOffers()

Method that returns the list of items that the user is currently selling
```python
wf.marketplace.myOffers()
```
- <>.marketplace.history()

Method that returns the selling/buying history of the user
```python
wf.marketplace.history()
```
### <>.chests
- <>.chests.list()

Method that returns the list of chests available for the user
```python
wf.chests.list()
```
- <>.chests.keys()

Method that returns the dict of key chests owned by the user. Key is chest_id, value is the amount of keys for that chest.
```python
wf.chests.keys()
```
- <>.chests.open(chest_id)

Method that opens user chests given the chest_id and returns the content of it.
```python
wf.chests.open(10)
# Example output
{
  "data": {
    "chests": [],
    "prize": {
      "type": "game_item",
      "value": {
        "id": "ar30_shop",
        "count": 1,
        "duration_type": "hour",
        "duration": 1
      },
      "name": "FN FAL DSA-58"
    }
  },
  "state": "Success"
}
```
## Properties
- <>.me

It's basically the cached version of `<>.user()` to quickly access nickname and email.
```python
wf.me
# Example output
{
    "state": "auth",
    "user_id": 9999999,
    "email": "foo@bar.com",
    "username": "foobar",
    "territory": "pc"
}
```
## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[GNU GPLv2](https://choosealicense.com/licenses/gpl-2.0/)
