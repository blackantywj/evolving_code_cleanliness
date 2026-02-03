package org.example.domain;

import lombok.Data;
import lombok.experimental.Accessors;

@Data
@Accessors(chain = true)
public class LineAnalyseEntity {
  private String name;
  private int oldStartRow = 0;
  private int newStartRow = 0;
  private int oldChars = 0;
  private int newChars = 0;
}
