package org.example.utils;

import com.alibaba.fastjson.JSON;
import com.github.gumtreediff.tree.ITree;
import com.github.gumtreediff.tree.TreeContext;
import com.mongodb.MongoClient;
import com.mongodb.MongoClientOptions;
import com.mongodb.MongoCredential;
import com.mongodb.ServerAddress;
import com.mongodb.client.DistinctIterable;
import edu.lu.uni.serval.gen.jdt.exp.ExpJdtTreeGenerator;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections4.CollectionUtils;
import org.apache.commons.lang3.StringUtils;
import org.bson.Document;
import org.eclipse.jdt.core.dom.*;
import org.example.HierarchicalActionSet;
import org.example.common.ContentWrapper;

import java.io.File;
import java.io.IOException;
import java.sql.SQLException;
import java.util.*;
import java.util.function.Consumer;
import java.util.function.Function;

@Slf4j
public class Helper {

  public static boolean isNotFound(String content) {
    return content == null || "404".equalsIgnoreCase(content) || content.isEmpty();
  }

  public static <T> void deepVisit(List<T> res, Function<T, List<T>> childrenFunc, Consumer<T> consumer) {
    if (CollectionUtils.isNotEmpty(res)) {
      for (T t : res) {
        if (consumer != null) {
          consumer.accept(t);
        }
        if (childrenFunc != null) {
          deepVisit(childrenFunc.apply(t), childrenFunc, consumer);
        }
      }
    }
  }


  public static void main(String[] args) {
    String content = "12\n\n\3";
    ContentWrapper cw = ContentWrapper.create(content);
    System.out.println(cw.getLine(-1));
    System.out.println(cw.getLine(0));
    System.out.println(cw.getLine(1));
    System.out.println(cw.getLine(2));
    System.out.println(cw.getLine(3));
    System.out.println(cw.getLine(4));
    System.out.println(cw.getLine(5));
  }


  public static List<ASTNode> getChildren(ASTNode node) {
    return getChildren0(node);
  }

