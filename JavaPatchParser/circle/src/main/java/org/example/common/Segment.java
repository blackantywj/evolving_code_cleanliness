package org.example.common;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class Segment {
  private int startRow;
  private int endRow;
  private String code;

  public static Segment create(ContentWrapper wrapper, int startPosition, int length) {
    return Segment.builder()
        .startRow(wrapper.getLine(startPosition))
        .endRow(wrapper.getLine(startPosition + length - 1))
        .code(wrapper.content.substring(startPosition, startPosition + length))
        .build();
  }

  public static Segment createByPatch(int startRow, int rowRange) {
    return Segment.builder()
        .startRow(startRow)
        .endRow(startRow + rowRange - 1)
        .build();
  }


  public boolean isIn(Segment s) {
    return s.startRow <= this.startRow && this.endRow <= s.endRow;
  }

  public boolean isOverlap(Segment s) { // 有交集,重叠
    return !(s.startRow > this.endRow || s.endRow < this.startRow);
  }

  public int getRowRange() {
    return endRow - startRow + 1;
  }
  public int getFirstLineChars() {
    // System.out.println(code);
    if (code.equals("\n")){
      return 0;
    }
    return code.split("\n")[0].length();
  }
}