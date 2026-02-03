package org.example.domain;

import lombok.Getter;
import org.apache.commons.lang3.StringUtils;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class ChangeMap {
  @Getter
  private Map<String, Map<String, Integer>> countMap = new HashMap<>();


  public void addOne(String k1, String k2) {
    addValue(k1, k2, 1);
  }

  public void addValue(String k1, String k2, int c) {
    Map<String, Integer> map = countMap.computeIfAbsent(k1, k -> new HashMap<>());
    map.put(k2, map.getOrDefault(k2, 0) + c);
  }

  public String toString(String title) {
    List<String> names = Arrays.asList("INS,DEL,MOV,UPD".split(","));
    StringBuilder sb = new StringBuilder();
    if (StringUtils.isNotBlank(title)) {
      sb.append(StringUtils.rightPad(title, 100, "-"));
    }
    countMap.entrySet().forEach(e1 -> {
      sb.append("\n").append(e1.getKey());
      for (String name : names) {
        sb.append("\t").append(e1.getValue().getOrDefault(name, 0));
      }
    });
    return sb.toString();
  }
  public String toString() {
    return toString(null);
  }

  public ChangeMap add(ChangeMap others) {
    others.countMap.entrySet().forEach(e1 -> e1.getValue().entrySet().forEach(e2 -> this.addValue(e1.getKey(), e2.getKey(), e2.getValue())));
    return this;
  }

  public boolean isEmpty() {
    return countMap.isEmpty();
  }

  public void clear() {
  }
}
