from pprint import pprint
from tree_sitter import Language, Parser
from index import get_node_content
from circle import get_circle

language = "c"

my_language = Language('./builds/my-languages.so', language)
parser = Parser()
parser.set_language(my_language)
query = my_language.query("(function_definition) @function")


def get_child(node, child_types):
    """
    获取子节点
    :param node:
    :param child_types:
    :return:
    """
    if not isinstance(child_types, list):
        child_types = [child_types]
    children = node.named_children
    for child in children:
        for child_type in child_types:
            if child.type == child_type:
                return child
    return None


def get_params(params, content):
    """
    获取参数
    :param params:
    :return:
    """
    results = []
    params = params.named_children
    for param in params:
        name = get_child(param, ["identifier", "pointer_declarator"])
        if not name:
            continue
        name = get_node_content(content, name)
        results.append(name)
    return results


def parse_code(content):
    """
    解析代码
    获取函数名、参数名、圈复杂度
    :param content: 代码
    :return:
    """
    function_datas = {}
    tree = parser.parse(bytes(content, "utf8"))
    captures = query.captures(tree.root_node)
    for node, alias in captures:
        start = node.start_point[0]
        rows = node.end_point[0] - node.start_point[0] + 1
        declarator = get_child(node, "function_declarator")
        body = get_child(node, "compound_statement")
        name = get_child(declarator, "identifier")
        params = get_child(declarator, "parameter_list")
        name = get_node_content(content, name)
        params = get_params(params, content)
        # pprint(body)
        circle, statements = get_circle(body)
        statements = [{"start": statement.start_point[0], "rows": statement.end_point[0] - statement.start_point[0] + 1, "type": statement.type, "content": content} for statement in statements]
        # statements = [get_node_content(content, statement) for statement in statements]
        circle = circle + 1
        # get_node_content(content, body)
        # print(name, params, circle)
        data = {
            "params"           : params,
            "circle"           : circle,
            "circle_statements": statements,
            "rows"             : rows,
            "start"            : start
        }
        if name:
            function_datas[name] = data
    return function_datas


if __name__ == '__main__':
    content = """
    Status CreateBiTree(BiTree *T, char *str){ //申请结点
    char ch;
    ch=getchar();
    if (ch=='#') //#代表空指针
        (*T)=NULL;
    else {
        (*T)=(BiTree) malloc(sizeof(BiTNode));//申请结点
        (*T)->data=ch;                        //生成根结点
        (*T)->visitcount = 0;
        CreateBiTree(&(*T)->lchild);             //构造左子树
        CreateBiTree(&(*T)->rchild) ;             //构造右子树
    }
    return 1;
}"""
    results = parse_code(content)
    pprint(results)