  public static List<ASTNode> getChildren0(ASTNode node) {
    List<ASTNode> res = new ArrayList<>();
    if (node == null) {
    } else if (node instanceof CompilationUnit) { // 源码文件
      CompilationUnit real = (CompilationUnit) node;
      res.addAll(real.types());
    } else if (node instanceof TypeDeclaration) { // 单个类文件
      TypeDeclaration real = (TypeDeclaration) node;
      res.addAll(real.bodyDeclarations());
    } else if (node instanceof EnumDeclaration) { // 枚举
      EnumDeclaration real = (EnumDeclaration) node;
      res.addAll(real.bodyDeclarations());
    } else if (node instanceof AnnotationTypeDeclaration) { // 元注解 public @interface Cmd {}
      AnnotationTypeDeclaration real = (AnnotationTypeDeclaration) node;
      res.addAll(real.bodyDeclarations());
    } else if (node instanceof TypeDeclarationStatement) {// 方法体内部类
      TypeDeclarationStatement real = (TypeDeclarationStatement) node;
      res.add(real.getDeclaration());
    } else if (node instanceof FieldDeclaration) { // 字段 private ModuleConfigManager moduleConfigManager;
      res.addAll(((FieldDeclaration) node).fragments());
    } else if (node instanceof MethodDeclaration) { // 方法 public void init(){......}
      res.add(((MethodDeclaration) node).getBody());
    } else if (node instanceof Block) { // 代码块 {......}
      res.addAll(((Block) node).statements());
    } else if (node instanceof VariableDeclarationStatement) { // 局部变量 ApplicationModel applicationModel=ApplicationModel.defaultModel();
      VariableDeclarationStatement real = (VariableDeclarationStatement) node;
      res.addAll(real.modifiers());
      res.addAll(real.fragments());
    } else if (node instanceof VariableDeclarationExpression) { // for循环里面的变量定义 int i=0
      VariableDeclarationExpression real = (VariableDeclarationExpression) node;
      res.addAll(real.fragments());
    } else if (node instanceof VariableDeclarationFragment) { // 局部变量部分 applicationModel=ApplicationModel.defaultModel();
      res.addAll(((VariableDeclarationFragment) node).extraDimensions());
    } else if (node instanceof FieldAccess) { // 访问对象字段 TestService.class.getMethods().length
      res.add(((FieldAccess) node).getExpression());
    } else if (node instanceof ExpressionStatement) { // 方法调用? builder.append('a');
      res.add(((ExpressionStatement) node).getExpression());
    } else if (node instanceof Assignment) { // 字段语句 parameters=new HashMap<>()
      Assignment assignment = (Assignment) node;
      res.addAll(Arrays.asList(assignment.getLeftHandSide(), assignment.getRightHandSide()));
    } else if (node instanceof ClassInstanceCreation) { // 对象创建 new TopicIdPartition(uuid,replica & REPLICA_MASK)
      ClassInstanceCreation real = (ClassInstanceCreation) node;
      res.addAll(real.typeArguments());
      res.addAll(real.arguments());
    } else if (node instanceof ConstructorInvocation) { // this(...)
      ConstructorInvocation real = (ConstructorInvocation) node;
      res.addAll(real.typeArguments());
      res.addAll(real.arguments());
    } else if (node instanceof SuperConstructorInvocation) { // super(...)
      SuperConstructorInvocation real = (SuperConstructorInvocation) node;
      res.addAll(real.typeArguments());
      res.addAll(real.arguments());
    } else if (node instanceof SuperMethodInvocation) { // super.xx()
      SuperMethodInvocation real = (SuperMethodInvocation) node;
      res.addAll(real.typeArguments());
      res.addAll(real.arguments());
    } else if (node instanceof ArrayCreation) { // new int[1]
      ArrayCreation real = (ArrayCreation) node;
      res.addAll(real.dimensions());
    } else if (node instanceof ArrayAccess) { // newPartitions[newPartitions.length - 1]
      ArrayAccess real = (ArrayAccess) node;
      res.add(real.getArray());
      res.add(real.getIndex());
    } else if (node instanceof ArrayInitializer) { // {"var31","var32"}
      ArrayInitializer real = (ArrayInitializer) node;
      res.addAll(real.expressions());
    } else if (node instanceof ThrowStatement) { // throw new NoSuchElementException();
      ThrowStatement real = (ThrowStatement) node;
      res.add(real.getExpression());
    } else if (node instanceof MethodInvocation) {
      MethodInvocation mi = (MethodInvocation) node;
      res.add(mi.getExpression());
      res.addAll(mi.typeArguments());
      res.addAll(mi.arguments());
    } else if (node instanceof IfStatement) {
      IfStatement real = (IfStatement) node;
      res.add(real.getExpression());
      res.add(real.getThenStatement());
      res.add(real.getElseStatement());
    } else if (node instanceof SwitchStatement) { // switch
      SwitchStatement real = (SwitchStatement) node;
      res.add(real.getExpression());
      res.addAll(real.statements());
    } else if (node instanceof SwitchCase) { // case
      SwitchCase real = (SwitchCase) node;
      res.add(real.getExpression());
    } else if (node instanceof ForStatement) { // for (int i=0; i < partitions.length; i++) { ... }
      ForStatement real = (ForStatement) node;
      res.addAll(real.initializers());
      res.add(real.getExpression());
      res.addAll(real.updaters());
      res.add(real.getBody());
    } else if (node instanceof EnhancedForStatement) { // for (T t :list) { ... }
      EnhancedForStatement real = (EnhancedForStatement) node;
      res.add(real.getParameter());
      res.add(real.getExpression());
      res.add(real.getBody());
    } else if (node instanceof WhileStatement) { // while(){...}
      WhileStatement real = (WhileStatement) node;
      res.add(real.getExpression());
      res.add(real.getBody());
    } else if (node instanceof DoStatement) {// do{...}while()
      DoStatement real = (DoStatement) node;
      res.add(real.getExpression());
      res.add(real.getBody());
    } else if (node instanceof ParenthesizedExpression) { // 括号 (!leaderOnly)
      ParenthesizedExpression real = (ParenthesizedExpression) node;
      res.add(real.getExpression());
    } else if (node instanceof CastExpression) { // cast 符号
      CastExpression real = (CastExpression) node;
      res.add(real.getExpression());
    } else if (node instanceof PostfixExpression) { // j++
      PostfixExpression real = (PostfixExpression) node;
      res.add(real.getOperand());
    } else if (node instanceof PrefixExpression) { // !iterator.hasNext()
      PrefixExpression real = (PrefixExpression) node;
      res.add(real.getOperand());
    } else if (node instanceof InfixExpression) { // 二元表达式
      InfixExpression real = (InfixExpression) node;
      res.add(real.getLeftOperand());
      res.add(real.getRightOperand());
      res.addAll(real.extendedOperands());
    } else if (node instanceof LambdaExpression) { // lambda
      LambdaExpression real = (LambdaExpression) node;
      res.addAll(real.parameters());
      res.add(real.getBody());
    } else if (node instanceof ConditionalExpression) { // 三元表达式 isLeader ? partition | LEADER_FLAG : partition
      ConditionalExpression real = (ConditionalExpression) node;
      res.add(real.getExpression());
      res.add(real.getThenExpression());
      res.add(real.getElseExpression());
    } else if (node instanceof ReturnStatement) { // return
      ReturnStatement real = (ReturnStatement) node;
      res.add(real.getExpression());
    } else if (node instanceof LabeledStatement) { // loop: ...
      LabeledStatement real = (LabeledStatement) node;
      res.add(real.getBody());
    } else if (node instanceof TryStatement) { // try
      TryStatement real = (TryStatement) node;
      res.addAll(real.resources());
      res.add(real.getBody());
      res.addAll(real.catchClauses());
      res.add(real.getFinally());
    } else if (node instanceof CatchClause) { // catch
      CatchClause real = (CatchClause) node;
      res.add(real.getException());
      res.add(real.getBody());
    } else if (node instanceof SynchronizedStatement) { // synchronized (this.requestsWrite) {......}
      SynchronizedStatement real = (SynchronizedStatement) node;
      res.add(real.getExpression());
      res.add(real.getBody());
    } else if (node instanceof Initializer) { // static{}
      Initializer real = (Initializer) node;
      res.add(real.getBody());
    } else if (node instanceof ThisExpression
        || node instanceof SimpleName || node instanceof SimpleType || node instanceof QualifiedName
        || node instanceof NullLiteral || node instanceof NumberLiteral || node instanceof CharacterLiteral
        || node instanceof BooleanLiteral || node instanceof StringLiteral || node instanceof TypeLiteral
        || node instanceof SingleVariableDeclaration
        || node instanceof BreakStatement
        || node instanceof Modifier
        || node instanceof InstanceofExpression
        || node instanceof ParameterizedType
        || node instanceof ExpressionMethodReference
        || node instanceof CreationReference
        || node instanceof ContinueStatement
        || node instanceof SuperFieldAccess // super.applicationModel
        || node instanceof SingleMemberAnnotation // @SuppressWarnings("unchecked")
        || node instanceof Dimension // []
        || node instanceof EmptyStatement // ";\n"
        || node instanceof MarkerAnnotation
        || node instanceof ArrayType // byte[]
        || node instanceof SuperMethodReference // super::deleteTestTopic
        || node instanceof AssertStatement // assert memoryConfig.getFixedMemoryPerSlot() != null;
        || node instanceof AnnotationTypeMemberDeclaration // 元注解内部方法
    ) {
      // DO Nothing
    } else {
      log.error("暂不支持的节点 => " + node.getClass() + "\n" + StringUtils.abbreviate(node.toString(), 1000));
//      throw new RuntimeException("暂不支持的节点 => " + node);
    }
    return res;
  }

