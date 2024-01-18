# 尤其要注意本脚本里面有四个绝对地址不要改成相对地址，我也不知道为什么否则很有可能报错，找不到文件地址
# 步骤一 导入PyQt5中相关的模块且创建一个自定义的QTextEdit来处理鼠标事件-------------------------------------------------------------------

from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QTextEdit
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QTextCursor
import sys
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QTextCursor


class MyTextEdit(QTextEdit):
    leftClicked = pyqtSignal(str)
    doubleClicked = pyqtSignal(str)
    middleClicked = pyqtSignal(QTextCursor)  # 定义一个新的信号，可以传递一个QTextCursor对象
    rightClicked = pyqtSignal(QTextCursor)
    def contextMenuEvent(self, event):
        # 不调用父类的contextMenuEvent方法，即可禁用上下文菜单
        pass

    def selectWordUnderCursor(self, cursor):#定义光标的左右选择范围为字母
        pos = cursor.position()
        text = self.toPlainText()

        # 查找左侧的字母
        start = pos
        while start > 0 and text[start - 1].isalpha():
            start -= 1

        # 查找右侧的字母
        end = pos
        while end < len(text) and text[end].isalpha():
            end += 1

        # 选取这个范围
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        return cursor.selectedText()

    def mousePressEvent(self, event):
        try:
            super().mousePressEvent(event)
            cursor = self.cursorForPosition(event.pos())
            word = self.selectWordUnderCursor(cursor)
            if word:
                if event.button() == Qt.LeftButton:
                    self.leftClicked.emit(word)
                elif event.button() == Qt.MiddleButton:
                    self.middleClicked.emit(cursor) #注意这里发射的是光标
                elif event.button() == Qt.RightButton:
                    self.rightClicked.emit(cursor)
        except Exception as e:
            print(f"mousePressEvent exception: {e}")

    def mouseDoubleClickEvent(self, event):
        try:
            super().mouseDoubleClickEvent(event)
            cursor = self.cursorForPosition(event.pos())
            word = self.selectWordUnderCursor(cursor)
            if word:
                self.doubleClicked.emit(word)
        except Exception as e:
            print(f"mouseDoubleClickEvent exception: {e}")



