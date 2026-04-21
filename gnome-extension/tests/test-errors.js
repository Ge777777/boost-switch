import {subtitleForReason} from '../src/lib/errors.js';

function assertEqual(actual, expected, message) {
    if (actual !== expected)
        throw new Error(`${message}: expected ${expected}, got ${actual}`);
}

assertEqual(subtitleForReason('inactive_session'), '当前会话未激活', 'inactive subtitle');
assertEqual(subtitleForReason('sysfs_missing'), '未找到 boost 开关', 'missing subtitle');
