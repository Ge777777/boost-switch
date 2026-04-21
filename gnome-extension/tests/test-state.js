import {normalizeStatus} from '../src/lib/state.js';

function assertEqual(actual, expected, message) {
    if (actual !== expected)
        throw new Error(`${message}: expected ${expected}, got ${actual}`);
}

const model = normalizeStatus({
    supported: true,
    available: true,
    enabled: true,
    can_toggle: true,
    backend: 'polkit-dbus',
    reason: 'ok',
    message: 'CPU Boost 已开启',
});

assertEqual(model.checked, true, 'checked');
assertEqual(model.sensitive, true, 'sensitive');
assertEqual(model.subtitle, '已开启', 'subtitle');
