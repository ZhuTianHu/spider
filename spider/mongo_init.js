db.crawl_statistics.ensureIndex({"uid": 1, "task_type": 1, "batch_id": 1, "site_name": 1}, {unique: true, dropDups: true})
db.task.ensureIndex({"status": 1})
db.site.ensureIndex({"uid": 1, "site_name": 1})
db.task_conf.ensureIndex({"uid: 1, task_type": 1})
