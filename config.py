from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    COIN_API_KEY: str
    DATABASE_URL: str

    class Config:
        # Loads the environment variables from a '.env' file
        env_file = ".env"
        env_file_encoding = "utf-8"


config = AppConfig()
# Example of using the configuration
if __name__ == "__main__":
    config = AppConfig()
    print(config.COIN_API_KEY)