# 步骤二 初始化窗口并且设定日志打印
class MainWindow(QWidget):
    class TextStream(QObject):
        message = pyqtSignal(str)  # 创建一个信号

        def write(self, message):
            self.message.emit(str(message))  # 发射信号，传递输出信息
            sys.__stdout__.write(str(message))  # 将输出同时写入控制台

        def flush(self):
            pass  # 对于文本控件不需要实现flush方法

    def __init__(self):
        super().__init__()
        self.initUI()

        # 设置输出流重定向
        self.output_stream = self.TextStream()
        self.output_stream.message.connect(self.on_message)
        sys.stdout = self.output_stream  # 重定向标准输出
        sys.stderr = self.output_stream  # 重定向错误输出



    def on_message(self, message):
        # 在日志区域显示输出
        self.log_area.moveCursor(QTextCursor.End)
        self.log_area.insertPlainText(message)
        QApplication.processEvents()  # 处理所有事件

    def initUI(self):
        self.setWindowTitle("shushu大学英语阅读器版本1.0.0.0")  # 设置窗口标题

        # 创建网格布局
        layout = QGridLayout()

        # 创建输入区并设置为类的属性
        self.input_area = QTextEdit()
        self.input_area.setPlaceholderText("在这里输入英语文本")
        self.input_area.setStyleSheet("""
            
            background-color: #121212; /* 使用更暗的背景色 */
            color: #a9a9a9; /* 使用更柔和的文本色 */
        """)

        # 创建并设置日志区为类的属性
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)  # 设置为只读
        self.log_area.setPlaceholderText("在这里显示日志信息")
        self.log_area.setStyleSheet("""
            font-size: 20pt; /* 调整字号为20pt */
            
            background-color: #121212; /* 使用更暗的背景色 */
            color: #a9a9a9; /* 使用更柔和的文本色 */
        """)

        # 创建缓存区并设置为类的属性
        self.cache_area = MyTextEdit()
        self.cache_area.setReadOnly(True)
        self.cache_area.setPlaceholderText("在这里显示缓存的单词")
        self.cache_area.setStyleSheet("""
            font-size: 20pt; /* 调整字号为20pt */
            
            background-color: #121212; /* 使用更暗的背景色 */
            color: #a9a9a9; /* 使用更柔和的文本色 */
        """)

        # 创建阅读区并设置为类的属性
        self.read_area = MyTextEdit()
        # self.read_area.setReadOnly(True)
        self.read_area.setPlaceholderText("在这里显示阅读的内容")
         # 设置阅读区的样式
        self.read_area.setStyleSheet("""
            font-family: Arial; /* 设置字体为Arial */
            font-size: 20pt; /* 调整字号为20pt */
            font-weight: bold; /* 加粗字体 */                   
            background-color: #121212; /* 使用更暗的背景色 */
            color: #a9a9a9; /* 使用更柔和的文本色 */
            font-style:italic;
        """)

        # 创建详情区并设置为类的属性
        self.detail_area = QTextEdit()
        self.detail_area.setReadOnly(True)
        self.detail_area.setPlaceholderText("在这里显示单词的详情")
        self.detail_area.setStyleSheet("""
            font-size: 20pt; /* 调整字号为20pt */
            
            background-color: #121212; /* 使用更暗的背景色 */
            color: #a9a9a9; /* 使用更柔和的文本色 */
        """)


        # 添加控件到布局
        layout.addWidget(self.input_area, 0, 0, 1, 2)  # 输入区
        layout.addWidget(self.log_area, 0, 2, 1, 2)  # 日志区
        layout.addWidget(self.cache_area, 1, 0, 2, 1)  # 缓存区
        layout.addWidget(self.read_area, 1, 1, 2, 2)  # 阅读区
        layout.addWidget(self.detail_area, 1, 3, 2, 1)  # 详情区

        # 设置布局的行列比例
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(2, 2)
        layout.setColumnStretch(3, 1)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 3)
        layout.setRowStretch(2, 1)

        # 应用布局到窗口
        self.setLayout(layout)

        # 设置窗口为最大化
        self.showMaximized()


# 步骤三定义重载字典更新显示函数，并且设定输入区文本改变就调用此函数，和一些应用文字格式函数-------------------------------------------------------------------
import csv
import re
import os
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtGui import QTextCursor, QTextCharFormat