  public static boolean isSameMethod(MethodDeclaration md, MethodDeclaration template) {
    if (md == template) {
      return true;
    } else if (md == null || template == null) {
      return false;
    }
    return Objects.equals(getMethodKey(template), getMethodKey(md));
  }

  private static String getMethodKey(MethodDeclaration template) {
    StringBuilder sb = new StringBuilder(); // 通过方法签名寻找
    String classSign = Helper.getClassSign(template.getParent());
    if (!classSign.isEmpty()) {
      sb.append(classSign).append("#");
    }
    sb.append(Helper.getClassSign(template.getParent()));
    sb.append(Helper.getMethodSign(template));
    return sb.toString();
  }

  private static String getClassSign(ASTNode node) {
    if (!(node instanceof TypeDeclaration)) {
      return "";
    }
    TypeDeclaration td = (TypeDeclaration) node;
    return td.getName().toString();
  }

  public static <T> List<T> toList(DistinctIterable<T> iterable) {
    List<T> res = new ArrayList<>();
    for (T t : iterable) {
      res.add(t);
    }
    return res;
  }

  public static ITree generateITreeForSourceCode(String content) {
    try {
      TreeContext tc = new ExpJdtTreeGenerator().generateFromString(content);
      if (tc != null) {
        return tc.getRoot();
      }
    } catch (IOException e) {
      log.error("代码解析异常", e);
      log.error("代码如下\n" + content);
    }
    return null;
  }

