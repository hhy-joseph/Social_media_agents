from setuptools import setup, find_packages

setup(
    name="ig_agent",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'ig_agent': [
            'prompts/*.txt',
            'static/*.svg',
        ],
    },
    install_requires=[
        "langchain-core>=0.1.0",
        "langchain-xai>=0.1.0",
        "langgraph>=0.1.0",
        "pydantic>=2.0.0",
        "cairosvg>=2.7.0",
    ],
    extras_require={
        "full": [
            "instagrapi>=2.0.0",
            "langchain-community>=0.0.16",
        ],
    },
    entry_points={
        'console_scripts': [
            'ig_agent=ig_agent.cli:main',
        ],
    },
    description="A multi-agent system for Instagram content generation",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/ig_agent",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
)