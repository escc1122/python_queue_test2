"""
Queue Names 集中管理
"""

class QueueNames:
    """所有 Queue 名稱的定義"""
    
    # ========== Email 相關 ==========
    EMAIL_WELCOME = "email.welcome"
    EMAIL_NOTIFICATION = "email.notification"
    EMAIL_RESET_PASSWORD = "email.reset_password"
    
    # ========== Data 相關 ==========
    DATA_PROCESS = "data.process"
    DATA_ANALYZE = "data.analyze"
    DATA_EXPORT = "data.export"
    
    # ========== Report 相關 ==========
    REPORT_GENERATE = "report.generate"
    REPORT_SEND = "report.send"
    
    # ========== 共用 Queue ==========
    NOTIFICATION = "notification"
    LOG_USER_ACTION = "log.user_action"
    LOG_SYSTEM_EVENT = "log.system_event"


class ContextQueues:
    """各個 Context 監聽的 Queue 配置"""
    
    EMAIL = [
        QueueNames.EMAIL_WELCOME,
        QueueNames.EMAIL_NOTIFICATION,
        QueueNames.EMAIL_RESET_PASSWORD,
        QueueNames.NOTIFICATION,  # 共用
        QueueNames.LOG_USER_ACTION,  # 共用
    ]
    
    DATA = [
        QueueNames.DATA_PROCESS,
        QueueNames.DATA_ANALYZE,
        QueueNames.DATA_EXPORT,
        QueueNames.LOG_SYSTEM_EVENT,  # 共用
    ]
    
    REPORT = [
        QueueNames.REPORT_GENERATE,
        QueueNames.REPORT_SEND,
        QueueNames.NOTIFICATION,  # 共用
        QueueNames.LOG_USER_ACTION,  # 共用
    ]
