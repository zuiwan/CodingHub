# CodingLife_Server
Your all-round manager of coding life.


## Deploy
```bash
cd /root/CodingLife_Server
git pull
sh tool/restart.sh
```


## Procedure
- new feature
1. create branch feature/NAME
2. development on local environment
3. review code, and commit with message like `[DEV] user login.`
4. push code
5. login the server, checkout the origin/feature/NAME as feature/NAME (git pull && git checkout -b...), and do restart server.
6. do integration testing by postman or script code locally.
7. if bug or something, fix it, and commit&push and pull&restart.
8. on branch dev, do `git merge feature/NAME --no-ff`, and the feature is finished.


## 数据库ORM

建表：写OrmModel，然后在`tool/create_db.py` 和 `tool/database_manager.py` 中import新建的OrmModel即可。
改表：改OrmModel即可。

数据库的migrate和upgrade操作都放到了`tool/restart.sh`中。