"""
Voice Transcription Pipeline

Primary:  Groq Whisper API  (whisper-large-v3)  — free, no local deps
Fallback: Local OpenAI Whisper                  — requires `openai-whisper` + ffmpeg

Supports auto-detection of English, Urdu, and mixed speech.
"""
import os
import logging
import tempfile

logger = logging.getLogger(__name__)

# Map MIME types → file extensions accepted by Whisper
_MIME_TO_EXT = {
    'audio/ogg': '.ogg',
    'audio/ogg; codecs=opus': '.ogg',
    'audio/mpeg': '.mp3',
    'audio/mp4': '.mp4',
    'audio/webm': '.webm',
    'audio/wav': '.wav',
    'audio/x-wav': '.wav',
    'audio/aac': '.aac',
}


class VoiceTranscriber:
    """
    Transcribes WhatsApp voice notes (ptt/audio) to text.
    Language is auto-detected — no need to specify English vs Urdu.
    """

    def __init__(self, groq_client=None):
        self.groq_client = groq_client
        self._local_model = None  # lazy-loaded if needed

    def transcribe(self, audio_data: bytes, mime_type: str = 'audio/ogg') -> dict:
        """
        Transcribe raw audio bytes.

        Returns:
            {
                "success": bool,
                "text": str,
                "language": str,   # e.g. "en", "ur"
                "source": str      # "groq-whisper" | "local-whisper"
                "error": str       # only on failure
            }
        """
        if self.groq_client:
            result = self._transcribe_groq(audio_data, mime_type)
            if result['success']:
                return result
            logger.warning('Groq Whisper failed, trying local Whisper fallback: %s', result.get('error'))

        return self._transcribe_local(audio_data, mime_type)

    # ------------------------------------------------------------------
    # Primary: Groq Whisper API
    # ------------------------------------------------------------------

    def _transcribe_groq(self, audio_data: bytes, mime_type: str) -> dict:
        ext = _MIME_TO_EXT.get(mime_type.split(';')[0].strip(), '.ogg')
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name

            with open(tmp_path, 'rb') as f:
                response = self.groq_client.audio.transcriptions.create(
                    model='whisper-large-v3',
                    file=(f'audio{ext}', f, mime_type.split(';')[0].strip()),
                    response_format='verbose_json',
                    # No language hint — let Whisper detect English / Urdu automatically
                )

            return {
                'success': True,
                'text': (response.text or '').strip(),
                'language': getattr(response, 'language', 'unknown'),
                'source': 'groq-whisper',
            }
        except Exception as e:
            logger.error('Groq Whisper error: %s', e)
            return {'success': False, 'error': str(e), 'text': ''}
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)

    # ------------------------------------------------------------------
    # Fallback: Local OpenAI Whisper
    # ------------------------------------------------------------------

    def _transcribe_local(self, audio_data: bytes, mime_type: str) -> dict:
        try:
            import whisper  # openai-whisper package
        except ImportError:
            msg = (
                'No transcription service available. '
                'Set GROQ_API_KEY or install openai-whisper: pip install openai-whisper'
            )
            logger.error(msg)
            return {
                'success': False,
                'error': msg,
                'text': '[Voice note — transcription unavailable]',
                'language': 'unknown',
                'source': 'none',
            }

        ext = _MIME_TO_EXT.get(mime_type.split(';')[0].strip(), '.ogg')
        tmp_path = None
        try:
            if self._local_model is None:
                logger.info('Loading local Whisper model (base)…')
                self._local_model = whisper.load_model('base')

            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name

            result = self._local_model.transcribe(tmp_path)
            return {
                'success': True,
                'text': (result.get('text') or '').strip(),
                'language': result.get('language', 'unknown'),
                'source': 'local-whisper',
            }
        except Exception as e:
            logger.error('Local Whisper error: %s', e)
            return {
                'success': False,
                'error': str(e),
                'text': '[Voice note — transcription failed]',
                'language': 'unknown',
                'source': 'local-whisper',
            }
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
