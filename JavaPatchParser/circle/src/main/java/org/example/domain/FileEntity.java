package org.example.domain;

import com.alibaba.fastjson.annotation.JSONField;
import lombok.Data;
import org.apache.commons.lang3.StringUtils;
import org.example.JavaCompareActions;
import org.example.PatchHunks;
import org.example.utils.Helper;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.FieldDeclaration;
import com.github.javaparser.ast.body.VariableDeclarator;
import org.deeplearning4j.models.embeddings.wordvectors.WordVectors;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTParser;
import org.deeplearning4j.models.embeddings.loader.WordVectorSerializer;
//import org.deeplearning4j.models.word2vec.Word2VecModel;
//import org.deeplearning4j.util.SerializationUtils;

import java.util.*;
import java.io.File;


@Data
public class FileEntity {
  private String patch;
  private String OldFileName;
  private String NewFileName;
  private String fileName;
  private String newFileContent;
  private String oldFileContent;
  private String repository;
  private String commitSha;
  private String message;
  private String mongoId;
  private String release_time;
  private PersonInfo committer;
  private PersonInfo author;


  @JSONField(serialize = false)
  private JavaCompareActions jca;
  @JSONField(serialize = false)
  private PatchHunks ph;

  public String getCommitterName() {
    String name = null;
    // 获取 committer 名称
    if (name == null && committer != null) {
      name = committer.getName();
    }
    // 获取 author 名称
//    if (name == null && author != null) {
//      name = author.getName();
//    }
    return name;
  }

  @Data
  public static class PersonInfo {
    private String name;
    private String email;
    // 2022-12-26T12:36:24Z
    @JSONField(format = "yyyy-MM-dd'T'HH:mm:ss'Z'")
    private Date date;
  }

  public JavaCompareActions getJca() {
    if (jca == null && isValid()) {
      // 自动编译
      jca = JavaCompareActions.create(oldFileContent, newFileContent);
    }
    return jca;
  }

  public PatchHunks getPh() {
    if (ph == null && isValid()) {
      // 自动编译
      ph = PatchHunks.create(patch);
    }
    return ph;
  }

  public boolean isValid() {
    return StringUtils.isBlank(getInvalidMessage());
  }

  public String getInvalidMessage() {
    if (Helper.isNotFound(oldFileContent)) {
      return "老代码不存在";
    } else if (Helper.isNotFound(newFileContent)) {
      return "新代码不存在";
    } else if (StringUtils.isBlank(patch) || !patch.contains("@@")) {
      return "补丁文件格式异常";
    } else if (!fileName.toLowerCase().endsWith(".java")) {
      return "不支持" + StringUtils.substringAfterLast(fileName, ".") + "格式";
    }
    return null;
  }

  public String getCommitUrl() {
    return String.format("https://github.com/%s/commit/%s", repository, commitSha);
  }

  public String toString() {
    return Helper.toShortString(this);
  }

  public String toShortString(int i) {
    return Helper.toShortString(this, i);
  }

  public List<MethodPair> extractMethods() {
    JavaCompareActions jca = getJca();
    getJca().setPh(getPh());
    return jca.extractMethods();
  }
}
