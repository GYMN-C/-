# 纪检监察智能助手系统

基于DeepSeek大模型的电网+纪检监察智能审核平台，提供法规检索、量纪参考、案例分析和文书审核等核心功能。


## 功能特性

- **法规条款智能检索**：快速查找党纪法规和企业规章制度
- **违纪行为量纪参考**：提供类似案例的处理标准参考
- **案例库智能分析**：基于历史案例进行智能匹配分析
- **文书规范性审核**：自动检查纪检监察文书的规范性
- **文档智能处理**：支持PDF/DOCX/TXT文档上传与解析
- **安全保密设计**：机密级数据保护机制

## 技术架构

- 前端：HTML5 + CSS3 + JavaScript
- 后端：Python Flask
- AI引擎：DeepSeek大模型API
- 文档处理：PyPDF2/python-docx/pdfminer.six(需额外安装)

## 安装部署

### 环境要求

- Python 3.8+
- DeepSeek API密钥

### 安装步骤

1. 克隆仓库：
   ```bash
   git clone https://github.com/your-repo/discipline-inspection-ai.git
   cd discipline-inspection-ai
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境变量：
   ```bash
   cp .env.example .env
   # 在.env文件中填写您的DeepSeek API密钥
   ```

4. 运行应用：
   ```bash
   python app.py
   ```

5. 访问应用：
   ```
   http://localhost:5000
   ```

### 生产部署

推荐使用Gunicorn+Nginx部署：
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 使用说明

1. 上传纪检监察相关文档(PDF/DOCX/TXT)
2. 选择需要的功能模块
3. 输入问题或选择预设问题模板
4. 获取AI生成的参考建议

## 开发路线图

- [ ] 集成完整文档解析能力
- [ ] 增加多轮对话上下文支持
- [ ] 开发案件审查报告自动生成功能
- [ ] 构建电网行业违纪行为知识图谱

## 贡献指南

欢迎提交Issue和Pull Request。对于重大变更，请先开Issue讨论。

## 许可证

本项目采用 [MIT License](LICENSE)。

## 免责声明

本系统提供的建议仅供参考，实际执纪工作应遵循相关法律法规和程序规定。

---

**纪检监察信息化建设五年规划 - 电网+大模型数据处理系统**
```
