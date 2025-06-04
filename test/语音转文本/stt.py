from vosk import Model, KaldiRecognizer
import pyaudio
import json
import time
import sys
import os # 导入 os 模块用于检查模型路径是否存在

# 设置默认参数
DEFAULT_SILENCE_THRESHOLD_SECONDS = 2.0
DEFAULT_RECORDING_TIMEOUT_SECONDS = 60.0
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_CHUNK_SIZE = 4000


class VoskMicTranscriber:
    """
    使用 Vosk 库从麦克风进行语音识别的类。
    初始化时加载 Vosk 模型和 PyAudio，识别方法可重复调用。
    实现了上下文管理器以便使用 'with' 语句，但这里提供一个只返回实例的函数。
    """
    def __init__(self, model_path, rate=DEFAULT_SAMPLE_RATE, chunk_size=DEFAULT_CHUNK_SIZE,
                 silence_threshold_seconds=DEFAULT_SILENCE_THRESHOLD_SECONDS,
                 recording_timeout_seconds=DEFAULT_RECORDING_TIMEOUT_SECONDS):
        # __init__ 方法保持不变，负责初始化耗时资源
        if not os.path.exists(model_path):
             raise FileNotFoundError(f"Vosk model path not found: {model_path}")

        print(f"正在加载 Vosk 模型: {model_path} ...")
        try:
            self.model = Model(model_path)
            self.rec = KaldiRecognizer(self.model, rate)
            print("Vosk 模型加载成功。")
        except Exception as e:
            print(f"加载 Vosk 模型或初始化识别器失败: {e}", file=sys.stderr)
            self.model = None
            self.rec = None
            raise # 失败则抛出异常

        print("正在初始化 PyAudio...")
        try:
            self.pyaudio_instance = pyaudio.PyAudio()
            print("PyAudio 初始化成功。")
        except Exception as e:
             print(f"初始化 PyAudio 失败: {e}", file=sys.stderr)
             self.pyaudio_instance = None
             raise # 如果 PyAudio 失败，同样抛出异常

        self.rate = rate
        self.chunk_size = chunk_size
        self.silence_threshold_seconds = silence_threshold_seconds
        self.recording_timeout_seconds = recording_timeout_seconds

        print("VoskMicTranscriber 初始化完成。")


    def listen_and_transcribe(self):
        """
        启动麦克风录音，直到检测到静音或达到最大时长，然后返回识别结果。

        Returns:
            str: 识别到的文本，如果初始化失败或录音出错则返回空字符串。
        """
        # listen_and_transcribe 方法也保持不变
        if not self.rec or not self.pyaudio_instance:
            print("Transcriber 未正确初始化，无法执行转录。", file=sys.stderr)
            return ""

        stream = None
        result = ''
        print("请讲话 (检测到静音自动停止)...")

        try:
            stream = self.pyaudio_instance.open(format=pyaudio.paInt16,
                                                channels=1,
                                                rate=self.rate,
                                                input=True,
                                                frames_per_buffer=self.chunk_size)
            stream.start_stream()

            last_speech_time = time.time()
            start_time = time.time()
            speech_started = False

            while True:
                current_time = time.time()
                if current_time - start_time > self.recording_timeout_seconds:
                    print(f"\n达到最大录音时长 ({self.recording_timeout_seconds}s)，停止录音。")
                    break
                try:
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                except IOError as e:
                     print(f"\n录音IO错误: {e}", file=sys.stderr)
                     break
                if not data:
                     print("\n未读取到音频数据，停止录音。", file=sys.stderr)
                     break

                if self.rec.AcceptWaveform(data):
                    part = json.loads(self.rec.Result())
                    recognized_text = part.get('text', '')
                    if recognized_text:
                        result += recognized_text + ' '
                        last_speech_time = current_time
                        speech_started = True
                        print(f"识别到一段: {recognized_text.strip()}")
                else:
                    partial_result = json.loads(self.rec.PartialResult())
                    partial_text = partial_result.get('partial', '')
                    if partial_text:
                        last_speech_time = current_time
                        speech_started = True
                        print(f"正在听: {partial_text}", end='\r')

                if speech_started and (current_time - last_speech_time > self.silence_threshold_seconds):
                    print(f"\n检测到静音超过 {self.silence_threshold_seconds} 秒，停止录音。")
                    break

        except Exception as e:
            print(f"\n录音或识别过程中发生未知错误: {e}", file=sys.stderr)

        finally:
            if stream is not None:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception as e:
                     print(f"关闭音频流时出错: {e}", file=sys.stderr)

        try:
             final_part = json.loads(self.rec.FinalResult())
             final_text = final_part.get('text', '')
             result += final_text
        except Exception as e:
             print(f"获取最终识别结果时出错: {e}", file=sys.stderr)

        return result.strip()


    def close(self):
        """
        释放 PyAudio 资源。在程序结束时调用。
        """
        print("正在释放 PyAudio 资源...")
        if self.pyaudio_instance is not None:
            try:
                self.pyaudio_instance.terminate()
                self.pyaudio_instance = None
                print("PyAudio 资源已释放。")
            except Exception as e:
                print(f"释放 PyAudio 资源时出错: {e}", file=sys.stderr)

    # 虽然不通过 with 语句使用，但 __enter__ 和 __exit__ 仍然存在于类定义中
    # 如果将来决定改回使用 with，这些方法是必须的
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

