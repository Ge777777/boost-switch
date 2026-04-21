from boost_switch.sysfs import SysfsBoostRepository


def test_read_and_write_simulated_boost_file(tmp_path):
    boost_path = tmp_path / "devices/system/cpu/cpufreq/boost"
    boost_path.parent.mkdir(parents=True)
    boost_path.write_text("1\n", encoding="utf-8")

    repo = SysfsBoostRepository(sysfs_root=tmp_path)
    assert repo.read_enabled() is True

    repo.write_enabled(False)
    assert boost_path.read_text(encoding="utf-8") == "0\n"
