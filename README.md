## 链家 乐有家 Q房网 爬虫<br>
[![Python](https://img.shields.io/badge/Python-3.6%2B-brightgreen.svg)](https://www.python.org)<br>
以天为单位的保存每套房源信息，目前每天的数据已经很平稳，波动不大，但是也还有很多可以优化的地方；<br>
1.【可伸缩】产品发现与产品析取分为不同的spider（urlspider、contentspider） 【√】<br>
2.【更稳定】增量url池，不以每天房源列表的url为准，因为房源列表有反爬，可能今天爬得到的url，明天就没了，增量url池可以很大程度缓解这个问题，每天维护url池，让数据更稳定分析更准确 【TODO】<br>
3.【更快速】contentspider改为scrapy-redis分布式监听redis，每天url存入redis，分布式的析取房源信息 【TODO】<br>
<br>
感兴趣的同学帮忙star点一下，你的star也是我维护升级的动力<br>
<br>
### 数据分析维度<br>
1.所有中介房源详细信息<br>
2.近n日降价/涨价房源占总房源数比例<br>
3.近n日降价/涨价房源详细信息<br>
4.近n日7/30日带看次数占总房源数比例<br>
etc...<br>
<br>
### 部分数据及分析展示<br>
图1.所有中介房源详细信息（这里只展示了部分字段）-广州市番禺区-2018年11月13日（7680条）<br>
<br>
![image](https://github.com/roytian1217/apartment/blob/master/screenshots/apt-all.png)<br>
<br>
图2.降价房源占总房源比例-链家-广州市番禺区-2018年8月底至10月下旬，广州市番禺区二手房降价比例在增加。<br>
例如从8月底到11月13号，广州市番禺区降价房源数量为1670套（图3），13号当天总房源5441套，那么降价比例就是1670/5441=0.3069，那么就是三成的房源有降价（降价幅度可另外分析）<br>
<br>
![image](https://github.com/roytian1217/apartment/blob/master/screenshots/price-down-rate.png)<br>
<br>
图3.近2个半月（2018年8月底至11月13日）降价房源详细信息（这里只展示了部分字段）-链家-广州市番禺区（1670条）<br>
<br>
![image](https://github.com/roytian1217/apartment/blob/master/screenshots/price-down-lianjia.png)<br>
<br>
图4.最近一个月近7日带看、30日带看走势-链家-广州市番禺区 ，可以分析出节假日看房的人较多(感觉这个不用分析也能推测出来[哭笑])<br>
<br>
![image](https://github.com/roytian1217/apartment/blob/master/screenshots/check-rate.png)<br>
<br>
<br>
**疑问解答及对数据感兴趣的可以联系笔者**<br>
QQ 373119611