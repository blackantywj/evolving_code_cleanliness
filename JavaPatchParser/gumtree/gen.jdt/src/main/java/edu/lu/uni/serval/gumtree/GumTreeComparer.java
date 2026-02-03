package edu.lu.uni.serval.gumtree;

import com.github.gumtreediff.actions.ActionGenerator;
import com.github.gumtreediff.actions.model.Action;
import com.github.gumtreediff.matchers.Matcher;
import com.github.gumtreediff.matchers.Matchers;
import com.github.gumtreediff.tree.ITree;
import edu.lu.uni.serval.gumtree.GumTreeGenerator.GumTreeType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;

public class GumTreeComparer {

  private static Logger log = LoggerFactory.getLogger(GumTreeComparer.class);

  public List<Action> compareTwoCodeBlocksWithGumTree(String oldCodeBlock, String newCodeBlock) {
    // Generate GumTree.
    ITree oldTree = new GumTreeGenerator().generateITreeForCodeBlock(oldCodeBlock, GumTreeType.EXP_JDT);
    ITree newTree = new GumTreeGenerator().generateITreeForCodeBlock(newCodeBlock, GumTreeType.EXP_JDT);
    if (oldTree != null && newTree != null) {
      if (oldTree.isIsomorphicTo(newTree)) { // TODO: this method should be improved.
        System.out.println(true);
      }

      Matcher m = Matchers.getInstance().getMatcher(oldTree, newTree);
      m.match();
      ActionGenerator ag = new ActionGenerator(oldTree, newTree, m.getMappings());
      ag.generate();
      List<Action> actions = ag.getActions(); // change actions from bug to patch
      return actions;
    }

    return null;
  }

  public List<Action> compareTwoContentsWithGumTree(String prevContent, String revContent) {
    // Generate GumTree.
    ITree oldTree = null;
    ITree newTree = null;
    try {
      oldTree = new GumTreeGenerator().generateITreeForSourceCode(prevContent, GumTreeType.EXP_JDT);
      newTree = new GumTreeGenerator().generateITreeForSourceCode(revContent, GumTreeType.EXP_JDT);
    } catch (Exception e) {
      if (oldTree == null) {
        log.info("Null Tree of Previous File: " + prevContent);
      } else if (newTree == null) {
        log.info("Null Tree of Revised File: " + revContent);
      }
    }
    if (oldTree != null && newTree != null) {
      Matcher m = Matchers.getInstance().getMatcher(oldTree, newTree);
      m.match();
      ActionGenerator ag = new ActionGenerator(oldTree, newTree, m.getMappings());
      ag.generate();
      List<Action> actions = ag.getActions(); // change actions from bug to patch
      return actions;
    }

    return null;

  }
}
