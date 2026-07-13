"""Resume parsing service"""

import uuid
import re
from typing import Dict, Any
from pathlib import Path
import PyPDF2
from docx import Document

PLACEHOLDER_VALUES = {"待解析", "未知", "未知候选人", "无", "暂无", "n/a", "na", "none", "null"}


def clean_text_value(value: Any) -> str | None:
    if value is None:
        return None

    cleaned = str(value).strip().strip(":：,，;；")
    if not cleaned:
        return None
    if cleaned.lower() in PLACEHOLDER_VALUES:
        return None
    return cleaned


class ResumeParser:
    """Resume parser for PDF and DOCX files"""

    def __init__(self):
        self.upload_dir = Path("uploads/resumes")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save_file(self, file_content: bytes, filename: str) -> str:
        """
        Save uploaded file to disk

        Args:
            file_content: File content as bytes
            filename: Original filename

        Returns:
            Path to saved file
        """
        # Generate unique filename
        file_ext = Path(filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = self.upload_dir / unique_filename

        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)

        return str(file_path)

    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text content
        """
        text = ""
        try:
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

        return text.strip()

    def extract_text_from_docx(self, file_path: str) -> str:
        """
        Extract text from DOCX file

        Args:
            file_path: Path to DOCX file

        Returns:
            Extracted text content
        """
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            raise ValueError(f"Failed to extract text from DOCX: {str(e)}")

        return text.strip()

    def extract_text(self, file_path: str) -> str:
        """
        Extract text from resume file (PDF or DOCX)

        Args:
            file_path: Path to resume file

        Returns:
            Extracted text content
        """
        file_ext = Path(file_path).suffix.lower()

        if file_ext == ".pdf":
            return self.extract_text_from_pdf(file_path)
        elif file_ext in [".docx", ".doc"]:
            return self.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

    def parse_with_rules(self, resume_text: str, filename: str) -> Dict[str, Any]:
        """
        Parse resume text locally with deterministic rules.

        PDF/DOCX extraction gives raw text; this method extracts the fields
        needed by the recruiting workflow without calling an LLM.
        """
        email_match = re.search(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", resume_text)
        phone_match = re.search(
            r"(?:\+?86[-\s]?)?(?:1[3-9]\d{9}|\d{3,4}[-\s]?\d{7,8})",
            resume_text,
        )

        lines = [
            cleaned
            for line in resume_text.splitlines()
            if (cleaned := clean_text_value(line))
        ]
        name = self.extract_name(lines, filename)

        skills_seed = [
            "Python", "Java", "JavaScript", "TypeScript", "React", "Vue",
            "Node.js", "FastAPI", "Django", "Spring", "SQL", "PostgreSQL",
            "MySQL", "Redis", "Docker", "Kubernetes", "Linux", "机器学习",
            "深度学习", "项目管理", "销售", "运营", "产品",
        ]
        lower_text = resume_text.lower()
        skills = [
            skill
            for skill in skills_seed
            if skill.lower() in lower_text
        ]

        years_match = re.search(r"(\d{1,2})\s*(?:年|years?)", resume_text, re.IGNORECASE)

        return {
            "name": name,
            "email": email_match.group(0) if email_match else None,
            "phone": phone_match.group(0).strip() if phone_match else None,
            "current_company": None,
            "current_title": None,
            "years_of_experience": int(years_match.group(1)) if years_match else None,
            "location": None,
            "skills": skills,
            "education": None,
            "summary": "\n".join(lines[:8])[:500] if lines else "",
            "parser": "rules",
        }

    def extract_name(self, lines: list[str], filename: str) -> str:
        label_patterns = [
            r"(?:姓名|名字|name)[ \t]*[:：][ \t]*([A-Za-z\u4e00-\u9fff· ]{2,30})",
            r"^([A-Za-z\u4e00-\u9fff· ]{2,30})[ \t]*(?:的)?(?:个人)?简历$",
        ]
        joined_head = "\n".join(lines[:20])
        for pattern in label_patterns:
            match = re.search(pattern, joined_head, re.IGNORECASE)
            if match:
                candidate = clean_text_value(match.group(1))
                if candidate and self.looks_like_name(candidate):
                    return candidate

        for line in lines[:12]:
            if self.looks_like_name(line):
                return line

        fallback = clean_text_value(Path(filename).stem)
        if fallback and fallback.lower() not in {"resume", "cv"}:
            return fallback

        return "未知候选人"

    def looks_like_name(self, value: str) -> bool:
        lowered = value.lower()
        blocked_tokens = [
            "email", "phone", "tel", "@", "简历", "履历", "工作经历",
            "教育经历", "项目经历", "求职", "岗位", "应聘", "个人信息",
            "联系方式", "github", "linkedin",
        ]
        if any(token in lowered for token in blocked_tokens):
            return False
        if value.lower() in PLACEHOLDER_VALUES:
            return False

        compact = re.sub(r"\s+", "", value)
        if re.fullmatch(r"[\u4e00-\u9fff·]{2,6}", compact):
            return True
        if re.fullmatch(r"[A-Za-z]+(?:\s+[A-Za-z]+){1,3}", value):
            return True
        return False

    def parse_resume(
        self, file_content: bytes, filename: str
    ) -> Dict[str, Any]:
        """
        Parse resume file and extract structured information

        Args:
            file_content: File content as bytes
            filename: Original filename

        Returns:
            Structured resume data including file path
        """
        # Save file
        file_path = self.save_file(file_content, filename)

        # Extract text
        resume_text = self.extract_text(file_path)

        if not resume_text:
            raise ValueError("No text could be extracted from this resume")

        parsed_data = self.parse_with_rules(resume_text, filename)

        # Add file path and raw text
        parsed_data["resume_url"] = file_path
        parsed_data["resume_text"] = resume_text[:1000]  # First 1000 chars

        return parsed_data


# Global parser instance
resume_parser = ResumeParser()
