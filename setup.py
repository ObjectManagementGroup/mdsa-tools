from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()


setup(name='omgmdsa',
      version='0.1',
      description='Support tools for OMG Model-Driven Specification Authoring',
      long_description=readme(),
      url='https://github.com/ObjectManagementGroup/MDSATools.git',
      author='Object Management Group',
      author_email='jason@omg.org',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'errutils @ git+https://github.com/jasonmccsmith/errutils',
          'click'
      ],
      entry_points = {
          'console_scripts': [
              'md2latex=omgmdsa.md2latex:main',
              'makechangebartex=omgmdsa.makechangebartex:main'
          ],
      },
      include_package_data=True,
      include_package_files=True,
      zip_safe=False)
