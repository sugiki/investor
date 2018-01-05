from os.path import dirname, abspath, join

ROOT_DIR = dirname(dirname(abspath(__file__)))
RESOURCE_DIR = join(ROOT_DIR, 'resources')
LIB_DIR = join(ROOT_DIR, 'investor')
TMP_DIR = join(ROOT_DIR, 'tmp')


SQLALCHEMY_ENGINE = 'mysql+mysqldb://root:pass@127.0.0.1:3306/investor'
