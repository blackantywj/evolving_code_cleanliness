package org.example.domain;

import lombok.Data;
import lombok.experimental.Accessors;
import org.bson.Document;
import org.example.utils.Helper;

import java.util.ArrayList;
import java.util.List;

@Data
@Accessors(chain = true)
public class FileAnalyseEntity {

  private String gcMongoId;
  private String commitSha;
  private String fileName;
  private String Author;
  private String committer;
  private String date;
  private List<String> NewClassName;
  private List<String> OldClassName;
  private String repository;
  private int oldRows;
  private int newRows;
  private int unixTime; // 存储秒数
  private int OldTryCatchNum;
  private int NewTryCatchNum;
  private List<MethodAnalyseEntity> methods = new ArrayList<>();
  private List<LineAnalyseEntity> lines = new ArrayList<>();

  public Document toDocument() {
    return Helper.toDocument(this);
  }

  public static void main(String[] args) {
    FileAnalyseEntity entity = new FileAnalyseEntity().setFileName("123");
    System.out.println(entity);
    Document document = entity.toDocument();
    System.out.println(document);
    entity = Helper.fromDocument(document, FileAnalyseEntity.class);
    System.out.println(entity);
  }

  public String getCommitUrl() {
    return String.format("https://github.com/%s/commit/%s", repository, commitSha);
  }
}
