import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="occam-jayarap", # Replace with your own username
    version="0.0.1",
    author="Pradeep Kumar Jayaraman",
    author_email="pradeep.kumar.jayaraman@autodesk.com",
    description="Lightweight Pythonic wrapper around pythonocc",
    url="git.autodesk.com/jayarap/occam",
    packages=["occam"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)