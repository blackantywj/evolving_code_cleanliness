import jieba
from wordcloud import WordCloud


def get_content_from_txt(file_path_list: list):
    pref = ">" * 20
    prex = "<" * 20
    # 过滤词
    ignore_words = [pref, prex, "Reviewers","FLINK","python","Sergey","Nuyanzin","slinkydeveloper","task","test","apache",
                    "org","KAFKA","close","ISSUE","stream","client","Fix","fix","gmail","Add","add","support","code","set",
                    "use","new","commit","slf4j","frame","KIP","update","Update","reactor","Support","status","usage","WIP",
                    "Co","pom","xml","Remove","Rename","Refactor"]
    content = ''
    for file_path in file_path_list:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                flag = True
                for ignore_word in ignore_words:
                    if ignore_word in line:
                        print(line)
                        flag = False
                if flag:
                    content += line
    return content


def get_word_cloud(content):
    word_list = jieba.cut(content)
    word_space_split = ' '.join(word_list)
    wordcloud = WordCloud(background_color='white', width=1000, height=860, margin=2).generate(word_space_split)
    return wordcloud


def main():
    file_path1 = "wrong.txt"
    content = get_content_from_txt([file_path1])
    word_cloud = get_word_cloud(content)
    word_cloud.to_file('wrong.png')


if __name__ == '__main__':
    main()
