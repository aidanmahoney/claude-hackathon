from setuptools import setup, find_packages

setup(
    name="uw-course-checker",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.25.2",
        "python-dotenv>=1.0.0",
        "sqlalchemy>=2.0.23",
        "apscheduler>=3.10.4",
        "click>=8.1.7",
        "twilio>=8.10.0",
        "pydantic>=2.5.2",
        "pydantic-settings>=2.1.0",
    ],
    entry_points={
        "console_scripts": [
            "uw-course-checker=src.cli:cli",
        ],
    },
    author="",
    description="Real-time course availability monitoring tool for UW Madison",
    keywords="course enrollment uw-madison monitoring",
    python_requires=">=3.9",
)
