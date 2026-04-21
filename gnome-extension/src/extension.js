import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import GObject from 'gi://GObject';

import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as QuickSettings from 'resource:///org/gnome/shell/ui/quickSettings.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

import {createSystemProxy, unpackPayload} from './lib/dbus.js';
import {normalizeStatus} from './lib/state.js';
import {buildToggleViewModel} from './lib/presenter.js';


const POLL_INTERVAL_SECONDS = 5;

const BoostToggle = GObject.registerClass(
class BoostToggle extends QuickSettings.QuickToggle {
    constructor(extension) {
        super({
            title: 'CPU Boost',
            subtitle: '加载中…',
            iconName: 'computer-chip-symbolic',
            toggleMode: true,
        });

        this._extension = extension;
        this._settings = extension.getSettings();
        this._proxy = null;
        this._busy = false;
        this._state = {
            checked: false,
            sensitive: false,
            subtitle: '加载中…',
        };
        this._signalId = 0;
        this._pollId = 0;

        this.connect('clicked', () => {
            void this._onClicked();
        });
    }

    setProxy(proxy) {
        this._disconnectProxy();
        this._proxy = proxy;
        this._signalId = this._proxy.connectSignal('StatusChanged', (_proxy, _sender, [payload]) => {
            this._state = normalizeStatus(unpackPayload(payload));
            this._applyState();
        });
        this._refresh();
        this._ensurePollFallback();
    }

    showUnavailable(message) {
        this._state = normalizeStatus({
            supported: false,
            available: false,
            enabled: false,
            can_toggle: false,
            reason: 'service_unavailable',
            message,
        });
        this._applyState();
    }

    async _onClicked() {
        if (!this._proxy || this._busy || !this.sensitive)
            return;

        const desired = !this._state.checked;
        this._busy = true;
        this._applyState();

        this._proxy.SetBoostRemote(desired, (result, error) => {
            this._busy = false;
            if (error) {
                this.showUnavailable(error.message);
                return;
            }

            const payload = unpackPayload(result?.[0] ?? result);
            this._state = normalizeStatus(payload);
            this._applyState();
        });
    }

    _refresh() {
        if (!this._proxy)
            return;

        this._proxy.GetStatusRemote((result, error) => {
            if (error) {
                this.showUnavailable(error.message);
                return;
            }

            const payload = unpackPayload(result?.[0] ?? result);
            this._state = normalizeStatus(payload);
            this._applyState();
        });
    }

    _ensurePollFallback() {
        if (this._pollId !== 0) {
            GLib.source_remove(this._pollId);
            this._pollId = 0;
        }

        if (!this._settings.get_boolean('enable-poll-fallback'))
            return;

        this._pollId = GLib.timeout_add_seconds(
            GLib.PRIORITY_DEFAULT,
            POLL_INTERVAL_SECONDS,
            () => {
                this._refresh();
                return GLib.SOURCE_CONTINUE;
            }
        );
    }

    _disconnectProxy() {
        if (this._proxy && this._signalId !== 0)
            this._proxy.disconnectSignal(this._signalId);
        this._signalId = 0;
        this._proxy = null;
    }

    _applyState() {
        const model = buildToggleViewModel(this._state, this._busy);
        this.checked = model.checked;
        this.sensitive = model.sensitive;
        this.subtitle = model.subtitle;
    }

    destroy() {
        if (this._pollId !== 0) {
            GLib.source_remove(this._pollId);
            this._pollId = 0;
        }
        this._disconnectProxy();
        super.destroy();
    }
});

const BoostIndicator = GObject.registerClass(
class BoostIndicator extends QuickSettings.SystemIndicator {
    constructor(extension) {
        super();

        this._settings = extension.getSettings();
        this._indicator = this._addIndicator();
        this._indicator.icon_name = 'computer-chip-symbolic';
        this._settings.bind('show-indicator', this._indicator, 'visible', Gio.SettingsBindFlags.DEFAULT);

        this._toggle = new BoostToggle(extension);
        this.quickSettingsItems.push(this._toggle);
    }

    setProxy(proxy) {
        this._toggle.setProxy(proxy);
    }

    showUnavailable(message) {
        this._toggle.showUnavailable(message);
    }

    destroy() {
        this.quickSettingsItems.forEach(item => item.destroy());
        super.destroy();
    }
});

export default class BoostSwitchExtension extends Extension {
    enable() {
        this._indicator = new BoostIndicator(this);
        Main.panel.statusArea.quickSettings.addExternalIndicator(this._indicator);

        createSystemProxy()
            .then(proxy => {
                if (this._indicator)
                    this._indicator.setProxy(proxy);
            })
            .catch(error => {
                if (this._indicator)
                    this._indicator.showUnavailable(error.message);
            });
    }

    disable() {
        this._indicator?.destroy();
        this._indicator = null;
    }
}
