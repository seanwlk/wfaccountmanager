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
pip install git+https://github.com/seanwlk/wfaccountmanager # Live updated library
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
# {"status" : "Captcha Required", "url" : "capthca URL to resolve"}
# {"status" : "Email code Required"}
# {"status" : "Steamguard 2FA Required"}

wf.postSteam2FA("ASB1G") # Setting the 2FA gotten on the app, via mail or captcha
# returns /minigames/user/info
```

When using steam with the `login()` method the returned data will contain a `steam` key with inside the `steamID` the `auth_token` and `steamguard_token` which will allow you to login in a future session without user and password but by passing those parameters only.
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
- <>.inventory()
Native API that returns the content of the user battlepass inventory. It also has information of the user characters in other servers.
```python
wf.inventory() # Returns content from /minigames/inventory/api/list
```
- <>.listCrates()
Native API that returns crafting information such as available crates, crafting resources and crafting items available
```python
wf.listCrates() # Returns content from /minigames/craft/api/user-info
```
- <>.startCraftCrate(chest_id) and <>.openCraftCrate(chest_id)

Both these methods are used to manage the crafting crates. The first initiates the crate opening. When it's ready you can open it with the secodn method. The `chest_id` is given in `<>.listCrates()`.
```python
wf.startCraftCrate(7694963) # Returns actual http response from server
wf.openCraftCrate(7694963) # Returns actual http response from server with chest content
```
## Properties
- <>.me
It's basically the cached version of `<>.user()` to quickly access nickname and email.
```
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