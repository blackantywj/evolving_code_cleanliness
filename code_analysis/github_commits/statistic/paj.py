from py4j.java_gateway import JavaGateway

# 连接到运行中的 Java Gateway 服务
gateway = JavaGateway()  # 默认连接本地的Gateway

# 获取 Java 类
java_parser_example = gateway.jvm.com.example.JavaCodeParser()

# Java 代码示例
java_code = """
import java.util.*;
public class Test {
    int x = 10;
    String name = "Alice";
    boolean isActive = true;
    List<String> items;
    double salary;
}
"""

# 调用 Java 方法提取变量名
variable_names = java_parser_example.extractVariableNames(java_code)

# 输出结果
print(variable_names)  # 输出: ['a', 'b', 'c', 'name', 'address', 'x', 'flag']
