from glob import glob
from setuptools import setup


package_name = "dggrs_bringup"


setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", glob("launch/*.launch.py")),
        (f"share/{package_name}/config", glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="DGGRS Contributors",
    maintainer_email="maintainers@example.com",
    description="Launch and configuration package for the DGGRS scaffold.",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "mock_inputs_node = dggrs_bringup.mock_inputs_node:main",
        ],
    },
)
