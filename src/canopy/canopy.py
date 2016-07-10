from package import RootPackageInterface
from package import Locker
from repository import RepositoryManager
from installer import InstallationManager
from plugin import PluginManager
from downloader import DownloadManager
from dispatcher import EventDispatcher
from autoload import AutoloadGenerator
from config import ConfigSourceInterface
from util import Filesystem
from util import Silencer
from io import IOInterface

from shutil import copyfile
from datetime import datetime
from random import randint
import re
import os


class Canopy(object):
    VERSION = '@package_version@'
    BRANCH_ALIAS_VERSION = '@package_branch_alias_version@'
    RELEASE_DATE = '@release_date@'

    def __init__(self):
        self.package = None
        self.locker = None
        self.repositoryManager = None
        self.downloadManager = None
        self.installationManager = None
        self.pluginManager = None
        self.config = None
        self.eventDispatcher = None
        self.autoloadGenerator = None

    @property
    def package(self):
        return self.__package

    @package.setter
    def package(self, package):
        if not isinstance(package, RootPackageInterface):
            raise AttributeError("Package is not of type RootPackageInterface")
        self.__package = package

    @property
    def locker(self):
        return self.__locker

    @package.setter
    def locker(self, locker):
        if not isinstance(locker, Locker):
            raise AttributeError("Locker is not of type Locker")
        self.__locker = locker

    @property
    def repositoryManager(self):
        return self.__repositoryManager

    @package.setter
    def repositoryManager(self, repositoryManager):
        if isinstance(repositoryManager, RepositoryManager):
            raise AttributeError("repositoryManager is not of type RepositoryManager")
        self.__repositoryManager = repositoryManager

    @property
    def downloadManager(self):
        return self.__downloadManager

    @package.setter
    def downloadManager(self, downloadManager):
        if isinstance(downloadManager, DownloadManager):
            raise AttributeError("downloadManager is not of type DownloadManager")
        self.__downloadManager = downloadManager

    @property
    def installationManager(self):
        return self.__installationManager

    @package.setter
    def installationManager(self, installationManager):
        if isinstance(installationManager, InstallationManager):
            raise AttributeError("installationManager is not of type InstallationManager")
        self.__installationManager = installationManager

    @property
    def pluginManager(self):
        return self.__pluginManager

    @package.setter
    def pluginManager(self, pluginManager):
        if isinstance(pluginManager, PluginManager):
            raise AttributeError("pluginManager is not of type PluginManager")
        self.__pluginManager = pluginManager

    @property
    def config(self):
        return self.__config

    @package.setter
    def config(self, config):
        if isinstance(config, Config):
            raise AttributeError("config is not of type Config")
        self.__config = config

    @property
    def eventDispatcher(self):
        return self.__eventDispatcher

    @package.setter
    def eventDispatcher(self, eventDispatcher):
        if isinstance(eventDispatcher, EventDispatcher):
            raise AttributeError("eventDispatcher is not of type EventDispatcher")
        self.__eventDispatcher = eventDispatcher

    @property
    def autoloadGenerator(self):
        return self.__autoloadGenerator

    @package.setter
    def autoloadGenerator(self, autoloadGenerator):
        if isinstance(autoloadGenerator, AutoloadGenerator):
            raise AttributeError("autoloadGenerator is not of type AutoloadGenerator")
        self.__autoloadGenerator = autoloadGenerator


