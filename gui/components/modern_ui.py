"""BAAH 的公共视觉组件；只负责展示，不读取或修改业务配置。"""
from contextlib import contextmanager
from nicegui import ui


_defaults_ready = False


def apply_theme():
    """通过 NiceGUI 官方默认样式接口统一控件，按页面应用明暗配色。"""
    global _defaults_ready
    if not _defaults_ready:
        for control in (ui.input, ui.number, ui.select, ui.textarea):
            control.default_props('outlined dense')
            control.default_style('max-width: 100%')
        ui.label.default_classes('baah-text')
        ui.button.default_props('no-caps unelevated')
        ui.card.default_props('flat bordered')
        _defaults_ready = True
    ui.colors(primary='#3B82F6', secondary='#64748B', accent='#6366F1',
              positive='#16886C', negative='#DC4758', warning='#B7791F',
              dark='#182234', dark_page='#101827')
    ui.query('body').classes('baah-page')
    ui.add_css(STYLES)


def page_shell(*, home=False):
    """统一首页与编辑页外框；高度由正常文档流计算，避免绝对定位遮挡。"""
    return ui.column().classes('baah-shell baah-home' if home else 'baah-shell baah-editor')


def surface(extra=''):
    """统一可复用面板，允许调用方继续挂接原有绑定。"""
    return ui.card().classes(f'baah-surface {extra}')


def form_row():
    """可换行的常用表单行；不强制 display，保留 NiceGUI 的显隐控制。"""
    return ui.row().classes('baah-form-row')


def form_grid():
    """按容器可用宽度排列表单分组，无需每个页面单独计算列数。"""
    return ui.element('div').classes('baah-form-grid')


@contextmanager
def setting_group(title=None):
    """设置区块统一边距与标题，可嵌入动态表单而不接管其状态。"""
    with surface('baah-setting-group') as card:
        if title:
            ui.label(title).classes('baah-group-title')
        yield card


def operation_bar():
    """共用操作栏允许按钮自然换行，长翻译不会挤掉其他操作。"""
    return ui.row().classes('baah-operation-bar')


def notice_box(text, *, tone='info'):
    """共用静态提醒框：只展示传入文字，调用方继续负责原有条件和显隐。"""
    if tone not in {'info', 'warning'}:
        raise ValueError(f'Unsupported notice tone: {tone}')
    with ui.row().classes(f'baah-notice-box baah-notice-{tone}').props('role=note') as box:
        ui.icon('info_outline' if tone == 'info' else 'warning').classes(
            'baah-notice-icon').props('aria-hidden=true')
        ui.label(text).classes('baah-notice-body')
    return box


def navigation_item(label, selected, on_click, *, icon=None):
    """使用原生按钮提供键盘可达性，选中态仅改变样式。"""
    return ui.button(label, on_click=on_click, color=None, icon=icon).props('flat align=left').classes(
        'baah-nav-item' + (' baah-nav-selected' if selected else '')
    )


def log_panel(title):
    """折叠仅隐藏内容，不销毁日志实例，保持后台输出绑定有效。"""
    with ui.expansion(title, icon='terminal', value=False).classes('baah-log-panel'):
        return ui.log(max_lines=1000).props('visible').classes('baah-log')


def description_panel(title):
    """说明紧随当前表单标题，默认折叠以保留编辑空间。"""
    return ui.expansion(title, icon='info_outline', value=False).classes('baah-description')


