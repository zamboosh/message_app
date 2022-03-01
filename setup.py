from setuptools import setup, find_packages

setup(
    name='message_app',
    extra_require=dict(test=['pytest']),
    packages=find_packages(where='src'),
    package_dir={"": "src"}
)