  public static String getMethodCircleTag(boolean oldFlag, boolean newFlag) {
    String tag;
    if (oldFlag && newFlag) {
      tag = "函数圈复杂度修改前后都符合规范";
    } else if (oldFlag) {
      tag = "函数圈复杂度修改前符合规范,修改后不符合规范"; // 反向
    } else if (newFlag) {
      tag = "函数圈复杂度修改前不符合规范,修改后符合规范"; // 正向
    } else {
      tag = "函数圈复杂度修改前后都不符合规范";
    }
    return tag;
  }

  public static String getMethodRowsTag(boolean oldFlag, boolean newFlag) {
    String tag;
    if (oldFlag && newFlag) {
      tag = "函数行数修改前后都符合规范";
    } else if (oldFlag) {
      tag = "函数行数修改前符合规范,修改后不符合规范"; // 反向
    } else if (newFlag) {
      tag = "函数行数修改前不符合规范,修改后符合规范"; // 正向
    } else {
      tag = "函数行数修改前后都不符合规范";
    }
    return tag;
  }

  public static String getMethodArgsTag(boolean oldFlag, boolean newFlag) {
    String tag;
    if (oldFlag && newFlag) {
      tag = "函数参数修改前后都符合规范";
    } else if (oldFlag) {
      tag = "函数参数修改前符合规范,修改后不符合规范"; // 反向
    } else if (newFlag) {
      tag = "函数参数修改前不符合规范,修改后符合规范"; // 正向
    } else {
      tag = "函数参数修改前后都不符合规范";
    }
    return tag;
  }

  public static String getFileRowTag(boolean oldFlag, boolean newFlag) {
    String tag;
    if (oldFlag && newFlag) {
      tag = "文件行数修改前后都符合规范";
    } else if (oldFlag) {
      tag = "文件行数修改前符合规范,修改后不符合规范"; // 反向
    } else if (newFlag) {
      tag = "文件行数修改前不符合规范,修改后符合规范"; // 正向
    } else {
      tag = "文件行数修改前后都不符合规范";
    }
    return tag;
  }

  public static String getLineCharTag(boolean oldFlag, boolean newFlag) {
    String tag;
    if (oldFlag && newFlag) {
      tag = "行字符数修改前后都符合规范";
    } else if (oldFlag) {
      tag = "行字符数修改前符合规范,修改后不符合规范"; // 反向
    } else if (newFlag) {
      tag = "行字符数修改前不符合规范,修改后符合规范"; // 正向
    } else {
      tag = "行字符数修改前后都不符合规范";
    }
    return tag;
  }

  public static String getMethodNumeTag(boolean oldFlag, boolean newFlag) {
    String tag;
    if (oldFlag && newFlag) {
      tag = "函数名修改前后都符合规范";
    } else if (oldFlag) {
      tag = "函数名修改前符合规范,修改后不符合规范"; // 反向
    } else if (newFlag) {
      tag = "函数名修改前不符合规范,修改后符合规范"; // 正向
    } else {
      tag = "函数名修改前后都不符合规范";
    }
    return tag;
  }

  public static String getMethodArgsListTag(boolean oldFlag, boolean newFlag) {
    String tag;
    if (oldFlag && newFlag) {
      tag = "函数参数名修改前后都符合规范";
    } else if (oldFlag) {
      tag = "函数参数名修改前符合规范,修改后不符合规范"; // 反向
    } else if (newFlag) {
      tag = "函数参数名修改前不符合规范,修改后符合规范"; // 正向
    } else {
      tag = "函数参数名修改前后都不符合规范";
    }
    return tag;
  }

  public static String getClassNumeTag(boolean oldFlag, boolean newFlag) {
    String tag;
    if (oldFlag && newFlag) {
      tag = "类名修改前后都符合规范";
    } else if (oldFlag) {
      tag = "类名修改前符合规范,修改后不符合规范"; // 反向
    } else if (newFlag) {
      tag = "类名修改前不符合规范,修改后符合规范"; // 正向
    } else {
      tag = "类名修改前后都不符合规范";
    }
    return tag;
  }

