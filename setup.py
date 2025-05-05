from setuptools import setup, find_packages

setup(
    name="tg_summary",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "flask",
        "python-telegram-bot",
        "google-generativeai",
        "firebase-admin",
        "google-cloud-firestore",
        "python-dotenv",
        "stripe>=8.0.0",
        "stripe",
    ],
)
