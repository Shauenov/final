import subprocess
from app.core.logger import logger

class TranscoderService():
  def transcodeToHls(self, input_path: str, output_path: str) -> bool:
    try:
        cmd = "ffmpeg -i %s -c:v h264 -c:a aac -strict -2 -start_number 0 -hls_time 10 -hls_list_size 0 -f hls %s" % (input_path, output_path)
        res = subprocess.call(cmd, shell=True)

        if res != 0:
            return False
        return True
    except Exception as e:
        logger.error("Transcoding error: %s", e)
        return False
        