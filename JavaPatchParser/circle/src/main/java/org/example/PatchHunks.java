package org.example;

import lombok.Data;
import org.example.common.Segment;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

public class PatchHunks {
  private final List<Hunk> hunks = new ArrayList<>();

  @Data
  public static class Hunk {
    private Segment bug;
    private Segment fix;
    private List<String> hunk = new ArrayList<>();
    private String summary = "";

    @Override
    public String toString() {
      StringBuilder sb = new StringBuilder();
      sb.append(String.format("@@ -%d,%d +%d,%d @@%s", bug.getStartRow(), bug.getRowRange(), fix.getStartRow(), fix.getRowRange(), summary));
      sb.append("\n").append(hunk.stream().collect(Collectors.joining("\n")));
      return sb.toString();
    }
  }

  private static final Pattern pattern = Pattern.compile("@@ -(\\d+),(\\d+) \\+(\\d+),(\\d+) @@(.*)$");

  public static PatchHunks create(String text) {
    PatchHunks ph = new PatchHunks();
    Hunk current = null;
    for (String line : text.split("\n")) {
      Matcher matcher = pattern.matcher(line);
      if (matcher.find()) {
        ph.hunks.add(current = new Hunk());
        current.setBug(Segment.createByPatch(Integer.parseInt(matcher.group(1)), Integer.parseInt(matcher.group(2))));
        current.setFix(Segment.createByPatch(Integer.parseInt(matcher.group(3)), Integer.parseInt(matcher.group(4))));
        current.setSummary(matcher.group(5));
      } else if (current != null) {
        current.hunk.add(line);
      }
    }
    return ph;
  }

  public Hunk findFixHunk(Segment segment) {
    return hunks.stream().filter(h -> segment.isOverlap(h.getFix())).findFirst().orElse(null);
  }

  public Hunk findBugHunk(Segment segment) {
    return hunks.stream().filter(h -> segment.isOverlap(h.getBug())).findFirst().orElse(null);
  }

  @Override
  public String toString() {
    return hunks.stream().map(Object::toString).collect(Collectors.joining("\n"));
  }

  public static void main(String[] args) {
    PatchHunks ph = create("@@ -134,7 +136,17 @@ public Object decode(Channel channel, InputStream input) throws IOException {\n" +
        " \n" +
        "         ClassLoader originClassLoader = Thread.currentThread().getContextClassLoader();\n" +
        "         try {\n" +
        "-            if (Boolean.parseBoolean(System.getProperty(SERIALIZATION_SECURITY_CHECK_KEY, \"true\"))) {\n" +
        "+            ScopeModel scopeModel = channel.getUrl().getScopeModel();\n" +
        "+            if (scopeModel instanceof ModuleModel) {\n" +
        "+                scopeModel = scopeModel.getParent();\n" +
        "+            } else {\n" +
        "+                scopeModel = ApplicationModel.defaultModel();\n" +
        "+            }\n" +
        "+            String serializationSecurityCheck = ConfigurationUtils.getSystemConfiguration(\n" +
        "+                scopeModel).getString(SERIALIZATION_SECURITY_CHECK_KEY, \"true\");\n" +
        "+\n" +
        "+\n" +
        "+            if (Boolean.parseBoolean(serializationSecurityCheck)) {\n" +
        "                 CodecSupport.checkSerialization(frameworkModel.getServiceRepository(), path, version, serializationType);\n" +
        "             }\n" +
        "             Object[] args = DubboCodec.EMPTY_OBJECT_ARRAY;");
    System.out.println(ph.toString());
  }
}