class MainWindow1(MainWindow):  # 继承自原有的MainWindow类

    def __init__(self):
        super().__init__()
        self.load_and_display()  # 初始化时加载并显示字典内容
        # 输入区文本发生变化时，连接到load_and_display函数
        self.input_area.textChanged.connect(self.load_and_display)
        self.load_cache_file()
        
    def load_cache_file(self):##这个主要是用在后面几步，但是这里应用style有用到
        cache_file_path = r"C:\Users\zourunze\Desktop\englishreader-fianl-python\cache\cache.txt"
        try:
            with open(cache_file_path, 'r', encoding='utf-8') as cache_file:
                self.cache_content = cache_file.read()
                self.cache_words = self.cache_content.split()
                self.cache_area.setPlainText(self.cache_content)
                print(f"Cache file 已经加载")
        except FileNotFoundError:
            print(f"Cache file '{cache_file_path}' not found.")




    def load_and_display(self):
        # 尝试加载CSV字典
        dict_path = r"C:\Users\zourunze\Desktop\englishreader-fianl-python\dict\mydict.csv"
        if os.path.exists(dict_path):
            print("正在加载CSV字典...")
            self.word_dict = self.load_word_dict(dict_path)  # 加载字典
            print("CSV字典加载成功！")
        else:
            print(f"字典文件 {dict_path} 不存在。")
            return  # 如果字典不存在则不进行任何操作
        # 获取输入区的文本并更新输出区
        text = self.input_area.toPlainText()
        self.update_output_area(text)

    def load_word_dict(self, file_path):###导入的词典经过了小写转换
        # 从文件路径加载词典
        word_dict = {}
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                word = row['word'].lower()  # 假设CSV中有'word'字段
                # 对exchange字段进行预处理，将其分割成列表
                exchange_data = row.get('exchange', '').lower()
                exchange_words = re.split(r'[^a-zA-Z]+', exchange_data)
                exchange_words = [ex_word for ex_word in exchange_words if ex_word]
                # 存储整行数据，并将exchange字段存储为列表
                word_dict[word] = {k: v.lower() for k, v in row.items() if k != 'word'}
                word_dict[word]['exchange'] = exchange_words
        return word_dict

    def update_output_area(self, text):
        self.read_area.clear()  # 清空读取区域
        # 使用正则表达式分割文本为单词和非单词，包括空格和标点
        tokens = re.findall(r'\b\w+\b|\s|[^(\w|\s)]', text)
        for token in tokens:
            if re.match(r'\b\w+\b', token):  # 如果是单词
                # print(f"这确实是一个单词而非符号【{token}】")
                self.if_it_is_word(token)
            else:  # 如果是非单词符号
                self.read_area.moveCursor(QTextCursor.End)
                self.read_area.setCurrentCharFormat(QTextCharFormat())  # 重置格式
                self.read_area.insertPlainText(token)  # 直接插入非单词字符


    def if_it_is_word(self, word):
        word_lower = word.lower()
        for key, word_info in self.word_dict.items():
            # 检查单词是否为字典的key
            if word_lower == key:
                # print(f"已经在字典里找到单词的基本形式: {key}")
                self.apply_style_to_word(word, word_info)
                return  # 单词已找到，退出函数
            elif word_lower in word_info.get('exchange', []):  # 直接检查预处理的列表
                # print(f"单词的变化形式: {', '.join(word_info['exchange'])}")
                self.apply_style_to_word(word, word_info)
                return  # 单词已找到，退出函数
        # 如果不在字典的key或exchange字段中，正常显示单词
        print(f"{word_lower}未查询不是key或exchange")
        self.read_area.insertHtml(word)

    def apply_style_to_word(self, word, word_info):
        # print(f"开始设置该单词{word}样式")
        # print(f"该单词{word}熟练度是"+"【"+word_info['familiarity']+"】")
        background_color = ''
        # 根据熟悉度设置背景颜色
        if word_info['familiarity'] == '2':
            background_color = 'background-color:pink;'  # 深黄色
        elif word_info['familiarity'] == '1':
            background_color = 'background-color:#FFD700;'  # 亮黄色

        #是否在缓冲区如果存在就加下划线
        if self.lemma(word.lower()) in self.cache_words:###文章对比的时候经过了小写转换和词形还原
            text_decoration = 'text-decoration: underline;'  # 添加下划线
        else:
            text_decoration = ''  # 无下划线

        text_color = ''
        # 根据标签设置文字颜色
        if word_info['tag'] == 'gk':
            text_color = 'color:green;'
        elif word_info['tag'] == 'mykaoyan':
            text_color = 'color:red;'
        elif word_info['tag'] == 'cet6':
            text_color = 'color:darkcyan;'
        elif word_info['tag'] == 'ielts':
            text_color = 'color:purple;'
        
        # 应用样式并添加带样式的单词到输出区
        styled_word = f'<span style="{background_color} {text_color} {text_decoration} font-style:normal;">{word}</span>'#在字典设置为非斜体
        self.read_area.insertHtml(styled_word)


