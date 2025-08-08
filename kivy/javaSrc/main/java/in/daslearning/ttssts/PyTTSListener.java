package in.daslearning.ttssts;

import android.speech.tts.UtteranceProgressListener;

public class PyTTSListener extends UtteranceProgressListener {
    public static PyTTSCallback callback;

    public interface PyTTSCallback {
        void onStart(String id);
        void onDone(String id);
        void onError(String id, int errorCode);
    }

    public static void setCallback(PyTTSCallback cb) {
        callback = cb;
    }

    @Override
    public void onStart(String utteranceId) {
        if (callback != null) callback.onStart(utteranceId);
    }

    @Override
    public void onDone(String utteranceId) {
        if (callback != null) callback.onDone(utteranceId);
    }

    // Required abstract method from API < 21 (deprecated)
    @Override
    public void onError(String utteranceId) {
        // Optionally map to the newer callback
        if (callback != null) callback.onError(utteranceId, -1); // -1 for unknown error
    }

    @Override
    public void onError(String utteranceId, int errorCode) {
        if (callback != null) callback.onError(utteranceId, errorCode);
    }
}
