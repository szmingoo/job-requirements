from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import aiofiles
from pathlib import Path
from pydantic import BaseModel

UPLOAD_DIR = Path("/root/resume-screening/back/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

def empty_folder(folder_path=r"/root/resume-screening/back/uploads"):
    import os
    import glob
    import shutil
    files = glob.glob(os.path.join(folder_path, '*'))
    for f in files:
        if os.path.isfile(f):
            os.remove(f)
        elif os.path.isdir(f):
            shutil.rmtree(f)

class Requirements(BaseModel):
    # report: str
    position: str


import fitz  # PyMuPDF
import re
import jieba
import os
import requests

# 加载停用词
def load_stopwords(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        stopwords = set(file.read().split())
    return stopwords

stopwords = load_stopwords('/root/resume-screening/back/stopwords.txt')  # 替换为你的停用词文件路径

# 预处理文本
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\W+', ' ', text)
    words = jieba.cut(text)
    filtered_words = [word for word in words if word not in stopwords]
    return ' '.join(filtered_words)

# 提取PDF文本
def extract_text_from_pdf(pdf_path):
    if not os.path.isfile(pdf_path) or os.path.getsize(pdf_path) == 0:
        raise ValueError(f"Empty or invalid PDF document: {pdf_path}")
    document = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()
    return text



def generate_summary(prompt):
    s = requests.session()
    s.trust_env = False
    url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'
    header = {'Authorization': 'Bearer sk-115a76a9850a4b40812cb9a9be093a4b', 'Content-Type': 'application/json'}
    data = {
        "model": "qwen-max",
        "input": {
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个简历筛选专家，拥有30余年的全行业的人力资源管理经验，精通各个岗位人才的选拔标准，善于从众多简历中根据岗位要求进行简历筛选。能够深入理解各个岗位的职责、岗位任职资格。 细节控，你对简历的细节十分关注，能从简历细节中找到最佳的候选者。你有着很严谨、公平评判标准，能严格遵循第一性原理评判，精准识别简历中的优势和劣势。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        },
    }
    r = s.post(url=url, json=data, headers=header)
    return r.json()["output"]["text"]

rules_prompt='''
报告模板：
姓名|学历|期望薪资|工作经历简述|综合得分|亮点评价|缺点评价|联系方式

请结合上述任职要求、报告模板、候选人的简历生成报告：
1、综合得分：
简历中提及到的则计满分（注意！！无需关注熟练度，只要简历中提及到就计分），否则计为0分（例如任职要求中说明熟练掌握Excel【权重20分】，但此人简历中没有提及到则计为0分即总分减20，提及到了用过Excel但不熟练则计20分）！！！
切记不满足任职要求中【必须项】的简历综合得分计为0分（例如任职要求中【必须项】是女士，但是简历中的学历写的是男性，所以综合得分计为0分）！！！
累加所有符合任职要求的得分，最多100分。
你计算的好，将会有奖励！！！
2、工作经历简述：
简单总结的字数一定要在18个字以内，要简洁！！！
不需列出公司名字！！
不要列出时间段！！
只需列出每段工作的年限，每段经验要拆开说明不要做合并。
你总结的好，将会有奖励！！！
3、亮点评价：
简单总结的字数一定要在18个字以内，要简洁！！！
偏硬性，而不是软性如沟通能力好、性格好有耐心等；
不需说具体的工作经验年限，说有就行了。
你总结的好，将会有奖励！！！
4、缺陷评价：
简单总结的字数一定要在18个字以内，要简洁！！！
偏弱性，而不是强性如沟通能力差、性格差无耐心等。
你总结的好，将会有奖励！！！
5、学历：
只需要写当前最高学历，如初中、高中、专科、本科、研究生、博士，不要写其他（比如研究生在读、本科在读）
不要写学校名称！！
你总结的好，将会有奖励！！！
6、联系方式：
只展示手机号，不要写邮箱和微信号！！！


报告例子：
姓名	学历	期望薪资	工作经历简述	综合得分	亮点评价	缺点评价	联系方式
罗四	本科	5-8K	3年电催+5年销售管理	80	多元背景，兼具市场推广与电催经验	无直接法催/调解标注经验	17725163636
刘六	大专	10-11K	2年催收，1年电话销售，6年相关	70	多年电话销售及催收经验，带团队培训	缺乏法催/调解直接经验	151787996670
'''

def summarize_resumes(pdf_dir,position):
    summaries = []
    for pdf_file in os.listdir(pdf_dir):
        if pdf_file.endswith('.pdf'):
            pdf_path = os.path.join(pdf_dir, pdf_file)
            try:
                text = extract_text_from_pdf(pdf_path)
                preprocessed_text = preprocess_text(text)
                prompt = f"""
任职要求：
{position}

候选人的简历内容：
{preprocessed_text}

{rules_prompt}
"""
                summary = generate_summary(prompt)
                summaries.append((pdf_file, summary))
            except Exception as e:
                print(f"Error processing {pdf_file}: {e}")
    return summaries

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = UPLOAD_DIR / file.filename
        async with aiofiles.open(file_path, "wb") as buffer:
            while content := await file.read(1024):  # 分块读取文件以避免占用大量内存
                await buffer.write(content)
        return {"filename": file.filename + "上传成功"}
    except Exception as e:
        return {"error": str(e)}

def extract_html(position):
    pdf_dir = r"/root/resume-screening/back/uploads"
    summaries = summarize_resumes(pdf_dir,position)

    info = []
    for pdf_file, summary in summaries:
        info.append(f"Summary of {pdf_file}:\n{summary}\n")

    combined_prompt = f'''请根据{info}生成html表格报告代码，报告内容如下：
    姓名|学历|期望薪资|工作经历简述|综合得分|亮点评价|缺点评价|联系方式

    输出的html代码中要把每一行的边框颜色加深，table上面显示<h2>简历筛选报告</h2>，并把style设置为table {{width: 100%;border-collapse: collapse;border: 2px solid #000;}}th, td {{padding: 8px;text-align: center;border: 1px solid #000;}}th {{background-color: #f2f2f2;}}

    注意：请输出完整的信息！！要把每个人的报告信息都写到html代码里，不要省略、不要偷懒、不要说更多的信息、不要说按照上述格式等偷懒行为。
    '''

    response = generate_summary(combined_prompt)
    import re
    # 使用正则表达式提取从 <!DOCTYPE html> 到 </html> 的内容
    pattern = re.compile(r'<!DOCTYPE html>.*?</html>', re.DOTALL)
    match = pattern.search(response)
    if match:
        extracted_html = match.group(0)
        return extracted_html
    else:
        return "No match found"

@app.post("/api/report")
async def generate_report(requirements: Requirements):
    try:
        # report = requirements.report
        position = requirements.position
        # print("report:", report)
        print("position:", position)
        htmlContent = extract_html(position)
        if htmlContent:
            empty_folder()
            return {"code": "200", "message": "ok","htmlContent":htmlContent}
    except Exception as e:
        return {"error": str(e)}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8073, reload=True)

# uvicorn main:app --reload --port 8073
# gunicorn -w 4 -k uvicorn.workers.UvicornWorker farui:app -b 0.0.0.0:8072 --daemon
