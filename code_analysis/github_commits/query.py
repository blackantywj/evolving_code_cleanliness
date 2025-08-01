from tree_sitter import Language, Parser
from index import get_node

# 声明CPP代码解析器
CPP_LANGUAGE = Language('builds/my-languages.so', 'cpp')
cpp_parser = Parser()
cpp_parser.set_language(CPP_LANGUAGE)

cpp_code_snippet = '''
#include <stdio.h>

int cmp(a, b){
	return a > b? 1: 0;
}

int main(){
	int arr[] = {5, 2, 1, 3, 0};
	char s[] = {'h', 'e', 'l', 'l', 'o'};
	int n = 5;
	int i, j, tmp;
	
	for(i = 0; i < n; i++){
		for(j = n - i - 1; j > 0; i--) {
			if(cmp(arr[j - 1], arr[j])){
				tmp = arr[j-1];
				arr[j-1] = arr[j];
				arr[j] = tmp;
			}
		}
	}
	printf("%s\n", s);
	return 0;
    希望有人能看到这里，🤗这是代码中错误的片段。
}
'''

cpp_code_snippet = '''
# include <stdio.h>

int cmp(a, b){
	return a > b? 1: 0;
}

'''

# 定义query
cpp_query_text = '''
(function_declarator declarator: (identifier)@1 )
(initializer_list) @2
(call_expression) @3
(assignment_expression  right:(_) @4)
(ERROR) @error
'''

my_query_text = '''
(function_definition) @1
'''
# query = CPP_LANGUAGE.query(cpp_query_text)
query = CPP_LANGUAGE.query(my_query_text)

# 获取具体语法树
tree = cpp_parser.parse(bytes(cpp_code_snippet, "utf8"))

root_node = tree.root_node
cpp_loc = cpp_code_snippet.split('\n')

# 获取节点
# capture: list[Node, str]
capture = query.captures(root_node)
for node, alias in capture:
    for child in node.children:
        get_node(cpp_loc, child)
        for child2 in child.children:
            get_node(cpp_loc, child2)
            for child3 in child2.children:
                get_node(cpp_loc, child3)