class Config:

    RELATIVE_PATHS = 1

    defaultConfig = {
        'process-timeout': 300,
        'use-include-path': False,
        'preferred-install': 'auto',
        'notify-on-install': True,
        'github-protocols': ['git', 'https', 'ssh'],
        'canopy-dir': 'canopy',
        'bin-dir': '{canopy}/bin',
        'cache-dir': '{home}/cache',
        'data-dir': '{home}',
        'cache-files-dir': '{cache-dir}/files',
        'cache-repo-dir': '{cache-dir}/repo',
        'cache-vcs-dir': '{cache-dir}/vcs',
        'cache-ttl': 15552000, # 6 months,
        'cache-files-ttl': None, # fallback to cache-ttl
        'cache-files-maxsize': '300MiB',
        'bin-compat': 'auto',
        'discard-changes': False,
        'autoloader-suffix': None,
        'sort-packages': False,
        'optimize-autoloader': False,
        'classmap-authoritative': False,
        'prepend-autoloader': True,
        'github-domains': ['github.com'],
        'store-auths': 'prompt',
        'platform': [],
        'archive-format': 'tar',
        'archive-dir': '.'
    }

    defaultRepositories = {
        'canopymods': {
            'type': 'Cano',
            'url': 'https?://canopymods.org',
            'allow_ssl_downgrade': True
        }
    }

    def __init__(self, useEnvironment = True, baseDir = None):
        self.__configSource = None
        self.__authConfigSource = None
        self.config = Config.defaultConfig
        self.__repositories = Config.defaultConfig
        self.useEnvironment = useEnvironment
        self.baseDir = baseDir

    @property
    def configSource(self):
        return self.__configSource


    @configSource.setter
    def configSource(self, source):
        if not isinstance(source, ConfigSourceInterface):
            raise AttributeError("source not of type ConfigSourceInterface")
        self.__configSource = source


    @property
    def authConfigSource(self):
        return self.__authConfigSource

    @authConfigSource.setter
    def setAuthConfigSource(self, source):
        if not isinstance(source, ConfigSourceInterface):
            raise AttributeError("source not of type ConfigSourceInterface")
        self.__configSource = source

    @property
    def repositories(self):
        return self.__repositories

    def merge(self, config):
        self.config.update(config['config'])

        self.repositories.update(config['repositories'])

    def get(self, key="", flags = 0):
        if key in [
            'my_vendor-dir',
            'bin-dir',
            'process-timeout',
            'data-dir',
            'cache-dir',
            'cache-files-dir',
            'cache-repo-dir',
            'cache-vcs-dir',
            'cafile',
            'capath'
        ]:
            env = "CANOPY_{}".format(key.replace("-", "_").upper())
            envHome = os.environ.get("HOME") or os.environ.get("USERPROFILE") or ""

            val = (self.process(self.getComposerEnv(env)) or self.config[key]).rstrip("/\\")
            val = re.sub(r"^(\$HOME|~)(/|$)", envHome.rstrip("/\\"), "/", val)

            if key[-4:] != '-dir':
                return val

            return val if flags & self.RELATIVE_PATHS == self.RELATIVE_PATHS else self.realpath(val)
        elif key == 'cache-ttl':
            return self.config[key]

        elif key == 'cache-files-maxsize':
            return 0
        elif 'cache-files-ttl':
            return self.config[key] or self.config['cache-ttl']
        elif key == 'home':
            envHome = os.environ.get("HOME") or os.environ.get("USERPROFILE") or ""
            val = re.sub(r"^(\$HOME|~)(/|$)", envHome.rstrip("/\\"), "/", self.config[key])
            return val
        elif key == 'bin-compat':
            val = self.getComposerEnv('COMPOSER_BIN_COMPAT') or self.config[key]

            if val not in ['auto', 'full']:
                raise RuntimeError("Invalid value for 'bin-compat': {}. Expected auto, full".format(val))

            return val
        elif key == 'discard-changes':
            env = self.getComposerEnv('COMPOSER_DISCARD_CHANGES')
            if env:
                if env not in ['stash', 'true', 'false', '1', '0']:
                    raise RuntimeError(
                            "Invalid value for COMPOSER_DISCARD_CHANGES: {}. Expected 1, 0, true, false or stash"
                            .format(env))
                elif env == 'stash':
                    return 'stash'

                return env in ['true', '1']
            if self.config[key] not in [True, False, 'stash']:
                raise RuntimeError("Invalid value for 'discard-changes': {}. Expected true, false, or stash"
                                   .format(self.config[key]))
            return self.config[key]
        elif key == 'github-protocols':
            if self.config['github-protocols'][0] == 'http':
                raise RuntimeError(
                        "The http protocol for github is not available anymore, update your config's github-protocols to use https"
                )
            return self.config[key]
        elif key == 'disable-tls':
            return key not in [False, 'false']
        else:
            if key not in self.config:
                return None
            return self.process(self.config[key], flags)

    def all(self, flags):
        all = {
            'repositories': self.repositories
        }

        for key in self.config:
            all['config'][key] = self.get(key, flags)

        return all

    def raw(self):
        return {
            'repositories': self.repositories,
            'config': self.config
        }

    def has(self, key):
        return key in self.config

    def process(self, value, flags):

        if isinstance(value, basestring):
            regex = r'#\{\$(.+)\}#'

            def replace(match):
                return self.config.get(match.group(1), flags)

            value = re.sub(regex, replace, value)
        return value

    def realpath(self, path):
        # first check against a regex
        regex = r'{^(?:/|[a-z]:|[a-z0-9.]+://)}i'
        if re.match(regex, path):
            return path

        return self.baseDir + '/' + path

    def getComposerEnv(self, var):
        if self.useEnvironment:
            return os.environ[var]
        return False


