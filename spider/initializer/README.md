# Initializer

## 功能
读取站点信息信息，初始化站点抓取任务

## 设计
> * scan_site:
主功能函数，由timer周期性调用，扫描站点信息，初始化各个站点的抓取任务

> * get_site:
获取一个站点信息，失败返回None

> * check_site:
检查站点是否需要初始化抓取任务

> * add_task:
将站点的任务加入任务集合(task collection)

## 问题
### add_task
mongo的原子性只支持一个document上的操作，当一个站点的init_urls中的链接超过一条, add_task就需要在task collection中插入多条任务，目前逻辑为一条失败add_task就认为失败，改站点的状态不修改，下次扫描时仍会初始化改站点的抓取任务。产生的影响是可能同一条任务在task collection中出现多条。（目前认为这是可容忍的）

## ToDo
### 1.
在设计中，如果一个站点的初始化任务列表不能通过一组url表示(init_urls字段)，Initializer可以调用init_module字段指定的一段代码生成该站点的初始化抓取任务。改功能在版本中没有实现
