# Favorite API Doc

## Gateway
```
/api/v1/favorite
```

#### GET
参数位置：args（?后面的参数）

|参数名|是否必选|数据类型|位置|默认值|描述|
|---|---|---|---|---|---|
|token|False|string|header||私有收藏权限判断|
|kw|False|string|args||关键字（name, content, description等中出现的）|
|catalog|False|string|args||目录|
|tag|False|string|args||标签|
|is_unread|False|bool|args||是否未读|
|is_recommended|False|bool|args||是否推荐|
#### POST

|参数名|是否必选|数据类型|位置|默认值|描述|
|---|---|---|---|---|---|
|token|True|string|header||登录认证|
|action|True|string|body|"update"|可选"update","create"|
|id|False|string|body||收藏id，action="create"时不需要|
|name|False|string|body|||
|description|False|string|body||cli端创建收藏时的message|
|owner_id|False|string|body||
|tags|False|string|body||#标签,多个标签以英文逗号分割|
|origin|False|string|body||#出处，暂时不用|
|source|False|string|body|| #出处|
|is_private|False|bool|body|| #是否私有|
|is_recommended|False|bool|body||是否推荐（is_private=False）|
|is_unread|False|bool|body||#是否未读|
|catalog|False|string|body||#目录|
|url|False|string|body||#url类收藏|
|content_id|False|string|body||#爬虫爬取到的网页内容（mongodb那边的id）|
|project_id|False|string|body||#所属项目id|


#### DELETE

|参数名|是否必选|数据类型|位置|默认值|描述|
|---|---|---|---|---|---|
|token|True|string|header||登录认证|
|id|True|string|args||删除的收藏id|