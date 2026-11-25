class AppError(Exception):
    pass


class ConfigError(AppError):
    pass


class RegistryError(AppError):
    pass


class GraphError(AppError):
    pass


class OutputError(AppError):
    pass
