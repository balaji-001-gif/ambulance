from setuptools import setup, find_packages

setup(
    name="bas_ambulance",
    version="1.0.0",
    description="BAS Ambulance Service Management",
    author="Antigravity",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "frappe",
    ],
)
