package org.example.circle;

import lombok.Getter;
import org.eclipse.jdt.core.dom.ASTNode;
import org.example.utils.Helper;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Function;

@Getter
public class Circle {
  protected final ASTNode astNode;
  protected String astNodeType;
  protected int circle = 0;
  protected List<Circle> children = new ArrayList<>();

  public Circle(ASTNode astNode) {
    this.astNode = astNode;
    if (astNode != null) {
      this.astNodeType = astNode.getClass().getSimpleName();
    }
  }

  public static Circle empty() {
    return new Circle(null);
  }

  protected <T> int countIf(Class<T> clazz, Function<T, Integer> function) {
    if (Helper.isInstanceOf(astNode.getClass(), clazz)) {
      return function.apply((T) astNode);
    }
    return 0;
  }

  public int getDeepCircle() {
    int circle = this.circle;
    for (Circle c : children) {
      circle += c.getDeepCircle();
    }
    return circle;
  }

  public void appendStatements(List statements) {
    if (statements == null) {
      return;
    }
    for (Object node : statements) {
      if (node instanceof ASTNode) {
        appendStatement((ASTNode) node);
      }
    }
  }

  public StatementCircle appendStatement(ASTNode node) {
    if (node == null) {
      return null;
    }
    StatementCircle circle = new StatementCircle(node);
    children.add(circle);
    return circle;
  }

  public Map<ASTNode, Circle> listValidMap() {
    Map<ASTNode, Circle> map = new HashMap<>();
    if (circle > 0) {
      map.put(astNode, this);
    }
    for (Circle c : children) {
      map.putAll(c.listValidMap());
    }
    return map;
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("节点类型: ").append(astNode == null ? null : astNode.getClass().getSimpleName());
    sb.append(", 自己的圈: ").append(getCircle());
    sb.append(", 所有的圈: ").append(getDeepCircle());
    return sb.toString();
  }


}
