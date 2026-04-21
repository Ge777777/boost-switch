import {buildToggleViewModel} from '../src/lib/presenter.js';

function assertEqual(actual, expected, message) {
    if (actual !== expected)
        throw new Error(`${message}: expected ${expected}, got ${actual}`);
}

const ready = buildToggleViewModel({checked: true, sensitive: true, subtitle: '已开启'}, false);
assertEqual(ready.checked, true, 'checked');
assertEqual(ready.sensitive, true, 'sensitive');

const busy = buildToggleViewModel({checked: true, sensitive: true, subtitle: '已开启'}, true);
assertEqual(busy.sensitive, false, 'busy sensitive');
assertEqual(busy.subtitle, '切换中…', 'busy subtitle');
