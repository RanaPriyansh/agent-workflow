from setuptools import setup
setup(
    name="thielon-agent-workflow",
    version="0.1.0",
    py_modules=["thielon_workflow"],
    install_requires=["redis>=4.0", "pydantic>=2.0", "networkx>=3.0"],
    python_requires=">=3.9",
)
