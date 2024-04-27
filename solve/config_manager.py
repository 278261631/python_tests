import configparser
import os


class ConfigManager:
    def __init__(self, config_name='config.ini'):
        self.config_path = os.path.join(os.path.dirname(__file__), config_name)
        self.config = configparser.ConfigParser()
        self.default_config = {
            'database': {
                'path': 'fits_wcs_recent.db',
            },
            'download': {
                'temp_download_path': 'E:/test_download/thread/',
                'recent_data': False
            }
        }

    def read_config(self):
        # 检查配置文件是否存在
        if not os.path.exists(self.config_path):
            # 如果配置文件不存在，创建并写入默认配置
            self.create_default_config()

        # 读取配置文件
        self.config.read(self.config_path)

    def create_default_config(self):
        with open(self.config_path, 'w') as configfile:
            self.config = configparser.ConfigParser()
            for section, options in self.default_config.items():
                self.config[section] = options
            self.config.write(configfile)
        print(f"Default configuration file '{self.config_path}' has been created.")

    def get(self, section, option):
        # 确保配置文件已被读取
        if not self.config.sections():
            self.read_config()
        return self.config.get(section, option)


# 实例化ConfigManager并提供默认配置文件路径
ini_config = ConfigManager()
