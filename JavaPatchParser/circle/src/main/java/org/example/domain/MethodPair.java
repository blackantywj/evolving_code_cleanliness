package org.example.domain;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.Stack;

import org.apache.commons.lang3.builder.EqualsBuilder;
import org.apache.commons.lang3.builder.HashCodeBuilder;
import org.eclipse.jdt.core.dom.ASTNode;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.example.HierarchicalActionSet;
import org.example.JavaCompareActions;
import org.example.circle.Circle;
import org.example.circle.MethodCircle;
import org.example.utils.Helper;

import lombok.Data;

@Data
public class MethodPair {
  private MethodDeclaration oldMethod;
  private MethodDeclaration newMethod;
  private List<HierarchicalActionSet> actionSetList = new ArrayList<>();
  private MethodCircle oldCircle;
  private MethodCircle newCircle;
  private List<String> oldArgsList;
  private List<String> newArgsList;
  private int oldArgs;
  private int newArgs;
  private int oldRows;
  private int newRows;
  private String oldSource;
  private String newSource;

  public MethodPair calcCircle() {
    oldCircle = new MethodCircle(oldMethod);
    newCircle = new MethodCircle(newMethod);
    return this;
  }

  public MethodPair calcArgs(JavaCompareActions jca) {
    oldArgs = jca.getOldUnit().getArgs(oldMethod);
    newArgs = jca.getNewUnit().getArgs(newMethod);
    return this;
  }

  public MethodPair calcOldArgsList(JavaCompareActions jca) {
    oldArgsList = jca.getOldUnit().getArgsList(oldMethod);
    // newArgsList = jca.getNewUnit().getArgsList(newMethod);
    return this;
  }

  public MethodPair calcNewArgsList(JavaCompareActions jca) {
    // oldArgsList = jca.getOldUnit().getArgsList(oldMethod);
    newArgsList = jca.getNewUnit().getArgsList(newMethod);
    return this;
  }

  public MethodPair calcRows(JavaCompareActions jca) {
    oldRows = jca.getOldUnit().getRows(oldMethod);
    newRows = jca.getNewUnit().getRows(newMethod);
    return this;
  }

  public String getOldMethodCode() {
    return extractMethodSource(oldMethod, oldSource);
  }
  public String getNewMethodCode() {
    return extractMethodSource(newMethod, newSource);
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) return true;
    if (o == null || getClass() != o.getClass()) return false;
    MethodPair that = (MethodPair) o;
    return new EqualsBuilder().append(oldMethod, that.oldMethod).append(newMethod, that.newMethod).isEquals();
  }

  @Override
  public int hashCode() {
    return new HashCodeBuilder(17, 37).append(oldMethod).append(newMethod).toHashCode();
  }

  public String getMethodName() {
    if (newMethod != null) {
      return newMethod.getName().toString();
    } else if (oldMethod != null) {
      return oldMethod.getName().toString();
    }
    return null;
  }

  public String getMethodSign() {
    if (newMethod != null) {
      return Helper.getMethodSign(newMethod);
    } else if (oldMethod != null) {
      return Helper.getMethodSign(oldMethod);
    }
    return null;
  }

  public String getNewMethodName() {
    if (newMethod != null) {
      return newMethod.getName().toString();
    } 
    return null;
  }

  public String getOldMethodName() {
    if (oldMethod != null) {
      return oldMethod.getName().toString();
    }
    return null;
  }  

  private static class CirclePair {
    private final Circle oldCircle;
    private final Circle newCircle;
    private final HierarchicalActionSet actionSet;

    private CirclePair(Circle oldCircle, Circle newCircle, HierarchicalActionSet actionSet) {
      this.oldCircle = oldCircle;
      this.newCircle = newCircle;
      this.actionSet = actionSet;
    }

    public String getActionName() {
      return actionSet.getAction().getName();
    }

    public String getAstNodeType() {
      String astNodeType = actionSet.getAstNodeType();
      if (oldCircle.getAstNode() != null) {
        astNodeType = oldCircle.getAstNodeType();
      } else if (newCircle.getAstNode() != null) {
        astNodeType = newCircle.getAstNodeType();
      }
      return astNodeType;
    }

    @Override
    public boolean equals(Object o) {
      if (this == o) return true;

      if (o == null || getClass() != o.getClass()) return false;

      CirclePair that = (CirclePair) o;

      return new EqualsBuilder().append(oldCircle, that.oldCircle).append(newCircle, that.newCircle).isEquals();
    }

    @Override
    public int hashCode() {
      return new HashCodeBuilder(17, 37).append(oldCircle).append(newCircle).toHashCode();
    }
  }

  public ChangeMap createChangeMap() {
    ChangeMap changeMap = new ChangeMap();
    Map<ASTNode, Circle> circleMap = new HashMap<>();
    circleMap.putAll(oldCircle.listValidMap());
    circleMap.putAll(newCircle.listValidMap());
    Stack<HierarchicalActionSet> stack = new Stack<>();
    stack.addAll(actionSetList);
    Set<CirclePair> pairs = new HashSet<>();
    while (!stack.isEmpty()) {
      HierarchicalActionSet actionSet = stack.pop();
      Circle oldCircle = actionSet.getOldTreeWrapper().map(t -> t.getCircle(circleMap)).orElse(Circle.empty());
      Circle newCircle = actionSet.getNewTreeWrapper().map(t -> t.getCircle(circleMap)).orElse(Circle.empty());
      if (oldCircle.getCircle() != newCircle.getCircle()) {
        CirclePair pair = new CirclePair(oldCircle, newCircle, actionSet);
        if (!pairs.contains(pair)) {
          pairs.add(pair);
        }
      }
      stack.addAll(actionSet.getSubActions());
    }
    for (CirclePair pair : pairs) {
      changeMap.addOne(pair.getAstNodeType(), pair.getActionName());
    }
    return changeMap;
  }

    /**
   * 从 MethodDeclaration 切出源码（包含注解/签名/方法体等）。
   * 适用于离线解析：必须传入整份文件源码 fallbackSource。
   */
  private String extractMethodSource(MethodDeclaration md, String fallbackSource) {
    if (md == null) return null;
    if (fallbackSource == null) return null;

    int start = md.getStartPosition();
    int len = md.getLength();

    if (start < 0 || len <= 0) return null;

    int end = start + len;
    return safeSubstring(fallbackSource, start, end);
  }

  /** 防御性 substring，避免越界/空指针 */
  private String safeSubstring(String s, int begin, int end) {
    if (s == null) return null;
    int n = s.length();
    int b = Math.max(0, Math.min(begin, n));
    int e = Math.max(0, Math.min(end, n));
    if (e <= b) return "";
    return s.substring(b, e);
  }
}
