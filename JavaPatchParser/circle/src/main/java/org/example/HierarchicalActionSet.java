package org.example;

import com.github.gumtreediff.actions.model.*;
import com.github.gumtreediff.tree.ITree;
import lombok.Data;
import lombok.Getter;
import lombok.Setter;
import org.apache.commons.collections4.CollectionUtils;
import org.eclipse.jdt.core.dom.ASTNode;
import org.eclipse.jdt.core.dom.Block;
import org.eclipse.jdt.core.dom.IfStatement;
import org.example.circle.Circle;
import org.example.common.CompilationUnitWrapper;
import org.example.common.Segment;
import org.example.domain.ChangeMap;
import org.example.utils.Helper;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * Hierarchical code change actions of GumTree results
 *
 * @author kui.liu
 */
public class HierarchicalActionSet implements Comparable<HierarchicalActionSet> {

  private String astNodeType;
  private Action action;
  private Action parentAction;
  private String actionString;
  private Integer startPosition;
  private HierarchicalActionSet parent = null;
  private List<HierarchicalActionSet> subActions = new ArrayList<>();
  private JavaCompareActions jca;
  @Getter
  @Setter
  private PatchHunks.Hunk hunk;
  private ITreeWrapper oldTreeWrapper;
  private ITreeWrapper newTreeWrapper;

  public void setJavaCompareActions(JavaCompareActions jca) {
    this.jca = jca;
    getOldTreeWrapper().ifPresent(w -> w.setUnit(jca.getOldUnit()));
    getNewTreeWrapper().ifPresent(w -> w.setUnit(jca.getNewUnit()));
  }


  @Data
  public static class ITreeWrapper {
    private final ITree tree;
    private final ASTNode astNode;
    private final HierarchicalActionSet has;
    private CompilationUnitWrapper unit;
    private Segment segment;

    public ITreeWrapper(HierarchicalActionSet has, ITree tree) {
      this.has = has;
      this.tree = tree;
      this.astNode = (ASTNode) tree.getAttach();
    }

    public <T> T getParentNode(Class<T> clazz) {
      ASTNode current = astNode;
      while (current != null) {
        if (Helper.isInstanceOf(current.getClass(), clazz)) {
          return (T) current;
        }
        current = current.getParent();
      }
      return null;
    }


    public void setUnit(CompilationUnitWrapper unit) {
      this.unit = unit;
      this.segment = Segment.create(unit.getWrapper(), tree.getPos(), tree.getLength());
    }

    public Circle getCircle(Map<ASTNode, Circle> circleMap) {
      Circle circle = null;
      if (astNode != null) {
        circle = circleMap.get(astNode); // 根据原始节点向上搜索?
        if (circle == null && astNode.getParent() instanceof Block && astNode.getParent().getParent() instanceof IfStatement) {
          // 处理 else
          IfStatement ifs = (IfStatement) astNode.getParent().getParent();
          Block block = (Block) astNode.getParent();
          if (ifs.getElseStatement() == block) {
            circle = circleMap.get(ifs.getElseStatement());
          }
        }
      }
      return circle;
    }
  }

  public Optional<ITreeWrapper> getOldTreeWrapper() {
    return Optional.ofNullable(oldTreeWrapper);
  }

  public Optional<ITreeWrapper> getNewTreeWrapper() {
    return Optional.ofNullable(newTreeWrapper);
  }

  private boolean isInsert() {
    return action instanceof Insert;
  }

  private boolean isMove() {
    return action instanceof Move;
  }

  private boolean isUpdate() {
    return action instanceof Update;
  }

  public boolean isDelete() {
    return action instanceof Delete;
  }

  public String getAstNodeType() {
    return astNodeType;
  }

  public Action getAction() {
    return action;
  }

  public void setAction(Action action) {
    this.action = action;
    if (isDelete()) {
      this.oldTreeWrapper = new ITreeWrapper(this, action.getNode());
    } else if (isInsert()) {
      this.newTreeWrapper = new ITreeWrapper(this, action.getNode());
    } else if (isUpdate()) {
      Update update = (Update) action;
      this.oldTreeWrapper = new ITreeWrapper(this, update.getNode());
      this.newTreeWrapper = new ITreeWrapper(this, update.getNewNode());
    } else if (isMove()) {
      Move move = (Move) action;
      this.oldTreeWrapper = new ITreeWrapper(this, move.getNode());
      this.newTreeWrapper = new ITreeWrapper(this, move.getNewNode());
    } else {
      throw new RuntimeException("暂时不支持的action => " + action);
    }

  }

  public Action getParentAction() {
    return parentAction;
  }

  public void setParentAction(Action parentAction) {
    this.parentAction = parentAction;
  }

