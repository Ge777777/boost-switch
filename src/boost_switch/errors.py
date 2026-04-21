class BoostSwitchError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class UnsupportedError(BoostSwitchError):
    def __init__(self, message: str = "当前机器不支持 boost 开关") -> None:
        super().__init__("unsupported", message)


class SysfsMissingError(BoostSwitchError):
    def __init__(self, message: str = "未找到 boost sysfs 路径") -> None:
        super().__init__("sysfs_missing", message)


class PermissionDeniedError(BoostSwitchError):
    def __init__(self, message: str = "当前请求未通过授权") -> None:
        super().__init__("permission_denied", message)
