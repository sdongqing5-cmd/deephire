"""Resume parsing service"""

import uuid
import re
import unicodedata
from datetime import datetime
from typing import Dict, Any
from pathlib import Path
import PyPDF2
from docx import Document

PLACEHOLDER_VALUES = {"待解析", "未知", "未知候选人", "无", "暂无", "n/a", "na", "none", "null"}
NAME_CHARS = r"A-Za-z\u2e80-\u9fff·"
SECTION_HEADING_TOKENS = [
    "个人信息", "基本信息", "联系方式", "报考信息", "教育背景", "教育经历",
    "实习经历", "工作经历", "项目经历", "校园经历", "社会实践", "荣誉技能",
    "荣誉奖项", "专业技能", "个人优势", "自我评价", "求职意向", "应聘岗位",
    "主修课程", "证书", "语言能力",
]
EXPERIENCE_SECTION_TOKENS = [
    "工作经历", "工作经验", "实习经历", "实习经验",
    "work experience", "internship experience", "internship",
]
EDUCATION_SECTION_TOKENS = [
    "教育背景", "教育经历", "education", "academic background",
]


def normalize_resume_text(value: Any) -> str:
    return unicodedata.normalize("NFKC", str(value))


def clean_text_value(value: Any) -> str | None:
    if value is None:
        return None

    cleaned = normalize_resume_text(value).strip().strip(":：,，;；")
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
        email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+", resume_text)
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
        lower_text = normalize_resume_text(resume_text).lower()
        skills = [
            skill
            for skill in skills_seed
            if skill.lower() in lower_text
        ]

        latest_experience = self.extract_latest_experience(resume_text)
        experience_years = self.extract_years_of_experience(resume_text)
        education_status = self.extract_education_status(resume_text)

        if education_status.get("is_currently_enrolled") and not latest_experience.get("is_current"):
            latest_experience = {
                "title": None,
                "company": None,
                "is_current": False,
            }

        return {
            "name": name,
            "email": email_match.group(0) if email_match else None,
            "phone": phone_match.group(0).strip() if phone_match else None,
            "current_company": latest_experience.get("company"),
            "current_title": latest_experience.get("title"),
            "years_of_experience": experience_years,
            "location": None,
            "skills": skills,
            "education": None,
            "latest_graduation_date": education_status.get("latest_graduation_date"),
            "is_currently_enrolled": education_status.get("is_currently_enrolled"),
            "summary": "\n".join(lines[:8])[:500] if lines else "",
            "parser": "rules",
        }

    def extract_name(self, lines: list[str], filename: str) -> str:
        label_patterns = [
            rf"(?:姓\s*名|姓名|名字|name)[ \t]*[:：][ \t]*([{NAME_CHARS}]{{2,8}})(?=\s|$)",
            rf"^([{NAME_CHARS} ]{{2,30}})[ \t]*(?:的)?(?:个人)?简历$",
        ]
        joined_head = "\n".join(lines[:20])
        for pattern in label_patterns:
            match = re.search(pattern, joined_head, re.IGNORECASE)
            if match:
                candidate = clean_text_value(match.group(1))
                if candidate and self.looks_like_name(candidate):
                    return candidate

        filename_name = self.extract_name_from_filename(filename)
        if filename_name:
            return filename_name

        for line in lines[:12]:
            if self.looks_like_name(line):
                return line

        fallback = clean_text_value(Path(filename).stem)
        if fallback and fallback.lower() not in {"resume", "cv"} and not self.is_section_heading(fallback):
            return fallback

        return "未知候选人"

    def looks_like_name(self, value: str) -> bool:
        value = normalize_resume_text(value).strip()
        lowered = value.lower()
        blocked_tokens = [
            "email", "phone", "tel", "@", "简历", "履历", "工作经历",
            "教育经历", "项目经历", "求职", "岗位", "应聘", "个人信息",
            "联系方式", "github", "linkedin",
        ]
        if any(token in lowered for token in blocked_tokens):
            return False
        if self.is_section_heading(value):
            return False
        if value.lower() in PLACEHOLDER_VALUES:
            return False

        compact = re.sub(r"\s+", "", value)
        if re.fullmatch(rf"[\u2e80-\u9fff·]{{2,6}}", compact):
            return True
        if re.fullmatch(r"[A-Za-z]+(?:\s+[A-Za-z]+){1,3}", value):
            return True
        return False

    def is_section_heading(self, value: str) -> bool:
        compact = re.sub(r"\s+", "", normalize_resume_text(value)).strip(":：")
        return compact in SECTION_HEADING_TOKENS

    def extract_name_from_filename(self, filename: str) -> str | None:
        stem = normalize_resume_text(Path(filename).stem)
        stem = re.sub(r"[【\[].*?[】\]]", " ", stem)
        stem = re.sub(r"(?:简历|resume|cv|个人|候选人)", " ", stem, flags=re.IGNORECASE)

        for candidate in re.findall(rf"[{NAME_CHARS}]{{2,6}}", stem):
            candidate = clean_text_value(candidate)
            if candidate and self.looks_like_name(candidate):
                return candidate

        return None

    def extract_years_of_experience(self, resume_text: str) -> int | None:
        explicit_years = self.extract_explicit_experience_years(resume_text)
        if explicit_years is not None:
            return explicit_years

        lines = [
            cleaned
            for line in resume_text.splitlines()
            if (cleaned := clean_text_value(line))
        ]

        section_text = self.extract_experience_section_text(lines)
        if not section_text:
            return None

        ranges = self.extract_date_ranges(section_text)
        if not ranges:
            return None

        merged_ranges = self.merge_month_ranges(ranges)
        total_months = sum(end - start + 1 for start, end in merged_ranges)
        return max(total_months // 12, 0)

    def extract_explicit_experience_years(self, resume_text: str) -> int | None:
        patterns = [
            re.compile(r"(?:工作年限|工作经验|从业年限|相关工作经验)[：:\s]*([0-9]{1,2}(?:\.[0-9])?)\s*年", re.IGNORECASE),
            re.compile(r"([0-9]{1,2}(?:\.[0-9])?)\s*年(?:工作经验|工作年限|从业经验|相关经验)", re.IGNORECASE),
        ]

        for pattern in patterns:
            match = pattern.search(normalize_resume_text(resume_text))
            if not match:
                continue

            value = float(match.group(1))
            return max(int(value), 0)

        return None

    def extract_latest_experience(self, resume_text: str) -> Dict[str, str | None]:
        lines = [
            cleaned
            for line in resume_text.splitlines()
            if (cleaned := clean_text_value(line))
        ]
        section_lines = self.extract_experience_section_lines(lines)
        if not section_lines:
            return {"title": None, "company": None, "is_current": False}

        latest_record: dict[str, str | int | None] | None = None

        for line in section_lines:
            parsed = self.parse_experience_header_line(line)
            if not parsed:
                continue

            if latest_record is None or int(parsed["sort_end"]) > int(latest_record["sort_end"]):
                latest_record = parsed

        if not latest_record:
            return {"title": None, "company": None, "is_current": False}

        return {
            "title": clean_text_value(latest_record.get("title")),
            "company": clean_text_value(latest_record.get("company")),
            "is_current": bool(latest_record.get("is_current")),
        }

    def extract_experience_section_text(self, lines: list[str]) -> str:
        return "\n".join(self.extract_experience_section_lines(lines))

    def extract_experience_section_lines(self, lines: list[str]) -> list[str]:
        collected: list[str] = []
        in_experience_section = False

        for line in lines:
            compact = re.sub(r"\s+", "", normalize_resume_text(line)).strip(":：")
            lowered = compact.lower()

            if any(token in lowered for token in EXPERIENCE_SECTION_TOKENS):
                in_experience_section = True
                continue

            if in_experience_section and self.is_section_heading(line):
                in_experience_section = False

            if in_experience_section:
                collected.append(line)

        return collected

    def extract_education_section_lines(self, lines: list[str]) -> list[str]:
        collected: list[str] = []
        in_education_section = False

        for line in lines:
            compact = re.sub(r"\s+", "", normalize_resume_text(line)).strip(":：")
            lowered = compact.lower()

            if any(token in lowered for token in EDUCATION_SECTION_TOKENS):
                in_education_section = True
                continue

            if in_education_section and self.is_section_heading(line):
                in_education_section = False

            if in_education_section:
                collected.append(line)

        return collected

    def extract_date_ranges(self, text: str) -> list[tuple[int, int]]:
        patterns = [
            re.compile(
                r"(?P<start_year>20\d{2}|19\d{2})[./-年\s]*(?P<start_month>1[0-2]|0?[1-9])?"
                r"(?:月)?\s*[至到~-]+\s*"
                r"(?:(?P<end_year>20\d{2}|19\d{2})[./-年\s]*(?P<end_month>1[0-2]|0?[1-9])?(?:月)?|(?P<present>至今|现在|present|current))",
                re.IGNORECASE,
            ),
        ]

        ranges: list[tuple[int, int]] = []
        for pattern in patterns:
            for match in pattern.finditer(text):
                start = self.year_month_to_index(
                    match.group("start_year"),
                    match.group("start_month"),
                )
                if start is None:
                    continue

                if match.group("present"):
                    now = datetime.now()
                    end = now.year * 12 + now.month - 1
                else:
                    end = self.year_month_to_index(
                        match.group("end_year"),
                        match.group("end_month"),
                    )

                if end is None or end < start:
                    continue
                ranges.append((start, end))

        return ranges

    def year_month_to_index(self, year: str | None, month: str | None) -> int | None:
        if not year:
            return None

        parsed_year = int(year)
        parsed_month = int(month) if month else 1
        parsed_month = min(max(parsed_month, 1), 12)
        return parsed_year * 12 + parsed_month - 1

    def merge_month_ranges(self, ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
        if not ranges:
            return []

        sorted_ranges = sorted(ranges)
        merged = [sorted_ranges[0]]

        for start, end in sorted_ranges[1:]:
            last_start, last_end = merged[-1]
            if start <= last_end + 1:
                merged[-1] = (last_start, max(last_end, end))
            else:
                merged.append((start, end))

        return merged

    def extract_education_status(self, resume_text: str) -> Dict[str, Any]:
        lines = [
            cleaned
            for line in resume_text.splitlines()
            if (cleaned := clean_text_value(line))
        ]
        education_lines = self.extract_education_section_lines(lines)
        if not education_lines:
            return {
                "latest_graduation_date": None,
                "is_currently_enrolled": None,
            }

        latest_end: tuple[int, int] | None = None

        for line in education_lines:
            for start, end in self.extract_date_ranges(line):
                year = end // 12
                month = end % 12 + 1
                candidate_end = (year, month)
                if latest_end is None or candidate_end > latest_end:
                    latest_end = candidate_end

        if latest_end is None:
            return {
                "latest_graduation_date": None,
                "is_currently_enrolled": None,
            }

        graduation_date = f"{latest_end[0]:04d}-{latest_end[1]:02d}"
        now = datetime.now()
        is_currently_enrolled = latest_end > (now.year, now.month)

        return {
            "latest_graduation_date": graduation_date,
            "is_currently_enrolled": is_currently_enrolled,
        }

    def parse_experience_header_line(self, line: str) -> dict[str, str | int] | None:
        normalized_line = normalize_resume_text(line)
        date_pattern = re.compile(
            r"(?P<start_year>20\d{2}|19\d{2})[./-年\s]*(?P<start_month>1[0-2]|0?[1-9])?"
            r"(?:月)?\s*[至到~-]+\s*"
            r"(?:(?P<end_year>20\d{2}|19\d{2})[./-年\s]*(?P<end_month>1[0-2]|0?[1-9])?(?:月)?|(?P<present>至今|现在|present|current))",
            re.IGNORECASE,
        )
        match = date_pattern.search(normalized_line)
        if not match:
            return None

        start_index = self.year_month_to_index(match.group("start_year"), match.group("start_month"))
        if start_index is None:
            return None

        is_current = bool(match.group("present"))
        if is_current:
            now = datetime.now()
            end_index = now.year * 12 + now.month - 1
        else:
            end_index = self.year_month_to_index(match.group("end_year"), match.group("end_month"))
            if end_index is None:
                return None

        prefix = normalized_line[:match.start()].strip(" |｜-—·•\t")
        if not prefix:
            return None

        segments = [
            clean_text_value(segment)
            for segment in re.split(r"\s{2,}|\t+|\s+\|\s+|\s+｜\s+", prefix)
        ]
        segments = [segment for segment in segments if segment]
        if not segments:
            return None

        if len(segments) >= 2:
            title, company = segments[0], segments[1]
        else:
            title, company = self.split_title_and_company(segments[0])

        if not title:
            return None

        return {
            "title": title,
            "company": company or "",
            "sort_end": end_index,
            "is_current": is_current,
        }

    def split_title_and_company(self, prefix: str) -> tuple[str | None, str | None]:
        title_tokens = [
            "专员", "助理", "经理", "顾问", "法务", "律师", "工程师", "产品", "运营",
            "实习生", "主管", "总监", "分析师", "研究员", "编辑", "设计师",
        ]

        for token in title_tokens:
            index = prefix.find(token)
            if index != -1:
                split_index = index + len(token)
                title = clean_text_value(prefix[:split_index])
                company = clean_text_value(prefix[split_index:])
                return title, company

        return clean_text_value(prefix), None

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
        parsed_data["resume_text"] = resume_text

        return parsed_data


# Global parser instance
resume_parser = ResumeParser()
