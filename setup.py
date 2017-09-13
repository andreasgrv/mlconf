from setuptools import setup

setup(
      name='mlconf',
      packages=['mlconf'],
      version='0.0.1',
      author='Andreas Grivas',
      author_email='andreasgrv@gmail.com',
      description='Machine learning config utilities bundle.',
      license='BSD',
      keywords=['config','argparse'],
      classifiers=[],
      install_requires=['pyyaml', 'argparse'],
      tests_require=['pytest']
      )
