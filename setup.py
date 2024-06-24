from setuptools import setup

with open("readme.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pytailwind',
    version='0.0.3',
    packages=['pytailwind'],
    url='https://github.com/shashstormer/pytailwindcss',
    license='MIT License',
    author='shashstormer',
    author_email='shashanka5398@gmail.com',
    description='A tailwind parser written completely in python without js dependency (unofficial)',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries',
    ],
    project_urls={
        'GitHub': 'https://github.com/shashstormer/pytailwindcss',
    },
)
