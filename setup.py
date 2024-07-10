import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="occwl",  # package name
    version="3.0.0",
    author="Pradeep Kumar Jayaraman, Joseph G. Lambourne",
    author_email="pradeep.kumar.jayaraman@autodesk.com, joseph.lambourne@autodesk.com",
    description="Lightweight Pythonic wrapper around pythonocc",
    url="https://github.com/AutodeskAILab/occwl",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
)
