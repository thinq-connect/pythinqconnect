
![Local Image](https://www.lge.co.kr/kr/main/thinq/images/main/thinq_logo.png)

# Project Description

The thinqconnect provides a robust interface for interacting with the [LG ThinQ Connect](https://thinq.developer.lge.com/ko/cloud/about/service/ThinQ-Connect) Open API.
This SDK is designed to facilitate seamless integration with a range of LGE appliances, bases on [LG ThinQ Connect](https://thinq.developer.lge.com/ko/cloud/about/service/ThinQ-Connect).

# Key Features
* Profile Retrieval: Access detailed profiles of 27 different home appliances.
* Device Management: Query and retrieve lists of connected devices and their statuses.
* Device Control: Execute commands to control your appliances directly through the API.
* Event Handling: Utilize AWS IoT Core for MQTT connections to receive device events and push notifications via callbacks.

This SDK is an essential tool for developers looking to integrate ThinQ Connect capabilities into their applications, ensuring efficient and reliable smart home management.


# Installation and usage
## Installation
```
pip install thinqconnect
```

## Usage

### Obtaining and Using a Personal Access Token
To use the ThinQ Connect Python SDK, you need to obtain a Personal Access Token from the LG ThinQ Developer Site.
Follow the steps below to get your token and configure your environment.

Steps to Obtain a Personal Access Token

1.	Sign Up or Log In:
    * Visit the [LG ThinQ Developer Site](https://thinq.developer.lge.com).
2.	Navigate to Cloud Developer:
	* After logging in, go to the Cloud Developer section.
3.	Navigate to Docs.
4. Locate ThinQ Connect:
	* Within the docs, find and select ThinQ Connect.
5.	Generate Personal Access Token:
	* Under the ThinQ Connect section, locate PAT (Personal Access Token).
    * If you don’t have an account, sign up for one. If you already have an account, log in using your LG ThinQ Account.
	* Follow the instructions provided to generate and copy your Personal Access Token.

After obtaining your Personal Access Token, you need to configure your environment to use it with the SDK.


### Client ID Requirements
Each client device must use a unique Client ID. This Client ID should be a randomly generated value, and using a uuid4 format is recommended.
Be cautious with excessive client creation, as it may lead to your API calls being blocked.
```py
import uuid
client_id = str(uuid.uuid4())
```

### Country Codes
When initializing the SDK, you will also need to provide a country code.
Refer to the table below for the appropriate country code to use:
| **Country** |             **Code**             | **Country** |         **Code**        | **Country** |             **Code**             |
|:-----------:|:--------------------------------:|:-----------:|:-----------------------:|:-----------:|:--------------------------------:|
|      AE     | United Arab   Emirates           |      GD     | Grenada                 |      NG     | Nigeria                          |
|      AF     | Afghanistan                      |      GE     | Georgia                 |      NI     | Nicaragua                        |
|      AG     | Antigua and Barbuda              |      GH     | Gana                    |      NL     | Netherlands                      |
|      AL     | Albania                          |      GM     | Gambia                  |      NO     | Norway                           |
|      AM     | Armenia                          |      GN     | Guinea                  |      NP     | Nepal                            |
|      AO     | Angola                           |      GQ     | Equatorial Guinea       |      NZ     | New Zealand                      |
|      AR     | Argentina                        |      GR     | Greece                  |      OM     | Oman                             |
|      AT     | Austria                          |      GT     | Guatemala               |      PA     | Panama                           |
|      AU     | Australia                        |      GY     | Guyana                  |      PE     | Peru                             |
|      AW     | Aruba                            |      HK     | Hong Kong               |      PH     | Philippines                      |
|      AZ     | Azerbaijan                       |      HN     | Honduras                |      PK     | Pakistan                         |
|      BA     | Bosnia and Herzegovina           |      HR     | Croatia                 |      PL     | Poland                           |
|      BB     | Barbados                         |      HT     | Haiti                   |      PR     | Puerto Rico                      |
|      BD     | Bangladesh                       |      HU     | Hungary                 |      PS     | Occupied Palestinian Territory   |
|      BE     | Belgium                          |      ID     | Indonesia               |      PT     | Portugal                         |
|      BF     | Burkina Faso                     |      IE     | Ireland                 |      PY     | Paraguay                         |
|      BG     | Bulgaria                         |      IL     | Israel                  |      QA     | Qatar                            |
|      BH     | Bahrain                          |      IN     | India                   |      RO     | Romania                          |
|      BJ     | Benin                            |      IQ     | Iraq                    |      RS     | Serbia                           |
|      BO     | Bolivia                          |      IR     | Iran                    |      RU     | Russian Federation               |
|      BR     | Brazil                           |      IS     | Iceland                 |      RW     | Rwanda                           |
|      BS     | Bahamas                          |      IT     | Italy                   |      SA     | Saudi Arabia                     |
|      BY     | Belarus                          |      JM     | Jamaica                 |      SD     | Sudan                            |
|      BZ     | Belize                           |      JO     | Jordan                  |      SE     | Sweden                           |
|      CA     | Canada                           |      JP     | Japan                   |      SG     | Singapore                        |
|      CD     | Democratic Republic of the Congo |      KE     | Kenya                   |      SI     | Slovenia                         |
|      CF     | Central African Republic         |      KG     | Kyrgyzstan              |      SK     | Slovakia                         |
|      CG     | Republic of the Congo            |      KH     | Cambodia                |      SL     | Sierra Leone                     |
|      CH     | Switzerland                      |      KN     | Saint Kitts and Nevis   |      SN     | Senegal                          |
|      CI     | Republic of Ivory Coast          |      KR     | Korea                   |      SO     | Somalia                          |
|      CL     | Chile                            |      KW     | Kuwait                  |      SR     | Suriname                         |
|      CM     | Cameroon                         |      KZ     | Kazakhstan              |      ST     | Sao Tome and Principe            |
|      CN     | China                            |      LA     | Laos                    |      SV     | El Salvador                      |
|      CO     | Colombia                         |      LB     | Lebanon                 |      SY     | Syrian Arab Republic             |
|      CR     | Costa Rica                       |      LC     | Saint Lucia             |      TD     | Chad                             |
|      CU     | Cuba                             |      LK     | Sri Lanka               |      TG     | Togo                             |
|      CV     | Cape Verde                       |      LR     | Liberia                 |      TH     | Thailand                         |
|      CY     | Cyprus                           |      LT     | Lithuania               |      TN     | Tunisia                          |
|      CZ     | Czech Republic                   |      LU     | Luxembourg              |      TR     | Turkey                           |
|      DE     | Germany                          |      LV     | Latvia                  |      TT     | Trinidad and Tobago              |
|      DJ     | Djibouti                         |      LY     | Libyan Arab Jamahiriya  |      TW     | Taiwan                           |
|      DK     | Denmark                          |      MA     | Morocco                 |      TZ     | United Republic of Tanzania      |
|      DM     | Dominica                         |      MD     | Republic of Moldova     |      UA     | Ukraine                          |
|      DO     | Dominican Republic               |      ME     | Montenegro              |      UG     | Uganda                           |
|      DZ     | Algeria                          |      MK     | Macedonia               |      US     | USA                              |
|      EC     | Ecuador                          |      ML     | Mali                    |      UY     | Uruguay                          |
|      EE     | Estonia                          |      MM     | Myanmar                 |      UZ     | Uzbekistan                       |
|      EG     | Egypt                            |      MR     | Mauritania              |      VC     | Saint Vincent and the Grenadines |
|      ES     | Spain                            |      MT     | Malta                   |      VE     | Venezuela                        |
|      ET     | Ethiopia                         |      MU     | Mauritius               |      VN     | Vietnam                          |
|      FI     | Finland                          |      MW     | Malawi                  |      XK     | Kosovo                           |
|      FR     | France                           |      MX     | Mexico                  |      YE     | Yemen                            |
|      GA     | Gabon                            |      MY     | Malaysia                |      ZA     | South Africa                     |
|      GB     | United Kingdom                   |      NE     | Niger                   |      ZM     | Zambia                           |

### Simple Test
```py
import asyncio
from aiohttp import ClientSession
from thinqconnect.thinq_api import ThinQApi

async def test_devices_list():
    async with ClientSession() as session:
        thinq_api = ThinQApi(session=session, access_token='your_personal_access_token', country_code='your_contry_code', client_id='your_client_id')
        response = await thinq_api.async_get_device_list()
        print("device_list : %s", response.body)

asyncio.run(test_devices_list())
```
Ensure that you keep your Personal Access Token and Client ID secure and do not expose them in your source code or public repositories.


# License
Apache License

# Available Device Types and Properties
For detailed information on Device Properties, please refer to the following page: [LG ThinQ Connect - Device Profile](https://thinq.developer.lge.com/ko/cloud/docs/thinq-connect/device-profile)


### DEVICE\_AIR\_CONDITIONER

### Main

|     | resources | properties |
| --- | --- | --- |
| 1   | air\_con\_job\_mode | current\_job\_mode |
| 2   | operation | air\_con\_operation\_mode |
| 3   | operation |air\_clean\_operation\_mode |
| 4   | temperature | current\_temperature |
| 5   | temperature | target\_temperature |
| 6   | temperature | heat\_target\_temperature |
| 7   | temperature | cool\_target\_temperature |
| 8   | temperature | temperature\_unit |
| 9   | two\_set\_temperature | two\_set\_current\_temperature |
| 10  | two\_set\_temperature | two\_set\_heat\_target\_temperature |
| 11  | two\_set\_temperature | two\_set\_cool\_target\_temperature |
| 12  | two\_set\_temperature | two\_set\_temperature\_unit |
| 13  | timer | relative\_hour\_to\_start |
| 14  | timer | relative\_minute\_to\_start |
| 15  | timer | relative\_hour\_to\_stop |
| 16  | timer | relative\_minute\_to\_stop |
| 17  | timer | absolute\_hour\_to\_start |
| 18  | timer | absolute\_minute\_to\_start |
| 19  | timer | absolute\_hour\_to\_stop |
| 20  | timer | absolute\_minute\_to\_stop |
| 21  | sleep\_timer | sleep\_timer\_relative\_hour\_to\_stop |
| 22  | sleep\_timer | sleep\_timer\_relative\_minute\_to\_stop |
| 23  | power\_save | power\_save\_enabled |
| 24  | air\_flow | wind\_strength |
| 25  | air\_flow | wind\_step |
| 26  | air\_quality\_sensor | pm1 |
| 27  | air\_quality\_sensor | pm2 |
| 28  | air\_quality\_sensor | pm10 |
| 29  | air\_quality\_sensor | odor |
| 30  | air\_quality\_sensor | humidity |
| 31  | air\_quality\_sensor | total\_pollution |
| 32  | air\_quality\_sensor | monitoring\_enabled |
| 33  | filter\_info | used\_time |
| 34  | filter\_info | filter\_lifetime |

### DEVICE\_AIR\_PURIFIER

### Main

|     | resources | properties |
| --- | --- | --- |
| 1   | air\_purifier\_job\_mode | current\_job\_mode |
| 2   | air\_purifier\_job\_mode | personalization\_mode |
| 3   | operation | air\_purifier\_operation\_mode |
| 4   | timer | absolute\_hour\_to\_start |
| 5   | timer | absolute\_minute\_to\_start |
| 6   | timer | absolute\_hour\_to\_stop |
| 7   | timer | absolute\_minute\_to\_stop |
| 8   | air\_flow | wind\_strength |
| 9   | air\_quality\_sensor | monitoring\_enabled |
| 10  | air\_quality\_sensor | pm1 |
| 11  | air\_quality\_sensor | pm2 |
| 12  | air\_quality\_sensor | pm10 |
| 13  | air\_quality\_sensor | odor |
| 14  | air\_quality\_sensor | humidity |
| 15  | air\_quality\_sensor | total\_pollution |

### DEVICE\_AIR\_PURIFIER\_FAN

### Main

|     | resources | properties |
| --- | --- | --- |
| 1   | air\_fan\_job\_mode | current\_job\_mode |
| 2   | operation | air\_fan\_operation\_mode |
| 3   | timer | absolute\_hour\_to\_start |
| 4   | timer | absolute\_minute\_to\_start |
| 5   | timer | absolute\_hour\_to\_stop |
| 6   | timer | absolute\_minute\_to\_stop |
| 7   | sleep\_timer | sleep\_timer\_relative\_hour\_to\_stop |
| 8   | sleep\_timer | sleep\_timer\_relative\_minute\_to\_stop |
| 9   | air\_flow | warm\_mode |
| 10  | air\_flow | wind\_temperature |
| 11  | air\_flow | wind\_strength |
| 12  | air\_flow | wind\_angle |
| 13  | air\_quality\_sensor | monitoring\_enabled |
| 14  | air\_quality\_sensor | pm1 |
| 15  | air\_quality\_sensor | pm2 |
| 16  | air\_quality\_sensor | pm10 |
| 17  | air\_quality\_sensor | humidity |
| 18  | air\_quality\_sensor | temperature |
| 19  | air\_quality\_sensor | odor |
| 20  | air\_quality\_sensor | total\_pollution |
| 21  | display | display\_light |
| 22  | misc | uv\_nano |

### DEVICE\_CEILING\_FAN

### Main

|     | resources | properties |
| --- | --- | --- |
| 1   | air\_flow | wind\_strength |
| 2   | operation | ceiling\_fan\_operation\_mode |

### DEVICE\_COOKTOP

### Main

|     | resources | properties |
| --- | --- | --- |
| 1   | operation | operation\_mode |

### Sub

|     | resources | properties |
| --- | --- | --- |
| 1   | cooking\_zone | current\_state |
| 2   | power | power\_level |
| 3   | remote\_control\_enable | remote\_control\_enabled |
| 4   | timer | remain\_hour |
| 5   | timer | remain\_minute |

### DEVICE\_DEHUMIDIFIER

### Main

|     | resources | properties |
| --- | --- | --- |
| 1   | operation | dehumidifier\_operation\_mode |
| 2   | dehumidifier\_job\_mode | current\_job\_mode |
| 3   | humidity | current\_humidity |
| 4   | air\_flow | wind\_strength |

### DEVICE\_DISH\_WASHER

### Main

|     | resources | properties |
| --- | --- | --- |
| 1   | run\_state | current\_state |
| 2   | dish\_washing\_status | rinse\_refill |
| 3   | preference | rinse\_level |
| 4   | preference | softening\_level |
| 5   | preference | machine\_clean\_reminder |
| 6   | preference | signal\_level |
| 7   | preference | clean\_light\_reminder |
| 8   | door\_status | door\_state |
| 9   | operation | dish\_washer\_operation\_mode |
| 10  | remote\_control\_enable | remote\_control\_enabled |
| 11  | timer | relative\_hour\_to\_start |
| 12  | timer | relative\_minute\_to\_start |
| 13  | timer | remain\_hour |
| 14  | timer | remain\_minute |
| 15  | timer | total\_hour |
| 16  | timer | total\_minute |
| 17  | dish\_washing\_course | current\_dish\_washing\_course |

### DEVICE\_DRYER

### Main

|     | resources | properties |
| --- | --- | --- |
| 1   | run\_state | current\_state |
| 2   | operation | dryer\_operation\_mode |
| 3   | remote\_control\_enable | remote\_control\_enabled |
| 4   | timer | remain\_hour |
| 5   | timer | remain\_minute |
| 6   | timer | total\_hour |
| 7   | timer | total\_minute |
| 8   | timer | relative\_hour\_to\_stop |
| 9   | timer | relative\_minute\_to\_stop |
| 10  | timer | relative\_hour\_to\_start |
| 11  | timer | relative\_minute\_to\_start |

### DEVICE\_HOME\_BREW

### Main

|     | resources | properties |
| --- | --- | --- |
| 1   | run\_state | current\_state |
| 2   | recipe | beer\_remain |
| 3   | recipe | flavor\_info |
| 4   | recipe | hop\_oil\_info |
| 5   | recipe | wort\_info |
| 6   | recipe | yeast\_info |
| 7   | recipe | recipe\_name |
| 8   | timer | elapsed\_day\_state |
| 9   | timer | elapsed\_day\_total |

### DEVICE\_HOOD

### Main

|     | resources | properties |
| --- | --- | --- |
| 1   | ventilation | fan\_speed |
| 2   | lamp | lamp\_brightness |
| 3   | operation | hood\_operation\_mode |
| 4   | timer | remain\_minute |
| 5   | timer | remain\_second |

### DEVICE\_HUMIDIFIER

### Main

|     | resources | properties |
| --- | --- | --- |
| 1   | humidifier\_job\_mode | current\_job\_mode |
| 2   | operation | humidifier\_operation\_mode |
| 3   | operation | auto\_mode |
| 4   | operation | sleep\_mode |
| 5   | operation | hygiene\_dry\_mode |
| 6   | timer | absolute\_hour\_to\_start |
| 7   | timer | absolute\_hour\_to\_stop |
| 8   | timer | absolute\_minute\_to\_start |
| 9   | timer | absolute\_minute\_to\_stop |
| 10  | sleep\_timer | sleep\_timer\_relative\_hour\_to\_stop |
| 11  | sleep\_timer | sleep\_timer\_relative\_minute\_to\_stop |
| 12  | humidity | target\_humidity |
| 13  | humidity | warm\_mode |
| 14  | air\_flow | wind\_strength |
| 15  | air\_quality\_sensor | monitoring\_enabled |
| 16  | air\_quality\_sensor | total\_pollution |
| 17  | air\_quality\_sensor | pm1 |
| 18  | air\_quality\_sensor | pm2 |
| 19  | air\_quality\_sensor | pm10 |
| 20  | air\_quality\_sensor | humidity |
| 21  | air\_quality\_sensor | temperature |
| 22  | display | display\_light |
| 23  | mood\_lamp | mood\_lamp\_state |

### DEVICE\_KIMCHI\_REFRIGERATOR

### Main

|     | resources | properties |
| --- | --- | --- |
| 1   | refrigeration | one\_touch\_filter |
| 2   | refrigeration | fresh\_air\_filter |

### Sub

|     | resources | properties |
| --- | --- | --- |
| 1   | temperature | target\_temperature |

### DEVICE\_MICROWAVE\_OVEN

### Main

|     | resources | properties |
| --- | --- | --- |
| 1   | run\_state | current\_state |
| 2   | timer | remain\_minute |
| 3   | timer | remain\_second |
| 4   | ventilation | fan\_speed |
| 5   | lamp | lamp\_brightness |

### DEVICE\_OVEN

### Main

|     | resources | properties |
| --- | --- | --- |
| 1   | info | oven\_type |

### Sub

|     | resources | properties |
| --- | --- | --- |
| 1   | run\_state | current\_state |
| 2   | operation | oven\_operation\_mode |
| 3   | cook | cook\_mode |
| 4   | remote\_control\_enable | remote\_control\_enabled |
| 5   | temperature | target\_temperature\_c |
| 6   | temperature | target\_temperature\_f |
| 7   | timer | remain\_hour |
| 8   | timer | remain\_minute |
| 9   | timer | remain\_second |
| 10  | timer | target\_hour |
| 11  | timer | target\_minute |
| 12  | timer | target\_second |
| 13  | timer | timer\_hour |
| 14  | timer | timer\_minute |
| 15  | timer | timer\_second |

### DEVICE\_PLANT\_CULTIVATOR

### Main - Empty

### Sub

|     | resources | properties |
| --- | --- | --- |
| 1   | run\_state | current\_state |
| 2   | run\_state | growth\_mode |
| 3   | run\_state | wind\_volume |
| 4   | light | brightness |
| 5   | light | duration |
| 6   | light | start\_hour |
| 7   | light | start\_minute |
| 8   | light | end\_hour |
| 9   | light | end\_minute |
| 10  | temperature | day\_target\_temperature |
| 11  | temperature | night\_target\_temperature |
| 12  | temperature | temperature\_state |

### DEVICE\_REFRIGERATOR

### Main

|     | resources | properties |
| --- | --- | --- |
| 1   | power\_save | power\_save\_enabled |
| 2   | eco\_friendly | eco\_friendly\_mode |
| 3   | sabbath | sabbath\_mode |
| 4   | refrigeration | rapid\_freeze |
| 5   | refrigeration | express\_mode |
| 6   | refrigeration | fresh\_air\_filter |
| 7   | water\_filter\_info | used\_time |
| 8   | water\_filter\_info | water\_filter\_info\_unit |

### Sub

|     | resources | properties |
| --- | --- | --- |
| 1   | door\_status | door\_state |
| 2   | temperature | location\_name |
| 3   | temperature | target\_temperature |
| 4   | temperature | temperature\_unit |

### DEVICE\_ROBOT\_CLEANER

### Main

|     | resources | properties |
| --- | --- | --- |
| 1   | run\_state | current\_state |
| 2   | robot\_cleaner\_job\_mode | current\_job\_mode |
| 3   | operation | clean\_operation\_mode |
| 4   | battery | battery\_level |
| 5   | battery | battery\_percent |
| 6   | timer | absolute\_hour\_to\_start |
| 7   | timer | absolute\_minute\_to\_start |
| 8   | timer | running\_hour |
| 9   | rtimer | unning\_minute |

### DEVICE\_STICK\_CLEANER

### Main

|     | resources | properties |
| --- | --- | --- |
| 1   | run\_state | current\_state |
| 2   | stick\_cleaner\_job\_mode | current\_job\_mode |
| 3   | battery | battery\_level |

### DEVICE\_STYLER

### Main

|     | resources | properties |
| --- | --- | --- |
| 1   | run\_state | current\_state |
| 2   | operation | styler\_operation\_mode |
| 3   | remote\_control\_enable | remote\_control\_enabled |
| 4   | timer | relative\_hour\_to\_stop |
| 5   | timer | relative\_minute\_to\_stop |
| 6   | timer | remain\_hour |
| 7   | timer | remain\_minute |
| 8   | timer | total\_hour |
| 9   | timer | total\_minute |

### DEVICE\_SYSTEM\_BOILER

### Main

|     | resources | properties |
| --- | --- | --- |
| 1   | boiler\_job\_mode | current\_job\_mode |
| 2   | operation | boiler\_operation\_mode |
| 3   | operation | hot\_water\_mode |
| 4   | temperature | current\_temperature |
| 5   | temperature | target\_temperature |
| 6   | temperature | heat\_target\_temperature |
| 7   | temperature | cool\_target\_temperature |
| 8   | temperature | heat\_max\_temperature |
| 9   | temperature | heat\_min\_temperature |
| 10  | temperature | cool\_max\_temperature |
| 11  | temperature | cool\_min\_temperature |
| 12  | temperature | temperature\_unit |

### DEVICE\_WASHER

### Main - Empty

### Sub

|     | resources | properties |
| --- | --- | --- |
| 1   | run\_state | current\_state |
| 2   | operation | washer\_operation\_mode |
| 3   | remote\_control\_enable | remote\_control\_enabled |
| 4   | timer | remain\_hour |
| 5   | timer | remain\_minute |
| 6   | timer | total\_hour |
| 7   | timer | total\_minute |
| 8   | timer | relative\_hour\_to\_stop |
| 9   | timer | relative\_minute\_to\_stop |
| 10  | timer | relative\_hour\_to\_start |
| 11  | timer | relative\_minute\_to\_start |
| 12  | detergent | detergent\_setting |

### DEVICE\_WATER\_HEATER

### Main

|     | resources | properties |
| --- | --- | --- |
| 1   | water\_heater\_job\_mode | current\_job\_mode |
| 2   | operation | water\_heater\_operation\_mode |
| 3   | temperature | current\_temperature |
| 4   | temperature | target\_temperature |

### DEVICE\_WATER\_PURIFIER

### Main

|     | resources | properties |
| --- | --- | --- |
| 1   | run\_state | cock\_state |
| 2   | run\_state | sterilizing\_state |
| 3   | water\_info | water\_type |

### DEVICE\_WINE\_CELLAR

### Main

|     | resources | properties |
| --- | --- | --- |
| 1   | operation | light\_brightness |
| 2   | operation | optimal\_humidity |
| 3   | operation | sabbath\_mode |
| 4   | operation | light\_status |

### Sub

|     | resources | properties |
| --- | --- | --- |
| 1   | temperature | location\_name |
| 2   | temperature | target\_temperature |
| 3   | temperature | temperature\_unit |
