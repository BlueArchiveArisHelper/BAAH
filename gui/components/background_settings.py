"""全局背景图片的文件管理、显示设置及页面初始化。"""
import asyncio
from io import BytesIO
import math
from pathlib import Path
import tempfile

from fastapi import HTTPException
from fastapi.responses import FileResponse
from nicegui import app, events, run, ui
from PIL import Image, ImageOps, UnidentifiedImageError

from modules.configs.MyConfig import MyConfigger
from .modern_ui import form_row, operation_bar


BACKGROUND_NAME = 'background.png'
BACKGROUND_URL = '/baah/background.png'
IMAGE_FORMATS = ('PNG', 'JPEG', 'WEBP', 'BMP', 'GIF', 'TIFF')


def _background_path() -> Path:
    return Path(MyConfigger.USER_STORAGE_FOLDER) / BACKGROUND_NAME


@app.get(BACKGROUND_URL)
def background_image() -> FileResponse:
    """仅提供固定背景文件；替换后刷新不得继续使用旧图片缓存。"""
    path = _background_path()
    if not path.is_file():
        raise HTTPException(status_code=404)
    return FileResponse(path, media_type='image/png', headers={'Cache-Control': 'no-store'})


def _validate_scale(value) -> float:
    scale = float(value)
    if not math.isfinite(scale) or not 20.0 <= scale <= 200.0:
        raise ValueError('Invalid background scale')
    return round(scale, 1)


def _current_scale(shared_softwareconfig) -> float:
    try:
        return _validate_scale(shared_softwareconfig.softwareconfigdict['BACKGROUND_PIC_SCALE'])
    except (TypeError, ValueError, OverflowError):
        return 100.0


def save_background_image(data: bytes) -> None:
    """转为静态 PNG，保留原尺寸与透明度；完整写入后才替换旧文件。"""
    with Image.open(BytesIO(data), formats=IMAGE_FORMATS) as source:
        image = ImageOps.exif_transpose(source).convert('RGBA')
    path = _background_path()
    temporary = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=path.parent, suffix='.png', delete=False) as output:
            temporary = Path(output.name)
        image.save(temporary, format='PNG')
        temporary.replace(path)
    finally:
        image.close()
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def apply_background(shared_softwareconfig) -> None:
    """在等待浏览器前注册页面背景；缺失或损坏的图片退回纯色底层。"""
    image = 'none'
    size = 'auto'
    if shared_softwareconfig.softwareconfigdict['BACKGROUND_PIC_NAME']:
        try:
            with Image.open(_background_path(), formats=('PNG',)) as source:
                source.verify()
                width, height = source.size
            scale = _current_scale(shared_softwareconfig) / 100.0
            image = f'url("{BACKGROUND_URL}")'
            # 1080px 高度为基准；由 CSS 随视窗高度调整，不需要刷新或监听 resize。
            size = (f'calc(100dvh * {width * scale:g} / 1080) '
                    f'calc(100dvh * {height * scale:g} / 1080)')
        except (OSError, ValueError, Image.DecompressionBombError):
            pass
    # 以实际可用图片决定表面样式，配置中有文件名并不代表文件仍然有效。
    if image == 'none':
        ui.query('body').classes(remove='baah-has-background')
    else:
        ui.query('body').classes('baah-has-background')
    ui.add_css(f'body.baah-page {{ --baah-background-image: {image}; --baah-background-size: {size}; }}')


def background_settings(shared_softwareconfig) -> None:
    """设置仅在明确操作后保存；缩放输入为草稿，不直接绑定共享配置。"""
    from starlette.formparsers import MultiPartParser
    # 由于锁定的aiofiles库有bug，超过spool_max_size的上传文件会报错，这里修改下默认大小（默认1MB） 
    MultiPartParser.spool_max_size = 1024 * 1024 * 10  # 10 MB
    text = shared_softwareconfig.get_text

    def save_setting(key, value):
        previous = shared_softwareconfig.softwareconfigdict[key]
        shared_softwareconfig.softwareconfigdict[key] = value
        try:
            shared_softwareconfig.save_software_config()
        except OSError:
            shared_softwareconfig.softwareconfigdict[key] = previous
            raise

    def show_error(key):
        ui.notify(text(key), type='negative')

    async def upload_image(event: events.UploadEventArguments):
        try:
            await run.io_bound(save_background_image, await event.file.read())
            save_setting('BACKGROUND_PIC_NAME', BACKGROUND_NAME)
        except (UnidentifiedImageError, ValueError, Image.DecompressionBombError):
            show_error('notice_background_invalid_image')
            uploader.reset()
            return
        except OSError:
            show_error('notice_background_file_error')
            uploader.reset()
            return
        ui.navigate.reload()

    def confirm_scale():
        try:
            value = _validate_scale(scale.value)
        except (TypeError, ValueError, OverflowError):
            show_error('notice_background_invalid_scale')
            return
        try:
            save_setting('BACKGROUND_PIC_SCALE', value)
        except OSError:
            show_error('notice_background_file_error')
            return
        ui.navigate.reload()

    def clear_image():
        try:
            _background_path().unlink(missing_ok=True)
            save_setting('BACKGROUND_PIC_NAME', '')
        except OSError:
            show_error('notice_background_file_error')
            return
        ui.navigate.reload()

    ui.label(text('setting_display')).classes('baah-section-title')
    ui.link(text('desc_background_refresh'), target = 'https://www.gamekee.com/ba/614736',new_tab=True).classes('baah-help-text')
    with form_row():
        uploader = ui.upload(on_upload=upload_image, auto_upload=True,
                             on_rejected=lambda: show_error('notice_background_invalid_image')).props(
            'accept=".png,.jpg,.jpeg,.webp,.bmp,.gif,.tif,.tiff" flat no-border hide-upload-btn'
        ).classes('baah-background-upload')
        # 使用原生上传触发器打开本地选择器，外观只保留一个选择按钮。
        with uploader.add_slot('header'):
            with ui.button(text('button_background_select'), icon='image'):
                ui.element('q-uploader-add-trigger')
        with operation_bar():
            scale = ui.number(text('config_background_scale'), value=_current_scale(shared_softwareconfig),
                              min=20.0, max=200.0, step=10, precision=1, format='%.1f', suffix='%').classes(
                'baah-background-scale')
            ui.button(text('button_background_apply_scale'), on_click=confirm_scale)
            ui.button(text('button_background_clear'), on_click=clear_image, color='negative')
