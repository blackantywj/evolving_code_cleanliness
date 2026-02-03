package org.example.service;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.regex.Pattern;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;

import org.apache.commons.lang3.StringUtils;
import org.bson.Document;
import org.bson.conversions.Bson;
import org.bson.types.ObjectId;
import org.example.common.EntityScanner;
import org.example.domain.FileEntity;
import org.example.utils.Helper;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.serializer.SerializerFeature;
import com.mongodb.BasicDBObject;
import com.mongodb.MongoClient;
import com.mongodb.QueryOperators;
import com.mongodb.client.AggregateIterable;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.Accumulators;
import com.mongodb.client.model.Aggregates;
import com.mongodb.client.model.BsonField;
import com.mongodb.client.model.Projections;

import lombok.Data;
import lombok.Getter;
import lombok.experimental.Accessors;
import lombok.extern.slf4j.Slf4j;

@Getter
@Slf4j
public class GithubCommitService {

  private final MongoClient client;
  private final MongoCollection<Document> collection;

  public GithubCommitService(MongoClient client) {
    this.client = client;
    MongoDatabase database = client.getDatabase("github");
    collection = database.getCollection("github_commit_2022");
  }


  public List<String> listRepositories() {
  //   List<String> list = new ArrayList<>();
  //   list.add("google/nomulus");
  //   return list;
   return Helper.toList(collection.distinct("repository", String.class));
  }

  public EntityScanner<FileEntity> findFilesByRepository(String repository) {
    if (StringUtils.isBlank(repository)) {
      return EntityScanner.empty();
    }
    // 数据量太大, 不进行聚合
    Query query = new Query().setRepository(repository);
    EntityScanner<FileEntity> scanner = query.getFullScanner(collection, this::convert);
    scanner.setTotal(query.queryFullCount(collection));
    return scanner;
  }

  public EntityScanner<FileEntity> listByIdAndFileName(String id, String fileName) {
    if (StringUtils.isBlank(id) || StringUtils.isBlank(fileName)) {
      return EntityScanner.empty();
    }
    Query query = new Query().setId(id).setFileName(fileName);
    return query.getScanner(collection, this::convert);
  }


  public EntityScanner<FileEntity> listByCommitShaAndFileNameLike(String commitSha, String fileName) {
    if (StringUtils.isBlank(commitSha)) {
      return EntityScanner.empty();
    }
    Query query = new Query().setCommitSha(commitSha).setFileNameLike(fileName);
    return query.getScanner(collection, this::convert);
  }


  @Data
  @Accessors(chain = true)
  private static class Query {
    private String id;
    private String repository;
    private String commitSha;
    private String fileName;
    private String fileNameLike;
    private String committer;

    private BasicDBObject filter() {
      List<Bson> list = new ArrayList<>();
      if (StringUtils.isNotBlank(id)) {
        list.add(new BasicDBObject().append("_id", new ObjectId(id)));
      }
      if (StringUtils.isNotBlank(commitSha)) {
        list.add(new BasicDBObject().append("commit_sha", commitSha));
      }
      if (StringUtils.isNotBlank(repository)) {
        list.add(new BasicDBObject().append("repository", repository));
      }
      String startDate = "2022-01-01";
      String endDate = "2024-12-15";

      BasicDBObject releaseTimeCondition = new BasicDBObject("release_time",
              new BasicDBObject(QueryOperators.GTE, startDate)
                      .append(QueryOperators.LTE, endDate));
      list.add(releaseTimeCondition);
      list.add(new BasicDBObject().append("commit_sha", new BasicDBObject(QueryOperators.NE, null)));
      list.add(new BasicDBObject().append("datas", new BasicDBObject(QueryOperators.NE, null)));
      return new BasicDBObject().append(QueryOperators.AND, list);
//      if (StringUtils.isNotBlank(committer)) {
//        list.add(new BasicDBObject().append("committer", committer));
//      }
//      list.add(new BasicDBObject().append("committer", new BasicDBObject(QueryOperators.NE, null)));
      // list.add(new BasicDBObject().append("repository", new BasicDBObject(QueryOperators., null)));

    }

