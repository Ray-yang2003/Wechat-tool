import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import jieba
from wordcloud import WordCloud
from collections import Counter
import re
import streamlit as st

st.set_option('deprecation.showPyplotGlobalUse', False)
st.title('我的第一个网页app')
st.write('这是一个关于微信聊天记录分析的数据可视化app')
# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体为黑体
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 读取CSV文件
df = pd.read_csv('msg.csv')
dfs = [df.query("IsSender == 0"), df.query("IsSender == 1")]
# TODO 数据预处理（根据需求进行）
# 只保留文本聊天
df = df[df['Type'] == 1]


labels = ['Nut','Potato']
data = {}
for i in range(2):
    data[labels[i]] = [
        len(dfs[i].query("Type == 1")),
        len(dfs[i].query("Type == 3")),
        len(dfs[i].query("Type == 34")),
        len(dfs[i].query("Type == 43")),
        len(dfs[i].query("Type == 47")),
    ]

# 聊天统计
data = (
    pd.DataFrame(data, index=["Text", "Image", "Voice", "Video", "Sticker"])
    .reset_index()
    .melt("index")
    .rename(columns={"index": "Type", "variable": "Person", "value": "Count"})
)
g = sns.catplot(data, kind="bar", x="Type", y="Count", hue="Person", palette="dark", alpha=0.6, height=6)

for ax in g.axes.ravel():
    for i in range(2):
        ax.bar_label(ax.containers[i], fontsize=9)
sns.move_legend(g, "upper right")
plt.yscale("log")

g.figure.set_size_inches(6, 5)
g.figure.set_dpi(150)
st.header('聊天类型统计')
st.pyplot()



# 只取'IsSender','StrContent','StrTime'列
selected_columns = ['IsSender', 'StrContent', 'StrTime']  # 将要保留的列名放入一个列表中
df = df[selected_columns]
# 每天聊天频率柱状图
# 将StrTime列的数据转换为日期时间格式
df['StrTime'] = pd.to_datetime(df['StrTime'])

# 创建一个新的Date列，只保留日期部分
df['Date'] = df['StrTime'].dt.date

# 根据每一天统计聊天频率
chat_frequency = df['Date'].value_counts().sort_index()

# 生成柱状图
plt.xlabel('Date')
plt.ylabel('Frequency')
plt.title('Chat Frequency by Day')

# 双方信息数量对比
sent_by_me = df[df['IsSender'] == 1]['StrContent']
sent_by_others = df[df['IsSender'] == 0]['StrContent']
# 统计数量
count_sent_by_me = len(sent_by_me)
count_sent_by_others = len(sent_by_others)
# 创建饼状图
labels = ['Nut', 'Potato']
sizes = [count_sent_by_me, count_sent_by_others]
colors = ['#FF6347','#9ACD32']

explode = (0, 0.05)
plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90)

plt.axis('equal')
plt.title('Comparison of the number of chats')
plt.legend()
st.header('聊天数量饼图')
st.pyplot()



# 根据一天中的每一个小时进行统计聊天频率，并生成柱状图
# 将时间字符串转换为时间类型并提取小时
df['DateTime'] = pd.to_datetime(df['StrTime'])
df['Hour'] = df['DateTime'].dt.hour

# 统计每个小时的聊天频率
hourly_counts = df['Hour'].value_counts().sort_index().reset_index()
hourly_counts.columns = ['Hour', 'Frequency']

# 绘制柱状图和数据拟合曲线
plt.figure(figsize=(10, 6))
ax = sns.barplot(x='Hour', y='Frequency', data=hourly_counts, color="#E6AAAA")

# 添加核密度估计曲线
sns.kdeplot(df['Hour'], color='#C64F4F', linewidth=1, ax=ax.twinx())

# 设置图形标题和轴标签
plt.title('Chat Frequency by Hour')
plt.xlabel('Hour of the Day')
plt.ylabel('Frequency')
st.header('每小时聊天频率和密度曲线')
st.pyplot()



