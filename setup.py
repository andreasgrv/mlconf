from setuptools import setup

setup(
      name='mlconf',
      packages=['mlconf'],
      version='0.0.1',
      author='Andreas Grivas',
      author_email='andreasgrv@gmail.com',
      url = 'https://github.com/andreasgrv/mlconf',
      download_url = 'https://github.com/andreasgrv/mlconf/archive/0.0.1.tar.gz',
      license='BSD',
      keywords=['config','argparse'],
      classifiers=[],
      install_requires=['pyyaml', 'argparse'],
      tests_require=['pytest']
      )
