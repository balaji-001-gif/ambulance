from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="bas_ambulance",
    version="1.0.0",
    description="Ambulance Service Management for ERPNext v15+",
    author="BAS Technologies",
    author_email="admin@bas.in",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
