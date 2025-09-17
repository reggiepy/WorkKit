# *_*coding:utf-8 *_*
# @File   : sound.py
# @Author : Reggie
# @Time   : 2025/08/28 13:30
import math
import struct
import wave
from pathlib import Path


def generate_sound(success_sound_file: str):
    """
    重新生成“成功提示音”，生成两个连续音调的 WAV 文件。

    :param str success_sound_file: 输出 WAV 文件路径
    :returns: 三元组 (文件路径或 None, 状态信息, 状态码)
        - 成功: (success_sound_file, "success", 0)
        - 失败: (None, 错误信息, 1)

    音调参数固定为：
        - 第一个音调：800Hz, 0.3秒
        - 第二个音调：1000Hz, 0.4秒
        - 采样率：44100Hz
        - 音量：50%
    """
    sample_rate = 44100
    duration1, duration2 = 0.3, 0.4
    frequency1, frequency2 = 800, 1000
    volume = 0.5  # 音量比例

    output_path = Path(success_sound_file)
    try:
        # 确保目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with wave.open(output_path.as_posix(), 'w') as wav_file:
            # 参数: 单声道, 16bit, 采样率
            wav_file.setparams((1, 2, sample_rate, 0, 'NONE', 'not compressed'))

            # 写入第一个音调
            for i in range(int(sample_rate * duration1)):
                t = i / sample_rate
                sample = int(32767 * volume * math.sin(2 * math.pi * frequency1 * t))
                wav_file.writeframes(struct.pack('<h', sample))  # 小端 16bit

            # 写入第二个音调
            for i in range(int(sample_rate * duration2)):
                t = i / sample_rate
                sample = int(32767 * volume * math.sin(2 * math.pi * frequency2 * t))
                wav_file.writeframes(struct.pack('<h', sample))

        return success_sound_file, "success", 0

    except Exception as e:
        # 生成失败，尝试写空占位文件
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path.as_posix(), 'w') as f:
                f.write('')
        except Exception:
            pass
        return None, f"生成提示音失败: {str(e)}", 1


if __name__ == '__main__':
    print(generate_sound("test.wav"))
