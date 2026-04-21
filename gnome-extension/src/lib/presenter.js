export function buildToggleViewModel(state, busy) {
    if (busy) {
        return {
            checked: state.checked,
            sensitive: false,
            subtitle: '切换中…',
        };
    }

    return {
        checked: state.checked,
        sensitive: state.sensitive,
        subtitle: state.subtitle,
    };
}
