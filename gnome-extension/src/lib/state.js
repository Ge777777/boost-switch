import {subtitleForReason} from './errors.js';

export function normalizeStatus(payload) {
    const checked = Boolean(payload.enabled);
    const sensitive = Boolean(payload.available) && Boolean(payload.can_toggle);
    return {
        checked,
        sensitive,
        subtitle: payload.reason === 'ok' ? (checked ? '已开启' : '已关闭') : subtitleForReason(payload.reason),
        reason: payload.reason,
        message: payload.message ?? '',
    };
}
