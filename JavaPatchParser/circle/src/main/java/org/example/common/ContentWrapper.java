package org.example.common;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;

public class ContentWrapper {
  public final String content;
  private final int[] linePosArray;

  private ContentWrapper(String content) {
    this.content = content;
    List<Integer> res = new ArrayList<>();
    if (content != null) {
      for (int i = 0; i < content.length(); i++) {
        if (content.charAt(i) == '\n') {
          res.add(i);
        }
      }
    }
    linePosArray = new int[res.size()];
    for (int i = 0; i < linePosArray.length; i++) {
      linePosArray[i] = res.get(i);
    }
  }

  public static ContentWrapper create(Object content) {
    return new ContentWrapper(content == null ? null : Objects.toString(content));
  }

  public int getLine(int pos) {
    if (pos < 0 || pos >= content.length()) { // 越界
      return -1;
    }
    int index = Arrays.binarySearch(linePosArray, pos);
    if (index == -1) { // 索值不是数组元素，且小于数组内元素，索引值为 -1。
      return 1;
    } else if (index == -(linePosArray.length + 1)) { // 搜索值不是数组元素，且大于数组内元素，索引值为 -(length + 1);
      return linePosArray.length + 1;
    } else if (index < 0) {
      return -index; //  搜索值不是数组元素，且在数组范围内，从1开始计数，得“-插入点索引值”；
    }
    return index + 1;
  }

  public int getRows() {
    return linePosArray.length + 1;
  }
}
