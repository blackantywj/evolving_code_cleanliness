from tree_sitter import Language, Parser

# 注意C++对应cpp，C#对应c_sharp（！这里短横线变成了下划线）
# 看仓库名称
C_LANGUAGE = Language('builds/my-languages.so', 'c')
CPP_LANGUAGE = Language('builds/my-languages.so', 'cpp')
JAVA_LANGUAGE = Language('builds/my-languages.so', 'java')
PYTHON_LANGUAGE = Language('builds/my-languages.so', 'python')
JAVASCRIPT_LANGUAGE = Language('builds/my-languages.so', 'javascript')
# CS_LANGUAGE = Language('builds/my-languages.so', 'c_sharp')

# 举一个CPP例子
cpp_parser = Parser()
cpp_parser.set_language(CPP_LANGUAGE)

c_parser = Parser()
c_parser.set_language(C_LANGUAGE)

java_parser = Parser()
java_parser.set_language(JAVA_LANGUAGE)

python_parser = Parser()
python_parser.set_language(PYTHON_LANGUAGE)
# 这是b站网友写的代码，解析看看
cpp_code_snippet = '''
# include <stdio.h>

int cmp(a, b){
	return a > b? 1: 0;
}

'''
python_code_snippet = '''
def main():
    print("hello world")
'''

# 没报错就是成功
tree = cpp_parser.parse(bytes(cpp_code_snippet, "utf8"))
# 注意，root_node 才是可遍历的树节点
root_node = tree.root_node
# print(root_node)

# tree = python_parser.parse(bytes(python_code_snippet, "utf8"))
# root_node = tree.root_node
print(root_node)
for child in root_node.children:
    print(child)
    for child2 in child.children:
        print(child2)
        for child3 in child2.children:
            print(child3)
