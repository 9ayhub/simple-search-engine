# coding=utf-8
import unittest,os
from app import app

class WatchlistTestCase(unittest.TestCase):
    def setUp(self):
        # 使用flask提供的测试客户端进行测试，flask自带测试客户端，直接模拟终端请求
        self.client = app.test_client()

    # 测试URL
    def test_url(self):
        print("======测试URL========")
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('全文检索', data)
        self.assertIn('使用说明', data)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/404')
        data = response.get_data(as_text=True)
        self.assertIn('抱歉', data)
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/read')
        data = response.get_data(as_text=True)
        self.assertIn('序号', data)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/read')
        data = response.get_data(as_text=True)
        self.assertIn('序号', data)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/article/2010')
        data = response.get_data(as_text=True)
        self.assertIn('返回', data)
        self.assertEqual(response.status_code, 200)

        print("======URL测试通过========")

    # 测试输入为空
    def test_empty_query(self):
        print("=====测试输入为空======")
        response = self.client.post("/", data={"query": ""})
        data = response.get_data(as_text=True)
        self.assertIn('请在搜索框输入您想要查询的内容~', data)
        print("=====输入为空测试通过======")

    # 测试正常输入
    def test_normal_query(self):
        print("=====测试正常输入======")
        response = self.client.post("/", data={"query": "搜索"})
        data = response.get_data(as_text=True)
        self.assertIn('结果', data)
        print("=====正常输入测试通过======")

    # 测试继续搜索
    def test_continue_search(self):
        print("=====测试继续搜索======")
        response = self.client.post("/", data={"query": "【搜索】"})
        data = response.get_data(as_text=True)
        self.assertIn('结果', data)
        print("=====继续搜索测试通过======")

    # 测试错误输入
    def test_wrong_query(self):
        print("=====测试错误输入======")
        response = self.client.post("/", data={"query": "砖业"})
        data = response.get_data(as_text=True)
        self.assertIn('仍然', data)
        print("=====错误输入测试通过======")

    # 测试文章简介
    def test_article_introduction(self):
        print("=====测试文章简介======")
        path = "assets\\books"  # 文件夹目录
        files = os.listdir(path)  # 得到文件夹下的所有文件名称
        for file in files:
            title = file[0:-4]
            response = self.client.post("/read", data={"title": title})
            data = response.get_data(as_text=True)
            self.assertIn('阅读原文', data)
        print("=====文章简介测试通过======")

    # 测试阅读原文
    def test_article(self):
        print("=====测试阅读原文======")
        path = "assets\\books"  # 文件夹目录
        files = os.listdir(path)  # 得到文件夹下的所有文件名称
        for file in files:
            title = file[0:-4]
            path = '/article/' + title
            response = self.client.get(path)
            data = response.get_data(as_text=True)
            self.assertIn('返回', data)
            self.assertEqual(response.status_code, 200)
        print("=====阅读原文测试通过======")

if __name__ == '__main__':
    unittest.main()