#!/usr/bin/python
# -*- coding: GBK -*-
import re, string, jieba, codecs, os, math, time, sys, linecache
import Correct as correct
from collections import Counter
from scipy import stats

# ������������
def create_inverted_index_line(line, page, line_id):
    # �����ʱ�
    sp_data = line.split()

    # ��ƵTF�������ĵ��г��ֵĴ�����
    words = list(sp_data)
    dic_word_count = Counter(words)

    # ������index
    for word in dic_word_count.keys():
        if word in index.keys():
            exist_in_same_book = 0
            for i in index[word]:
                if i[0] == page:
                    exist_in_same_book = 1
                    i[1] += dic_word_count[word]
                    i[2].append(line_id)
                    break
            if exist_in_same_book:
                continue
            else:
                dic_word_count[word] = [page, dic_word_count[word], [line_id]]
                index[word].append(dic_word_count[word])
        else:
            dic_word_count[word] = [page, dic_word_count[word], [line_id]]
            index[word] = [dic_word_count[word]]


# ��ʼ��(������������,����tf-idf)
def init():
    # ����data\\page�µ��ļ�
    # ����ÿ���ļ�xx.txt�����ȷִʣ����ִʽ��д��fenci.txt
    # Ȼ���������������������index���ܵ��������ϲ�
    print('>>>������������')
    N = 0
    path = "assets\\books"  # �ļ���Ŀ¼
    files = os.listdir(path)  # �õ��ļ����µ������ļ�����
    N = len(files)
    s = []
    for file in files:  # �����ļ���
        line_id = 0
        if not os.path.isdir(file):  # �ж��Ƿ����ļ��У������ļ��вŴ�
            with open(path + "\\" + file, encoding='utf-8', errors='ignore') as open_file:
                for line in open_file.readlines():
                    # ȥ���
                    line = re.sub(r"[0-9\s+\.\!\/_,$%^*()?;��:-����+\"\']+|[+��������;:������~@#��%����&*����]+", " ", line)
                    # �ִ�
                    seg_list = jieba.cut(line, cut_all=True)
                    s = " ".join(seg_list)
                    #������������
                    create_inverted_index_line(s, file, line_id)
                    line_id += 1

    print('>>>����tf-idf')
    # �ĵ�Ƶ��df��������t���ĵ���������
    # w = (1 + log(tf))*log_10(N/df)
    i = 0
    for key in index.keys():
        df = len(index[key])
        i += 1
        for file_tf in index[key]:
            tf = file_tf[1]
            w = (1.0 + math.log(tf)) * math.log10(N / df)
            file_tf.append(w)


def get_content(page):
    file_path = 'assets/books/' + page[0]
    line_number = page[1][1] + 1
    content = linecache.getline(file_path, line_number).strip()
    return content


def pure_search(query):
    query = re.sub(r"[0-9\s+\.\!\/_,$%^*()?;��:-����+\"\']+|[+��������;:������~@#��%����&*����]+", " ", query)
    # �ִ�
    fenci = jieba.lcut(query)

    pages = {}
    for word in fenci:
        if word in index:
            for page in index[word]:
                # pages: {"Ѱ����˫.txt"�� [tf-idf, [line_id, line_id...]]}
                title = page[0]
                if title in pages:
                    pages[title][0] += page[3]
                    pages[title][1].append(page[2])
                else:
                    pages[title] = [page[3], [page[2]]]

    for key in pages.keys():
        page = pages[key]
        temp = []
        for i in page[1]:
            temp += i
        zhongshu = stats.mode(temp)[0][0]
        page[1] = zhongshu
    # page_list��[('��ˮ����.txt', [0.0, 27]), ('���ҹ��.txt', [0.0, 15])...], [(���⣬[tf-idf, ����])]
    page_list = sorted(pages.items(), key=lambda item: item[1], reverse=True)

    for item in page_list:
        item[1][1] = get_content(item)
        # ���ҵ�����content�е�λ�ã����滻����Ϊhtml��ʽ���Ӵ֣�
        query_position = []
        for word in fenci:
            nPos = item[1][1].find(word)
            if nPos != -1:
                query_position.append(nPos)
        query_position.sort()
        # ����content����
        MAX_LEN = 100
        if len(item[1][1]) > MAX_LEN:
            least_content =  query_position[-1] - query_position[0]
            start = query_position[0] - int(MAX_LEN/4)
            if start < 0: start = 0
            end = start + least_content + MAX_LEN - 10
            if end > start + MAX_LEN:
                end = start + MAX_LEN
            if end > len(item[1][1]):
                end = len(item[1][1])
            item[1][1] = item[1][1][start:end]
        for word in fenci:
            new_word = "<b style=\"color:#34ae7d\">" + word + "</b>"
            item[1][1] = item[1][1].replace(word, new_word);
        item[1][1] = "<p>" + item[1][1] + "</p>"
    # [('Ѱ����˫.txt', [0.27300127206373764, '�Ҳ�˵���֪��������������кö��ˣ����ǵ�������Ǳ�һ�����¡�����....']),...]
    return page_list


# [('Ѱ����˫.txt', [0.27300127206373764, '�Ҳ�˵���֪��������������кö��ˣ����ǵ�������Ǳ�һ�����¡�����....']),...]
def search_api(query):
    if len(index) == 0:
        init()
    return pure_search(query)


# שҵ-->רҵ
def correct_query_api(query):
    return correct.auto_correct_sentence(query)


index = {}


# ====================================================== #


def test():
    print(search_api('ѧϰ�ǻ�'))
    # print(correct_query_api("שҵ"))


# ����
if __name__ == '__main__':
    test()


