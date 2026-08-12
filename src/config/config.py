from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    base_url: str = Field(..., description="Initial URL to start web-scrapping from")
    draft_url: str = Field(..., description="Draft URL to start web-scrapping from")
    immaculate_grid_url: str = Field(..., description="Immaculate Grid URL to start gather grid data from")
    stats_table_key: str = Field(...,
                                 description="Unique ID that identifies which stats table to scrap from on a given player stats page")
    db_host: str = Field(..., description="PostgreSQL host")
    db_port: int = Field(5432, description="PostgreSQL port")
    db_name: str = Field(..., description="PostgreSQL database name")
    db_user: str = Field(..., description="PostgreSQL user")
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
