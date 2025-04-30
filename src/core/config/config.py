from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

from src.core.config.models import (
    RunConfig, 
    Current_ApiPrefix,
    Mode, 
    DatabaseConfig, 
    RedisSettings, 
    )


logger = logging.getLogger(__name__)

logging.basicConfig(
        level=logging.DEBUG,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter='__',
        env_prefix='FAST__',
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )
    run: RunConfig = RunConfig()  # Keep defaults as fallback
    data: Current_ApiPrefix = Current_ApiPrefix()
    mode: Mode = Mode()
    db: DatabaseConfig
    redis_settings: RedisSettings = RedisSettings()
    #elastic:ElasticSearch = ElasticSearch()
    #email:Email_Settings = Email_Settings()


settings = Settings()
assert settings.mode.mode in ('DEV', 'TEST')