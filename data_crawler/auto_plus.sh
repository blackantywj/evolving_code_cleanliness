#!/bin/bash
# "google/guava" "google/gson" "google/ExoPlayer*" "google/dagger" "google/guice*" "google/auto" "google/tsunami-security-scanner" "google/android-classyshark-" "google/closure-compiler" "google/agera*"
# "apache/dubbo" "apache/kafka" "apache/incubator-seata" "apache/flink" "apache/skywalking" "apache/rocketmq" "apache/shardingsphere" "apache/hadoop" "apache/pulsar" "apache/druid" "apache/zookeeper"
# 定义要传入search.py的参数列表
# "google/error-prone" "google/nomulus"
PARAM_LIST=("spring-projects/spring-boot" "spring-projects/spring-framework" "spring-projects/spring-security" "spring-projects/spring-authorization-server" "spring-projects/spring-ai" "spring-projects/spring-data-jpa" "spring-projects/spring-kafka" "spring-projects/spring-batch" "spring-projects/spring-session" "spring-projects/spring-data-mongodb")
# spring-projects/spring-boot" "spring-projects/spring-framework" "spring-projects/spring-security" "spring-projects/spring-authorization-server" "spring-projects/spring-ai" "spring-projects/spring-data-jpa" "spring-projects/spring-kafka" "spring-projects/spring-batch" "spring-projects/spring-session" "spring-projects/spring-data-mongodb)  # 请根据实际情况修改参数列表
# 替代 error-prone nomulus j2cl
NEW_COMMAND="python search.py"
CONDA_ENV="ifcap"  # 替换为您的conda环境名称

# 监控时间阈值（以秒为单位，3分钟 = 180秒）
TIMEOUT=80
# 初始等待时间阈值（避免死循环，如果一开始就没有HTTP字段，等到超过初始等待时间就退出）
INITIAL_WAIT_TIME=60  # 初始等待时间设定为60秒

# 函数：监控screen会话直到没有HTTP字段
monitor_screen() {
    local SCREEN_NAME=$1
    local PARAM=$2
    local START_TIME
    local CURRENT_TIME
    local ELAPSED_TIME
    local INITIAL_ELAPSED_TIME

    start_time=$(date +%s)        # 记录脚本开始的时间
    initial_wait_time=$(date +%s) # 初始等待时间开始

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
                return 0  # 返回1表示没有HTTP字段，任务失败
            fi
            
            # 如果3分钟没有HTTP字段
            if [ $elapsed_time -ge $TIMEOUT ]; then
                echo "No HTTP found for 3 minutes, killing the current process and starting a new one."
                # 杀死screen会话中的进程
                screen -S "$SCREEN_NAME" -X quit

                # 启动新命令
                # screen -dmS "$SCREEN_NAME" bash -c "source ~/anaconda3/etc/profile.d/conda.sh && conda activate $CONDA_ENV && $NEW_COMMAND $PARAM"
                return 0 # 返回0表示成功，继续执行
            fi
        fi
        
        # 每10秒检查一次
        sleep 10
    done
}

# 遍历 PARAM_LIST 中的每个参数
for PARAM in "${PARAM_LIST[@]}"; do
    # 对每个 PARAM，先执行 -r PARAM --sf 1 然后执行 -r PARAM --df 1
    # 1. 执行 -r PARAM --sf 1
    echo "Starting -r $PARAM -sf 1"
    IFS="/" read -r part1 part2 <<< "$PARAM"
    sf_screen_name="sf$part2"
    screen -dmS "$sf_screen_name" bash -i -c "source ~/anaconda3/etc/profile.d/conda.sh && conda activate $CONDA_ENV && $NEW_COMMAND -r $PARAM -sf 1"
    if ! monitor_screen "$sf_screen_name" "-r $PARAM -sf 1"; then
        echo "-r $PARAM --sf 1 failed, exiting."
        exit 1  # 如果 -r PARAM --sf 1 执行失败，则退出
    fi

    # 2. 执行 -r PARAM --df 1
    echo "Starting -r $PARAM -df 1"
    df_screen_name="df$part2"
    screen -dmS "$df_screen_name" bash -c "source ~/anaconda3/etc/profile.d/conda.sh && conda activate $CONDA_ENV && $NEW_COMMAND -r $PARAM -df 1"
    if ! monitor_screen "$df_screen_name" "-r $PARAM -df 1"; then
        echo "-r $PARAM --df 1 failed, exiting."
        exit 1  # 如果 -r PARAM --df 1 执行失败，则退出
    fi

done

echo "All tasks completed successfully."



# #!/bin/bash

# # 定义要传入search.py的参数列表
# PARAM_LIST=("apache/dubbo" "apache/kafka" "apache/flink", "apache/skywalking", "apache/rocketmq", "apache/shardingsphere", "apache/hadoop", "apache/pulsar", "apache/druid")  # 请根据实际情况修改参数列表
# NEW_COMMAND="python search.py -r"

# # 监控时间阈值（以秒为单位，3分钟 = 180秒）
# TIMEOUT=180
# # 初始等待时间阈值（避免死循环，如果一开始就没有HTTP字段，等到超过初始等待时间就退出）
# INITIAL_WAIT_TIME=60  # 初始等待时间设定为60秒

# # 循环处理每个参数
# for PARAM in "${PARAM_LIST[@]}"; do
#     SCREEN_NAME="${PARAM#*/}"  # 每个参数对应一个新的screen会话名称
#     start_time=$(date +%s)        # 记录脚本开始的时间
#     initial_wait_time=$(date +%s) # 初始等待时间开始
    
#     # 启动一个新的screen会话并运行search.py
#     screen -dmS "$SCREEN_NAME" bash -c "source ~/anaconda3/etc/profile.d/conda.sh && conda activate cap && $NEW_COMMAND $PARAM"

#     # 初始化超时计数器
#     while true; do
#         # 获取当前时间
#         current_time=$(date +%s)

#         # 获取screen会话输出的内容并检查是否有"HTTP"字段
#         # 使用screen -S <session_name> -X hardcopy <filename>将screen会话输出保存到文件
#         screen -S "$SCREEN_NAME" -X hardcopy /tmp/screen_output.txt

#         # 检查文件中是否包含"HTTP"字段
#         if grep -q "http" /tmp/screen_output.txt; then
#             echo "HTTP found, continuing to monitor."
#             # 找到HTTP后重置初始等待时间
#             initial_wait_time=$(date +%s)  # 重新计算初始等待时间
#             start_time=$current_time       # 重置开始时间，用于计算 elapsed_time
#         else
#             # 计算 elapsed_time，超时判断
#             elapsed_time=$((current_time - start_time))
#             initial_elapsed_time=$((current_time - initial_wait_time))

#             # 如果超过初始等待时间且没有找到HTTP，则退出循环
#             if [ $initial_elapsed_time -ge $INITIAL_WAIT_TIME ]; then
#                 echo "No HTTP found in the initial period ($INITIAL_WAIT_TIME seconds), exiting."
#                 screen -S "$SCREEN_NAME" -X quit
#                 break
#             fi
            
#             # 如果3分钟没有HTTP字段
#             if [ $elapsed_time -ge $TIMEOUT ]; then
#                 echo "No HTTP found for 3 minutes, killing the current process and starting a new one."
#                 # 杀死screen会话中的进程
#                 screen -S "$SCREEN_NAME" -X quit

#                 # 启动新命令
#                 screen -dmS "$SCREEN_NAME" bash -c "$NEW_COMMAND $PARAM"
#                 break
#             fi
#         fi
        
#         # 每10秒检查一次
#         sleep 10
#     done
# done
