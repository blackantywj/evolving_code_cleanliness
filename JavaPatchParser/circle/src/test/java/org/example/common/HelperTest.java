package org.example.common;

import org.apache.commons.io.FileUtils;
import org.apache.commons.io.IOUtils;
import org.example.HierarchicalActionSet;
import org.example.JavaCompareActions;
import org.example.domain.LineAnalyseEntity;
import org.example.domain.MethodPair;
import org.example.template.T1;
import org.example.template.T2;
import org.example.utils.Helper;
import org.junit.Test;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

public class HelperTest {

  public String getJavaCode(Class clazz) throws IOException {
    String userDir = System.getProperty("user.dir");
    System.out.println(userDir);
    List<File> dirs = new ArrayList<>();
    dirs.add(new File(userDir, "src/main/java"));
    dirs.add(new File(userDir, "src/test/java"));
    String path = clazz.getName().replaceAll("\\.", "/") + ".java";

    for (File dir : dirs) {
      File file = new File(dir, path);
      if (file.isFile()) {
        return FileUtils.readFileToString(file, StandardCharsets.UTF_8);
      }
    }
    return null;
  }

  public String getJavaCode(String path) throws IOException {
    InputStream is = getClass().getClassLoader().getResourceAsStream(path);
    return IOUtils.readLines(is, StandardCharsets.UTF_8).stream().collect(Collectors.joining("\n"));
  }

  @Test
  public void testLineAnalyseEntity() throws IOException {
    String j1 = getJavaCode(T1.class);
    String j2 = getJavaCode(T2.class);
    JavaCompareActions jca = JavaCompareActions.create(j1, j2);

    for (HierarchicalActionSet has : Helper.distinctActionsByFirstLine(jca.getGumTree())) {
      LineAnalyseEntity lineAnalyse = new LineAnalyseEntity()
          .setName(has.getAction().getName())
          .setOldStartRow(has.getOldStartRow())
          .setNewStartRow(has.getNewStartRow())
          .setOldChars(has.getOldFirstLineChars())
          .setNewChars(has.getNewFirstLineChars());
      System.out.println(lineAnalyse);
    }
  }

  @Test
  public void testMethodAnalyseEntity() throws IOException {
    String j1 = getJavaCode("1.java");
    String j2 = getJavaCode("2.java");
    JavaCompareActions jca = JavaCompareActions.create(j1, j2);

    List<MethodPair> methodEntities = jca.extractMethods();
    for (MethodPair entity : methodEntities) {
      entity.calcCircle();
      System.out.println("方法: " + entity.getMethodSign());
      System.out.println("老方法圈: " + entity.getOldCircle() );
      System.out.println("新方法圈: " + entity.getNewCircle());
      System.out.println(entity.createChangeMap());
    }
  }

}