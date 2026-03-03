from pprint import pprint
from tree_sitter import Language, Parser
from index import get_node_content
from circle import get_circle

language = "cpp"

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
    if not node:
        return None
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
    if not params:
        return results
    params = params.named_children
    # print(params)
    for param in params:
        # print(param)
        # print(get_node_content(content, param))
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
        # print(params)
        name = get_node_content(content, name)
        params = get_params(params, content)
        circle, statements = get_circle(body)
        statements = [{"start": statement.start_point[0], "rows": statement.end_point[0] - statement.start_point[0] + 1, "type": statement.type, "content": content} for statement in statements]
        # statements = [get_node_content(content, statement) for statement in statements]
        # pprint(body)
        circle = circle + 1
        # get_node_content(content, body)
        # print(name, params, circle)
        data = {
            "params"           : params,
            "circle"           : circle,
            "circle_statements": statements,
            "rows"             : rows,
            "start"            : start,
        }
        if name:
            function_datas[name] = data
    return function_datas


if __name__ == '__main__':
    content = '''float GetTriangleSquar(const point_float *pt0, const point_float pt1, const point_float pt2)  // 计算三角形面积
{
    point_float AB, BC;
    AB.x = pt1.x - pt0.x;
    AB.y = pt1.y - pt0.y;
    BC.x = pt2.x - pt1.x;
    BC.y = pt2.y - pt1.y;
    return fabs((AB.x * BC.y - AB.y * BC.x)) / 2.0f;
}'''
    results = parse_code(content)
    pprint(results)