# 步骤四定义阅读区和缓冲区的鼠标动作函数并运行-------------------------------------------------------------------
import requests
import pandas as pd
import threading
class MainWindow2(MainWindow1):  # 继承自MainWindow1
    def __init__(self):
        super().__init__()
  
        # 连接MyTextEdit的信号到对应的槽函数
        self.read_area.leftClicked.connect(self.on_left_click)
        self.read_area.doubleClicked.connect(self.on_double_click)
        self.read_area.middleClicked.connect(self.on_middle_click)
        self.read_area.rightClicked.connect(self.on_right_click)


    # 函数，用来处理单词的不同鼠标动作
    def on_left_click(self, word):
        print(f"{word}已被单击")


            
    def on_double_click(self, word):
        print(f"{word}已被双击")

        
    def on_middle_click(self, cursor):
        word = cursor.selectedText()
        print(f"{word}已被中键点击")
        word_lower = word.lower()
        for key, word_info in self.word_dict.items():
            # 检查单词是否为字典的key
            if word_lower == key or word_lower in word_info.get('exchange', []):  # 直接检查预处理的列表
                # 定义一个列表，存储你想要的键
                # 清空self.detail_area中的内容
                self.detail_area.clear()
                # 将单词本身插入到self.detail_area中
                self.detail_area.insertPlainText("word------------\n"+ key + "\n")
                # 遍历列表中的键，并插入到self.detail_area中
                # 如果键在字典中存在，就获取它的值，否则返回空字符串
                key="translation"
                val = word_info.get(key, "")
                val = val.replace("\\n", "\n")
                self.detail_area.insertPlainText(key + "-----\n" + val + "\n") 
                key="tag"
                val = word_info.get(key, "")
                self.detail_area.insertPlainText(key + "-------------\n" + val + "\n") 
                key="exchange"
                val = word_info.get(key, "")
                val = "\n".join(val)
                self.detail_area.insertPlainText(key + "--------\n" + val + "\n") 
                break
                
        else:# 如果不在字典的key或exchange字段中，正常显示单词
            print(f"{word_lower}该单词在字典里未查询到既不是key也不是exchange")
        # 在单独的线程中播放音频
        threading.Thread(target=play_stream, args=(word.lower(),)).start()#！！！！！！！这里是播放音频在步骤六实现


    def lemma(self,word):##还原词形这一步非常重要！！！！！！！！！！！！！！！！！！！
        for key, word_info in self.word_dict.items():
            if word.lower() == key or word.lower() in word_info.get('exchange', []):  # 直接检查预处理的列表
                print(f"经过lemma已找到还原词形{key}")
                return key
        else:
            print(f"经过lemma{word}在字典里无还原词形")
            return word

    def on_right_click(self,cursor):#给单词增加或者去掉标记，且将其加入缓冲区
        word = cursor.selectedText().lower()#小写转化
        print(f"{word}已被右键点击")
        word=self.lemma(word)
        cache_file_path = r"C:\Users\zourunze\Desktop\englishreader-fianl-python\cache\cache.txt"
        # 读取已有的单词到列表中
        existing_words = []
        if os.path.exists(cache_file_path):
            with open(cache_file_path, "r") as file:
                for line in file:
                    existing_words.append(line.strip())
        # 检查是否存在并删除单词
        if word in existing_words:
            print(f"!!!!!!!!!!!!{word}已存在缓冲区")
        else:
            # 如果不存在，则将单词添加到列表
            existing_words.append(word)
            print(f"{word}已经加入缓冲区")
        # 将更新后的单词列表写回缓存文件
        with open(cache_file_path, "w") as file:
            for w in existing_words:
                file.write(w + "\n")

        self.format_exchange(cursor)
        # 刷新显示
        self.load_cache_file()
        #缓冲区的光标切换到最后一行
        cachecursor = self.cache_area.textCursor()
        cachecursor.movePosition(QTextCursor.End)
        self.cache_area.setTextCursor(cachecursor)
        self.update_familiarity(word.lower(), "1")

    def format_exchange(self, cursor):
        format = cursor.charFormat()  # 获取当前光标位置的字符格式
        font = format.font()

        # 切换下划线状态：如果当前有下划线，则去掉；如果没有，则添加
        font.setUnderline(not font.underline())
        if font.underline():
            print("添加下划线")
        else:
            print("移除下划线")
        format.setFont(font)
        cursor.mergeCharFormat(format)  # 将修改后的字符格式应用于当前光标位置的字符



