from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "智慧学生管理系统"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Database - MySQL
    DATABASE_URL: str = "mysql+pymysql://root:3274594297@localhost:3306/student_manager"

    # JWT
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    class Config:
        env_file = ".env"


settings = Settings()
