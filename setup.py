from setuptools import setup

setup(
      name='mlconf',
      packages=['mlconf'],
      version='0.0.2',
      author='Andreas Grivas',
      author_email='andreasgrv@gmail.com',
      url = 'https://github.com/andreasgrv/mlconf',
      download_url = 'https://github.com/andreasgrv/mlconf/archive/0.0.2.tar.gz',
      license='BSD',
      keywords='config argparse yaml machine-learning',
      install_requires=['pyyaml', 'argparse'],
      tests_require=['pytest'],
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.6' ],
      )
