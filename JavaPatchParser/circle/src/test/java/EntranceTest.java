import java.io.IOException;
import java.sql.SQLException;

import org.example.Entrance;
import org.example.utils.Helper;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class EntranceTest {

  private static Entrance entrance;

  @BeforeClass
  public static void init() throws SQLException {
    // usePublic(); // 使用公共的环境,开发用
    useLocal(); // 使用本地的环境,实际跑的时候用
  }

  @Test
  public void test_calcAttributes() throws IOException {
    entrance.calcAttributes(); // 计算所有指标
  }


  //  @Test
  //  public void test_analyseMethodCircles() throws IOException {
  //    // entrance.printMethodCircles(10); // 打印圈复杂度的印详细和汇总
  //    entrance.analyseMethodCircles(10); // 根据圈复杂度分析,并输出统计结果
  //  }

  //  @Test
  //  public void test_analyseFileRows() throws IOException {
  //    entrance.printFileRows(2000 ); // 打印文件行数的详细和汇总
  //    // entrance.analyseFileRows(2000 ); // 根据文件行数分析,并输出统计结果
  //  }

  //  @Test
  //  public void test_analyseLineChars() throws IOException {
  //    entrance.printLineChars(80); // 打印文件行字符的详细和汇总
  //    // entrance.analyseLineChars(80); // 根据文件行字符数分析,并输出统计结果
  //  }

  //  @Test
  //  public void test_analyseMethodRows() throws IOException {
  //    // entrance.printMethodRows(30); // 打印函数行数的详细和汇总
  //    entrance.analyseMethodRows(30 ); // 根据函数行数分析,并输出统计结果
  //  }

  //  @Test
  //  public void test_analyseMethodNames() throws IOException {
  //    // entrance.printMethodNames(); // 打印函数行数的详细和汇总
  //    entrance.analyseMethodNames(); // 根据函数行数分析,并输出统计结果
  //  }

  //    @Test
  //    public void test_analyseClassNames() throws IOException {
  //      entrance.printClassNames(); // 打印函数行数的详细和汇总
  //      // entrance.analyseMethodRows(41 ); // 根据函数行数分析,并输出统计结果
  //    }

  //    @Test
  //    public void test_analyseMethodArgs() throws IOException {
  //      // entrance.printVariableNames(); // 打印函数参数个数的详细和汇总
  //      entrance.analyseMethodArgs(3 ); // 根据函数参数个数分析,并输出统计结果
  //    }

  //  @Test
  //  public void test_analyseTryCatchNum() throws IOException {
  //    entrance.printTryCatchNum(); // 打印函数参数个数的详细和汇总
  //    // entrance.analyseTryCatchNum(); // 根据函数参数个数分析,并输出统计结果
  //  }

  //    @Test
  //    public void test_calcSummary() throws IOException {
  //      entrance.calcSummary(); // 计算汇总值
  //    }

  private static void usePublic() throws SQLException {
    entrance = new Entrance(Helper.createPublicMongoClient());
  }

  private static void useLocal() throws SQLException {
    entrance = new Entrance(Helper.createLocalMongoClient());
  }

  @AfterClass
  public static void close() throws SQLException {
    entrance.close();
  }


}
