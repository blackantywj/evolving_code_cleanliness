package org.example.common;

import lombok.Data;
import org.example.utils.Helper;

import java.io.*;
import java.nio.charset.StandardCharsets;

@Data
public class PrintWrapper {
  private final PrintWriter pw;
  private int count;
  private long last = System.currentTimeMillis();

  public PrintWrapper(String path) throws FileNotFoundException {
    File file = Helper.getOutputFile(path);
    this.pw = new PrintWriter(new OutputStreamWriter(new FileOutputStream(file), StandardCharsets.UTF_8));
  }

  public void close() {
    pw.close();
  }

  public void println(String s) {
    count += 1;
    pw.println(s);
    long curr = System.currentTimeMillis();
    if (count % 100 == 0 || (curr - last) >= 1000 * 3) {
      pw.flush();
      last = curr;
    }
  }
}
