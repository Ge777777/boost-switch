export function subtitleForReason(reason) {
    switch (reason) {
    case 'ok':
        return '已关闭';
    case 'inactive_session':
        return '当前会话未激活';
    case 'permission_denied':
        return '需要授权';
    case 'sysfs_missing':
        return '未找到 boost 开关';
    case 'service_unavailable':
        return '服务不可达';
    default:
        return '状态未知';
    }
}