    private Bson datasFilter() {
      List<BasicDBObject> list = new ArrayList<>();
      if (StringUtils.isNotBlank(fileName)) {
        list.add(new BasicDBObject().append("datas.fileName", fileName));
      } else {
        list.add(new BasicDBObject().append("datas.fileName", Pattern.compile("java$")));
      }
      if (StringUtils.isNotBlank(fileNameLike)) {
        list.add(new BasicDBObject().append("datas.fileName", Pattern.compile(".*" + fileNameLike + ".*")));
      }
      list.add(new BasicDBObject().append("datas.patch", Pattern.compile("@@")));
      return new BasicDBObject().append(QueryOperators.AND, list);
    }

    public List<Bson> buildQuery() {
      List<Bson> agg = new ArrayList<>();
      agg.add(Aggregates.match(filter())); // 外层过滤
      agg.add(Aggregates.unwind("$datas"));
      agg.add(Aggregates.match(datasFilter())); // 内层过滤
      List<String> fieldNames = Arrays.asList("repository", "commit_sha", "message", "committer", "author", "datas");
      List<String> firstNames = Arrays.asList("repository", "commit_sha", "message", "committer", "author");
      agg.add(Aggregates.project(Projections.include(fieldNames)));
      List<BsonField> group = new ArrayList<>();
      group.add(new BsonField("mongoId", new BasicDBObject().append("$first", "$_id")));
      firstNames.forEach(name -> group.add(new BsonField(name, new BasicDBObject().append("$first", "$" + name))));
      group.add(new BsonField("datas", new BasicDBObject().append("$push", "$datas")));
      agg.add(Aggregates.group("_id", group));
      return agg;
    }

    public <T> EntityScanner<T> getScanner(MongoCollection<Document> collection, Function<Document, Stream<T>> func) {
      List<Bson> agg = buildQuery();
      log.info("查询语句 => " + agg);
      AggregateIterable<Document> documents = collection.aggregate(agg);
      return new EntityScanner<T>(documents.iterator(), func);
    }

    public <T> EntityScanner<T> getFullScanner(MongoCollection<Document> collection, Function<Document, Stream<T>> func) {
      return new EntityScanner<T>(collection.find(filter()).iterator(), func);
    }

    public int queryFullCount(MongoCollection<Document> collection) {
      List<Bson> agg = new ArrayList<>();
      agg.add(Aggregates.match(filter()));
      agg.add(Aggregates.project(new BasicDBObject().append("files", new BasicDBObject().append("$size", "$datas")).append("repository", 1)));
      agg.add(Aggregates.group("$repository", Accumulators.sum("files", "$files")));
      AggregateIterable<Document> aggregate = collection.aggregate(agg);
      return StreamSupport.stream(aggregate.spliterator(), false).mapToInt(d -> d.getInteger("files")).sum();
    }
  }

  private Stream<FileEntity> convert(Document document) {
    Object obj = document.get("datas");
    List<Document> datas = new ArrayList<>();
    if (obj instanceof Document) { 
      datas.add((Document) obj);
    } else if (obj instanceof List) {
      datas.addAll((Collection<? extends Document>) obj);
    } else {
      log.error("未知数据 => " + datas);
    }
    return datas.stream().map(data -> {
      Map<String, Object> map = new HashMap<>();
      map.putAll(document);
      map.putAll(data);
      if (map.containsKey("_id") && !map.containsKey("mongoId")) {
        map.put("mongoId", map.get("_id").toString());
      }
      if (map.containsKey("mongoId")) {
        map.put("mongoId", map.get("mongoId").toString());
      }
      try {
        return JSON.parseObject(JSON.toJSONString(map), FileEntity.class);
      } catch (Exception e) {
        log.info("JSON =>\n" + JSON.toJSONString(map, SerializerFeature.PrettyFormat));
        log.error("处理异常", e);
      }
      return null;
    });
  }


}
