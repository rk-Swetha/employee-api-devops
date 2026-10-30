import os


class Settings:
    APP_NAME = os.getenv(
        "APP_NAME",
        "Employee Management API",
    )

    APP_ENV = os.getenv(
        "APP_ENV",
        "development",
    )

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./employee.db",
    )


settings = Settings()
