import os

def wav_to_pcm(wav_file):
    # 假设 wav_file = "音频文件.wav"
    # wav_file.split(".") 得到["音频文件","wav"] 拿出第一个结果"音频文件"  与 ".pcm" 拼接 等到结果 "音频文件.pcm"
    pcm_file = "%s.pcm" %(wav_file.split(".")[0])

    # 就是此前我们在cmd窗口中输入命令,这里面就是在让Python帮我们在cmd中执行命令
    os.system("ffmpeg -y  -i %s  -acodec pcm_s16le -f s16le -ac 1 -ar 16000 %s"%(wav_file,pcm_file))

    return pcm_file

#wav_to_pcm('voice/006.m4a')


def amr_to_pcm(amr_file):
    pcm_file = "%s.pcm" %(amr_file.split(".")[0])
    mp3_file = "%s.mp3" %(amr_file.split(".")[0])
    os.system("ffmpeg -y -i %s -ac 1 -ar 16.0k %s"%(amr_file,mp3_file))
    os.system("ffmpeg -y  -i %s  -acodec pcm_s16le -f s16le  %s"%(mp3_file,pcm_file))

    return pcm_file

amr_to_pcm('voice/010.amr')
