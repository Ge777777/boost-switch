import Gio from 'gi://Gio';

const XML = `<node>
  <interface name="io.github.ge777777.BoostSwitch1.Control">
    <method name="GetStatus">
      <arg direction="out" type="a{sv}" name="status"/>
    </method>
    <method name="SetBoost">
      <arg direction="in" type="b" name="enabled"/>
      <arg direction="out" type="a{sv}" name="status"/>
    </method>
    <method name="GetDiagnostics">
      <arg direction="out" type="a{sv}" name="diagnostics"/>
    </method>
    <signal name="StatusChanged">
      <arg type="a{sv}" name="status"/>
    </signal>
  </interface>
</node>`;

export const Proxy = Gio.DBusProxy.makeProxyWrapper(XML);

export const BUS_NAME = 'io.github.ge777777.BoostSwitch1';
export const OBJECT_PATH = '/io/github/ge777777/BoostSwitch1';

function unpackValue(value) {
    if (value?.deepUnpack)
        return unpackValue(value.deepUnpack());
    if (Array.isArray(value))
        return value.map(item => unpackValue(item));
    if (value && typeof value === 'object') {
        const normalized = {};
        for (const [key, item] of Object.entries(value))
            normalized[key] = unpackValue(item);
        return normalized;
    }
    return value;
}

export function unpackPayload(payload) {
    return unpackValue(payload);
}

export function createSystemProxy() {
    return new Promise((resolve, reject) => {
        new Proxy(
            Gio.DBus.system,
            BUS_NAME,
            OBJECT_PATH,
            (proxy, error) => {
                if (error)
                    reject(error);
                else
                    resolve(proxy);
            }
        );
    });
}
