from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=['settings.toml', '.secrets.toml'],
    environments=True,
)
