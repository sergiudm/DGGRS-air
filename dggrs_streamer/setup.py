from setuptools import find_packages, setup


package_name = "dggrs_streamer"


setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="DGGRS Contributors",
    maintainer_email="maintainers@example.com",
    description="High-level ROS 2 streaming package scaffold for DGGRS.",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "streamer_node = dggrs_streamer.streamer_node:main",
        ],
    },
)