  public void setActionString(String actionString) {
    this.actionString = actionString;

    int atIndex = actionString.indexOf("@AT@") + 4;
    int lengthIndex = actionString.indexOf("@LENGTH@");
    if (lengthIndex == -1) {
      this.startPosition = Integer.parseInt(actionString.substring(atIndex).trim());
    } else {
      this.startPosition = Integer.parseInt(actionString.substring(atIndex, lengthIndex).trim());
    }

    String nodeType = actionString.substring(0, actionString.indexOf("@@"));
    nodeType = nodeType.substring(nodeType.indexOf(" ") + 1);
    this.astNodeType = nodeType;
  }

  public HierarchicalActionSet getParent() {
    return parent;
  }

  public void setParent(HierarchicalActionSet parent) {
    this.parent = parent;
  }

  public List<HierarchicalActionSet> getSubActions() {
    return subActions;
  }

  public void setSubActions(List<HierarchicalActionSet> subActions) {
    this.subActions = subActions;
  }

  @Override
  public int compareTo(HierarchicalActionSet o) {
//		int result = this.startPosition.compareTo(o.startPosition);
//		if (result == 0) {
//			result = this.length >= o.length ? -1 : 1;
//		}
    return this.startPosition.compareTo(o.startPosition);//this.action.compareTo(o.action);
  }

  private List<String> strList = new ArrayList<>();

  public String toCode() {
    StringBuilder sb = new StringBuilder();
    getOldTreeWrapper().map(w -> w.segment).ifPresent(s -> sb.append(String.format("== 老代码(%d-%d) ==\n%s\n", s.getStartRow(), s.getEndRow(), s.getCode())));
    getNewTreeWrapper().map(w -> w.segment).ifPresent(s -> sb.append(String.format("== 新代码(%d-%d) ==\n%s\n", s.getStartRow(), s.getEndRow(), s.getCode())));
    return sb.toString();
  }

  public String toStringWithCode() {
    StringBuilder sb = new StringBuilder();
    sb.append(this);
    sb.append(toCode());
    return sb.toString();
  }

  @Override
  public String toString() {
    String str = actionString;
    if (strList.size() == 0) {
      strList.add(str);
      for (HierarchicalActionSet actionSet : subActions) {
        actionSet.toString();
        List<String> strList1 = actionSet.strList;
        for (String str1 : strList1) {
          strList.add("---" + str1);
        }
      }
    } else {
      strList.clear();
      strList.add(str);
      for (HierarchicalActionSet actionSet : subActions) {
        actionSet.toString();
        List<String> strList1 = actionSet.strList;
        for (String str1 : strList1) {
          strList.add("---" + str1);
        }
      }
    }

    str = "";
    for (String str1 : strList) {
      str += str1 + "\n";
    }

    return str;
  }

  public ChangeMap createChangeMap(boolean deep) {
    ChangeMap changeMap = new ChangeMap();
    String k1 = getAstNodeType();
    String k2 = action.getName();
    if (ASTNodeMap.statements.contains(k1)) {
      changeMap.addOne(k1, k2);
    }
    List<HierarchicalActionSet> subActions = getSubActions();
    if (CollectionUtils.isNotEmpty(subActions)) {
      if (deep) {
        for (HierarchicalActionSet a : subActions) {
          changeMap.add(a.createChangeMap(true));
        }
      } else if (changeMap.isEmpty()) {
        for (HierarchicalActionSet a : subActions) {
          ChangeMap tmp = a.createChangeMap(false);
          if (!tmp.isEmpty()) {
            changeMap.add(tmp);
            break;
          }
        }
      }
    }
    return changeMap;
  }

  public int getOldStartRow() {
    return getOldTreeWrapper().map(w -> w.segment).map(m -> m.getStartRow()).orElse(0);
  }

  public int getNewStartRow() {
    return getNewTreeWrapper().map(w -> w.segment).map(m -> m.getStartRow()).orElse(0);
  }

  public int getOldFirstLineChars() {
    return getOldTreeWrapper().map(w -> w.segment).map(m -> m.getFirstLineChars()).orElse(0);
  }

  public int getNewFirstLineChars() {
    return getNewTreeWrapper().map(w -> w.segment).map(m -> m.getFirstLineChars()).orElse(0);
  }


}


function createCircleChangeMap() {
    changeMap = new ChangeMap();
    for each actionSet in actionSetList {
        oldCircle = calculateOldCircle(actionSet);
        newCircle = calculateNewCircle(actionSet);
        
        if oldCircle != newCircle {
            changeMap.add(actionSet.getAstNodeType(), actionSet.getActionName());
        }
        
        // 深度分析子动作
        for each subAction in actionSet.getSubActions() {
            changeMap.add(subAction.createCircleChangeMap());
        }
    }
    return changeMap;
}