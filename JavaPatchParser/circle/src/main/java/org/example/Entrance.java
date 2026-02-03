package org.example;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.lang3.StringUtils;
import org.example.common.EntityScanner;
import org.example.common.PrintWrapper;
import org.example.domain.ChangeMap;
import org.example.domain.FileAnalyseEntity;
import org.example.domain.FileEntity;
import org.example.domain.LineAnalyseEntity;
import org.example.domain.MethodAnalyseEntity;
import org.example.domain.MethodPair;
import org.example.service.FileAnalyseService;
import org.example.service.GithubCommitService;
import org.example.utils.Helper;

import com.mongodb.MongoClient;

import lombok.Data;
import lombok.experimental.Accessors;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class Entrance {
  private final GithubCommitService githubCommitService;
  private final FileAnalyseService fileAnalyseService;
  private final MongoClient client;

  public Entrance(MongoClient client) {
    this.client = client;
    githubCommitService = new GithubCommitService(client);
    fileAnalyseService = new FileAnalyseService(client);
  }

  @Data
  @Accessors(chain = true)
  private static class Summary {
    private String repository;
    private int oldRows;
    private int oldMethods;
    private int newRows;
    private int newMethods;

    public String toString() {
      return String.format("仓库: %s, 老代码行数: %d, 老代码方法数: %d, 新代码行数: %d, 新代码方法数: %d",
          repository, oldRows, oldMethods, newRows, newMethods);
    }
  }

  @Data
  @Accessors(chain = true)
  private static class ChangeOutput {
    private Map<String, ChangeMap> cmMap = new HashMap<>();
    private String type;
    private String repository;
    private String fileName;
    private String commitSha;
    private String methodName;
    private String committer;
    private String author;

    public ChangeOutput setFileEntity(FileEntity fe) {
      return this.setRepository(fe.getRepository())
          .setCommitSha(fe.getCommitSha())
          .setFileName(fe.getFileName());
    }

    public static CSVPrinter createCSVPrinter(String path) throws IOException {
      File file = Helper.getOutputFile(path);
      CSVFormat writeFormat = CSVFormat.Builder.create()
          .setHeader("type", "repository", "commitSha", "author", "committer", "fileName", "methodName", "direction", "statement", "INS", "DEL", "MOV", "UPD") // INS,DEL,MOV,UPD
          .build();
      return new CSVPrinter(new OutputStreamWriter(new FileOutputStream(file)), writeFormat);
    }

    public ChangeOutput add(String tag, ChangeMap cm) {
      cmMap.computeIfAbsent(tag, k -> new ChangeMap()).add(cm);
      return this;
    }

    public void write(CSVPrinter csvPrinter) throws IOException {
      for (Map.Entry<String, ChangeMap> e1 : cmMap.entrySet()) {
        for (Map.Entry<String, Map<String, Integer>> e2 : e1.getValue().getCountMap().entrySet()) {
          List<Object> objects = new ArrayList<>();
          objects.add(type);
          objects.add(repository);
          objects.add(commitSha);
          objects.add(author);
          objects.add(committer);
          objects.add(fileName);
          objects.add(methodName);
          objects.add(e1.getKey());
          objects.add(e2.getKey());
          objects.add(e2.getValue().getOrDefault("INS", 0));
          objects.add(e2.getValue().getOrDefault("DEL", 0));
          objects.add(e2.getValue().getOrDefault("MOV", 0));
          objects.add(e2.getValue().getOrDefault("UPD", 0));
          System.out.println(objects);
          csvPrinter.printRecord(objects);
        }
      }
    }
  }

  private static class ConsoleOutput {
    private final PrintWrapper printer;
    private Map<Type, Map<String, Map<String, Integer>>> summaryMap = new HashMap<>();
    private Map<String, Set<String>> commitMap = new TreeMap<>();

    public void close() {
      printer.close();
    }


    public void addCommit(String tag, String commitSha) {
      commitMap.computeIfAbsent(tag, k -> new HashSet<>()).add(commitSha);
    }

    enum Type {SUM, CHANGE}

    public ConsoleOutput(String path) throws IOException {
      this.printer = new PrintWrapper(path);
    }

    private Map<String, Integer> getMap(Type k1, String k2) {
      return summaryMap.computeIfAbsent(k1, k -> new TreeMap<>()).computeIfAbsent(k2, k -> new TreeMap<>());
    }

    public void printSummary() throws IOException {
      println("汇总", true);
      for (Map.Entry<String, Integer> entry : getMap(Type.CHANGE, "").entrySet()) {
        println(String.format("%s 数量: %d", entry.getKey(), entry.getValue()), true);
      }
      for (Map.Entry<String, Integer> entry : getMap(Type.SUM, "").entrySet()) {
        println(String.format("%s: %d", entry.getKey(), entry.getValue()), true);
      }
      println("提交数量", true);
      for (Map.Entry<String, Set<String>> entry : commitMap.entrySet()) {
        println(String.format("%s: %d", entry.getKey(), entry.getValue().size()), true);
      }
    }

    public void printRepository() throws IOException {
      List<String> repositories = summaryMap.values().stream().flatMap(s -> s.keySet().stream())
          .filter(e -> e.length() > 0)
          .distinct().collect(Collectors.toList());
      for (String repository : repositories) {
        println(String.format("[%s]", repository), true);
        for (Map.Entry<String, Integer> entry : getMap(Type.CHANGE, repository).entrySet()) {
          println(String.format("%s 数量: %d", entry.getKey(), entry.getValue()), true);
        }
        for (Map.Entry<String, Integer> entry : getMap(Type.SUM, repository).entrySet()) {
          println(String.format("%s: %d", entry.getKey(), entry.getValue()), true);
        }
      }
    }

    public void println(String s) throws IOException {
      println(s, false);
    }

    public void println(String s, boolean flag) throws IOException {
      this.printer.println(s);
      if (this.printer.getCount() % 100 == 0 || flag) {
        System.out.println(String.format("[%d] %s", this.printer.getCount(), s));
      }
    }

    public void addSummary(String tag, String change) {
      Helper.addOne(getMap(Type.SUM, ""), tag);
      Helper.addOne(getMap(Type.CHANGE, ""), change);
    }


    public void addRepository(String repository, String tag, String change) {
      Helper.addOne(getMap(Type.SUM, repository), tag);
      Helper.addOne(getMap(Type.CHANGE, repository), change);
    }
  }


  @Data
  @Accessors(chain = true)
  private static class CloudOutput {
    private final CloudPrinter right;
    private final CloudPrinter wrong;

    public CloudOutput(String path) throws FileNotFoundException {
      this.right = new CloudPrinter(path + "/right.txt");
      this.wrong = new CloudPrinter(path + "/wrong.txt");
    }

    private static class CloudPrinter {

      private final PrintWrapper printer;

      public CloudPrinter(String path) throws FileNotFoundException {
        this.printer = new PrintWrapper(path);
      }

      public void close() {
        this.endSegment();
        printer.close();
      }

      private FileEntity curr = null;
      private String beginKey = StringUtils.repeat(">", 20);
      private String endKey = StringUtils.repeat("<", 20);

      public int add(FileEntity fe) {
        int res = 0;
        if (curr == null || !fe.getCommitSha().equals(curr.getCommitSha())) {
          res = 1;
          this.endSegment();
          // >>>>>>>>>>>>>>>>>>>> apache/dubbo 16fc7b55ef20f97d2b5e7b983d4d10eb9afc4c82 63e2018185d52e6dee102430
          printer.println(beginKey + " " + fe.getRepository() + " " + fe.getCommitSha() + " " + fe.getMongoId());
        }
        // >>>>>>>>>>>>>>>>>>>> 文件名: dubbo-rpc/dubbo-rpc-triple/src/main/java/org/apache/dubbo/rpc/protocol/tri/call/ServerCall.java
        if (curr == null || !fe.getFileName().equals(curr.getFileName())) {
          printer.println(beginKey + " 文件名: " + fe.getFileName());
        }
        curr = fe;
        return res;
      }

      private void endSegment() {
        if (curr != null) {
          printer.println(curr.getMessage());
          printer.println(endKey);
          curr = null;
        }
      }
    }

    public void close() {
      right.close();
      wrong.close();
      Map<String, List<Counter>> counters = counterMap.values().stream().collect(Collectors.groupingBy(Counter::getRepository, Collectors.toList()));
      for (Map.Entry<String, List<Counter>> entry : counters.entrySet()) {
        System.out.println("仓库: " + entry.getKey());
        entry.getValue().stream().forEach(System.out::println);
      }
    }

    private Map<String, Counter> counterMap = new HashMap<>();

    @Data
    private static class Counter {
      private final String name;
      private final String repository;
      private int wrong;
      private int right;
      private int total;

      public Counter(FileEntity fe) {
        this.name = fe.getCommitterName();
        this.repository = fe.getRepository();
      }

      public String getKey() {
        return name + "," + repository;
      }

      public void add(String tag) {
        if (Helper.isPositive(tag)) {
          right++;
        } else if (Helper.isReverse(tag)) {
          wrong++;
        }
        total++;
      }

      public String toString() {
        return String.format("提交人: %s, 正向: %d, 反向: %d, 总数: %d", name, right, wrong, total);
      }
    }

    public void add(String tag, FileEntity fe) {
      CloudPrinter printer = Helper.isPositive(tag) ? right : Helper.isReverse(tag) ? wrong : null;
      if (printer == null || fe == null) {
        return;
      }
      int res = printer.add(fe);
      if (res > 0) {
        if (fe.getCommitterName() == null) {
          log.warn("提交人不存在!! => " + fe.toShortString(200));
          return;
        }
        Counter counter = new Counter(fe);
        counterMap.computeIfAbsent(counter.getKey(), k -> counter).add(tag);
      }
    }
  }

  public void calcAttributes() throws IOException {
    List<String> repositories = githubCommitService.listRepositories();
    for (int i = 0; i < repositories.size(); i++) {
      EntityScanner<FileEntity> scanner = githubCommitService.findFilesByRepository(repositories.get(i));
      System.out.println(String.format("分析仓库 => %s [%d/%d], 文件数: %s", repositories.get(i), i + 1, repositories.size(), scanner.getTotal()));
      for (FileEntity fe : scanner) {
        scanner.getCounter().addCount();
        try {
          if (!fe.isValid()) {
            scanner.getCounter().addError(fe.getInvalidMessage());
            continue;
          }
          // double m = fe.extractVariableNames();
          // 变量名 方法名 类名 之间的关系
          List<MethodPair> methods = fe.extractMethods();
          // System.out.println(fe.getCommitterName());
          FileAnalyseEntity entity = new FileAnalyseEntity()
              .setGcMongoId(fe.getMongoId())
              .setRepository(fe.getRepository())
              .setCommitSha(fe.getCommitSha())
              .setNewClassName(fe.getJca().getOldUnit().getClassNames())
              .setOldClassName(fe.getJca().getNewUnit().getClassNames())
              .setFileName(fe.getFileName())
              .setAuthor(fe.getAuthor().getName())
              .setCommitter(fe.getCommitter().getName())
              .setOldRows(fe.getJca().getOldUnit().getRows())
              .setNewRows(fe.getJca().getNewUnit().getRows())
              .setUnixTime((int) (System.currentTimeMillis() / 1000))
              .setOldTryCatchNum(fe.getJca().getOldUnit().getTryCatchNum())
              .setDate(fe.getRelease_time())
              .setNewTryCatchNum(fe.getJca().getNewUnit().getTryCatchNum());
          /* 添加注释分析 */
          String oldSource = fe.getJca().getOldUnit().getSource(); // 这里改成你实际能拿到源码的函数
          String newSource = fe.getJca().getNewUnit().getSource();
          for (MethodPair mp : methods) {
            mp.setOldSource(oldSource);
            mp.setNewSource(newSource);
            mp.calcCircle();
            MethodAnalyseEntity methodAnalyse = new MethodAnalyseEntity()
              .setMethodName(mp.getMethodName())
              .setOldMethodName(mp.getOldMethodName())
              .setNewMethodName(mp.getNewMethodName())
              .setMethodSign(mp.getMethodSign())
              .setOldCircle(mp.getOldCircle().getDeepCircle())
              .setNewCircle(mp.getNewCircle().getDeepCircle())
              .setOldArgs(mp.getOldArgs())
              .setNewArgs(mp.getNewArgs())
              .setOldArgsList(mp.getOldArgsList())
              .setNewArgsList(mp.getNewArgsList())
              .setOldRows(mp.getOldRows())
              .setNewRows(mp.getNewRows())
              .setOldCode(mp.getOldMethodCode())
              .setNewCode(mp.getNewMethodCode());
            entity.getMethods().add(methodAnalyse);
          }
          for (HierarchicalActionSet has : Helper.distinctActionsByFirstLine(fe.getJca().getGumTree())) {
            LineAnalyseEntity lineAnalyse = new LineAnalyseEntity()
                .setName(has.getAction().getName())
                .setOldStartRow(has.getOldStartRow())
                .setNewStartRow(has.getNewStartRow())
                .setOldChars(has.getOldFirstLineChars())
                .setNewChars(has.getNewFirstLineChars());
                entity.getLines().add(lineAnalyse);
          }
          fileAnalyseService.saveOrUpdate(entity);
          scanner.getCounter().addSuccess();
        } catch (Exception e) {
          log.error("分析参数异常", e);
          scanner.getCounter().addError("异常:" + e.getMessage());
        }
        scanner.getCounter().print(100);
      }
      scanner.getCounter().print(0);
      System.out.println("仓库 " + repositories.get(i) + " 分析完毕");
    }
  }


  public void calcSummary() {
    List<String> repositories = githubCommitService.listRepositories();
    List<Summary> summaries = new ArrayList<>();
    for (int i = 0; i < repositories.size(); i++) {
      EntityScanner<FileEntity> scanner = githubCommitService.findFilesByRepository(repositories.get(i));
      Summary summary = new Summary().setRepository(repositories.get(i));
      System.out.println(String.format("分析仓库 => %s [%d/%d], 文件数: %s", repositories.get(i), i + 1, repositories.size(), scanner.getTotal()));
      for (FileEntity fe : scanner) {
        scanner.getCounter().addCount();
        try {
          if (!fe.isValid()) {
            scanner.getCounter().addError(fe.getInvalidMessage());
            continue;
          }
          summary.oldRows += fe.getJca().getOldUnit().getRows();
          summary.oldMethods += fe.getJca().getOldUnit().getMethodDeclarations().size();
          summary.newRows += fe.getJca().getNewUnit().getRows();
          summary.newMethods += fe.getJca().getNewUnit().getMethodDeclarations().size();
          scanner.getCounter().addSuccess();
        } catch (Exception e) {
          log.error("分析参数异常", e);
          scanner.getCounter().addError("异常:" + e.getMessage());
        }
        scanner.getCounter().print(100);
      }
      scanner.getCounter().print(0);
      System.out.println(summary);
      System.out.println("仓库 " + repositories.get(i) + " 分析完毕");
      summaries.add(summary);
    }
    for (Summary summary : summaries) {
      System.out.println(summary);
    }
  }


  public void printMethodCircles(int threshold) throws IOException {
    ConsoleOutput console = new ConsoleOutput("data/MethodCircles/detail.txt");
    List<String> repositories = githubCommitService.listRepositories();
    for (String repository : repositories) {
      EntityScanner<FileAnalyseEntity> scanner = fileAnalyseService.findByRepository(repository);
      for (FileAnalyseEntity fae : scanner) {
        console.println(String.format("提交: %s", fae.getCommitUrl()));
        for (MethodAnalyseEntity mae : fae.getMethods()) {
          if (mae.getOldCircle() == 0 || mae.getNewCircle() == 0) {
            continue;
          }
          boolean oldFlag = mae.getOldCircle() <= threshold;
          boolean newFlag = mae.getNewCircle() <= threshold;
          String tag = Helper.getMethodCircleTag(oldFlag, newFlag);
          String change = String.format("%s: %d -> %d", tag, mae.getOldCircle(), mae.getNewCircle());
          console.addRepository(repository, tag, change);
          console.addSummary(tag, change);
          console.addCommit(tag, fae.getCommitSha());
          String committer;
          if ((fae.getCommitter() != null && fae.getCommitter().equals("web-flow")) || fae.getCommitter() == null)
            committer = fae.getAuthor();
          else
            committer = fae.getCommitter();
          console.println(String.format("提交: %s\n提交人: %s\n提交时间: %s\n%s\n函数: %s\n函数复杂度变化: %d -> %d",
              fae.getCommitUrl(), committer, fae.getDate(), fae.getFileName(), mae.getMethodSign(), mae.getOldCircle(), mae.getNewCircle()));
        }
      }
    }
    console.printRepository();
    console.printSummary();
    console.close();
  }

  public void analyseMethodCircles(int threshold) throws IOException {
    List<String> repositories = githubCommitService.listRepositories();
    CSVPrinter csvPrinter = ChangeOutput.createCSVPrinter("data/MethodCircles/analyse.csv");
    ChangeOutput co1 = new ChangeOutput().setType("汇总");
    CloudOutput cloud = new CloudOutput("data/MethodCircles");
    for (String repository : repositories) {
      // if (repository.contains("spring"))
      //   continue;
      ChangeOutput co2 = new ChangeOutput().setType("仓库").setRepository(repository);
      EntityScanner<FileAnalyseEntity> scanner = fileAnalyseService.findByCircle(repository, threshold);
      for (FileAnalyseEntity fae : scanner) {
        for (FileEntity fe : githubCommitService.listByIdAndFileName(fae.getGcMongoId(), fae.getFileName())) {
          if (!fe.isValid()) {
            System.err.println(String.format("格式异常 => 提交: %s, 文件: %s, 错误: %s", fe.getCommitUrl(), fe.getFileName(), fe.getInvalidMessage()));
            continue;
          }
          List<MethodPair> methods = fe.extractMethods();
          for (MethodPair me : methods) {
            me.calcCircle();
            boolean oldFlag = me.getOldCircle().getDeepCircle() <= threshold;
            boolean newFlag = me.getNewCircle().getDeepCircle() <= threshold;
            String tag = Helper.getDirection(oldFlag, newFlag);
            if (tag != null) {
              ChangeMap cm = me.createChangeMap();
              ChangeOutput co3 = new ChangeOutput().add(tag, cm)
                                                    .setType("方法")
                                                    .setFileEntity(fe)
                                                    .setMethodName(me.getMethodName())
                                                    .setCommitter(fe.getCommitter().getName())
                                                    .setAuthor(fe.getAuthor().getName());
              Stream.of(co1, co2, co3).forEach(c -> c.add(tag, cm));
              co3.write(csvPrinter);
              cloud.add(tag, fe);
            }
          }
          csvPrinter.flush();
        }
      }
      co2.write(csvPrinter);
    }
    co1.write(csvPrinter);
    csvPrinter.close();
    cloud.close();
  }


  public void printFileRows(int threshold) throws IOException {
    ConsoleOutput console = new ConsoleOutput("data/FileRows/detail.txt");
    List<String> repositories = githubCommitService.listRepositories();
    for (String repository : repositories) {
      EntityScanner<FileAnalyseEntity> scanner = fileAnalyseService.findByRepository(repository);
      // Set<String> idSet = new HashSet<>()
      for (FileAnalyseEntity fae : scanner) {
        if (fae.getOldRows() == 0 || fae.getNewRows() == 0) {
          continue;
        }
//        if (idSet.contains(fae.getGcMongoId())) {
//          continue;
//        }
        boolean oldFlag = fae.getOldRows() <= threshold;
        boolean newFlag = fae.getNewRows() <= threshold;
        String tag = Helper.getFileRowTag(oldFlag, newFlag);
        String key = String.format("%s: %d -> %d", tag, fae.getOldRows(), fae.getNewRows());
        console.addRepository(repository, tag, key);
        console.addSummary(tag, key);
        console.addCommit(tag, fae.getCommitSha());
        String committer;
        if ((fae.getCommitter() != null && fae.getCommitter().equals("web-flow")) || fae.getCommitter() == null)
          committer = fae.getAuthor();
        else
          committer = fae.getCommitter();
        console.println(String.format("提交: %s\n提交人: %s\n提交时间: %s\n文件: %s\n文件行数变化: %d -> %d", fae.getCommitUrl(), committer, fae.getDate(), fae.getFileName(), fae.getOldRows(), fae.getNewRows()));
      }
    }
    console.printRepository();
    console.printSummary();
    console.close();
  }

  public void analyseFileRows(int threshold) throws IOException {
    List<String> repositories = githubCommitService.listRepositories();
    CSVPrinter csvPrinter = ChangeOutput.createCSVPrinter("data/FileRows/analyse.csv");
    CloudOutput cloud = new CloudOutput("data/FileRows");
    ChangeOutput co1 = new ChangeOutput().setType("汇总");
    for (String repository : repositories) {
      // if (repository.contains("spring"))
      //   continue;
      ChangeOutput co2 = new ChangeOutput().setType("仓库").setRepository(repository);
      EntityScanner<FileAnalyseEntity> scanner = fileAnalyseService.findByFileRows(repository, threshold);
      for (FileAnalyseEntity fae : scanner) {
        for (FileEntity fe : githubCommitService.listByIdAndFileName(fae.getGcMongoId(), fae.getFileName())) {
          if (!fe.isValid()) {
            System.err.println(String.format("格式异常 => 提交: %s, 文件: %s, 错误: %s", fe.getCommitUrl(), fe.getFileName(), fe.getInvalidMessage()));
            continue;
          }
          boolean oldFlag = fae.getOldRows() <= threshold;
          boolean newFlag = fae.getNewRows() <= threshold;
          String tag = Helper.getDirection(oldFlag, newFlag);
          if (tag == null) {
            return;
          }
          cloud.add(tag, fe);
          List<MethodPair> methods = fe.extractMethods();
          for (MethodPair me : methods) {
            ChangeMap cm = new ChangeMap();
            for (HierarchicalActionSet actionSet : me.getActionSetList()) {
              cm.add(actionSet.createChangeMap(false));
            }
            ChangeOutput co3 = new ChangeOutput().setType("方法").setFileEntity(fe).setMethodName(me.getMethodName());
            Stream.of(co1, co2, co3).forEach(c -> c.add(tag, cm));
            co3.write(csvPrinter);
          }
          csvPrinter.flush();
        }
      }
      co2.write(csvPrinter);
    }
    co1.write(csvPrinter);
    csvPrinter.close();
    cloud.close();
  }

  public void printLineChars(int threshold) throws IOException {
    ConsoleOutput console = new ConsoleOutput("data/LineChars/detail.txt");
    List<String> repositories = githubCommitService.listRepositories();
    for (String repository : repositories) {
      EntityScanner<FileAnalyseEntity> scanner = fileAnalyseService.findByRepository(repository);
      for (FileAnalyseEntity fae : scanner) {
        console.println(String.format("提交: %s", fae.getCommitUrl()));
        for (LineAnalyseEntity le : fae.getLines()) {
          if (le.getOldChars() == 0 || le.getNewChars() == 0) {
            continue;
          }
          boolean oldFlag = le.getOldChars() <= threshold;
          boolean newFlag = le.getNewChars() <= threshold;
          String tag = Helper.getLineCharTag(oldFlag, newFlag);
          String key = String.format("%s: %d -> %d", tag, le.getOldChars(), le.getNewChars());
          console.addRepository(repository, tag, key);
          console.addSummary(tag, key);
          console.addCommit(tag, fae.getCommitSha());
          String committer;
          if ((fae.getCommitter() != null && fae.getCommitter().equals("web-flow")) || fae.getCommitter() == null || fae.getAuthor() != null)
            committer = fae.getAuthor();
          else
            committer = fae.getCommitter();
          console.println(String.format("提交: %s\n提交人: %s\n提交时间: %s\n文件: %s\n行字符数变化: %d -> %d, 位置: %s(%d:%d)"
              , fae.getCommitUrl(), committer, fae.getDate(), fae.getFileName(), le.getOldChars(), le.getNewChars(), le.getName()
              , le.getOldStartRow(), le.getNewStartRow()));
        }
      }
    }
    console.printRepository();
    console.printSummary();
    console.close();
  }

  public void analyseLineChars(int threshold) throws IOException {
    List<String> repositories = githubCommitService.listRepositories();
    CSVPrinter csvPrinter = ChangeOutput.createCSVPrinter("data/LineChars/analyse.csv");
    CloudOutput cloud = new CloudOutput("data/LineChars");
    ChangeOutput co1 = new ChangeOutput().setType("汇总");
    for (String repository : repositories) {
      // if (repository.contains("spring"))
      // continue;
      ChangeOutput co2 = new ChangeOutput().setType("仓库").setRepository(repository);
      for (FileAnalyseEntity fae : fileAnalyseService.findByLineChars(repository, threshold)) {
        for (FileEntity fe : githubCommitService.listByIdAndFileName(fae.getGcMongoId(), fae.getFileName())) {
          if (!fe.isValid()) {
            System.err.println(String.format("格式异常 => 提交: %s, 文件: %s, 错误: %s", fe.getCommitUrl(), fe.getFileName(), fe.getInvalidMessage()));
            continue;
          }
          ChangeOutput co3 = new ChangeOutput().setType("文件").setFileEntity(fe);
          for (HierarchicalActionSet has : Helper.distinctActionsByFirstLine(fe.getJca().getGumTree())) {
            boolean oldFlag = has.getOldFirstLineChars() <= threshold;
            boolean newFlag = has.getNewFirstLineChars() <= threshold;
            String tag = Helper.getDirection(oldFlag, newFlag);
            if (tag != null) {
              cloud.add(tag, fe);
              ChangeMap cm = has.createChangeMap(false);
              Stream.of(co1, co2, co3).forEach(c -> c.add(tag, cm));
            }
          }
          co3.write(csvPrinter);
        }
        csvPrinter.flush();
      }
      co2.write(csvPrinter);
    }
    co1.write(csvPrinter);
    csvPrinter.close();
    cloud.close();
  }

  public void printMethodRows(int threshold) throws IOException {
    ConsoleOutput console = new ConsoleOutput("data/MethodRows/detail.txt");
    List<String> repositories = githubCommitService.listRepositories();
    for (String repository : repositories) {
      EntityScanner<FileAnalyseEntity> scanner = fileAnalyseService.findByRepository(repository);
      for (FileAnalyseEntity fae : scanner) {
        console.println(String.format("提交: %s", fae.getCommitUrl()));
        for (MethodAnalyseEntity mae : fae.getMethods()) {
          if (mae.getOldRows() == 0 || mae.getNewRows() == 0) {
            continue;
          }
          boolean oldFlag = mae.getOldRows() <= threshold;
          boolean newFlag = mae.getNewRows() <= threshold;
          String tag = Helper.getMethodRowsTag(oldFlag, newFlag);
          String key = String.format("%s: %d -> %d", tag, mae.getOldRows(), mae.getNewRows());
          console.addRepository(repository, tag, key);
          console.addSummary(tag, key);
          console.addCommit(tag, fae.getCommitSha());
          String committer;
          if ((fae.getCommitter() != null && fae.getCommitter().equals("web-flow")) || fae.getCommitter() == null)
            committer = fae.getAuthor();
          else
            committer = fae.getCommitter();
          console.println(String.format("提交: %s\n提交人: %s\n提交时间: %s\n文件: %s\n函数: %s\n函数行数变化: %d -> %d",
              fae.getCommitUrl(), committer, fae.getDate(), fae.getFileName(), mae.getMethodSign(), mae.getOldRows(), mae.getNewRows()));
        }
      }
    }
    console.printRepository();
    console.printSummary();
    console.close();
  }

  public void analyseMethodRows(int threshold) throws IOException {
    List<String> repositories = githubCommitService.listRepositories();
    CSVPrinter csvPrinter = ChangeOutput.createCSVPrinter("data/MethodRows/analyse.csv");
    CloudOutput cloud = new CloudOutput("data/MethodRows");
    ChangeOutput co1 = new ChangeOutput().setType("汇总");
    for (String repository : repositories) {
      // if (repository.contains("spring"))
      // continue;
      ChangeOutput co2 = new ChangeOutput().setType("仓库").setRepository(repository);
      EntityScanner<FileAnalyseEntity> scanner = fileAnalyseService.findByMethodRows(repository, threshold);
      for (FileAnalyseEntity fae : scanner) {
        for (FileEntity fe : githubCommitService.listByIdAndFileName(fae.getGcMongoId(), fae.getFileName())) {
          if (!fe.isValid()) {
            System.err.println(String.format("格式异常 => 提交: %s, 文件: %s, 错误: %s", fe.getCommitUrl(), fe.getFileName(), fe.getInvalidMessage()));
            continue;
          }
          List<MethodPair> methods = fe.extractMethods();
          for (MethodPair me : methods) {
            boolean oldFlag = me.getOldRows() <= threshold;
            boolean newFlag = me.getNewRows() <= threshold;
            String tag = Helper.getDirection(oldFlag, newFlag);
            if (tag != null) {
              cloud.add(tag, fe);
              ChangeOutput co3 = new ChangeOutput().setType("方法").setFileEntity(fe).setMethodName(me.getMethodName());
              for (HierarchicalActionSet has : me.getActionSetList()) {
                ChangeMap cm = has.createChangeMap(false);
                Stream.of(co1, co2, co3).forEach(c -> c.add(tag, cm));
                co3.add(tag, cm);
              }
              co3.write(csvPrinter);
            }
          }
          csvPrinter.flush();
        }
      }
      co2.write(csvPrinter);
    }
    co1.write(csvPrinter);
    csvPrinter.close();
    cloud.close();
  }

  public void printMethodArgs(int threshold) throws IOException {
    ConsoleOutput console = new ConsoleOutput("data/MethodArgs/detail.txt");
    List<String> repositories = githubCommitService.listRepositories();
    for (String repository : repositories) {
      EntityScanner<FileAnalyseEntity> scanner = fileAnalyseService.findByRepository(repository);
      for (FileAnalyseEntity fae : scanner) {
        console.println(String.format("提交: %s", fae.getCommitUrl()));
        for (MethodAnalyseEntity mae : fae.getMethods()) {
          boolean oldFlag = mae.getOldArgs() <= threshold;
          boolean newFlag = mae.getNewArgs() <= threshold;
          String tag = Helper.getMethodArgsTag(oldFlag, newFlag);
          String key = String.format("%s: %d -> %d", tag, mae.getOldArgs(), mae.getNewArgs());
          console.addRepository(repository, tag, key);
          console.addSummary(tag, key);
          console.addCommit(tag, fae.getCommitSha());
          String committer;
          if (fae.getCommitter() != null && fae.getCommitter().equals("web-flow"))
            committer = fae.getAuthor();
          else
            committer = fae.getCommitter();
          console.println(String.format("提交: %s\n提交人: %s\n提交时间: %s\n文件: %s\n函数: %s\n函数参数变化: %d -> %d",
              fae.getCommitUrl(), committer, fae.getDate(), fae.getFileName(), mae.getMethodSign(), mae.getOldArgs(), mae.getNewArgs()));
        }
      }
    }
    console.printRepository();
    console.printSummary();
    console.close();
  }

  public void analyseMethodArgs(int threshold) throws IOException {
    List<String> repositories = githubCommitService.listRepositories();
    CSVPrinter csvPrinter = ChangeOutput.createCSVPrinter("data/MethodArgs/analyse.csv");
    CloudOutput cloud = new CloudOutput("data/MethodArgs");
    ChangeOutput co1 = new ChangeOutput().setType("汇总");
    for (String repository : repositories) {
      ChangeOutput co2 = new ChangeOutput().setType("仓库").setRepository(repository);
      EntityScanner<FileAnalyseEntity> scanner = fileAnalyseService.findMethodArgs(repository, threshold);
      for (FileAnalyseEntity fae : scanner) {
        for (FileEntity fe : githubCommitService.listByIdAndFileName(fae.getGcMongoId(), fae.getFileName())) {
          if (!fe.isValid()) {
            System.err.println(String.format("格式异常 => 提交: %s, 文件: %s, 错误: %s", fe.getCommitUrl(), fe.getFileName(), fe.getInvalidMessage()));
            continue;
          }
          List<MethodPair> methods = fe.extractMethods();
          for (MethodPair me : methods) {
            boolean oldFlag = me.getOldArgs() <= threshold;
            boolean newFlag = me.getNewArgs() <= threshold;
            String tag = Helper.getDirection(oldFlag, newFlag);
            if (tag != null) {
              cloud.add(tag, fe);
              ChangeOutput co3 = new ChangeOutput().setType("方法").setFileEntity(fe).setMethodName(me.getMethodName());
              for (HierarchicalActionSet has : me.getActionSetList()) {
                ChangeMap cm = has.createChangeMap(false);
                Stream.of(co1, co2, co3).forEach(c -> c.add(tag, cm));
                co3.add(tag, cm);
              }
              co3.write(csvPrinter);
            }
          }
          csvPrinter.flush();
        }
      }
      co2.write(csvPrinter);
    }
    co1.write(csvPrinter);
    csvPrinter.close();
    cloud.close();
  }

    public static boolean isSnakeCase(String variableName) {
      String snakeCaseRegex = "^[a-z]+(_[a-z0-9]+)*$";
      return Pattern.matches(snakeCaseRegex, variableName);
    }

    public static boolean isCamelCase(String variableName) {
        // String camelCaseRegex = "^[a-z]+([A-Z][a-z]*)*$";
        // return Pattern.matches(camelCaseRegex, variableName);
          if (variableName == null) {
              return false;
          }
          // 检查是否符合小驼峰或大驼峰的正则表达式
          return variableName.matches("^[a-z]+([A-Z0-9][a-z0-9]*)*$") || variableName.matches("^[A-Z][a-z0-9]*([A-Z][a-z0-9]*)*$");
    }

  public void printMethodNames() throws IOException {
    ConsoleOutput console = new ConsoleOutput("data/MethodNames/detail.txt");
    List<String> repositories = githubCommitService.listRepositories();
    for (String repository : repositories) {
      EntityScanner<FileAnalyseEntity> scanner = fileAnalyseService.findByRepository(repository);
      for (FileAnalyseEntity fae : scanner) {
        console.println(String.format("提交: %s", fae.getCommitUrl()));
        for (MethodAnalyseEntity mae : fae.getMethods()) {
          String nmn = mae.getNewMethodName();
          String omn = mae.getOldMethodName();
          if (nmn != null && (omn != nmn)){
            boolean nmnFlag = (isCamelCase(nmn) || isSnakeCase(nmn));
            boolean omnFlag = (isCamelCase(omn) || isSnakeCase(omn));
            // if (nmnFlag == false)
            //   System.out.println("1");
            String committer;
            if (fae.getCommitter() != null && fae.getCommitter().equals("web-flow"))
              committer = fae.getAuthor();
            else
              committer = fae.getCommitter();
            console.println(String.format("提交: %s\n提交人: %s\n提交时间: %s\n文件: %s\n函数: %s\n函数变量名变化: %b -> %b",
                fae.getCommitUrl(), committer, fae.getDate(), fae.getFileName(), mae.getMethodSign(), omnFlag, nmnFlag));
            String tag = Helper.getMethodNumeTag(omnFlag, nmnFlag);
            String key = String.format("%s: %b -> %b", tag, omnFlag, nmnFlag);
            console.addRepository(repository, tag, key);
            console.addSummary(tag, key);
            console.addCommit(tag, fae.getCommitSha());
              }
          }
          }
        }
    console.printRepository();
    console.printSummary();
    console.close();
  }

  public void analyseMethodNames() throws IOException {
    List<String> repositories = githubCommitService.listRepositories();
    CSVPrinter csvPrinter = ChangeOutput.createCSVPrinter("data/MethodNames/analyse.csv");
    CloudOutput cloud = new CloudOutput("data/MethodNames");
    ChangeOutput co1 = new ChangeOutput().setType("汇总");
    for (String repository : repositories) {
      ChangeOutput co2 = new ChangeOutput().setType("仓库").setRepository(repository);
      // EntityScanner<FileAnalyseEntity> scanner = fileAnalyseService.findMethodName(repository);
      // for (FileAnalyseEntity fae : scanner) {
      //   for (FileEntity fe : githubCommitService.listByIdAndFileName(fae.getGcMongoId(), fae.getFileName())) {
      //     if (!fe.isValid()) {
      //       System.err.println(String.format("格式异常 => 提交: %s, 文件: %s, 错误: %s", fe.getCommitUrl(), fe.getFileName(), fe.getInvalidMessage()));
      //       continue;
      //     }
      //     List<MethodPair> methods = fe.extractMethods();
      //     for (MethodPair me : methods) {
      //       continue;
      //       // boolean oldFlag = me.getOldArgs() <= threshold;
      //       // boolean newFlag = me.getNewArgs() <= threshold;
      //       // String tag = Helper.getDirection(oldFlag, newFlag);
      //       // if (tag != null) {
      //       //   cloud.add(tag, fe);
      //       //   ChangeOutput co3 = new ChangeOutput().setType("方法").setFileEntity(fe).setMethodName(me.getMethodName());
      //       //   for (HierarchicalActionSet has : me.getActionSetList()) {
      //       //     ChangeMap cm = has.createChangeMap(false);
      //       //     Stream.of(co1, co2, co3).forEach(c -> c.add(tag, cm));
      //       //     co3.add(tag, cm);
      //       //   }
      //       //   co3.write(csvPrinter);
      //       // }
      //     }
      //     csvPrinter.flush();
      //   }
      // }
      co2.write(csvPrinter);
    }
    co1.write(csvPrinter);
    csvPrinter.close();
    cloud.close();
  }

  public void printClassNames() throws IOException {
    ConsoleOutput console = new ConsoleOutput("data/ClassNames/detail.txt");
    List<String> repositories = githubCommitService.listRepositories();
    for (String repository : repositories) {
      EntityScanner<FileAnalyseEntity> scanner = fileAnalyseService.findByRepository(repository);
      for (FileAnalyseEntity fae : scanner) {
          console.println(String.format("提交: %s", fae.getCommitUrl()));
          List<String> ocn = fae.getOldClassName();
          List<String> ncn = fae.getNewClassName();
          boolean ocnFlag = true;
          boolean ncnFlag = true;
          if(ncn != null && (ocn != ncn)){
            for (String oldClassName : ocn) {
              if (!(isCamelCase(oldClassName) || isSnakeCase(oldClassName))){
                ocnFlag = false;
                break;
              }
            }
            for (String newClassName : ncn) {
              if (!(isCamelCase(newClassName) || isSnakeCase(newClassName))){
                ncnFlag = false;
                break;
              }
            }
            String tag = Helper.getClassNumeTag(ocnFlag, ncnFlag);
            String key = String.format("%s: %b -> %b", tag, ocnFlag, ncnFlag);
            console.addRepository(repository, tag, key);
            console.addSummary(tag, key);
            console.addCommit(tag, fae.getCommitSha());
            String committer;
            if (fae.getCommitter() != null && fae.getCommitter().equals("web-flow"))
              committer = fae.getAuthor();
            else
              committer = fae.getCommitter();
            console.println(String.format("提交: %s\n提交人: %s\n提交时间: %s\n文件: %s\n类名变化: %b -> %b",
            fae.getCommitUrl(), committer, fae.getDate(), fae.getFileName(), ocnFlag, ncnFlag));
        }
      }
    }
    console.printRepository();
    console.printSummary();
    console.close();
  }

  public void printVariableNames() throws IOException {
    ConsoleOutput console = new ConsoleOutput("data/VariableNames/detail.txt");
    List<String> repositories = githubCommitService.listRepositories();
    for (String repository : repositories) {
      EntityScanner<FileAnalyseEntity> scanner = fileAnalyseService.findByRepository(repository);
      for (FileAnalyseEntity fae : scanner) {
        console.println(String.format("提交: %s", fae.getCommitUrl()));
        for (MethodAnalyseEntity mae : fae.getMethods()) {
          List<String> oldMethodArgsList = mae.getOldArgsList();
          List<String> newMethodArgsList = mae.getNewArgsList();
          boolean oldMethodArgsListFlag = true;
          boolean newMethodArgsListFlag = true;
          if (oldMethodArgsList != null && newMethodArgsList != null){
            for (String oldArg : oldMethodArgsList) {
              if (!(isCamelCase(oldArg) || isSnakeCase(oldArg)))
                oldMethodArgsListFlag = false;
            }
            // 遍历新方法的参数，检查是否是新增的
            for (String newArg : newMethodArgsList) {
              if (!(isCamelCase(newArg) || isSnakeCase(newArg)))
                newMethodArgsListFlag = false;
              }

            String tag = Helper.getMethodArgsListTag(oldMethodArgsListFlag, newMethodArgsListFlag);
            String key = String.format("%s: %b -> %b", tag, oldMethodArgsListFlag, newMethodArgsListFlag);
            console.addRepository(repository, tag, key);
            console.addSummary(tag, key);
            console.addCommit(tag, fae.getCommitSha());
            String committer;
            if (fae.getCommitter() != null && fae.getCommitter().equals("web-flow"))
              committer = fae.getAuthor();
            else
              committer = fae.getCommitter();
            console.println(String.format("提交: %s\n提交人: %s\n提交时间: %s\n文件: %s\n函数: %s\n函数参数名变化: %b -> %b",
            fae.getCommitUrl(), committer, fae.getDate(), fae.getFileName(), mae.getMethodSign(), oldMethodArgsListFlag, newMethodArgsListFlag));
          }
          // 遍历老方法的参数，检查是否在新方法中
        }
      }
    }
    console.printRepository();
    console.printSummary();
    console.close();
  }

  public void printTryCatchNum() throws IOException {
    ConsoleOutput console = new ConsoleOutput("data/TryCatchNum/detail.txt");
    List<String> repositories = githubCommitService.listRepositories();
    for (String repository : repositories) {
      EntityScanner<FileAnalyseEntity> scanner = fileAnalyseService.findByRepository(repository);
      for (FileAnalyseEntity fae : scanner) {
        // console.println(String.format("提交: %s", fae.getCommitUrl()));
        int OldTryCatchNum = fae.getOldTryCatchNum();
        int NewTryCatchNum = fae.getNewTryCatchNum();
        String tag = Helper.getTryCatchNumTag(OldTryCatchNum, NewTryCatchNum);
        String key = String.format("%s: %d -> %d", tag, OldTryCatchNum, NewTryCatchNum);
        console.addRepository(repository, tag, key);
        console.addSummary(tag, key);
        console.addCommit(tag, fae.getCommitSha());    
        String committer;
        if ((fae.getCommitter() != null && fae.getCommitter().equals("web-flow")) || fae.getCommitter() == null)
          committer = fae.getAuthor();
        else
          committer = fae.getCommitter();      
        console.println(String.format("提交: %s\n提交人: %s\n提交时间: %s\n文件: %s\nTry-Catch个数变化: %d -> %d",
        fae.getCommitUrl(), committer, fae.getDate(), fae.getFileName(), OldTryCatchNum, NewTryCatchNum));
      }
    }
    console.printRepository();
    console.printSummary();
    console.close();
  }

  // public void analyseTryCatchNum() throws IOException {
  //   List<String> repositories = githubCommitService.listRepositories();
  //   CSVPrinter csvPrinter = ChangeOutput.createCSVPrinter("data/TryCatchNum/analyse.csv");
  //   ChangeOutput co1 = new ChangeOutput().setType("汇总");
  //   CloudOutput cloud = new CloudOutput("data/TryCatchNum");
  //   for (String repository : repositories) {
  //     ChangeOutput co2 = new ChangeOutput().setType("仓库").setRepository(repository);
  //     EntityScanner<FileAnalyseEntity> scanner = fileAnalyseService.findByRepository(repository);
  //     for (FileAnalyseEntity fae : scanner) {
  //       for (FileEntity fe : githubCommitService.listByIdAndFileName(fae.getGcMongoId(), fae.getFileName())) {
  //         if (!fe.isValid()) {
  //           System.err.println(String.format("格式异常 => 提交: %s, 文件: %s, 错误: %s", fe.getCommitUrl(), fe.getFileName(), fe.getInvalidMessage()));
  //           continue;
  //         }
  //         int oldNum = fae.getOldTryCatchNum();
  //         int newNum = fae.getNewTryCatchNum();
  //         String tag = Helper.getDirectionHL(oldNum, newNum);
  //         if (tag != null) {
  //           ChangeMap cm = fe.createChangeMap();
  //           ChangeOutput co3 = new ChangeOutput().add(tag, cm).setType("文件").setFileEntity(fe).setCommitter(fe.getCommitter().getName()).setAuthor(fe.getAuthor().getName());
  //           Stream.of(co1, co2, co3).forEach(c -> c.add(tag, cm));
  //           co3.write(csvPrinter);
  //           cloud.add(tag, fe);
  //         }
  //         csvPrinter.flush();
  //       }
  //     }
  //     co2.write(csvPrinter);
  //   }
  //   co1.write(csvPrinter);
  //   csvPrinter.close();
  //   cloud.close();
  // }
  
  public void close() {
    client.close();
  }

}





