  public static String getTryCatchNumTag(int oldNum, int newNum) {
    String tag = null;
    if (oldNum == newNum) {
      tag = "Try-Catch数量修改前后不变";
    } else if (oldNum>newNum) {
      tag = "Try-Catch数量修改后减少"; // 反向
    } else if (oldNum<newNum) {
      tag = "Try-Catch数量修改后增多"; // 正向
    }
    return tag;
  }

  public static String getDirection(boolean oldFlag, boolean newFlag) {
    String tag = null;
    if (oldFlag && !newFlag) {
      tag = "反向"; // 反向
    } else if (!oldFlag && newFlag) {
      tag = "正向"; // 正向
    }
    return tag;
  }

  public static String getDirectionHL(int oldNum, int newNum) {
    String tag = null;
    if (oldNum > newNum) {
      tag = "反向"; // 反向
    } else if (oldNum < newNum) {
      tag = "正向"; // 正向
    }
    return tag;
  }

  public static String getMethodSign(MethodDeclaration md) {
    if (md == null) {
      return null;
    }
    Block body = md.getBody();
    Javadoc doc = md.getJavadoc();
    md.setBody(null);
    md.setJavadoc(null);
    String res = md.toString().trim();
    md.setBody(body);
    md.setJavadoc(doc);
    return res;
  }

  public static String getMethodName(MethodDeclaration m) {
    return m.getName().toString();
  }

  public static boolean isInstanceOf(Class<?> thisClass, Class<?> superClass) {
    return thisClass.isAssignableFrom(superClass) || thisClass == superClass;
  }


  public static MongoClient createPublicMongoClient() throws SQLException {
    ServerAddress address = new ServerAddress("127.0.0.1", 27017);
    MongoCredential credential = MongoCredential.createScramSha1Credential("root", "admin", "123456".toCharArray());
    return new MongoClient(address, credential, MongoClientOptions.builder().build());
  }


  public static MongoClient createLocalMongoClient() throws SQLException {
    ServerAddress address = new ServerAddress("127.0.0.1", 27017);
    return new MongoClient(address);
  }

  public static <T> T fromDocument(Document document, Class<T> clazz) {
    String text = JSON.toJSONString(document);
    return JSON.parseObject(text, clazz);
  }

  public static Document toDocument(Object o) {
    if (o instanceof Document) {
      return (Document) o;
    }
    String text = JSON.toJSONString(o);
    return JSON.parseObject(text, Document.class);
  }

  public static File getOutputFile(String path) {
    File file = new File(path);
    File dir = file.getParentFile();
    if (!dir.isDirectory()) {
      log.info("创建父目录 => " + dir);
      dir.mkdirs();
    }
    return file;
  }


  public static String toShortString(Object o) {
    return toShortString(o, 200);
  }

  public static String toShortString(Object o, int i) {
    String text = JSON.toJSONString(o);
    Map<String, Object> map = JSON.parseObject(text, Map.class);
    for (Map.Entry<String, Object> entry : map.entrySet()) {
      if (entry.getValue() != null) {
        String s = JSON.toJSONString(entry.getValue());
        map.put(entry.getKey(), StringUtils.abbreviate(s, i));
      }
    }
    return JSON.toJSONString(map);
  }

  public static void addOne(Map<String, Integer> map, String key) {
    map.put(key, map.getOrDefault(key, 0) + 1);
  }

  public static boolean isPositive(String tag) {
    return "正向".equals(tag);
  }
  public static boolean isReverse(String tag) {
    return "反向".equals(tag);
  }


  @Data
  public static class RowChange {
    private final int oldRow;
    private final int newRow;
  }

  public static Collection<HierarchicalActionSet> distinctActionsByFirstLine(List<HierarchicalActionSet> gumTree) {
    Map<RowChange, HierarchicalActionSet> map = new LinkedHashMap<>();
    Stack<HierarchicalActionSet> stack = new Stack<>();
    stack.addAll(gumTree);
    while (!stack.isEmpty()) {
      HierarchicalActionSet has = stack.pop();
      RowChange rc = new RowChange(has.getOldStartRow(), has.getNewStartRow());
      if (!map.containsKey(rc)) {
        map.put(rc, has);
      }
      stack.addAll(has.getSubActions());
    }
    return map.values();
  }
}
