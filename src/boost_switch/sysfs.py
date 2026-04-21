from dataclasses import dataclass
from pathlib import Path

from boost_switch.contracts import SYSFS_BOOST_PATH
from boost_switch.errors import SysfsMissingError


@dataclass(slots=True)
class SysfsBoostRepository:
    sysfs_root: Path | None = None

    @property
    def boost_path(self) -> Path:
        if self.sysfs_root is None:
            return Path(SYSFS_BOOST_PATH)
        return self.sysfs_root / "devices/system/cpu/cpufreq/boost"

    def exists(self) -> bool:
        return self.boost_path.exists()

    def read_enabled(self) -> bool:
        if not self.exists():
            raise SysfsMissingError()
        return self.boost_path.read_text(encoding="utf-8").strip() == "1"

    def write_enabled(self, enabled: bool) -> None:
        if not self.exists():
            raise SysfsMissingError()
        self.boost_path.write_text("1\n" if enabled else "0\n", encoding="utf-8")
