package org.example.circle;

import org.eclipse.jdt.core.dom.ASTNode;
import org.eclipse.jdt.core.dom.MethodDeclaration;

import java.util.HashMap;
import java.util.Map;

public class MethodCircle extends Circle {
  private final MethodDeclaration md;

  public MethodCircle(MethodDeclaration md) {
    super(md);
    this.md = md;
    if (md != null) {
      this.circle = 1;
      this.init();
    }
  }

  private void init() {
    if (md.getBody() != null) {
      appendStatements(md.getBody().statements());
    }
  }



}



