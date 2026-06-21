#!/usr/bin/sh

export CONTAINER_IP=$(hostname -I | awk '{print $1}')

cd /app/BAAH
# BlockHaity：如果要做Docker内部更新，就把git pull删掉，让用户选择更新
if [ -f ".enable_auto_update" ]; then
    git pull
    python3 requireforyou.py --core
    uv pip install -r requireforyou.txt --system
fi

# 检测Docker网络模式,同时兼容端口映射和host模式
if ip link show docker0 &>/dev/null; then
    python3 jsoneditor.py --host 0.0.0.0 --no-show
elif ip link show podman0 &>/dev/null; then
    python3 jsoneditor.py --host 0.0.0.0 --no-show
else
    python3 jsoneditor.py --no-show
fi
