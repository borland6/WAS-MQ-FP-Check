python3 check_fixpack.py
cp -f fp-check.html index.html
# 1. 檢查是否存在名為 ibmfp 的容器（無論運行中或已停止）
if [ "$(docker ps -aq -f name=^ibmfp$)" ]; then
    echo "發現舊的容器，正在停止並移除..."
    # 2. 停止並移除容器
    docker rm -f ibmfp
else
    echo "沒有發現舊的容器，直接準備啟動。"
fi

# 3. 啟動新的容器
docker run -d --name ibmfp -p 8888:80 -v /home/dennis/ai-test/WAS-MQ-FP-Check/index.html:/usr/share/nginx/html/index.html nginx
