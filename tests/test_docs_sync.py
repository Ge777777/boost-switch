from pathlib import Path


def test_install_doc_references_real_scripts():
    text = Path("docs/operations/ubuntu-24-install.md").read_text(encoding="utf-8")
    for rel in [
        "scripts/install/install_local.sh",
        "scripts/verify/verify_simulated.sh",
        "scripts/verify/verify_host_integration.sh",
    ]:
        assert rel in text
        assert Path(rel).exists()
    assert "boostctl" in text
    assert "boost-switch-diag" in text
    assert "io.github.ge777777.BoostSwitch1.conf" in text
    assert "gnome-extensions info boost-switch@ge777777.github.io" in text
    assert "首次安装" in text
    assert "更新扩展目录" in text
    assert "重新登录 GNOME 会话" in text
    assert "前台 GNOME 会话手工复验" in text
    assert "手动点击 Quick Settings 开关" in text
    assert "闭环检查" not in text


def test_install_doc_mentions_repo_local_uv_and_runtime_venv():
    text = Path("docs/operations/ubuntu-24-install.md").read_text(encoding="utf-8")

    assert ".tools/uv/" in text
    assert "/usr/lib/boost-switch/venv" in text
    assert "不再依赖用户级 `uv`" in text


def test_local_rule_docs_explain_relaxed_authorization_boundary():
    readme_en = Path("README.md").read_text(encoding="utf-8")
    readme_zh = Path("README.zh-CN.md").read_text(encoding="utf-8")
    install_doc = Path("docs/operations/ubuntu-24-install.md").read_text(encoding="utf-8")
    polkit_readme = Path("system/polkit/README.md").read_text(encoding="utf-8")

    assert "not the default security baseline" in readme_en
    assert "broader authorization boundary" in readme_en
    assert "不是默认安全基线" in readme_zh
    assert "直接放行 boost 切换" in readme_zh
    assert "更宽松的本机授权边界" in install_doc
    assert "不应视为默认推荐配置" in install_doc
    assert "直接放行 `io.github.ge777777.boostswitch.set`" in polkit_readme
    assert "不是默认分发安全基线" in polkit_readme


def test_same_config_migration_doc_matches_repo_local_uv_mainline():
    text = Path("docs/operations/same-config-migration.md").read_text(encoding="utf-8")

    assert ".tools/uv/" in text
    assert "/usr/lib/boost-switch/venv" in text
    assert "command -v uv" not in text
    assert "python3 -m venv --help >/dev/null" in text


def test_bilingual_readmes_cover_install_and_ops_entrypoints():
    readme_en = Path("README.md").read_text(encoding="utf-8")
    readme_zh = Path("README.zh-CN.md").read_text(encoding="utf-8")

    expectations = [
        (readme_en, "README.zh-CN.md"),
        (readme_zh, "README.md"),
        (readme_en, "sudo bash scripts/install/install_local.sh --prefix /usr/lib/boost-switch"),
        (readme_zh, "sudo bash scripts/install/install_local.sh --prefix /usr/lib/boost-switch"),
        (readme_en, "boostctl status --json"),
        (readme_zh, "boostctl status --json"),
        (readme_en, "bash scripts/verify/verify_simulated.sh"),
        (readme_zh, "bash scripts/verify/verify_simulated.sh"),
        (readme_en, "bash scripts/verify/verify_host_integration.sh"),
        (readme_zh, "bash scripts/verify/verify_host_integration.sh"),
        (readme_en, "docs/operations/ubuntu-24-install.md"),
        (readme_zh, "docs/operations/ubuntu-24-install.md"),
        (readme_en, "docs/operations/uninstall.md"),
        (readme_zh, "docs/operations/uninstall.md"),
        (readme_en, "docs/operations/troubleshooting.md"),
        (readme_zh, "docs/operations/troubleshooting.md"),
        (readme_en, "docs/operations/same-config-migration.md"),
        (readme_zh, "docs/operations/same-config-migration.md"),
        (readme_en, "gnome-extensions info boost-switch@ge777777.github.io"),
        (readme_zh, "gnome-extensions info boost-switch@ge777777.github.io"),
        (readme_en, "CONTRIBUTING.md"),
        (readme_zh, "CONTRIBUTING.md"),
        (readme_en, "CODE_OF_CONDUCT.md"),
        (readme_zh, "CODE_OF_CONDUCT.md"),
        (readme_en, "SECURITY.md"),
        (readme_zh, "SECURITY.md"),
        (readme_en, "LICENSE"),
        (readme_zh, "LICENSE"),
        (readme_en, "Detailed operations docs and some current GNOME UI strings are still Chinese-first for now."),
        (readme_zh, "当前更细的运维文档以及部分 GNOME UI 字符串仍以中文为主。"),
    ]

    for text, needle in expectations:
        assert needle in text

    assert "Current Status" in readme_en
    assert "Supported Scope" in readme_en
    assert "Quick Start" in readme_en
    assert "Verify the Installation" in readme_en
    assert "Manual GNOME Check" in readme_en
    assert "Further Reading" in readme_en
    assert "Community" in readme_en
    assert "Architecture Summary" in readme_en
    assert "Repository Layout" in readme_en
    assert "License" in readme_en

    assert "当前状态" in readme_zh
    assert "适用范围" in readme_zh
    assert "快速开始" in readme_zh
    assert "验证安装" in readme_zh
    assert "前台 GNOME 手工复验" in readme_zh
    assert "延伸文档" in readme_zh
    assert "协作入口" in readme_zh
    assert "架构摘要" in readme_zh
    assert "仓库布局" in readme_zh
    assert "许可证" in readme_zh
