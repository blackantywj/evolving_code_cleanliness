package org.example.common;

import lombok.Data;
import org.bson.Document;

import java.util.Iterator;
import java.util.function.Function;
import java.util.stream.Stream;

/**
 * @Author youhl002
 * @Date 2023/3/3 13:25
 */
@Data
public class EntityScanner<T> implements Iterable<T> {
  private final Iterator<Document> outer;
  private final Function<Document, Stream<T>> func;
  private Counter counter = new Counter(0);

  public EntityScanner(Iterator<Document> iterator, Function<Document, Stream<T>> func) {
    this.outer = iterator;
    this.func = func;
  }

  public void initCounter(int total) {
    this.counter = new Counter(total);
  }

  public EntityScanner(Iterable<Document> iterator, Function<Document, Stream<T>> func) {
    this.outer = iterator.iterator();
    this.func = func;
  }

  public static <T> EntityScanner<T> empty() {
    return new EntityScanner(Stream.empty().iterator(), null);
  }

  @Override
  public Iterator<T> iterator() {
    return new Iterator<T>() {
      Iterator<T> inner = null;
      T t = null;

      @Override
      public boolean hasNext() {
        while (true) {
          if (inner != null && inner.hasNext()) {
            t = inner.next();
            if (t != null) {
              return true;
            }
            counter.addError("空数据");
          } else if (!outer.hasNext()) {
            return false;
          }
          inner = func.apply(outer.next()).iterator();
        }
      }

      @Override
      public T next() {
        return t;
      }
    };
  }

  public int getTotal() {
    return counter.getTotal();
  }

  public void setTotal(int total) {
    counter = new Counter(total);
  }
}
