package org.example.circle;

import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.eclipse.jdt.core.dom.*;
import org.example.utils.Helper;

import java.util.*;

@Slf4j
public class StatementCircle extends Circle {


  public StatementCircle(ASTNode node) {
    super(node);
    this.init();
  }

  private void init() {
    circle += countIf(IfStatement.class, this::calcIfStatement); // if
    circle += countIf(WhileStatement.class, this::calcWhileStatement); // while
    circle += countIf(DoStatement.class, this::calcDoStatement); // do
    circle += countIf(ForStatement.class, this::calcForStatement); // for
    circle += countIf(ConditionalExpression.class, this::calcConditionalExpression); // 三元表达式
    circle += countIf(SwitchStatement.class, this::calcSwitchStatement); // switch
    circle += countIf(SwitchCase.class, this::calcSwitchCase); // case
    circle += countIf(EnhancedForStatement.class, this::calcEnhancedForStatement); // 增强for循环
    circle += countIf(TryStatement.class, this::calcTryStatement); // try
    circle += countIf(CatchClause.class, this::calcCatchClause); // catch
    circle += countIf(VariableDeclarationStatement.class, this::calcVariableDeclarationStatement); //
    circle += countIf(VariableDeclarationExpression.class, this::calcVariableDeclarationExpression);
    // 处理代码块
    circle += countIf(ExpressionStatement.class, this::calcExpressionStatement);
    circle += countIf(Block.class, this::calcBlock);
  }

  private int calcVariableDeclarationExpression(VariableDeclarationExpression vde) {
    int circle = 0;
    for (Object o : vde.fragments()) {
      if (o instanceof VariableDeclarationFragment) {
        VariableDeclarationFragment real = (VariableDeclarationFragment) o;
        circle += calcInNormal(real.getInitializer());
      }
    }
    return circle;
  }

  private int calcVariableDeclarationStatement(VariableDeclarationStatement vds) {
    int circle = 0;
    for (Object o : vds.fragments()) {
      if (o instanceof VariableDeclarationFragment) {
        VariableDeclarationFragment real = (VariableDeclarationFragment) o;
        circle += calcInNormal(real.getInitializer());
      }
    }
    return circle;
  }

  private int calcExpressionStatement(ExpressionStatement es) {
    return calcInNormal(es.getExpression());
  }

  private int calcBlock(Block block) {
    int circle = 0;
    ASTNode parent = block.getParent();
    if (parent instanceof IfStatement && ((IfStatement) parent).getElseStatement() == block) { // 处理 else
      circle = 1;
      astNodeType = "ElseStatement";
    }
    appendStatements(block.statements());
    return circle;
  }

  private int calcEnhancedForStatement(EnhancedForStatement efs) {
    int circle = 1;
    appendStatement(efs.getBody());
    return circle;
  }

  private int calcCatchClause(CatchClause cc) {
    appendStatement(cc.getBody());
    return 1;
  }

  private int calcTryStatement(TryStatement ts) {
    appendStatements(ts.resources());
    appendStatement(ts.getBody());
    appendStatements(ts.catchClauses());
    if (ts.getFinally() != null) {
      // 主动将finally 对应的圈设置为1, Body默认为0,需要主动修改
      appendStatement(ts.getFinally());
    }
    return 1;
  }

  private int calcSwitchCase(SwitchCase sc) { // case "a": , default :
    return 1;
  }

  private int calcSwitchStatement(SwitchStatement ss) {
    int circle = calcInNormal(ss.getExpression());
    appendStatements(ss.statements());
    return circle;
  }

  private int calcForStatement(ForStatement fors) {
    int circle = 1;
    if (fors.getExpression() != null) { // 防止出现 for(;;) 死循环的情况
      circle = calcInCondition(fors.getExpression());
    }
    appendStatement(fors.getBody());
    return circle;
  }

  private int calcDoStatement(DoStatement dos) {
    int circle = calcInCondition(dos.getExpression());
    appendStatement(dos.getBody());
    return circle;
  }

  private int calcWhileStatement(WhileStatement ws) {
    int circle = calcInCondition(ws.getExpression());
    appendStatement(ws.getBody());
    return circle;
  }

  private int calcIfStatement(IfStatement ifs) {
    int circle = calcInCondition(ifs.getExpression());
    appendStatement(ifs.getThenStatement());
    if (ifs.getElseStatement() != null) {
      appendStatement(ifs.getElseStatement());
    }
    return circle;
  }

  private int calcInCondition(Expression expression) { // 判断条件中的表达式
    int circle = 0;
    if (expression instanceof BooleanLiteral || expression instanceof SimpleName // if(true) 或者 变量
        || expression instanceof InstanceofExpression // 类型检测
        || expression instanceof FieldAccess // 字段变量
        || expression instanceof QualifiedName // 常量
    ) {
      circle = 1;
    } else if (expression instanceof InfixExpression) { // 二元表达式
      circle = calcInfixExpression((InfixExpression) expression);
    } else if (expression instanceof MethodInvocation) { // 函数调用
      circle = 1 + calcInNormal(expression);
    } else if (expression instanceof SuperMethodInvocation) { // 父函数调用
      circle = 1 + calcInNormal(expression);
    } else if (expression instanceof ConditionalExpression) { // 三元表达式
      circle = 1 + calcConditionalExpression((ConditionalExpression) expression);
    } else if (expression instanceof PrefixExpression) { // !!pt.equals(classLoader.loadClass(pt.getName()))
      circle = calcInCondition(((PrefixExpression) expression).getOperand());
    } else if (expression instanceof ParenthesizedExpression) { // 括号表达式  (...)
      circle = calcInCondition(((ParenthesizedExpression) expression).getExpression());
    } else if (expression instanceof CastExpression) { // 强制转换表达式 cast
      circle = calcInCondition(((CastExpression) expression).getExpression());
    } else {
      log.warn("未知类型 => \n" + StringUtils.abbreviate(Objects.toString(expression), 200));
//      throw new RuntimeException("未知类型 => " + expression);
    }
    return circle;
  }


  private int calcInNormal(Expression expression) { // 非判断条件中的表达式,只考虑三元调用的情况
    Stack<Expression> stack = new Stack<>();
    stack.push(expression);
    int circle = 0;
    while (!stack.isEmpty()) {
      Expression exp = stack.pop();
      if (exp instanceof ConditionalExpression) { // 三元表达式
        circle += calcConditionalExpression((ConditionalExpression) exp);
      } else {
        for (ASTNode node : Helper.getChildren(exp)) {
          if (node instanceof Expression) {
            stack.add((Expression) node);
          }
        }
      }
    }
    return circle;
  }

  private static Set<String> LOGIC = new HashSet<>(Arrays.asList(
      "&", "&&", "|", "||"
  ));

  private int calcInfixExpression(InfixExpression ie) {
    String operator = ie.getOperator().toString();
    if (LOGIC.contains(operator)) {
      return calcInCondition(ie.getLeftOperand()) + calcInCondition(ie.getRightOperand());
    }
    return calcInNormal(ie.getLeftOperand()) + calcInNormal(ie.getRightOperand()) + 1;
  }


  private int calcConditionalExpression(ConditionalExpression ce) {
    int c1 = calcInCondition(ce.getExpression());
    int c2 = calcInNormal(ce.getThenExpression());
    int c3 = calcInNormal(ce.getElseExpression());
    return c1 + c2 + c3 + 1;
  }
}
