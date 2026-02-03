package org.example.common;

import lombok.Data;

import java.util.HashMap;
import java.util.Map;

/**
 * @Author youhl002
 * @Date 2023/3/3 15:34
 */
@Data
public class Counter {

  private final int total;
  private int success;
  private int count;

  private Map<String, Integer> errors = new HashMap<>();

  public Counter(int total) {
    this.total = total;
  }


  public void print(int i) {
    if (i > 0 && count % i != 0) {
      return;
    }
    String percent = "N/A";
    if (total != 0) {
      percent = String.format("%.2f%%", count * 100d / total);
    }
    System.out.println(String.format("当前进度: %d / %d = %s, 成功数: %d, 失败 => %s"
        , count, total, percent
        , success, errors));
  }

  public void addCount() {
    count++;
  }

  public void addError(String error) {
    errors.put(error, errors.getOrDefault(error, 0) + 1);
  }

  public void addSuccess() {
    success++;
  }
}
