"""
Configuration Loader for Forex Trading Bot
Reads YAML config files and provides easy access to settings
"""

import yaml
import os
from logger_config import setup_logger

logger = setup_logger('ConfigLoader')


class Config:
    """Load and manage configuration from YAML files"""
    
    def __init__(self, config_file='config.yaml', secret_file='config_secret.yaml'):
        """Initialize configuration loader"""
        self.config_file = config_file
        self.secret_file = secret_file
        self.data = {}
        self.secrets = {}
        
        self._load_config()
        self._load_secrets()
    
    def _load_config(self):
        """Load main configuration file"""
        try:
            if not os.path.exists(self.config_file):
                logger.error(f"Config file not found: {self.config_file}")
                raise FileNotFoundError(f"Config file not found: {self.config_file}")
            
            with open(self.config_file, 'r') as f:
                self.data = yaml.safe_load(f)
            
            logger.info(f"✅ Loaded configuration from {self.config_file}")
            logger.debug(f"Config keys: {list(self.data.keys())}")
            
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {self.config_file}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise
    
    def _load_secrets(self):
        """Load secrets file (API keys, passwords, etc.)"""
        try:
            if not os.path.exists(self.secret_file):
                logger.warning(f"Secrets file not found: {self.secret_file} (this is okay if not using API keys)")
                return
            
            with open(self.secret_file, 'r') as f:
                self.secrets = yaml.safe_load(f)
            
            logger.info(f"✅ Loaded secrets from {self.secret_file}")
            logger.debug("Secrets loaded (values hidden for security)")
            
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {self.secret_file}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading secrets: {e}")
            raise
    
    def get(self, key_path, default=None):
        """Get configuration value using dot notation"""
        try:
            keys = key_path.split('.')
            value = self.data
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    logger.debug(f"Key not found: {key_path}, using default: {default}")
                    return default
            
            logger.debug(f"Retrieved config: {key_path} = {value}")
            return value
            
        except Exception as e:
            logger.error(f"Error getting config key '{key_path}': {e}")
            return default
    
    def get_secret(self, key_path, default=None):
        """Get secret value (API keys, passwords)"""
        try:
            keys = key_path.split('.')
            value = self.secrets
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    env_var = '_'.join(keys).upper()
                    env_value = os.getenv(env_var)
                    if env_value:
                        logger.debug(f"Using environment variable: {env_var}")
                        return env_value
                    
                    logger.debug(f"Secret not found: {key_path}")
                    return default
            
            logger.debug(f"Retrieved secret: {key_path} (value hidden)")
            return value
            
        except Exception as e:
            logger.error(f"Error getting secret '{key_path}': {e}")
            return default
    
    def get_all(self):
        """Get entire configuration as dictionary"""
        return self.data
    
    def validate(self):
        """Validate that all required configuration is present"""
        required_keys = [
            'strategy.rsi_period',
            'strategy.rsi_oversold',
            'strategy.rsi_overbought',
            'risk.starting_capital',
            'risk.risk_per_trade',
            'symbols'
        ]
        
        all_valid = True
        
        for key in required_keys:
            value = self.get(key)
            if value is None:
                logger.error(f"❌ Required config missing: {key}")
                all_valid = False
            else:
                logger.debug(f"✅ Required config present: {key}")
        
        if all_valid:
            logger.info("✅ Configuration validation passed")
        else:
            logger.error("❌ Configuration validation failed")
        
        return all_valid


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TESTING CONFIG LOADER")
    print("="*70 + "\n")
    
    try:
        config = Config()
        
        print("--- Testing config.get() ---\n")
        print(f"RSI Period: {config.get('strategy.rsi_period')}")
        print(f"RSI Oversold: {config.get('strategy.rsi_oversold')}")
        print(f"RSI Overbought: {config.get('strategy.rsi_overbought')}")
        print(f"Starting Capital: ${config.get('risk.starting_capital')}")
        print(f"Risk Per Trade: {config.get('risk.risk_per_trade')*100}%")
        print(f"Symbols: {config.get('symbols')}")
        print(f"Max Retries: {config.get('error_handling.max_retries')}")
        
        print("\n--- Testing validation ---\n")
        if config.validate():
            print("✅ All required configuration present!")
        else:
            print("❌ Configuration validation failed!")
        
        print("\n--- Testing non-existent key ---\n")
        result = config.get('does.not.exist', default='DEFAULT_VALUE')
        print(f"Non-existent key: {result}")
        
        print("\n" + "="*70)
        print("✅ CONFIG LOADER TEST COMPLETE!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}\n")