# 词频分析
sent_by_me_text = ' '.join(sent_by_me.astype(str))
sent_by_others_text=' '.join(sent_by_others.astype(str))
all_text = ' '.join(df['StrContent'].astype(str))
# 使用jieba进行中文分词
words = list(jieba.cut(all_text, cut_all=False))
mywords = list(jieba.cut(sent_by_me_text, cut_all=False))
herwords = list(jieba.cut(sent_by_others_text, cut_all=False))


def is_chinese_word(word):
    for char in word:
        if not re.match(r'[\u4e00-\u9fff]', char):
            return False
    return True
with open('stopwords.txt', encoding='utf-8') as f: # 可根据需要打开停用词库，然后加上不想显示的词语
    con = f.readlines()
    stop_words = set() # 集合可以去重
    for i in con:
        i = i.replace("\n", " ")   # 去掉读取每一行数据的\n
        stop_words.add(i)
# stop_words

def correct(a):
    b=[]
    for word in a:
        if len(word) > 1 and is_chinese_word(word) and word not in stop_words:
            b.append(word)
    return b

Words = correct(words)
Mywords = correct(words)
Herwords = correct(herwords)

words_space_split = ' '.join(Words)
# print(words_space_split)
def word_fre_draw(a):
    a_counts = Counter(a)
    top_30_a= a_counts.most_common(30)
    words, frequencies = zip(*top_30_a)

    # 绘制水平柱状图
    plt.figure(figsize=(10, 15))
    plt.barh(words, frequencies, color='skyblue')
    plt.xlabel('Frequency')
    plt.ylabel('Words')
    plt.title('Top 30 Words in Chat Messages')

    st.pyplot()


# word_fre_draw(Words)
st.header('坚果的高频词')
word_fre_draw(Mywords)
st.header('土豆的高频词')
word_fre_draw(Herwords)

# 词云制作

wordcloud = WordCloud(font_path='‪C:\Windows\Fonts\STCAIYUN.TTF',  # 字体路径，例如'SimHei.ttf'
                      width=800, height=600,
                      background_color='white',  # 背景颜色
                      max_words=200,  # 最大显示的词数
                      max_font_size=100,  # 字体最大值
                      ).generate(words_space_split)

# 使用Matplotlib展示词云图
plt.figure(figsize=(10, 8))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')  # 关闭坐标轴
st.header('聊天词云')
st.pyplot()

# 一周贡献率
df['Weekday'] = df['StrTime'].dt.day_name()

# 计算每天的消息数量
weekday_counts = df['Weekday'].value_counts().reindex([
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
])

# 找出频率最高的那天
max_day = weekday_counts.idxmax()

# 制作饼状图
plt.figure(figsize=(8, 8))
explode = [0.1 if day == max_day else 0 for day in weekday_counts.index]  # 突出显示频率最高的那天
plt.pie(weekday_counts, labels=weekday_counts.index, explode=explode, autopct='%1.1f%%',
        startangle=140, colors=plt.cm.Paired.colors)
plt.title('Distribution of Messages During the Week')
st.header('一周中每天聊天数据')
st.pyplot()

# 最多的天数及月份
df['Date'] = pd.to_datetime(df['Date'])

# 提取年月日
df['YearMonth'] = df['Date'].dt.to_period('M')
df['Day'] = df['Date'].dt.date

# 计算每天的消息数量
daily_counts = df['Day'].value_counts()

# 找出消息最多的那一天
max_day = daily_counts.idxmax()
max_day_count = daily_counts.max()

# 计算每月的消息数量
monthly_counts = df['YearMonth'].value_counts()

# 找出消息最多的那个月
max_month = monthly_counts.idxmax()
max_month_count = monthly_counts.max()

# 打印结果
st.write(f"最多消息的一天是 {max_day}，共有 {max_day_count} 条消息。")
st.write(f"最多消息的一个月是 {max_month}，共有 {max_month_count} 条消息。")


# 计算消息总数
total_messages = len(df)

# 打印消息总数
st.write(f"一共聊了 {total_messages} 条消息。")

