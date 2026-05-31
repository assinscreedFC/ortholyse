import logging
import sys
import os
import json
import tempfile
from pydub import AudioSegment
from pydub.silence import detect_silence

from app.models.operation_fichier import _validate_audio_file

logger = logging.getLogger(__name__)

def find_ffmpeg():
    """Détecte le chemin de FFmpeg pour PyDub"""
    if getattr(sys, 'frozen', False):
        # En mode bundle PyInstaller
        base_path = sys._MEIPASS
        ffmpeg_path = os.path.abspath(os.path.join(base_path, '_internal', 'ffmpeg'))
    else:
        # En mode développement
        ffmpeg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../bin', 'ffmpeg'))
    return ffmpeg_path

AudioSegment.converter = find_ffmpeg()

def file_size_ms(file_path):
    """Retourne la durée du fichier audio en millisecondes"""
    fmt = _validate_audio_file(file_path)
    audio = AudioSegment.from_file(file_path, format=fmt)
    return len(audio)

def file_size_sec(file_path):
    """Retourne la durée du fichier audio en secondes"""
    return file_size_ms(file_path) / 1000

def extract_audio(file_path):
    """Extrait l'audio d'un fichier MP4 et l'exporte en MP3 (unique tempfile)."""
    fmt = _validate_audio_file(file_path)
    fd, output_name = tempfile.mkstemp(prefix="ortholyse_convert_", suffix=".mp3")
    os.close(fd)
    audio = AudioSegment.from_file(file_path, format=fmt)
    audio.export(output_name, format="mp3")
    return output_name

def split_audio(file_path):
    """Découpe un fichier audio en plusieurs segments dans un tempdir unique."""
    output_dir = tempfile.mkdtemp(prefix="ortholyse_split_")

    fmt = _validate_audio_file(file_path)
    audio = AudioSegment.from_file(file_path, format=fmt)
    format = fmt
    duration = file_size_ms(file_path)
    start = 0
    file_number = 0
    result = {}

    while start < duration:
        t1 = 290000  # durée du premier segment
        t2 = 310000  # durée du deuxième segment
        file_number += 1
        listSilence = []
        while not listSilence:
            s1 = min(duration, start + t1)
            s2 = min(duration, start + t2)
            if s1 == duration or s2 == duration:
                stop = 0
                break
            else:
                listSilence = detect_silence(audio[s1:s2], min_silence_len=900, silence_thresh=-40)
                if listSilence:
                    temp1, temp2 = listSilence[0]
                    stop = (temp1 + temp2) // 2
                t2 += 10000  # Augmente l'intervalle si pas de silence détecté

        end = min(duration, start + 290000 + stop)
        segment = audio[start:end]
        file_dir = os.path.join(output_dir, f'{file_number}.mp3')
        segment.export(file_dir, format=format)
        start = end

    result["file_count"] = file_number
    result["output_dir"] = output_dir
    return json.dumps(result)
