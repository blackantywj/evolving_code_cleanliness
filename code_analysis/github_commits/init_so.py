from tree_sitter import Language

Language.build_library(
  # so文件保存位置
  'builds/my-languages.so',

  # vendor文件下git clone的仓库
  [
    'vendor/tree-sitter-java',
    'vendor/tree-sitter-python',
    'vendor/tree-sitter-c',
    'vendor/tree-sitter-cpp',
    'vendor/tree-sitter-javascript',
  ]
)
