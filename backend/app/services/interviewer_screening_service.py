"""Interviewer Screening Service - 面试官筛选服务"""

from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.interviewer_screening import InterviewerScreening, ScreeningResult
from app.models.application import Application, ApplicationStatus
from app.services.application_service import ApplicationService


class InterviewerScreeningService:
    """面试官筛选服务"""

    @staticmethod
    async def push_to_interviewer(
        db: Session,
        application_id: str,
        interviewer_id: str,
        interviewer_name: str,
        hr_id: str,
        hr_name: str,
        comments: Optional[str] = None
    ) -> InterviewerScreening:
        """HR推送简历给面试官筛选"""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        # 检查是否已经推送给该面试官
        existing = db.query(InterviewerScreening).filter(
            InterviewerScreening.application_id == application_id,
            InterviewerScreening.interviewer_id == interviewer_id
        ).first()
        if existing:
            raise ValueError(f"Application already pushed to interviewer {interviewer_name}")

        # 1. 创建筛选记录
        screening = InterviewerScreening(
            id=f"scr_{datetime.now().timestamp()}",
            application_id=application_id,
            interviewer_id=interviewer_id,
            interviewer_name=interviewer_name,
            result=None,  # 待筛选
            comments=comments,
            created_at=datetime.now()
        )
        db.add(screening)

        # 2. 转换应聘状态
        await ApplicationService.transition_status(
            db=db,
            application_id=application_id,
            to_status=ApplicationStatus.PUSHED_TO_INTERVIEWER,
            operator_id=hr_id,
            operator_name=hr_name,
            reason=f"推送给面试官 {interviewer_name} 筛选"
        )

        # 3. TODO: 发送通知给面试官
        # await NotificationService.notify_interviewer_screening(screening)

        db.commit()
        db.refresh(screening)
        return screening

    @staticmethod
    async def submit_screening_result(
        db: Session,
        screening_id: str,
        interviewer_id: str,
        interviewer_name: str,
        result: ScreeningResult,
        comments: str
    ) -> InterviewerScreening:
        """面试官提交筛选结果"""

        screening = db.query(InterviewerScreening).filter(
            InterviewerScreening.id == screening_id
        ).first()
        if not screening:
            raise ValueError(f"Screening {screening_id} not found")

        # 验证权限
        if screening.interviewer_id != interviewer_id:
            raise ValueError("You are not authorized to submit this screening result")

        # 检查是否已经提交过
        if screening.result is not None:
            raise ValueError("Screening result already submitted")

        # 1. 更新筛选记录
        screening.result = result
        screening.comments = comments
        screening.screened_at = datetime.now()
        db.commit()

        # 2. 更新应聘状态
        if result == ScreeningResult.PASS:
            await ApplicationService.transition_status(
                db=db,
                application_id=screening.application_id,
                to_status=ApplicationStatus.INTERVIEWER_SCREENING_PASSED,
                operator_id=interviewer_id,
                operator_name=interviewer_name,
                reason="面试官筛选通过"
            )
        else:
            await ApplicationService.transition_status(
                db=db,
                application_id=screening.application_id,
                to_status=ApplicationStatus.INTERVIEWER_SCREENING_REJECTED,
                operator_id=interviewer_id,
                operator_name=interviewer_name,
                reason="面试官筛选未通过"
            )

        # 3. TODO: 发送通知给HR
        # await NotificationService.notify_hr_screening_result(screening)

        db.refresh(screening)
        return screening

    @staticmethod
    def get_pending_screenings(
        db: Session,
        interviewer_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[list[InterviewerScreening], int]:
        """获取面试官的待筛选简历列表"""

        query = db.query(InterviewerScreening).filter(
            InterviewerScreening.interviewer_id == interviewer_id,
            InterviewerScreening.result == None  # 未筛选
        )

        total = query.count()
        items = query.order_by(InterviewerScreening.created_at.desc()).offset(offset).limit(limit).all()

        return items, total

    @staticmethod
    def get_by_id(db: Session, screening_id: str) -> Optional[InterviewerScreening]:
        """根据ID获取筛选记录"""
        return db.query(InterviewerScreening).filter(
            InterviewerScreening.id == screening_id
        ).first()

    @staticmethod
    def get_by_application(
        db: Session,
        application_id: str
    ) -> list[InterviewerScreening]:
        """获取应聘记录的所有筛选记录"""
        return db.query(InterviewerScreening).filter(
            InterviewerScreening.application_id == application_id
        ).order_by(InterviewerScreening.created_at.desc()).all()

    @staticmethod
    def get_by_interviewer(
        db: Session,
        interviewer_id: str,
        result: Optional[ScreeningResult] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[list[InterviewerScreening], int]:
        """获取面试官的所有筛选记录（可按结果过滤）"""

        query = db.query(InterviewerScreening).filter(
            InterviewerScreening.interviewer_id == interviewer_id
        )

        if result is not None:
            query = query.filter(InterviewerScreening.result == result)

        total = query.count()
        items = query.order_by(InterviewerScreening.created_at.desc()).offset(offset).limit(limit).all()

        return items, total