class MainWindow3(MainWindow2):  # 继承自MainWindow2
    def __init__(self):
        super().__init__()
        self.cache_area.leftClicked.connect(self.cache_left_click)
        self.cache_area.middleClicked.connect(self.cache_middle_click)
        self.cache_area.rightClicked.connect(self.cache_right_click)
        
    # 函数，用来处理单词的不同鼠标动作
    def cache_left_click(self, word):
        print(f"{word}已被单击")
        self.update_familiarity(word.lower(), "1")

    def cache_middle_click(self, cursor):
        word = cursor.selectedText()
        print(f"{word}已被中键点击")
        self.toggle_strikeout(cursor)# 下划线切换函数很关键
        cache_file_path = r"C:\Users\zourunze\Desktop\englishreader-fianl-python\cache\cache.txt"
        # 读取已有的单词到列表中
        existing_words = []
        if os.path.exists(cache_file_path):
            with open(cache_file_path, "r") as file:
                for line in file:
                    existing_words.append(line.strip())
        # 检查是否存在并删除单词
        if word in existing_words:
            existing_words.remove(word)
            print(f"已删除单词{word}")
        else:
            # 如果不存在，则将单词添加到列表
            existing_words.append(word)
            print(f"已恢复单词{word}")
        # 将更新后的单词列表写回缓存文件
        with open(cache_file_path, "w") as file:
            for w in existing_words:
                file.write(w + "\n")
        # 不刷新显示


    def toggle_strikeout(self, cursor):  # 定义一个名为toggle_strikeout的方法，接受cursor光标，有和没有下划线相互切换
        format = cursor.charFormat()  # 获取当前光标位置的字符格式
        if format.fontStrikeOut():  # 检查当前字符格式是否有划线
            format.setFontStrikeOut(False)  # 如果有划线，就删除划线
            print("准备恢复")
        else:
            format.setFontStrikeOut(True)  # 如果没有划线，就添加划线
            print("准备删除--加上划线")
        cursor.mergeCharFormat(format)  # 将修改后的字符格式应用于当前光标位置的字符


    def cache_right_click(self, cursor):
        word = cursor.selectedText()
        print(f"{word}已被右键点击")
        self.update_familiarity(word.lower(), "2")

    def update_familiarity(self, word, value):
    # 获取CSV文件的路径
        csv_file_path = r'C:\Users\zourunze\Desktop\englishreader-fianl-python\dict\mydict.csv'
        # 读取CSV文件
        df = pd.read_csv(csv_file_path,dtype=str)
        word=self.lemma(word)
        # 检查单词是否存在
        if word in df['word'].values:
            # 打印原始的familiarity值
            old_value = df.loc[df['word'] == word, 'familiarity'].iloc[0]
            print(f"单词 '{word}' 的原始熟悉度: {old_value}")
            # 更新familiarity值
            df.loc[df['word'] == word, 'familiarity'] = value
            # 保存更改回CSV文件
            df.to_csv(csv_file_path, index=False)
            # 打印新的familiarity值
            new_value = df.loc[df['word'] == word, 'familiarity'].iloc[0]
            print(f"单词 '{word}' 的更新熟悉度: {new_value}")
        else:
            print(f"单词 '{word}' 在字典中未找到。")




# 步骤五播放音频功能-------------------------------------------------------------------
import pygame 
import io
# 初始化pygame的mixer模块

def play_stream(word):
    try:
        url = f"http://dict.youdao.com/dictvoice?type=0&audio={word}"
        # 初始化pygame
        pygame.init()
        pygame.mixer.init()
        # 从URL获取音频流
        response = requests.get(url)
        if response.status_code == 200:
            audio_stream = io.BytesIO(response.content)
            pygame.mixer.music.load(audio_stream)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy(): 
                # 检查音乐流播放是否完成
                pygame.time.Clock().tick(10)
    except:
        print("Failed to retrieve audio.")

# 步骤六程序入口点-------------------------------------------------------------------
import traceback
if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)  # 创建应用对象
        mainWin = MainWindow3()  # 创建主窗口对象
        mainWin.show()  # 显示主窗口
        sys.exit(app.exec_())  # 运行应用，并在退出时清理
    except Exception as e:
        error_info = traceback.format_exc()
        print(f"发生异常: {e}\n{error_info}")
        # 这里可以将错误信息写入文件或进行其他形式的报告
        sys.exit(1)  # 退出程序并返回错误状态