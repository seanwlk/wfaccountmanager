import setuptools

long_description = """# Warface Account Wrapper

## Usage

from wfaccountmanager import WFAccountManager

wf = WFAccountManager("west")
wf.login("email","password")

Full documentation available here: https://github.com/seanwlk/wfaccountmanager
"""

setuptools.setup(
  name="wfaccountmanager",
  version="0.0.7",
  author="seanwlk",
  author_email="seanwlk@my.com",
  description="Python Wrapper library for Warface that allows you to login and manage data",
  long_description_content_type="text/markdown",
  long_description=long_description,
  url="https://github.com/seanwlk/wfaccountmanager",
  install_requires=["steam","lxml"],
  packages=setuptools.find_packages(),
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    "Operating System :: OS Independent",
  ],
  python_requires='>=3.6',
)