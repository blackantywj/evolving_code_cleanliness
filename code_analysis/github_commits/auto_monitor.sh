#!/bin/bash

# 被监控的screen会话名称
SESSION_NAME="autoplus"
# 要触发运行的脚本路径
TRIGGER_SCRIPT="auto_plus.sh"

# 检测并执行
while true; do
  # 获取screen会话的输出
  OUTPUT=$(screen -S "$SESSION_NAME" -X hardcopy /tmp/screen_log && tail -n 100 /tmp/screen_log)
  
  # 检查是否包含指定字符串
  if echo "$OUTPUT" | grep -q "cumt@cumt-System-Product-Name"; then
    echo "Detected cumt@cumt-System-Product-Name, running script..."
    bash "$TRIGGER_SCRIPT"
    break
  fi
  
  # 延迟检查，避免高CPU占用
  sleep 1
done
