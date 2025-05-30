import os
import logging
import requests
import tempfile
from flask import Flask, request, render_template, jsonify, send_from_directory
from dotenv import load_dotenv
from http import HTTPStatus
from werkzeug.utils import secure_filename

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()  # 加载环境变量

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# 从环境变量获取配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-chat")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 2000))
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", 2000))
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

# 纪检监察专用系统提示
SYSTEM_PROMPT = """
你是一名专业的纪检监察AI助手，专门协助处理纪检相关业务。
你的职责包括：
1. 准确解读党纪法规和公司规章制度
2. 提供案例参考和量纪建议
3. 协助撰写和审核纪检监察文书
4. 保持回答严谨、准确、符合政策要求

重要提示：
- 引用法规条款时注明出处
- 提供量纪建议时说明理由
- 对于模糊问题要求澄清
- 不提供政治敏感性建议
"""

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 验证环境变量
if not DEEPSEEK_API_KEY:
    logger.error("DEEPSEEK_API_KEY 环境变量未设置！")
    raise ValueError("API密钥未配置")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def query_deepseek(user_input: str, document_context: str = "") -> str:
    """
    调用DeepSeek API获取响应（纪检监察专用）
    """
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # 构建消息 - 包含文档上下文
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if document_context:
        messages.append({"role": "user", "content": f"文档内容:\n{document_context}\n\n问题:{user_input}"})
    else:
        messages.append({"role": "user", "content": user_input})
    
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.6,
        "stop": None
    }
    
    try:
        logger.info(f"发送纪检监察请求到DeepSeek API，输入长度: {len(user_input)}")
        response = requests.post(
            API_URL, 
            json=payload, 
            headers=headers, 
            timeout=30
        )
        
        if response.status_code != HTTPStatus.OK:
            error_msg = f"API错误: HTTP {response.status_code} - {response.text}"
            logger.error(error_msg)
            return error_msg
        
        response_data = response.json()
        if "choices" not in response_data or not response_data["choices"]:
            logger.warning("API响应中未找到有效的选择项")
            return "无法获取有效响应，请稍后再试"
        
        return response_data["choices"][0]["message"]["content"]
    
    except requests.exceptions.Timeout:
        error_msg = "API请求超时"
        logger.error(error_msg)
        return error_msg
    except requests.exceptions.RequestException as e:
        error_msg = f"网络错误: {str(e)}"
        logger.error(error_msg)
        return error_msg
    except (KeyError, IndexError, TypeError, ValueError) as e:
        error_msg = f"响应解析错误: {str(e)}"
        logger.error(f"{error_msg}，原始响应: {response.text if 'response' in locals() else '无响应'}")
        return error_msg

def extract_keywords(text: str) -> list:
    """简单提取纪检监察关键词（实际项目应使用NLP技术）"""
    keywords = []
    for word in ["纪律", "条例", "法规", "违纪", "审查", "调查", "处分", "廉洁", "腐败", "案件"]:
        if word in text:
            keywords.append(word)
    return keywords[:3]  # 最多返回3个关键词

@app.route("/", methods=["GET"])
def home():
    """首页路由，返回纪检监察聊天界面"""
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """处理纪检监察聊天请求"""
    user_input = request.form.get("message", "").strip()
    document_ref = request.form.get("document_ref", "").strip()
    
    if not user_input:
        logger.warning("收到空输入")
        return jsonify({"response": "请输入有效内容"}), HTTPStatus.BAD_REQUEST
    
    if len(user_input) > MAX_INPUT_LENGTH:
        logger.warning(f"输入过长: {len(user_input)}字符")
        return jsonify({
            "response": f"输入内容过长，请控制在{MAX_INPUT_LENGTH}字符以内"
        }), HTTPStatus.BAD_REQUEST
    
    # 调用API（纪检监察专用）
    logger.info(f"处理纪检监察问题: {user_input[:50]}...")
    ai_response = query_deepseek(user_input, document_ref)
    
    # 提取关键词用于前端展示
    keywords = extract_keywords(user_input + ai_response)
    
    return jsonify({
        "response": ai_response,
        "keywords": keywords
    })

@app.route("/upload", methods=["POST"])
def upload_file():
    """处理纪检监察文档上传"""
    if 'file' not in request.files:
        return jsonify({"error": "未上传文件"}), HTTPStatus.BAD_REQUEST
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "未选择文件"}), HTTPStatus.BAD_REQUEST
    
    if not allowed_file(file.filename):
        return jsonify({"error": "不支持的文件类型，仅支持PDF、DOCX和TXT"}), HTTPStatus.BAD_REQUEST
    
    try:
        # 安全保存文件
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # 在实际项目中，这里应添加文档解析逻辑
        # 使用PyPDF2、python-docx等库提取文本内容
        
        # 模拟文档解析
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(1000)  # 只读取前1000字符作为演示
            
        # 生成文档摘要（实际项目应使用摘要算法）
        summary = "纪检监察文档摘要: " + content[:200] + "..." if len(content) > 200 else content
        
        # 提取关键词
        keywords = extract_keywords(content)
        
        return jsonify({
            "filename": filename,
            "summary": summary,
            "keywords": keywords
        })
    except Exception as e:
        logger.error(f"文档处理异常: {str(e)}")
        return jsonify({"error": "文档处理异常"}), HTTPStatus.INTERNAL_SERVER_ERROR

@app.errorhandler(HTTPStatus.BAD_REQUEST)
def bad_request(error):
    return jsonify({"error": "无效请求"}), HTTPStatus.BAD_REQUEST

@app.errorhandler(HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
def request_entity_too_large(error):
    return jsonify({
        "error": f"请求过大，请控制在{app.config['MAX_CONTENT_LENGTH'] // 1024 // 1024}MB以内"
    }), HTTPStatus.REQUEST_ENTITY_TOO_LARGE

@app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    logger.error(f"服务器错误: {error}")
    return jsonify({"error": "服务器内部错误"}), HTTPStatus.INTERNAL_SERVER_ERROR

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.getenv("PORT", 5000))
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug_mode,
        use_reloader=debug_mode
    )