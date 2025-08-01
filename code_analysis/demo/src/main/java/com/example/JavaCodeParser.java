package com.example;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.*;
import com.github.javaparser.ast.body.*;
import java.util.ArrayList;
import java.util.List;

public class JavaCodeParser {

    // 解析 Java 代码并提取变量名
    public String extractVariableNames(String javaCode) {
        System.out.println(javaCode);
        List<String> variableNames = new ArrayList<>();
        
        // 使用 JavaParser 来解析 Java 代码
        CompilationUnit cu = StaticJavaParser.parse(javaCode);
        
        // 遍历所有方法中的变量声明
        cu.findAll(VariableDeclarator.class).forEach(var -> {
            variableNames.add(var.getNameAsString());
        });
        // 将变量名用空格连接成一个字符串
        String result = String.join(" ", variableNames);
        System.out.println("Extracted Variable Names: " + result);  // 打印返回的字符串
        return result;  // 返回变量名字符串
    }
}
