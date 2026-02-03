package org.example.service;

import com.mongodb.BasicDBObject;
import com.mongodb.MongoClient;
import com.mongodb.QueryOperators;
import com.mongodb.client.AggregateIterable;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.Aggregates;
import com.mongodb.client.model.BsonField;
import lombok.Data;
import lombok.Getter;
import lombok.experimental.Accessors;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.bson.Document;
import org.bson.conversions.Bson;
import org.example.common.EntityScanner;
import org.example.domain.FileAnalyseEntity;
import org.example.utils.Helper;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.function.Function;
import java.util.stream.Stream;

@Getter
@Slf4j
public class FileAnalyseService {
  private final MongoClient client;
  private final MongoCollection<Document> collection;

  public FileAnalyseService(MongoClient client) {
    this.client = client;
    MongoDatabase database = client.getDatabase("github");
    collection = database.getCollection("file_analyse_correct_20250112");
  }

  public void saveOrUpdate(FileAnalyseEntity entity) {
    if (StringUtils.isBlank(entity.getGcMongoId()) || StringUtils.isBlank(entity.getFileName())) {
      log.warn("数据异常 => " + entity);
      return;
    }
    BasicDBObject query = new BasicDBObject();
    query.put("gcMongoId", entity.getGcMongoId());
    query.put("fileName", entity.getFileName());
    Document document = entity.toDocument();
    Document res = collection.findOneAndUpdate(query, new Document().append("$set", document));
    if (res == null) {
      collection.insertOne(document);
    }
  }

  @Data
  @Accessors(chain = true)
  private static class Query {
    private String repository;

    private <T> EntityScanner<T> findByThreshold(MongoCollection<Document> collection, Function<Document, Stream<T>> func, List<String> columns, int threshold) {
      boolean inArray = columns.stream().filter(c -> c.contains(".")).findFirst().isPresent();
      BasicDBObject filter = new BasicDBObject();
      if (StringUtils.isNotBlank(repository)) {
        filter.append("repository", repository);
      }
      BasicDBObject conditions = new BasicDBObject().append(QueryOperators.OR, Arrays.asList(
          new BasicDBObject()
              .append(columns.get(0), new BasicDBObject(QueryOperators.LTE, threshold))
              .append(columns.get(1), new BasicDBObject(QueryOperators.GT, threshold))
          , new BasicDBObject()
              .append(columns.get(0), new BasicDBObject(QueryOperators.GT, threshold))
              .append(columns.get(1), new BasicDBObject(QueryOperators.LTE, threshold))
      ));
      BasicDBObject sort = new BasicDBObject().append("gcMongoId", 1).append("fileName", 1);
      if (!inArray) {
        return new EntityScanner<>(collection.find(new BasicDBObject().append(QueryOperators.AND, Arrays.asList(filter, conditions))).sort(sort), func);
      }
      String unwind = StringUtils.substringBeforeLast(columns.get(0), ".");
      List<Bson> agg = new ArrayList<>();
      agg.add(Aggregates.match(filter)); // 外层过滤
      agg.add(Aggregates.unwind("$" + unwind));
      agg.add(Aggregates.match(conditions)); // 内层过滤
      List<BsonField> group = new ArrayList<>();

      List<String> firstNames = Arrays.asList("commitSha", "fileName", "gcMongoId", "newRows", "oldRows", "unixTime");
      group.add(new BsonField("_id", new BasicDBObject().append("_id", "$_id")));
      firstNames.forEach(name -> group.add(new BsonField(name, new BasicDBObject().append("$first", "$" + name))));
      group.add(new BsonField(unwind, new BasicDBObject().append("$push", "$" + unwind)));
      agg.add(Aggregates.group("_id", group));
      agg.add(Aggregates.sort(sort));
      AggregateIterable<Document> documents = collection.aggregate(agg);
      return new EntityScanner<T>(documents.iterator(), func);
    }

  }

  public EntityScanner<FileAnalyseEntity> findByCircle(String repository, int threshold) {
    if (StringUtils.isBlank(repository)) {
      return EntityScanner.empty();
    }
    Query query = new Query().setRepository(repository);
    return query.findByThreshold(collection, this::convert, Arrays.asList("methods.oldCircle", "methods.newCircle"), threshold);
  }

  public EntityScanner<FileAnalyseEntity> findMethodArgs(String repository, int threshold) {
    if (StringUtils.isBlank(repository)) {
      return EntityScanner.empty();
    }
    Query query = new Query().setRepository(repository);
    return query.findByThreshold(collection, this::convert, Arrays.asList("methods.oldArgs", "methods.newArgs"), threshold);
  }

  // public EntityScanner<FileAnalyseEntity> findMethodName(String repository) {
  //   if (StringUtils.isBlank(repository)) {
  //     return EntityScanner.empty();
  //   }
  //   Query query = new Query().setRepository(repository);
  //   return query.findByThreshold(collection, this::convert, Arrays.asList("methods.oldArgs", "methods.newArgs"), threshold);
  // }

  public EntityScanner<FileAnalyseEntity> findByMethodRows(String repository, int threshold) {
    if (StringUtils.isBlank(repository)) {
      return EntityScanner.empty();
    }
    Query query = new Query().setRepository(repository);
    return query.findByThreshold(collection, this::convert, Arrays.asList("methods.oldRows", "methods.newRows"), threshold);
  }

  public EntityScanner<FileAnalyseEntity> findByFileRows(String repository, int threshold) {
    if (StringUtils.isBlank(repository)) {
      return EntityScanner.empty();
    }
    Query query = new Query().setRepository(repository);
    return query.findByThreshold(collection, this::convert, Arrays.asList("oldRows", "newRows"), threshold);
  }

  public EntityScanner<FileAnalyseEntity> findByLineChars(String repository, int threshold) {
    if (StringUtils.isBlank(repository)) {
      return EntityScanner.empty();
    }
    Query query = new Query().setRepository(repository);
    return query.findByThreshold(collection, this::convert, Arrays.asList("lines.oldChars", "lines.newChars"), threshold);
  }

  private Stream<FileAnalyseEntity> convert(Document document) {
    return Stream.of(Helper.fromDocument(document, FileAnalyseEntity.class));
  }

  public EntityScanner<FileAnalyseEntity> findByRepository(String repository) {
    if (StringUtils.isBlank(repository)) {
      return EntityScanner.empty();
    }
    return new EntityScanner<>(collection.find(new BasicDBObject().append("repository", repository)), this::convert);
  }


}
