package org.example.service;

import com.mongodb.MongoClient;
import org.example.HierarchicalActionSet;
import org.example.common.EntityScanner;
import org.example.domain.FileEntity;
import org.example.domain.MethodPair;
import org.example.utils.Helper;
import org.junit.BeforeClass;
import org.junit.Test;

import java.sql.SQLException;
import java.util.List;

public class GithubCommitServiceTest {
  private static MongoClient client;
  private static GithubCommitService githubCommitService;

  @BeforeClass
  public static void init() throws SQLException {
    client = Helper.createPublicMongoClient();
    githubCommitService = new GithubCommitService(client);
  }

  @Test
  public void listByIdAndFileName() {
    String id = "63e2017c85d52e6dee1022bf";
    String fileName = "dubbo-rpc/dubbo-rpc-triple/src/test/java/org/apache/dubbo/rpc/protocol/tri/transport/AbstractH2TransportListenerTest.java";
    for (FileEntity entity : githubCommitService.listByIdAndFileName(id, fileName)) {
      System.out.println(entity.getFileName());
    }
  }

  @Test
  public void findFilesByRepository() {
    EntityScanner<FileEntity> scanner = githubCommitService.findFilesByRepository("apache/dubbo");
    for (FileEntity entity : scanner) {
      System.out.println(entity.toShortString(20));
    }
  }


  @Test
  public void test_1() {
    for (FileEntity fe : githubCommitService.listByCommitShaAndFileNameLike("600dfc77a301601f997fdf2c4f479a41b5e0ef2f", "HiveParserCalcitePlanner")) {
      System.out.println(fe.getCommitUrl() + " => " + fe.getFileName());
      if (!fe.isValid()) {
        continue;
      }
      List<MethodPair> methodEntities = fe.extractMethods();
      for (MethodPair me : methodEntities) {
        me.calcCircle();
        if (!me.getMethodName().contains("registerFrom")) {
          continue;
        }
        System.out.println(String.format("从 %d => %d", me.getOldCircle().getDeepCircle(), me.getNewCircle().getDeepCircle()));
        System.out.println("老方法: " + Helper.getMethodSign(me.getOldMethod()));
        System.out.println("新方法: " + Helper.getMethodSign(me.getNewMethod()));
        System.out.println("老方法圈: " + me.getOldCircle());
        System.out.println("新方法圈: " + me.getNewCircle());
        System.out.println(me.createChangeMap());
        for (HierarchicalActionSet ast : me.getActionSetList()) {
          System.out.println(ast);
          System.out.println(ast.toCode());
        }
      }

    }
  }
}