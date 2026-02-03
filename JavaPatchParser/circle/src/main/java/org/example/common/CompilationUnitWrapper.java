package org.example.common;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;
import java.util.stream.Collectors;

import org.apache.commons.collections4.CollectionUtils;
import org.eclipse.jdt.core.dom.ASTNode;
import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.eclipse.jdt.core.dom.SingleVariableDeclaration;
import org.eclipse.jdt.core.dom.StructuralPropertyDescriptor;
import org.eclipse.jdt.core.dom.TryStatement;
import org.eclipse.jdt.core.dom.TypeDeclaration;
import org.example.utils.Helper;

import com.github.gumtreediff.tree.ITree;

import lombok.Getter;

/**
 * @Author youhl002
 * @Date 2023/3/2 20:19
 */

@Getter
public class CompilationUnitWrapper {
  private final ContentWrapper wrapper;
  private final ITree tree;
  private final CompilationUnit unit;
  private final List<MethodDeclaration> methodDeclarations = new ArrayList<>();
  private final String source;

  public CompilationUnitWrapper(String content, ITree tree) {
    this.source = content;                 // ✅保存原始源码
    this.wrapper = ContentWrapper.create(content);
    this.tree = tree;
    this.unit = (CompilationUnit) tree.getAttach();
    Helper.deepVisit(Arrays.asList(unit), Helper::getChildren, node -> {
      if (node instanceof MethodDeclaration) {
        methodDeclarations.add((MethodDeclaration) node);
      }
    });
  }

  public int getRows() {
    return wrapper.getRows();
  }

  private Segment creatSegment(ASTNode astNode) {
    return Segment.create(wrapper, astNode.getStartPosition(), astNode.getLength());
  }

  public MethodDeclaration findMethodDeclaration(Segment segment, MethodDeclaration others) {
    List<MethodDeclaration> mds = methodDeclarations.stream().filter(md -> creatSegment(md).isOverlap(segment)).collect(Collectors.toList());
    if (CollectionUtils.isEmpty(mds)) { // 未搜索到代码段
      return null;
    } else if (others == null) { // 未找到比对函数
      return mds.get(0);
    }
    
    // 1. 函数签名完全匹配,只可能出现一个
    List<MethodDeclaration> founds = mds.stream().filter(m -> Helper.getMethodSign(m).equals(Helper.getMethodSign(others))).collect(Collectors.toList());
    if (founds.size() > 0) return founds.get(0);

    // 2. 函数名匹配,离得最近的函数
    founds = mds.stream().filter(m -> Helper.getMethodName(m).equals(Helper.getMethodName(others))).collect(Collectors.toList());
    if (founds.size() > 0) {
      Collections.sort(founds, (o1, o2) -> {
        // 比对函数开始位置
        int r1 = Math.abs(o1.getStartPosition() - others.getStartPosition());
        int r2 = Math.abs(o2.getStartPosition() - others.getStartPosition());
        int res = Integer.compare(r1, r2);
        if (res == 0) {
          // 比对函数末尾位置
          r1 = Math.abs(o1.getStartPosition() + o1.getLength() - others.getStartPosition() - others.getLength());
          r2 = Math.abs(o2.getStartPosition() + o2.getLength() - others.getStartPosition() - others.getLength());
          res = Integer.compare(r1, r2);
        }
        return res;
      });
      return founds.get(0);
    }
    return null;
  }

  public int getRows(MethodDeclaration method) {
    if (method == null) {
      return 0;
    }
    Segment segment = creatSegment(method);
    return segment.getEndRow() - segment.getStartRow() + 1;

  }

  public int getArgs(MethodDeclaration method) {
    if (method == null) {
      return 0;
    }
    return method.parameters().size();
  }

  public List<String> getArgsList(MethodDeclaration method) {
    if (method == null) {
      return null;
    }
    List<String> parameterNames = new ArrayList<>();
    List<?> parameters = method.parameters();

    for (Object param : parameters) {
        if (param instanceof SingleVariableDeclaration) {
            SingleVariableDeclaration variable = (SingleVariableDeclaration) param;
            parameterNames.add(variable.getName().toString());
        }
    }
    return parameterNames;
  }
  
  public int getTryCatchNum() {
      // // 创建 ASTParser
      // ASTParser parser = ASTParser.newParser(AST.JLS8);
      // parser.setSource(unit.toCharArray());
      // parser.setKind(ASTParser.K_COMPILATION_UNIT);

      // // 解析源码为 CompilationUnit
      // CompilationUnit cu = (CompilationUnit) parser.createAST(null);

      // 创建一个计数器
              // 使用队列进行非递归遍历
      Queue<ASTNode> queue = new LinkedList<>();
      queue.add(unit);

      // 遍历 AST，查找 TryStatement
        int tryCatchCount = 0;

        while (!queue.isEmpty()) {
            ASTNode current = queue.poll();

            // 检查是否是 TryStatement 节点
            if (current instanceof TryStatement) {
                tryCatchCount++;
            }

            // 将当前节点的子节点加入队列
            for (Object child : current.structuralPropertiesForType()) {
                StructuralPropertyDescriptor descriptor = (StructuralPropertyDescriptor) child;
                Object value = current.getStructuralProperty(descriptor);

                if (value instanceof ASTNode) {
                    queue.add((ASTNode) value);
                } else if (value instanceof List) {
                    for (Object item : (List<?>) value) {
                        if (item instanceof ASTNode) {
                            queue.add((ASTNode) item);
                        }
                    }
                }
            }
        }

        return tryCatchCount;
    }

    public List<String> getClassNames() {

      // 用于存储类名
      List<String> classNames = new ArrayList<>();

      // 使用队列进行非递归遍历
      Queue<ASTNode> queue = new LinkedList<>();
      queue.add(unit);

      while (!queue.isEmpty()) {
          ASTNode currentNode = queue.poll();

          // 检查是否为 TypeDeclaration 节点
          if (currentNode instanceof TypeDeclaration) {
              TypeDeclaration typeDeclaration = (TypeDeclaration) currentNode;
              classNames.add(typeDeclaration.getName().toString());
          }

          // 将当前节点的子节点加入队列
          for (Object property : currentNode.structuralPropertiesForType()) {
              StructuralPropertyDescriptor descriptor = (StructuralPropertyDescriptor) property;
              Object value = currentNode.getStructuralProperty(descriptor);

              if (value instanceof ASTNode) {
                  queue.add((ASTNode) value);
              } else if (value instanceof List) {
                  for (Object child : (List<?>) value) {
                      if (child instanceof ASTNode) {
                          queue.add((ASTNode) child);
                      }
                  }
              }
          }
      }

      return classNames;
  }
}