cd master;nohup  python master_service.py \
--port=9000 \
--max_task_size=20000000 \
--max_client_num=2000 \
--log_file_max_size=64000000 \
--log_file_num_backups=2 \
--log_file_prefix=/search/spider_log/article_spider_log/master.log \
--client_log_file_prefix=/search/spider_log/article_spider_log/client.log>/dev/null 2>&1 &

