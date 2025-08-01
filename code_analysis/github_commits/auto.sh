#!/bin/bash

# 定义要监控的screen会话名称和新命令
SCREEN_NAME="auto1"
NEW_COMMAND="python search.py"

# 监控时间阈值（以秒为单位，3分钟 = 180秒）
TIMEOUT=180
# 初始等待时间阈值（避免死循环，如果一开始就没有HTTP字段，等到超过初始等待时间就退出）
INITIAL_WAIT_TIME=60  # 初始等待时间设定为60秒

# 初始化超时计数器
start_time=$(date +%s)    # 记录脚本开始的时间
initial_wait_time=$(date +%s)  # 初始等待时间开始

# 循环监控screen输出
while true; do
    # 获取当前时间
    current_time=$(date +%s)

    # 获取screen会话输出的内容并检查是否有"HTTP"字段
    # 使用screen -S <session_name> -X hardcopy <filename>将screen会话输出保存到文件
    screen -S "$SCREEN_NAME" -X hardcopy /tmp/screen_output.txt
    
    # 检查文件中是否包含"HTTP"字段
    if grep -q "http" /tmp/screen_output.txt; then
        echo "HTTP found, continuing to monitor."
        # 找到HTTP后重置初始等待时间
        initial_wait_time=$(date +%s)  # 重新计算初始等待时间
        start_time=$current_time       # 重置开始时间，用于计算 elapsed_time
    else
        # 计算 elapsed_time，超时判断
        elapsed_time=$((current_time - start_time))
        initial_elapsed_time=$((current_time - initial_wait_time))

        # 如果超过初始等待时间且没有找到HTTP，则退出循环
        if [ $initial_elapsed_time -ge $INITIAL_WAIT_TIME ]; then
            echo "No HTTP found in the initial period ($INITIAL_WAIT_TIME seconds), exiting."
            screen -S "$SCREEN_NAME" -X quit
            # 启动新命令
            $NEW_COMMAND &
            break
        fi
        
        # 如果3分钟没有HTTP字段
        if [ $elapsed_time -ge $TIMEOUT ]; then
            echo "No HTTP found for 3 minutes, killing the current process and starting a new one."
            # 杀死screen会话中的进程
            screen -S "$SCREEN_NAME" -X quit
            
            # 启动新命令
            $NEW_COMMAND &
            break
        fi
    fi
    
    # 每10秒检查一次
    sleep 10
done
