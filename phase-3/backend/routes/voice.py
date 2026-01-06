"""
Voice transcription endpoint using OpenAI Whisper API.

Task: T-CHAT-015
Spec: specs/phase-3-chatbot/spec.md (US-CHAT-6)
"""
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
from middleware.auth import verify_token
from openai import OpenAI
import os
import tempfile

router = APIRouter(prefix="/api", tags=["voice"])

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY"))


@router.post("/{user_id}/transcribe")
async def transcribe_audio(
    user_id: str,
    audio: UploadFile = File(...),
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Transcribe audio to text using OpenAI Whisper API.

    This endpoint receives audio from the frontend, transcribes it using
    Whisper, and returns the text. This avoids CORS issues that occur
    when calling OpenAI API directly from the browser.

    Args:
        user_id: User ID from URL path
        audio: Audio file (webm, mp3, wav, etc.)
        authenticated_user_id: User ID from JWT token (injected)

    Returns:
        dict with 'text' key containing transcription

    Raises:
        HTTPException 403: If user_id doesn't match authenticated user
        HTTPException 400: If audio file is invalid
    """
    # 1. Verify user authentication
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot transcribe for another user"
        )

    # 2. Validate audio file
    if not audio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file is required"
        )

    # 3. Save uploaded audio to temporary file
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
            # Write uploaded audio to temp file
            content = await audio.read()
            temp_audio.write(content)
            temp_audio_path = temp_audio.name

        # 4. Transcribe using Whisper API (auto-detect language for Urdu support)
        with open(temp_audio_path, "rb") as audio_file:
            # Check if using Groq or OpenAI
            if os.getenv("GROQ_API_KEY"):
                # Groq Whisper API (whisper-large-v3)
                # Omit language parameter to auto-detect (supports English + Urdu)
                transcription = client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=audio_file
                    # language parameter omitted for auto-detection
                )
            else:
                # OpenAI Whisper API
                # Omit language parameter to auto-detect (supports 97+ languages including Urdu)
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                    # language parameter omitted for auto-detection
                )

        # 5. Clean up temp file
        os.unlink(temp_audio_path)

        # 6. Return transcription
        return {
            "text": transcription.text,
            "language": getattr(transcription, 'language', 'unknown')
        }

    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_audio_path' in locals() and os.path.exists(temp_audio_path):
            os.unlink(temp_audio_path)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )
