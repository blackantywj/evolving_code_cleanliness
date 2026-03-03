patch = """@@ -155,10 +155,8 @@ static int filter_frame(AVFilterLink *inlink, AVFrame *in)
     for (plane = 0; plane < rect->nb_planes; ++plane) {
         int hsub = plane == 1 || plane == 2 ? rect->hsub : 0;
         int vsub = plane == 1 || plane == 2 ? rect->vsub : 0;
-        int hdiv = 1 << hsub;
-        int vdiv = 1 << vsub;
-        int w = rect->width / hdiv;
-        int h = rect->height / vdiv;
+        int w = AV_CEIL_RSHIFT(rect->width, hsub);
+        int h = AV_CEIL_RSHIFT(rect->height, vsub);
         int xcenter = rect->cx * w;
         int ycenter = rect->cy * h;
         int k1 = rect->k1 * (1<<24);"""


def parse_patch(patch):
    """
    i.代码行数增加、减少、持平了多少，分别共计多少个
    ii.每行的字符数增加、减少、持平了多少，分别共计多少个
    :param patch:
    :return: 行数变化、字符数变化
    """
    lines = patch.splitlines()
    add_lines = []
    del_lines = []
    for line in lines:
        if line.startswith("+"):
            add_lines.append(line)
        elif line.startswith("-"):
            del_lines.append(line)
    add_lines = [line[1:] for line in add_lines]
    del_lines = [line[1:] for line in del_lines]
    add_lines_count = len(add_lines)
    del_lines_count = len(del_lines)
    total_lines_count = add_lines_count - del_lines_count
    add_lines_char_count = sum([len(line) for line in add_lines])
    del_lines_char_count = sum([len(line) for line in del_lines])
    add_lines_char_avg = add_lines_char_count / add_lines_count
    del_lines_char_avg = del_lines_char_count / del_lines_count
    total_lines_char_avg = add_lines_char_avg - del_lines_char_avg
    print(total_lines_count, total_lines_char_avg)
    return total_lines_count, total_lines_char_avg


if __name__ == '__main__':
    parse_patch(patch)