class Cache(object):
    def __init__(self, io, cache_dir, whitelist='a-z0-9', filesystem=None):
        self.__io = io
        self.__root = cache_dir.rstrip('/')
        self.__whitelist = whitelist
        self.__filesystem = filesystem or Filesystem()
        self.__enabled = True

        if not (os.isdir(self.__root)
            or Silencer.call('mkdir', self.__root, 0777, True))\
            and not os.access(self.__root, os.W_OK):
            self.io.write_error('<warning>Cannot create cache directory {}, or directory is not writable. Proceeding without cache</warning>'.format(self.__root))
            self.__enabled = False

    @property
    def is_enabled(self):
        return self.__enabled

    @property
    def root(self):
        return self.__root

    def read(self, file):
        file = self.__clean_filename(file)

        if self.is_enabled and os.path.isfile(file):
            self.__io.write_error('Reading {}{} from cache'.format(self.__root, file), True, IOInterface.DEBUG)

        with open(self.__root + file, 'r') as f:
            return f.read()

    def write(self, file, contents):
        file = self.__clean_filename(file)

        self.__io.write_error('Writing {}{} into cache', True, IOInterface.DEBUG)
        try:
            with open(file, 'w') as f:
                f.write(contents)
        except IOError as e:
            self.__io.write_error('<warning>Failed to write to cache: {}</warning>'.format(e.message), True, IOInterface.DEBUG)

            # TODO: need to remove any partially written file...
            raise e

    def copy_from(self, file, source):
        if self.is_enabled:
            file = self.__clean_filename(file)
            self.__filesystem.ensure_directory_exists(self.root+file)

            if not os.path.isfile(source):
                self.__io.write_error('<error>{} does not exist, cannot write to cache</error>'.format(source))
            self.__io.write_debug('Writing {}{} to cache from {}'.format(self.root, file, source))

            return copyfile(source, self.root + file)
        return False

    def copy_to(self, file, target):
        file = self.__clean_filename(file)
        if self.is_enabled and os.path.isfile(self.root + file):
            try:
                self.touch(self.root + file, datetime.now())
            except IOError:
                self.touch(self.root + file)

            self.io.write_debug('Reading {}{} from cache'.format(self.root, file))
            return copyfile(self.root + file, target)
        return False

    def gc_is_necessary(self):
        return not self.cache_collected and randint(0, 50)

    def remove(self, file):
        file = self.__clean_filename()
        if self.is_enabled and os.path.isfile(self.root + file):
            return os.remove(file)
        return False

    # TODO: finish out
    def gc(self, ttl, max_size):
        if self.is_enabled:
            expire = datetime()

    def touch(self, file, times=None):
        with open(file, 'a'):
            os.utime(file, times)

    def __clean_filename(self, file):
        return re.sub(r'{[^'+self.whitelist+']}i', '-', file)
