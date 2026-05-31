# =============================================================================
# Auteur  : GUIDJOU Danil
# Email   : danil.guidjou@etu.u-paris.fr
# Version : 1.0
# =============================================================================
import logging
import os
import shutil
import sys
import tempfile
from pathlib import Path

from pydub import AudioSegment
from pydub.silence import detect_silence

try:
    import magic  # type: ignore
    _HAS_MAGIC = True
except Exception:  # ImportError or libmagic native missing
    magic = None
    _HAS_MAGIC = False

logger = logging.getLogger(__name__)

# Whitelist of accepted audio formats (extension -> pydub format token).
FORMAT_FROM_EXT = {
    "mp3": "mp3",
    "wav": "wav",
    "m4a": "m4a",
    "mp4": "mp4",
    "ogg": "ogg",
    "flac": "flac",
}

# Accepted MIME types when python-magic + libmagic native lib are present.
AUDIO_MIME_WHITELIST = {
    "audio/mpeg",
    "audio/wav",
    "audio/x-wav",
    "audio/mp4",
    "audio/x-m4a",
    "audio/ogg",
    "audio/flac",
    "audio/x-flac",
    "video/mp4",  # mp4 container with audio
}


def _validate_audio_file(file_path: str) -> str:
    """Validate audio file via extension whitelist and (when available) MIME sniffing.

    Returns the canonical pydub format token. Raises ValueError on unknown
    extension or MIME mismatch. MIME check is a no-op if python-magic / libmagic
    native bindings are not loadable on the current platform.
    """
    ext = Path(file_path).suffix.lstrip(".").lower()
    if ext not in FORMAT_FROM_EXT:
        raise ValueError(f"unsupported audio extension: {ext!r}")

    if _HAS_MAGIC:
        try:
            mime = magic.from_file(file_path, mime=True)
        except Exception as e:
            logger.warning("magic MIME sniff failed for %s: %s", file_path, e)
        else:
            if mime not in AUDIO_MIME_WHITELIST:
                raise ValueError(f"unsupported audio MIME type: {mime!r}")
    return FORMAT_FROM_EXT[ext]

def find_ffmpeg():
    """Return a usable ffmpeg path.

    Order:
      1. PyInstaller bundle (frozen) -> _internal/ffmpeg.
      2. Vendored binary at app/../bin/ffmpeg (legacy dev layout, optional).
      3. System ffmpeg discovered via PATH (documented install path).
      4. Fallback to the literal string "ffmpeg" so pydub uses PATH at call time.
    """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        return os.path.abspath(os.path.join(base_path, '_internal', 'ffmpeg'))

    vendored = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bin', 'ffmpeg'))
    if os.path.isfile(vendored):
        return vendored

    system = shutil.which('ffmpeg')
    if system:
        return system

    return 'ffmpeg'

AudioSegment.converter = find_ffmpeg()

def file_size_Mo(file_path: str) -> float:
    """Retourne la taille du fichier en Mo"""
    #getsize retourne la taille en octect 
    # 1Mo = 2^20 octet 
    return os.path.getsize(file_path) / pow(2, 20)

def reel_file_format(file_path: str) -> str:
    """"
    Retourne le vrai format d'un fichier
    """
    return Path(file_path).suffix.lstrip(".")


def file_size_ms(file_path: str) -> int:
    """Retroune le duree de l'audio en ms"""
    frmt = reel_file_format(file_path)
    return len(AudioSegment.from_file(file_path , format=frmt))

def file_size_sec(file_path: str) -> float:
    """Retourne la duree de l'audio en seconde"""
    #on charge l'audio dans AudioSegment ...
    #puis on obtient la durée en ms -> / 1000 pour l'obtenir en sec
    frmt = reel_file_format(file_path)
    return ( len(AudioSegment.from_file(file_path , format=frmt)) / 1000)

def extract_audio_fmp4(file_pth: str) -> str:
    """"
    Extration d'un audio d'un fichier mp4.

    Writes to a unique temp file (tempfile.mkstemp with delete=False semantics)
    so concurrent runs do not collide and never overwrite a shared filename.
    Caller is responsible for deleting the returned path after use (the existing
    transcription() pipeline already does so via os.remove()).
    """
    frmt = _validate_audio_file(file_pth)
    fd, output_name = tempfile.mkstemp(prefix="ortholyse_convert_", suffix=".mp3")
    os.close(fd)  # we just want the unique path; pydub will write to it.
    audio = AudioSegment.from_file(file_pth, format=frmt)
    audio.export(output_name, format="mp3")
    return output_name

def detect_silnce_inInterval(audio):
    
    # on passe en parametre une segment dans les allentour ou on veut decouper l'audio
    # exemple si je veux decouper un audio chaque 5min -> 3000000ms 
    # donc on chereche le silence entre audio[29900 : 301000] 1s de reflection ou peutetre plus a voir avec les testes
    """
    cette fonction prend comme argument un segment d'un audio et retourne une liste de couple (debut, fin)
    de moment de silence dans le segment passer en parametre
    """
    #detection du silence
    # min_silence_len le temps minimale de silence 
    # silence_thresh le volume en db pour detecter le silence 
    # la durée min du silence est a 900ms et on defini -40db comme le seuil du silence
    # la durée du silence est a configurer par rapport aux tests a venir 
    # plus la durée est longue plus on est sur que la coupure est plus correcte !!! mais et si il ne ya pas de silence aussi long dans tout l'audio ? 
    return detect_silence(audio, min_silence_len=900, silence_thresh=-40)

    


def split_audio(file_path):
    """
    Decouper un fichier en plusieurs sous-fichiers de durée inferieurs.

    Writes fragments to a unique tempfile.mkdtemp directory instead of a fixed
    "fileSpliter/" in the CWD: avoids collisions across runs and ensures the
    patient-voice fragments end up under a tracked tempdir.
    """
    output_dir = tempfile.mkdtemp(prefix="ortholyse_split_")

    frmt = _validate_audio_file(file_path)
    audio = AudioSegment.from_file(file_path, format=frmt)
    
    duration = file_size_ms(file_path)  
    start = 0
    file_number = 0

    while start < duration:
        t1 = 290000 # init
        t2 = 310000 # init
        file_number += 1
        listSilence = []
        while(not listSilence):
            
            s1 = min(duration , start+t1) #debut de l'intarvalle ou on charche le silence
            s2 = min(duration , start+t2) #fin avec un intervalle de 20 seconde
            if(s1 == duration or s2 == duration): #si on atteint la fin de l'audio on a plus besoin de decouper on recupere juste la derniere partie 
                stop = 0
                break #puisque on est dans cette patie la listSilence =[] ==> TRUE ce qui provoque une boucle infini 
            else:
                listSilence = detect_silnce_inInterval(audio[s1: s2]) 
                temp1, temp2 = listSilence[0] #on recupere le premier moment de silence qui existe dans l'intervale [s1,S2]
                stop = ((temp1+temp2)//2) #on coup au millieu du silence 
                t2 += 10000 # si dans l'intervalle ou on cherche a decouper y a pas un moment de silence on augmente cette intervalle de 10sec

        end = min(duration , start+290000+ stop) #on decoupe l'audio en morceau de 5min -> 300sec -> 30000ms
        segement = audio[start:end]
        file_dir = os.path.join(output_dir, f'{file_number}.mp3')
        logger.debug("writing split fragment %s", file_dir)
        segement.export(file_dir, format=reel_file_format(file_path))
        start = end #actualise le debut pour la prochaine decoupe && condition de sortie de while
    
    #on retourne le nbr de fichier pour pouvoir les parcourir afin de faire de la transcription
    return file_number, output_dir