def style_chart_options(options):
    """历史图表复用页面色板，仅补充文字、网格和浮层外观，不改动数据。"""
    color = "getComputedStyle(document.body).getPropertyValue('--baah-muted').trim()"
    border = "getComputedStyle(document.body).getPropertyValue('--baah-border').trim()"
    options.setdefault('textStyle', {})[':color'] = color
    options.setdefault('legend', {}).setdefault('textStyle', {})[':color'] = color
    for axis in [options['xAxis'], *options['yAxis']]:
        axis.setdefault('axisLabel', {})[':color'] = color
        axis.setdefault('nameTextStyle', {})[':color'] = color
        line = axis.setdefault('splitLine', {}).setdefault('lineStyle', {})
        line.pop('color', None)
        line[':color'] = border
    options.setdefault('tooltip', {}).update({
        ':backgroundColor': "getComputedStyle(document.body).getPropertyValue('--baah-surface').trim()",
        ':borderColor': border,
        'textStyle': {':color': color},
    })
    return options


STYLES = '''
body.baah-page {
    --baah-bg: #f3f6fb; --baah-overlay-surface: #fff;
    --baah-surface: var(--baah-overlay-surface); --baah-soft: #f8fafd;
    --baah-text: #25344b; --baah-muted: #687a91; --baah-border: #e0e7f0;
    --baah-accent: #2563eb; --baah-selected: #eaf2ff; --baah-hover: #f0f5fc;
    --baah-category-selected: #bfdbfe; --baah-page-selected: #f0f6ff;
    background: var(--baah-bg); color: var(--baah-text);
    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif; font-size: 14px;
    margin: 0; overflow: auto; isolation: isolate;
}
body.body--dark.baah-page {
    --baah-bg: #101827; --baah-overlay-surface: #182234; --baah-soft: #1d2a40;
    --baah-text: #e2eaf6; --baah-muted: #a0b1c8; --baah-border: #2d3c53;
    --baah-accent: #93c5fd; --baah-selected: #233b60; --baah-hover: #213149;
    --baah-category-selected: #365b88; --baah-page-selected: #1f3049;
}
/* 只有存在有效背景图时，普通页面表面才透出中景。 */
body.baah-page.baah-has-background { --baah-surface: transparent; --baah-soft: transparent; }
/* 后景由 body 主题色提供；中景独立于前景，不参与布局或拦截操作。 */
body.baah-page::before {
    content: ''; position: fixed; inset: 0; z-index: -1; pointer-events: none;
    background-image: var(--baah-background-image, none);
    background-size: var(--baah-background-size, auto);
    background-position: right bottom; background-repeat: no-repeat;
    -webkit-mask-image: linear-gradient(to right, transparent 40%, #000 60%),
                        linear-gradient(to bottom, transparent 0%, #000 25%);
    -webkit-mask-composite: source-in;
    mask-image: linear-gradient(to right, transparent 40%, #000 60%),
                linear-gradient(to bottom, transparent 0%, #000 25%);
    mask-composite: intersect;
}
.baah-page .nicegui-content { padding: 0; gap: 0; }
.baah-page * { box-sizing: border-box; scrollbar-width: thin; scrollbar-color: #9aaac0 transparent; }
.baah-page ::-webkit-scrollbar { width: 8px; height: 8px; }
.baah-page ::-webkit-scrollbar-thumb { background: #9aaac0; border-radius: 8px; }
.baah-page :focus-visible { outline: 2px solid #3b82f6; outline-offset: 3px; }
.baah-shell { width: 100%; padding: 16px; gap: 12px; min-width: 0; }
.baah-editor { height: 100dvh; min-height: 540px; flex-wrap: nowrap; }
.baah-surface { background: var(--baah-surface); border: 1px solid var(--baah-border);
    border-radius: 12px; padding: 16px; box-shadow: 0 2px 8px #1c355305; min-width: 0; }
.baah-page .q-card { background: var(--baah-surface); border-color: var(--baah-border); border-radius: 12px; }
.baah-page .q-field { color: var(--baah-text); min-width: 0; }
.baah-page .q-field__control { border-radius: 8px; background: var(--baah-surface); }
/* 输入沿用所属表面底色，保留选中及焦点等状态。 */
.baah-page .q-field--filled .q-field__control:before { background: transparent; }
.baah-page .q-uploader, .baah-page .q-uploader__header { background: var(--baah-surface); }
.baah-page .q-field--outlined .q-field__control:before { border-color: var(--baah-border); }
.baah-page .q-field__label, .baah-muted { color: var(--baah-muted); }
.baah-page .q-checkbox__label, .baah-page .q-radio__label { overflow-wrap: anywhere; }
.baah-page .q-btn { border-radius: 8px; min-height: 34px; font-size: 13px; transition: background-color .15s, box-shadow .15s; }
.baah-page .q-btn__content { gap: 5px; }
.baah-page .q-btn:focus-visible { box-shadow: 0 0 0 3px #3b82f633; }
.baah-page .q-btn--round { border-radius: 50%; }
/* 浮层独立于背景状态，其内部卡片与输入也继承不透明的主题表面。 */
.baah-page .q-menu, .baah-page .q-dialog__inner {
    --baah-surface: var(--baah-overlay-surface); --baah-soft: var(--baah-overlay-surface);
}
.baah-page .q-menu { border: 1px solid var(--baah-border); background: var(--baah-surface); border-radius: 10px; }
.baah-page .q-dialog__inner > .q-card { max-width: min(720px, calc(100vw - 32px)); overflow: auto; max-height: calc(100dvh - 48px); }
.baah-header { width: 100%; flex: none; gap: 12px; padding: 12px 16px; }
.baah-title-row { width: 100%; align-items: center; justify-content: space-between; gap: 12px; }
.baah-brand { align-items: center; gap: 10px; min-width: 0; flex: 1 1 180px; }
.baah-brand-name { font-size: 18px; font-weight: 650; overflow-wrap: anywhere; min-width: 0; }
.baah-operation-bar { align-items: center; gap: 8px; flex-wrap: wrap; min-width: 0; }
.baah-connection { width: 100%; gap: 12px; align-items: center; padding-top: 12px; border-top: 1px solid var(--baah-border); }
.baah-connection > .q-field { flex: 1 1 160px; }
.baah-connection .baah-address { flex: 2 1 250px; gap: 8px; align-items: center; min-width: 0; }
.baah-address > .q-field { flex: 1 1 100px; }
.baah-connection .baah-serial { flex: 1 1 180px; min-width: 0; }
.baah-connection .baah-path { flex: 3 1 280px; min-width: 0; }
.baah-workspace { width: 100%; flex: 1 1 0; min-height: 0; flex-wrap: nowrap; gap: 12px; align-items: stretch; }
.baah-nav { width: 224px; flex: 0 0 224px; padding: 8px; gap: 0; overflow: hidden; flex-wrap: nowrap; }
.baah-nav .q-tabs { width: 100%; flex: none; padding-bottom: 12px; margin-bottom: 12px; border-bottom: 1px solid var(--baah-border); }
.baah-nav .q-tabs__content { flex-direction: column; align-items: stretch; width: 100%; }
.baah-nav .q-tab { min-height: 36px; justify-content: flex-start; border-radius: 8px; }
/* 一级和二级导航都将图标紧贴文字，分类分隔线两侧分别留出 12px。 */
.baah-nav .q-tab__content { width: 100%; flex-direction: row; justify-content: flex-start; gap: 8px; }
.baah-nav .q-tab__icon { width: 18px; height: 18px; font-size: 18px; margin: 0; flex: 0 0 18px; }
.baah-nav .q-tab__label { white-space: normal; text-align: left; font-size: 13px; font-weight: 700; }
/* 一级分类以粗体和较深选中底色突出层级，二级页面使用浅底色保留当前定位。 */
.baah-nav .q-tab--active { background: var(--baah-category-selected); color: var(--baah-accent); }
.baah-nav .q-tab__indicator { display: none; }
.baah-nav-scroll { width: 100%; min-height: 0; flex: 1 1 0; overflow: auto; gap: 4px; }
.baah-nav-item { width: 100%; text-align: left; padding: 8px 12px; color: var(--baah-muted); border-left: 3px solid transparent; }
.baah-nav-item .q-btn__content { justify-content: flex-start; gap: 8px; text-align: left; overflow-wrap: anywhere; }
.baah-nav-item .q-icon { font-size: 18px; flex: 0 0 18px; margin: 0; }
.baah-nav-item .q-btn__content > .block { min-width: 0; flex: 1; }
.baah-nav-selected { background: var(--baah-page-selected); color: var(--baah-accent); border-left-color: var(--baah-accent); font-weight: 650; }
.baah-main { flex: 1 1 0; min-width: 0; min-height: 0; padding: 0; overflow: auto; gap: 0; }
.baah-form { width: 100%; min-width: 0; padding: 24px; gap: 16px; }
.baah-form > .nicegui-column { max-width: 100%; }
.baah-form .nicegui-row, .baah-form .nicegui-column { min-width: 0; max-width: 100%; }
.baah-form .q-field, .baah-form .q-uploader { max-width: 100%; }
.baah-form .q-card { max-width: 100%; }
.baah-form iframe { max-width: 100%; border-radius: 10px; }
.baah-form .baah-text { overflow-wrap: anywhere; }
/* 标签独占首行，前缀、输入值、后缀共用第二行；长标签换行不会拆散数字与单位。 */
.baah-form .q-field--labeled .q-field__control { height: auto; min-height: 56px; }
.baah-form .q-field--labeled .q-field__control-container { display: grid; grid-template-columns: auto minmax(0, 1fr) auto; align-content: center; align-items: center; padding: 7px 0; min-width: 0; }
.baah-form .q-field--labeled .q-field__label { position: static; grid-column: 1 / -1; grid-row: 1; transform: none !important; max-width: 100%; width: auto; font-size: 12px; line-height: 1.35; white-space: normal; overflow-wrap: anywhere; }
.baah-form .q-field--labeled .q-field__native { grid-column: 2; grid-row: 2; padding-top: 0; min-height: 24px; min-width: 0; width: 100%; }
/* 清除 Quasar 浮动标签给单位预留的顶部间距，始终让单位和输入值对齐且不折行。 */
.baah-form .q-field--labeled .q-field__prefix { grid-column: 1; grid-row: 2; padding: 0 6px 0 0; white-space: nowrap; line-height: 24px; }
.baah-form .q-field--labeled .q-field__suffix { grid-column: 3; grid-row: 2; padding: 0 0 0 6px; white-space: nowrap; line-height: 24px; }
/* 前后附加图标与按钮对齐输入值，避免下拉箭头、清除和密码按钮停留在标签一行。 */
.baah-form .q-field--labeled .q-field__control > .q-field__marginal { align-self: flex-end; height: 26px; margin-bottom: 7px; }
.baah-form-body > .nicegui-row:first-child:has(> a[name]) > div { font-size: 16px !important; font-weight: 600; }
.baah-product-title { font-size: 20px; font-weight: 600; line-height: 1.5; }
.baah-notice { padding: 12px 16px; border-left: 3px solid var(--q-warning); background: var(--baah-soft); border-radius: 8px; }
.baah-notice-text { font-size: 14px; line-height: 1.8; color: var(--q-warning); }
.baah-list-items .baah-list-items { width: auto; flex: 0 1 auto; }
/* 仅纵向排列条目卡片内的字段，外层条目行和操作栏分别控制自身布局。 */
.baah-list-entry { flex-direction: column; flex-wrap: nowrap; align-items: center; }
.baah-form-title { font-size: 22px; font-weight: 650; line-height: 1.4; }
.baah-section-title { font-size: x-large; }
.baah-background-upload { width: auto; min-width: 0; box-shadow: none; }
.baah-background-upload .q-uploader__header { padding: 0; }
.baah-background-upload .q-uploader__list { display: none; }
.baah-background-scale { width: 200px; }
.baah-form-body { width: 100%; min-width: 0; gap: 16px; }
.baah-form-body > .nicegui-row:first-child { margin-bottom: 0; }
.baah-form-body > .nicegui-row:first-child > .baah-text { font-size: 16px !important; font-weight: 600; }
.baah-description { width: 100%; background: var(--baah-soft); border-radius: 8px; }
.baah-description .q-expansion-item__content { padding: 0 16px 12px; overflow-wrap: anywhere; }
.baah-description .q-item { min-height: 38px; font-size: 13px; color: var(--baah-muted); }
.baah-log-panel { width: 100%; flex: none; background: var(--baah-surface); border: 1px solid var(--baah-border); border-radius: 12px; overflow: hidden; }
.baah-log-panel .q-item { min-height: 40px; font-size: 13px; }
.baah-log { height: min(200px, 30dvh); min-height: 120px; width: 100%; padding: 0; border-top: 1px solid var(--baah-border); background: var(--baah-soft); font: 12px/1.7 Consolas, monospace; overflow: hidden; }
/* 日志使用 Quasar 自带滚动区，移除外层重复滚动与展开容器默认留白。 */
.baah-log-panel .q-expansion-item__content { padding: 0; }
.baah-log-panel .q-expansion-item__content > .nicegui-column { padding: 0; gap: 0; }
.baah-log .q-scrollarea__content { padding: 12px 16px; }
.baah-form .nicegui-row:has(.baah-flow-editor), .baah-form .nicegui-column:has(.baah-flow-editor) { width: 100%; }
.baah-flow-editor .q-uploader { box-shadow: none; border: 1px solid var(--baah-border); border-radius: 8px; }
/* 提醒正文统一使用主题文字色，长说明与图标分列，窄屏自然换行。 */
.baah-notice-box { width: 100%; max-width: 100%; min-width: 0; padding: 12px 16px; gap: 10px; align-items: flex-start; flex-wrap: nowrap; background: var(--baah-soft); border: 1px solid var(--baah-border); border-radius: 8px; border-left: 3px solid var(--q-primary); }
.baah-notice-icon { font-size: 20px; line-height: 25px; flex: 0 0 20px; color: var(--q-primary); }
.baah-notice-body { flex: 1; min-width: 0; line-height: 1.8; color: var(--baah-text); white-space: pre-line; overflow-wrap: anywhere; }
.baah-notice-warning { border-left-color: var(--q-warning); }
.baah-notice-warning .baah-notice-icon { color: var(--q-warning); }
.baah-resource-guide { width: 100%; gap: 12px; }
.baah-help-text { max-width: 100%; line-height: 1.8; color: var(--baah-muted); overflow-wrap: anywhere; }
.baah-described-field { width: 500px; max-width: 100%; gap: 8px; }
/* 图表筛选控件整体居中，换行后每一行仍保持居中。 */
.baah-chart-filters { width: 100%; justify-content: center; align-items: center; gap: 16px; flex-wrap: wrap; }
.baah-form-row { width: 100%; align-items: center; gap: 12px; flex-wrap: wrap; }
.baah-form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 280px), 1fr)); width: 100%; gap: 16px; align-items: start; }
.baah-setting-group { width: 100%; gap: 12px; }
.baah-group-title { font-size: 15px; font-weight: 600; }
.baah-list-editor { width: 100%; gap: 16px; }
.baah-list-items { width: 100%; gap: 12px; align-items: stretch; }
.baah-list-entry { padding: 12px; gap: 10px; min-width: 130px; }
.baah-list-entry .q-field { width: 128px; }
.baah-list-actions { gap: 8px; justify-content: center; }
.baah-team-row > .q-field { flex: 1 1 150px; }
.baah-image-preview { width: 300px; max-width: 100%; height: 150px; border: 1px dashed var(--baah-border); border-radius: 10px; overflow: hidden; background: var(--baah-soft); }
.baah-flow-editor { width: 100%; gap: 16px; }
.baah-flow-card { width: 100%; padding: 16px; gap: 12px; }
.baah-flow-card > .nicegui-row, .baah-flow-card > .nicegui-row > .nicegui-column { width: 100%; }
.baah-history-chart { width: 100%; height: 360px; max-height: 55vh; min-height: 260px; }
.baah-home { min-height: 100dvh; max-width: 1600px; margin: 0 auto; padding: 32px; gap: 24px; }
.baah-home-grid { display: grid; width: 100%; grid-template-columns: minmax(0, 1fr) minmax(320px, .58fr); gap: 24px; align-items: start; }
.baah-home-info { grid-column: 2; grid-row: 1; gap: 20px; width: 100%; }
.baah-home-configs { grid-column: 1; grid-row: 1; gap: 16px; width: 100%; }
.baah-home-title { font-size: 28px; font-weight: 650; line-height: 1.3; }
.baah-config-list { width: 100%; gap: 12px; }
.baah-config-card { flex-direction: row; width: 100%; align-items: center; gap: 12px; flex-wrap: wrap; padding: 16px; }
.baah-config-link { flex: 1 1 200px; min-width: 0; text-decoration: none; color: var(--baah-text); }
.baah-config-link:hover { color: #3b82f6; }
.baah-config-link .q-card { border: 0; padding: 0; box-shadow: none; }
.baah-config-link .baah-text { overflow-wrap: anywhere; font-weight: 600; }
.baah-config-actions { gap: 8px; align-items: center; }
.baah-release { width: 100%; padding: 16px; gap: 12px; max-height: 360px; overflow: auto; }
.baah-release .nicegui-html { overflow-wrap: anywhere; }
.baah-nav-toggle { display: none; }
/* 统一兼容旧页面中的红色提示和白底按钮，保证暗色与弹窗中的可读性。 */
.baah-form .baah-text[style*="color: red"] { color: var(--q-negative) !important; font-size: 14px !important; line-height: 1.8; }
@layer components {
    .baah-page .q-btn.bg-white, .baah-page .q-btn[style*="background-color: white"] { color: #25344b !important; }
    .baah-page a { color: var(--baah-accent) !important; }
    .baah-page.body--dark .text-grey-7, .baah-page.body--dark .text-gray-500 { color: var(--baah-muted) !important; }
    .baah-page.body--dark .q-btn--flat.text-primary { color: var(--baah-accent) !important; }
}
@media (max-width: 1100px) {
    .baah-nav { width: 200px; flex-basis: 200px; }
    .baah-form { padding: 20px; }
    .baah-home { padding: 20px; }
    .baah-home-grid { gap: 16px; }
}
@media (max-width: 899px) {
    .baah-shell { padding: 8px; gap: 8px; }
    .baah-editor { height: auto; min-height: 100dvh; }
    .baah-workspace { flex-direction: column; flex: auto; }
    .baah-nav { width: 100%; flex: none; }
    .baah-nav .q-tabs__content { flex-direction: row; }
    .baah-nav-scroll { flex: auto; max-height: 250px; }
    .baah-nav-toggle { display: inline-flex; }
    .baah-nav-collapsed .baah-nav { display: none; }
    .baah-main { overflow: visible; flex: auto; }
    .baah-form { padding: 16px; }
    .baah-form-grid { grid-template-columns: minmax(0, 1fr); }
    .baah-home-grid { grid-template-columns: minmax(0, 1fr); }
    .baah-home-configs { grid-column: 1; grid-row: 1; }
    .baah-home-info { grid-column: 1; grid-row: 2; }
    .baah-connection { gap: 10px; }
    .baah-operation-bar { width: 100%; }
}
@media (prefers-reduced-motion: reduce) {
    .baah-page *, .baah-page *:before, .baah-page *:after { transition-duration: 0s !important; animation-duration: 0s !important; }
}
'''
