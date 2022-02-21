from setuptools import setup

with open('./README.md') as doc:
    readme = doc.read()

setup(
    name="steer",
    version="1.0.2.post1",
    author="Fernando A.",
    url="https://github.com/fernando-gap/steer",
    license="MIT",
    packages=['steer/oauth', 'steer/drive'],
    description="Create URLS to use create google oauth2 and drive api requests.",
    long_description=readme,
    long_description_content_type="text/markdown"
)
