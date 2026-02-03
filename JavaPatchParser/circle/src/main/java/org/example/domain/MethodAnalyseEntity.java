package org.example.domain;

import java.util.List;

import lombok.Data;
import lombok.experimental.Accessors;

@Data
@Accessors(chain = true)
public class MethodAnalyseEntity {
  private String OldMethodName;
  private String NewMethodName;
  private String MethodName;
  private String methodSign;
  private String date;
  private List<String> oldArgsList;
  private List<String> newArgsList;
  private int oldCircle;
  private int newCircle;
  private int oldArgs;
  private int newArgs;
  private int oldRows;
  private int newRows;
  private String oldCode;
  private String NewCode;
}