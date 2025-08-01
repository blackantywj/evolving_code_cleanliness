from pprint import pprint

from tree_sitter import Language, Parser
from index import get_node_content

language = "python"

my_language = Language('builds/my-languages.so', language)
my_parser = Parser()
my_parser.set_language(my_language)

# query = PYTHON_LANGUAGE.query("""
# (function_definition
#   name: (identifier) @function.def)
#
# (call
#   function: (identifier) @function.call)
# """)

# query = PYTHON_LANGUAGE.query("""
# (function_definition
#   name: (identifier) @function.def
#   parameters: (parameters
#
#   ) @function.params
# )
# """)

query = my_language.query("""
(function_definition) @function
""")


def get_circle(body):
    """
    获取函数体中的圈复杂度
    :param body:
    :return:
    """
    circle = 0
    circle_type = ["if_statement", "for_statement", "while_statement", "try_statement", "conditional_expression"]
    for child in body.children:
        if child.type == "if_statement":
            print(child)
            circle += 1
        if child.type == "for_statement":
            print(child)
            circle += 1
        if child.type == "while_statement":
            print(child)
            circle += 1
        if child.type == "boolean_operator":
            """ and or """
            print(child)
            circle += 1
        if child.type == "try_statement":
            print(child)
            circle += 1
        if child.type == "conditional_expression":
            """ 三元运算符 a if a > b else b """
            print(child)
            circle += 1
        circle += get_circle(child)
    return circle


def parse_python(python_content):
    """
    解析python代码
    获取函数名、参数名、圈复杂度
    :param python_content: python代码
    :return:
    """
    function_datas = []
    tree = python_parser.parse(bytes(python_content, "utf8"))
    captures = query.captures(tree.root_node)
    for node, alias in captures:
        name, params, body = node.named_children
        params = params.named_children
        name = get_node_content(python_content, name)
        params = [get_node_content(python_content, param) for param in params]
        pprint(body)
        circle = get_circle(body)
        circle = circle + 1
        # get_node_content(python_content, body)
        print(name, params, circle)
        data = {
            "name"  : name,
            "params": params,
            "circle": circle
        }
        function_datas.append(data)
    split_content = python_content.splitlines()
    split_contents = [(i, len(line), line) for i, line in enumerate(split_content, 1)]
    result = {
        "function_datas": function_datas,
        "split_contents": split_contents
    }

    return result


if __name__ == '__main__':
    python_content = '''
    def main(a, b):
        for _ in range(10):
            if (a > b and a < b) or (a == b):
                print(1)
                return
            elif a > b:
                print(2)
            else:
                print(2)
            b = a if a > b else b
            for _ in range(10):
                print(a)
        for _ in range(10):
            for _ in range(10):
                print(a)
    def main1(a, b):
        for _ in range(10):
            for _ in range(10):
                print(a)
        for _ in range(10):
            for _ in range(10):
                print(a)
    '''
    results = parse_python(python_content)
    pprint(results)
