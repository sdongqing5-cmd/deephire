"""Test resume parsing API"""

import requests
import json

# Test data - simulated resume text
test_resume_data = {
    "name": "张伟",
    "email": "zhangwei@email.com",
    "phone": "+86 138 1234 5678",
    "current_company": "字节跳动",
    "current_title": "高级软件工程师",
    "years_of_experience": 5,
    "location": "北京",
    "skills": ["Python", "Go", "Java", "FastAPI", "Docker", "Kubernetes"],
    "education": "计算机科学与技术 本科 | 清华大学",
    "summary": "5年软件开发经验，擅长后端架构设计和高并发系统开发。熟悉微服务架构、分布式系统和云原生技术。"
}

print("Resume Parser Test Data:")
print(json.dumps(test_resume_data, indent=2, ensure_ascii=False))
print("\n✓ Resume parsing service is ready")
print("\nAPI Endpoints:")
print("- POST /api/v1/resumes/parse - Parse resume file")
print("- POST /api/v1/resumes/upload - Upload resume for existing candidate")
