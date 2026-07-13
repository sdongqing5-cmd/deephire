"""Assessment Service - 测评服务"""

from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.assessment import Assessment, AssessmentStatus
from app.models.application import Application, ApplicationStatus
from app.services.application_service import ApplicationService


class AssessmentService:
    """测评服务"""

    @staticmethod
    async def invite_assessment(
        db: Session,
        application_id: str,
        hr_id: str,
        hr_name: str,
        assessment_type: str,
        assessment_url: str,
        valid_days: int = 7
    ) -> Assessment:
        """邀请候选人参加测评"""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        # 1. 创建测评记录
        assessment = Assessment(
            id=f"ast_{datetime.now().timestamp()}",
            application_id=application_id,
            candidate_id=application.candidate_id,
            assessment_type=assessment_type,
            assessment_url=assessment_url,
            status=AssessmentStatus.INVITED,
            invited_at=datetime.now(),
            invited_by=hr_id,
            expires_at=datetime.now() + timedelta(days=valid_days)
        )
        db.add(assessment)

        # 2. 转换应聘状态
        await ApplicationService.transition_status(
            db=db,
            application_id=application_id,
            to_status=ApplicationStatus.ASSESSMENT_INVITED,
            operator_id=hr_id,
            operator_name=hr_name,
            reason=f"邀请测评：{assessment_type}"
        )

        # 3. TODO: 发送测评邀请邮件
        # await EmailService.send_assessment_invitation(assessment)

        db.commit()
        db.refresh(assessment)
        return assessment

    @staticmethod
    async def start_assessment(
        db: Session,
        assessment_id: str
    ) -> Assessment:
        """候选人开始测评"""

        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")

        # 检查是否过期
        if assessment.expires_at and datetime.now() > assessment.expires_at:
            assessment.status = AssessmentStatus.EXPIRED
            db.commit()
            raise ValueError("Assessment has expired")

        # 更新状态
        assessment.status = AssessmentStatus.IN_PROGRESS
        assessment.started_at = datetime.now()
        db.commit()

        # 更新应聘状态
        await ApplicationService.transition_status(
            db=db,
            application_id=assessment.application_id,
            to_status=ApplicationStatus.ASSESSMENT_IN_PROGRESS,
            operator_id="candidate",
            operator_name="候选人",
            reason="开始测评"
        )

        db.refresh(assessment)
        return assessment

    @staticmethod
    async def complete_assessment(
        db: Session,
        assessment_id: str,
        score: int,
        result_data: dict,
        report_url: Optional[str] = None
    ) -> Assessment:
        """完成测评（通常由测评系统回调）"""

        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")

        # 更新测评记录
        assessment.status = AssessmentStatus.COMPLETED
        assessment.score = score
        assessment.result_data = str(result_data)  # JSON格式
        assessment.report_url = report_url
        assessment.completed_at = datetime.now()
        db.commit()

        # 更新应聘状态
        await ApplicationService.transition_status(
            db=db,
            application_id=assessment.application_id,
            to_status=ApplicationStatus.ASSESSMENT_COMPLETED,
            operator_id="system",
            operator_name="测评系统",
            reason=f"测评完成，得分：{score}"
        )

        db.refresh(assessment)
        return assessment

    @staticmethod
    async def fail_assessment(
        db: Session,
        assessment_id: str,
        hr_id: str,
        hr_name: str,
        reason: str
    ) -> Assessment:
        """测评未通过"""

        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")

        # 更新测评记录
        assessment.status = AssessmentStatus.FAILED
        db.commit()

        # 更新应聘状态
        await ApplicationService.transition_status(
            db=db,
            application_id=assessment.application_id,
            to_status=ApplicationStatus.ASSESSMENT_REJECTED,
            operator_id=hr_id,
            operator_name=hr_name,
            reason=f"测评未通过：{reason}"
        )

        db.refresh(assessment)
        return assessment

    @staticmethod
    def get_by_id(db: Session, assessment_id: str) -> Optional[Assessment]:
        """根据ID获取测评记录"""
        return db.query(Assessment).filter(Assessment.id == assessment_id).first()

    @staticmethod
    def get_by_application(db: Session, application_id: str) -> list[Assessment]:
        """根据应聘记录获取所有测评"""
        return db.query(Assessment).filter(
            Assessment.application_id == application_id
        ).order_by(Assessment.invited_at.desc()).all()

    @staticmethod
    def get_by_candidate(db: Session, candidate_id: str) -> list[Assessment]:
        """根据候选人获取所有测评"""
        return db.query(Assessment).filter(
            Assessment.candidate_id == candidate_id
        ).order_by(Assessment.invited_at.desc()).all()

    @staticmethod
    async def resend_invitation(
        db: Session,
        assessment_id: str,
        hr_id: str,
        hr_name: str,
        extend_days: int = 7
    ) -> Assessment:
        """重新发送测评邀请"""

        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")

        # 延长有效期
        assessment.expires_at = datetime.now() + timedelta(days=extend_days)
        assessment.status = AssessmentStatus.INVITED
        db.commit()

        # TODO: 重新发送邮件
        # await EmailService.send_assessment_invitation(assessment)

        db.refresh(assessment)
        return assessment
