# Social networks URL patterns

## Google Plus

https://plus.google.com/+USERNAME/PAGE
https://plus.google.com/u/0/+USERNAME/PAGE
https://plus.google.com/USERID/PAGE
https://plus.google.com/u/0/USERID/PAGE
https://plus.google.com/communities/USERID/PAGE

USERID [\d]+
USERNAME [\w-]+
PAGE [\w-]+

```
^
(?:https?:\/\/)?
plus\.google\.com\/
(?:u\/0\/|communities\/)?
\+?
([\w-]+)
(?:\/[\w-]+)?
```

## Facebook

https://www.facebook.com/PAGENAME
https://www.facebook.com/PAGE.NAME
https://www.facebook.com/pages/PAGENAME/PAGEID
https://www.facebook.com/pages/PAGENAME/PAGEID?v=app_123456
https://www.facebook.com/pages/PAGENAME/VANITYURL/PAGEID?v=app_132456
https://www.facebook.com/#!/PAGEID
https://www.facebook.com/PAGENAME#!/pages/VANITYURL/45678
https://www.facebook.com/PAGENAME#!/PAGEID?v=app_123465

PAGEID [\d]+
PAGENAME [\w-]+
VANITYURL [\w-]+

```
^
(?:https?:\/\/)?
(?:www\.)?
facebook\.com\/
(?:[\w-]*#!\/)?
(?:pages\/)?
(?:[\w-]+\/)*
([\w.-]+)
```

## Youtube

https://www.youtube.com/c/USERNAME
https://www.youtube.com/user/USERNAME
https://www.youtube.com/channel/CHANNELID

USERNAME [\w-]+
CHANNELID [\w-]+

```
^
(?:https?:\/\/)?
(?:www\.)?
youtube\.com\/
(?:c\/|channel\/|user\/)
([\w-]+)
```
