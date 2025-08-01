package com.example;

import java.util.List;

// StartJavaParserGateway.java
import py4j.GatewayServer;

public class StartJavaParserGateway {
    public static void main(String[] args) {
        JavaCodeParser example = new JavaCodeParser();
                // 测试用 Java 代码
        String javaCode = """
            import java.util.*;
            public class Test {
                int x = 10;
                String name = "Alice";
                boolean isActive = true;
                List<String> items;
                double salary;
            }
        """;
        
        // 调用解析方法
        String variables = example.extractVariableNames(javaCode);
        
        // 打印变量名
        System.out.println("Extracted Variable Names: " + variables);
        GatewayServer server = new GatewayServer(example);
        server.start();  // 启动 Py4J Gateway 服务
        System.out.println("Gateway Server Started");
    }
}
