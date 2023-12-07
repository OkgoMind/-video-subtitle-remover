import warnings
warnings.filterwarnings('ignore')
import os
import torch
import logging
import platform
import stat
from fsplit.filesplit import Filesplit
import paddle
paddle.disable_signal_handler()
logging.disable(logging.DEBUG)  # 关闭DEBUG日志的打印
logging.disable(logging.WARNING)  # 关闭WARNING日志的打印
device = "cuda" if torch.cuda.is_available() else "cpu"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LAMA_CONFIG = os.path.join(BASE_DIR, 'inpaint', 'lama', 'configs', 'prediction', 'default.yaml')
LAMA_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'big-lama')
VIDEO_INPAINT_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'video')
MODEL_VERSION = 'V4'
DET_MODEL_BASE = os.path.join(BASE_DIR, 'models')
DET_MODEL_PATH = os.path.join(DET_MODEL_BASE, MODEL_VERSION, 'ch_det')

# ×××××××××××××××××××× [可以改] start ××××××××××××××××××××
# 容忍的像素点偏差
PIXEL_TOLERANCE_Y = 20  # 允许检测框纵向偏差50个像素点
PIXEL_TOLERANCE_X = 20  # 允许检测框横向偏差100个像素点
# 字幕区域偏移量
SUBTITLE_AREA_DEVIATION_PIXEL = 50
# 20个像素点以内的差距认为是同一行
TOLERANCE_Y = 20
# 高度差阈值
THRESHOLD_HEIGHT_DIFFERENCE = 20
# 【根据自己的GPU显存大小设置】最大同时处理的图片数量，设置越大处理效果越好，但是要求显存越高
# 1280x720p视频设置80需要25G显存，设置50需要19G显存
# 720x480p视频设置80需要8G显存，设置50需要7G显存
MAX_PROCESS_NUM = 70
# 【根据自己内存大小设置，应该大于等于MAX_PROCESS_NUM】
MAX_LOAD_NUM = 70
# 是否开启精细模式，开启精细模式将消耗大量GPU显存，如果您的显卡显存较少，建议设置为False
ACCURATE_MODE = True
# 是否开启快速模型，不保证inpaint效果
FAST_MODE = False
# ×××××××××××××××××××× [可以改] start ××××××××××××××××××××


# ×××××××××××××××××××× [不要改] start ××××××××××××××××××××
# 查看该路径下是否有模型完整文件，没有的话合并小文件生成完整文件
if 'best.ckpt' not in (os.listdir(os.path.join(LAMA_MODEL_PATH, 'models'))):
    fs = Filesplit()
    fs.merge(input_dir=os.path.join(LAMA_MODEL_PATH, 'models'))

if 'inference.pdiparams' not in os.listdir(DET_MODEL_PATH):
    fs = Filesplit()
    fs.merge(input_dir=DET_MODEL_PATH)

if 'ProPainter.pth' not in os.listdir(VIDEO_INPAINT_MODEL_PATH):
    fs = Filesplit()
    fs.merge(input_dir=VIDEO_INPAINT_MODEL_PATH)

# 指定ffmpeg可执行程序路径
sys_str = platform.system()
if sys_str == "Windows":
    ffmpeg_bin = os.path.join('win_x64', 'ffmpeg.exe')
elif sys_str == "Linux":
    ffmpeg_bin = os.path.join('linux_x64', 'ffmpeg')
else:
    ffmpeg_bin = os.path.join('macos', 'ffmpeg')
FFMPEG_PATH = os.path.join(BASE_DIR, '', 'ffmpeg', ffmpeg_bin)

if 'ffmpeg.exe' not in os.listdir(os.path.join(BASE_DIR, '', 'ffmpeg', 'win_x64')):
    fs = Filesplit()
    fs.merge(input_dir=os.path.join(BASE_DIR, '', 'ffmpeg', 'win_x64'))
# 将ffmpeg添加可执行权限
os.chmod(FFMPEG_PATH, stat.S_IRWXU+stat.S_IRWXG+stat.S_IRWXO)

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# 如果开启了快速模式，则强制关闭ACCURATE_MODE
if FAST_MODE:
    ACCURATE_MODE = False
# ×××××××××××××××××××× [不要改] end ××××××××××××××××××××
