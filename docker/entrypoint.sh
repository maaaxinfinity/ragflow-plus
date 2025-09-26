#!/bin/bash

# replace env variables in the service_conf.yaml file
rm -rf /ragflow/conf/service_conf.yaml
while IFS= read -r line || [[ -n "$line" ]]; do
    # Use eval to interpret the variable with default values
    eval "echo \"$line\"" >> /ragflow/conf/service_conf.yaml
done < /ragflow/conf/service_conf.yaml.template

# 等待MySQL服务启动
echo "等待MySQL服务启动..."
while ! mysql -h"${MYSQL_HOST:-mysql}" -P"${MYSQL_PORT:-3306}" -u"${MYSQL_USER:-root}" -p"${MYSQL_PASSWORD:-infini_rag_flow}" -e "SELECT 1;" >/dev/null 2>&1; do
    echo "MySQL服务未就绪，等待5秒后重试..."
    sleep 5
done
echo "MySQL服务已启动"

# 执行数据库迁移脚本
echo "执行数据库迁移..."
if [ -f "/ragflow/docker/migration.sql" ]; then
    mysql -h"${MYSQL_HOST:-mysql}" -P"${MYSQL_PORT:-3306}" -u"${MYSQL_USER:-root}" -p"${MYSQL_PASSWORD:-infini_rag_flow}" "${MYSQL_DBNAME:-rag_flow}" < /ragflow/docker/migration.sql
    echo "数据库迁移完成"
else
    echo "迁移脚本不存在，跳过迁移"
fi

/usr/sbin/nginx

export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/

PY=python3
if [[ -z "$WS" || $WS -lt 1 ]]; then
  WS=1
fi

function task_exe(){
    JEMALLOC_PATH=$(pkg-config --variable=libdir jemalloc)/libjemalloc.so
    while [ 1 -eq 1 ];do
      LD_PRELOAD=$JEMALLOC_PATH $PY rag/svr/task_executor.py $1;
    done
}

for ((i=0;i<WS;i++))
do
  task_exe  $i &
done

while [ 1 -eq 1 ];do
    $PY api/ragflow_server.py
done

wait;
