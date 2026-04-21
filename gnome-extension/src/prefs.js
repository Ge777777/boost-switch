import Adw from 'gi://Adw';
import Gio from 'gi://Gio';

import {ExtensionPreferences} from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';


function bindSwitch(settings, key, title, subtitle) {
    const row = new Adw.SwitchRow({title, subtitle});
    settings.bind(key, row, 'active', Gio.SettingsBindFlags.DEFAULT);
    return row;
}

export default class BoostSwitchPreferences extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const settings = this.getSettings();

        const page = new Adw.PreferencesPage();
        const group = new Adw.PreferencesGroup({title: 'Boost Switch'});

        group.add(bindSwitch(settings, 'show-indicator', '显示常驻图标', '在系统菜单中显示图标指示器'));
        group.add(bindSwitch(settings, 'notify-on-error', '错误时通知', '切换失败时弹出通知'));
        group.add(bindSwitch(settings, 'enable-poll-fallback', '启用轮询兜底', '在信号同步之外定期刷新状态'));
        group.add(bindSwitch(settings, 'debug-logging', '调试日志', '输出扩展调试日志'));

        page.add(group);
        window.add(page);
    }
}
