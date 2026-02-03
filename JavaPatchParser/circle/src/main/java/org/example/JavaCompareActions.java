package org.example;

import com.github.gumtreediff.actions.ActionGenerator;
import com.github.gumtreediff.actions.model.Action;
import com.github.gumtreediff.matchers.Matcher;
import com.github.gumtreediff.matchers.Matchers;
import com.github.gumtreediff.tree.ITree;
import lombok.Getter;
import org.apache.commons.collections4.CollectionUtils;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.example.common.CompilationUnitWrapper;
import org.example.domain.MethodPair;
import org.example.utils.Helper;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Getter
public class JavaCompareActions {

  private final List<HierarchicalActionSet> gumTree;
  private final CompilationUnitWrapper oldUnit;
  private final CompilationUnitWrapper newUnit;
  private PatchHunks ph;

  private JavaCompareActions(CompilationUnitWrapper oldUnit, CompilationUnitWrapper newUnit) {
    this.oldUnit = oldUnit;
    this.newUnit = newUnit;
    Matcher m = Matchers.getInstance().getMatcher(oldUnit.getTree(), newUnit.getTree());
    m.match();
    ActionGenerator ag = new ActionGenerator(oldUnit.getTree(), newUnit.getTree(), m.getMappings());
    ag.generate();
    List<Action> actions = ag.getActions();
    this.gumTree = new HierarchicalRegrouper().regroupGumTreeResults(actions);
    this.fillJca();
  }

  public void fillJca() {
    this.gumTree.forEach(this::fillJca);
  }

  private void fillJca(HierarchicalActionSet has) {
    has.setJavaCompareActions(this);
    if (CollectionUtils.isNotEmpty(has.getSubActions())) {
      has.getSubActions().forEach(this::fillJca);
    }
  }

  public void setPh(PatchHunks ph) { // 设置patch
    this.ph = ph;
    if (ph == null) {
      return;
    }
    this.gumTree.forEach(this::fillPatch);
  }

  private void fillPatch(HierarchicalActionSet has) {
    // 绑定 patch
    if (has.getHunk() == null) {
      has.getOldTreeWrapper().ifPresent(w -> has.setHunk(ph.findBugHunk(w.getSegment())));
    }
    if (has.getHunk() == null) {
      has.getNewTreeWrapper().ifPresent(w -> has.setHunk(ph.findFixHunk(w.getSegment())));
    }
    if (CollectionUtils.isNotEmpty(has.getSubActions())) {
      has.getSubActions().forEach(this::fillPatch);
    }
  }


  public static JavaCompareActions create(String prevContent, String revContent) {
    // Generate GumTree.
    ITree oldTree = Helper.generateITreeForSourceCode(prevContent);
    ITree newTree = Helper.generateITreeForSourceCode(revContent);
    if (oldTree != null && newTree != null) {
      return new JavaCompareActions(createWrapper(prevContent, oldTree), createWrapper(revContent, newTree));
    }
    return null;
  }
  
  public static CompilationUnitWrapper createWrapper(String content, ITree tree) {
    return new CompilationUnitWrapper(content, tree);
  }
  
  public List<MethodPair> extractMethods() {
    List<HierarchicalActionSet> allActionSets = getGumTree();
    Map<MethodPair, MethodPair> map = new LinkedHashMap<>();
    for (HierarchicalActionSet actionSet : allActionSets) {
      // 直接根据节点去获取 UPD 和 MOV
      MethodDeclaration oldMethod = actionSet.getOldTreeWrapper().map(w -> w.getParentNode(MethodDeclaration.class)).orElse(null);
      MethodDeclaration newMethod = actionSet.getNewTreeWrapper().map(w -> w.getParentNode(MethodDeclaration.class)).orElse(null);
      if (oldMethod == null && actionSet.getHunk() != null) {
        oldMethod = oldUnit.findMethodDeclaration(actionSet.getHunk().getBug(), newMethod);
      }
      if (newMethod == null && actionSet.getHunk() != null) {
        newMethod = newUnit.findMethodDeclaration(actionSet.getHunk().getFix(), oldMethod);
      }
      // 必须两边都匹配上才进行后续比较
      if (newMethod == null || oldMethod == null) {
        continue;
      }
      MethodPair mp = new MethodPair();
      mp.setOldMethod(oldMethod);
      mp.setNewMethod(newMethod);
      mp.calcArgs(this);
      mp.calcRows(this);
      mp.calcNewArgsList(this);
      mp.calcOldArgsList(this);
      // 追加变化片段
      map.computeIfAbsent(mp, k -> mp).getActionSetList().add(actionSet);
    }
    return new ArrayList<>(map.keySet());
  }
}
