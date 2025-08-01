from pprint import pprint
from tree_sitter import Language, Parser
from index import get_node_content
from circle import get_circle

language = "javascript"
my_language = Language('./builds/my-languages.so', language)
parser = Parser()
parser.set_language(my_language)
query = my_language.query("(function_declaration) @function")


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


def get_params(params):
    """
    获取参数
    :param params:
    :return:
    """
    results = []
    params = params.named_children
    print(params)
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
        name = get_child(node, "identifier")
        params = get_child(node, "formal_parameters")
        body = get_child(node, "statement_block")
        name = get_node_content(content, name)
        params = [get_node_content(content, param) for param in params.named_children]
        # pprint(body)
        # circle = get_circle(body)
        circle, statements = get_circle(body)
        statements = [{"start": statement.start_point[0], "rows": statement.end_point[0] - statement.start_point[0] + 1, "type": statement.type, "content": content} for statement in statements]
        # statements = [get_node_content(content, statement) for statement in statements]
        # print(statements)
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
function commaSep1(rule) {
    if (typeof rule === 'string') {
        return sep1(rule, ',')
    } else {
        return sep1(rule, comma)
    }
    var greeting = "Good" + ((now.getHours() > 18) ? " evening." : " day.");
}

function sep1(rule, separator) {
  var greeting = "Good" + ((now.getHours() > 18) ? " evening." : " day.");
  return seq(rule, repeat(seq(separator, rule)))
}
    """
    results = parse_code(content)
    pprint(results)
