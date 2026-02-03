package org.example.service;

import com.alibaba.fastjson.JSON;
import com.mongodb.MongoClient;
import org.bson.Document;
import org.example.utils.Helper;
import org.example.domain.FileAnalyseEntity;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import java.sql.SQLException;

public class FileAnalyseServiceTest {
  private static MongoClient client;
  private static FileAnalyseService fileAnalyseService;

  @BeforeClass
  public static void init() throws SQLException {
    client = Helper.createPublicMongoClient();
    fileAnalyseService = new FileAnalyseService(client);
  }

  @AfterClass
  public static void close() throws SQLException {
    client.close();
  }

  @Test
  public void test1() {
    fileAnalyseService.saveOrUpdate(new FileAnalyseEntity()
        .setGcMongoId("1").setCommitSha("2").setFileName("1"));
  }

  @Test
  public void findByCircle() {
    for (FileAnalyseEntity fae : fileAnalyseService.findByCircle("apache/dubbo", 5)) {
      System.out.println(JSON.toJSONString(fae));
      break;
    }
  }
}