_global_model_path = "D:/voiceModel/vosk-model-cn-0.22" # 使用一个全局变量或在函数参数中指定

def get_vosk_mic_transcriber_instance(model_path=_global_model_path,
                                     silence_threshold_seconds=DEFAULT_SILENCE_THRESHOLD_SECONDS,
                                     recording_timeout_seconds=DEFAULT_RECORDING_TIMEOUT_SECONDS):
    """
    创建并返回 VoskMicTranscriber 的实例。
    请注意：调用方负责在使用完毕后手动调用返回对象的 .close() 方法。
    """
    print("正在创建 VoskMicTranscriber 实例...")
    try:
        # 直接创建实例，不使用 with 语句
        transcriber = VoskMicTranscriber(model_path=model_path,
                                         silence_threshold_seconds=silence_threshold_seconds,
                                         recording_timeout_seconds=recording_timeout_seconds)
        print("VoskMicTranscriber 实例创建成功。")
        return transcriber
    except Exception as e:
        print(f"创建 VoskMicTranscriber 实例失败: {e}", file=sys.stderr)
        # 如果创建失败，返回 None 或者重新抛出异常都可以
        # 这里选择重新抛出异常，让调用方知道初始化失败了
        raise

# 示例用法
if __name__ == '__main__':
    # 请将此路径替换为你实际的 Vosk 模型路径
    model_path = "D:/voiceModel/vosk-model-small-cn-0.22"

    # 检查模型路径是否存在
    if not os.path.exists(model_path):
        print(f"错误：模型路径不存在 - {model_path}")
        print("请修改 model_path 变量为你实际的模型位置。")
        sys.exit(1) # 退出程序

    transcriber = None # 初始化为 None
    try:
        # 创建转录器实例 (在这里会加载模型和初始化 PyAudio，比较耗时)
        # 使用 'with' 语句可以确保在程序结束或出错时自动调用 transcriber.close()
        with VoskMicTranscriber(model_path=model_path,
                                 silence_threshold_seconds=DEFAULT_SILENCE_THRESHOLD_SECONDS, # 可以调整静音阈值
                                 recording_timeout_seconds=DEFAULT_RECORDING_TIMEOUT_SECONDS) as transcriber:

            print("\n转录器已准备就绪。可以开始录音。")

            # --- 第一次录音和识别 ---
            print("\n--- 请开始第一次讲话 ---")
            transcribed_text1 = transcriber.listen_and_transcribe()
            print("\n====== 第一次识别结果 ======")
            if transcribed_text1:
                print(transcribed_text1)
            else:
                print("未能识别到有效的语音。")
            print("==========================")

            # 可以在这里进行其他操作，例如处理第一次识别的结果

            # 间隔一段时间，准备进行下一次录音
            time.sleep(2)
            print("\n准备开始第二次录音...")
            time.sleep(1)

            # --- 第二次录音和识别 ---
            print("\n--- 请开始第二次讲话 ---")
            transcribed_text2 = transcriber.listen_and_transcribe()
            print("\n====== 第二次识别结果 ======")
            if transcribed_text2:
                print(transcribed_text2)
            else:
                print("未能识别到有效的语音。")
            print("==========================")

            # transcriber.close() 会在 'with' 块结束时自动调用

    except FileNotFoundError as e:
        print(e, file=sys.stderr)
    except Exception as e:
        print(f"程序运行过程中发生错误: {e}", file=sys.stderr)
        # 如果在初始化阶段就出错 (如模型加载失败)，transcriber 可能为 None，
        # 'with' 语句的 __exit__ 不会被调用，这里可以额外检查并清理 PyAudio
        # 但因为 __init__ 已经抛出异常且被外层 except 捕获，
        # 且 __init__ 中如果 PyAudio 初始化失败会抛出异常，
        # __exit__ 只会在 __init__ 成功后，但 listen_and_transcribe 内部出错时调用。
        # 这里的结构是安全的，外层 except 捕获初始化错误，with 语句捕获 listen_and_transcribe 错误并调用 close。
        # 如果是初始化 PyAudio 失败，__init__ 抛出异常，被外层 except 捕获，transcriber 变量仍然是 None，无需清理。