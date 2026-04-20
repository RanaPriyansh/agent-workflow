from setuptools import setup
setup(
    name="agent-workflow",
    version="0.2.0",
    py_modules=["agent_workflow"],
    install_requires=["redis>=4.0", "pydantic>=2.0", "networkx>=3.0"],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "agent-workflow=agent_workflow:main",
        ]
    },
)
