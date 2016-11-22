# Config

* spider config
    * set configuration files of spider in path `conf/`
    * set configuration of spider service in file `run.sh`
* spider webui config
    * set configuration files of webui server in path `webui/spider_control/__init__.py`
    * set configuration files of webui client in path `webui/spider_control/static/CrawlerUI/js/tableGlobalVar.js`

# Install

* `pip install -r requirements`
* run command `sh mongo_init.sh` to initialize mongodb indexes
* run command `sh run.sh`