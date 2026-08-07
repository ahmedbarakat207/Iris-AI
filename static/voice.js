document.addEventListener('DOMContentLoaded', () => {
    const voiceChatBtn = document.getElementById('voiceChatBtn');
    const voiceModal = document.getElementById('voiceModal');
    const closeVoiceBtn = document.getElementById('closeVoiceBtn');
    const voiceMuteBtn = document.getElementById('voiceMuteBtn');
    
    const iconMicOn = document.getElementById('icon-mic-on');
    const iconMicOff = document.getElementById('icon-mic-off');
    
    const voiceOrb = document.getElementById('voiceOrb');
    const voiceStatusText = document.getElementById('voiceStatusText');
    const voiceTranscription = document.getElementById('voiceTranscription');

    let stream = null;
    let audioContext = null;
    let analyser = null;
    let microphone = null;
    
    let mediaRecorder = null;
    let audioChunks = [];
    
    let currentState = 'IDLE'; // IDLE, LISTENING, RECORDING, PROCESSING, SPEAKING, MUTED
    let isMuted = false;
    let currentAudio = null;
    
    // VAD settings
    const SILENCE_THRESHOLD = 15; // Increased to 15 to ignore laptop fan noise
    const SILENCE_DURATION_MS = 1500; // 1.5 seconds of silence means they stopped talking
    const MAX_RECORDING_MS = 15000; // 15 second maximum recording time
    
    let lastVolume = 0;
    let lastSpeechTime = 0;
    let recordingStartTime = 0;
    let animationFrameId = null;

    if (!voiceChatBtn || !voiceModal) return;

    voiceChatBtn.addEventListener('click', async () => {
        voiceModal.classList.add('visible');
        setState('INITIALIZING');
        try {
            const res = await fetch('/api/voice/init');
            const data = await res.json();
            
            await initVoice();
            
            if (data.audio_url) {
                voiceTranscription.style.display = 'block';
                voiceTranscription.innerHTML = `
                <div dir="auto"><strong>Iris:</strong> Hi, How can I assist you today?</div>
                `;
                playAudioResponse(data.audio_url);
            }
        } catch (err) {
            console.error("Initialization failed:", err);
            setState('ERROR');
            voiceStatusText.textContent = 'Failed to load models';
        }
    });

    closeVoiceBtn.addEventListener('click', () => {
        hangUp();
    });

    voiceMuteBtn.addEventListener('click', () => {
        isMuted = !isMuted;
        
        if (stream) {
            stream.getAudioTracks().forEach(track => track.enabled = !isMuted);
        }
        
        if (isMuted) {
            iconMicOn.style.display = 'none';
            iconMicOff.style.display = 'block';
            voiceMuteBtn.classList.add('muted');
            
            if (currentState === 'RECORDING') stopRecording(false);
            setState('MUTED');
        } else {
            iconMicOn.style.display = 'block';
            iconMicOff.style.display = 'none';
            voiceMuteBtn.classList.remove('muted');
            
            if (currentState === 'MUTED') setState('LISTENING');
        }
    });

    function setState(newState) {
        currentState = newState;
        
        // Reset orb classes
        voiceOrb.className = 'voice-orb';
        
        switch (newState) {
            case 'INITIALIZING':
                voiceOrb.classList.add('processing'); // Use processing animation for loading
                voiceStatusText.textContent = 'Initializing AI models...';
                break;
            case 'IDLE':
            case 'LISTENING':
                voiceOrb.classList.add('idle');
                voiceStatusText.textContent = 'Listening...';
                break;
            case 'RECORDING':
                voiceStatusText.textContent = 'Recording...';
                break;
            case 'PROCESSING':
                voiceOrb.classList.add('processing');
                voiceStatusText.textContent = 'Thinking...';
                break;
            case 'SPEAKING':
                voiceOrb.classList.add('speaking');
                voiceStatusText.textContent = 'Speaking...';
                break;
            case 'MUTED':
                voiceOrb.classList.add('muted');
                voiceStatusText.textContent = 'Muted';
                break;
            case 'ERROR':
                voiceOrb.classList.add('idle');
                voiceStatusText.textContent = 'Error';
                break;
        }
    }

    async function initVoice() {
        try {
            voiceTranscription.style.display = 'none';
            voiceTranscription.innerHTML = '';
            setState('IDLE');
            
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Apply current mute state
            stream.getAudioTracks().forEach(track => track.enabled = !isMuted);

            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioContext.createAnalyser();
            analyser.fftSize = 256;
            analyser.smoothingTimeConstant = 0.5;
            
            microphone = audioContext.createMediaStreamSource(stream);
            microphone.connect(analyser);
            
            if (!isMuted) setState('LISTENING');
            
            detectVoiceActivity();
            
        } catch (err) {
            console.error("Error accessing microphone:", err);
            setState('ERROR');
            voiceStatusText.textContent = 'Microphone Denied';
        }
    }

    function detectVoiceActivity() {
        if (!analyser) return;
        
        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(dataArray);
        
        let sum = 0;
        for(let i = 0; i < dataArray.length; i++) {
            sum += dataArray[i];
        }
        let avgVolume = sum / dataArray.length;
        
        // Animate orb based on volume when not processing or muted
        if (currentState === 'LISTENING' || currentState === 'RECORDING') {
            const scale = 1 + Math.min((avgVolume / 255) * 0.4, 0.4);
            voiceOrb.style.transform = `scale(${scale})`;
        } else {
            voiceOrb.style.transform = '';
        }
        
        const now = Date.now();
        
        if (currentState === 'LISTENING' && avgVolume > SILENCE_THRESHOLD && !isMuted) {
            // Started talking!
            startRecording();
            lastSpeechTime = now;
            recordingStartTime = now;
        } else if (currentState === 'RECORDING') {
            if (now - recordingStartTime > MAX_RECORDING_MS) {
                // Force stop if they've been recording for too long
                setState('PROCESSING');
                stopRecording(true);
            } else if (avgVolume > SILENCE_THRESHOLD) {
                lastSpeechTime = now; // Update speech time
            } else if (now - lastSpeechTime > SILENCE_DURATION_MS) {
                // Stopped talking for threshold!
                setState('PROCESSING');
                stopRecording(true);
            }
        }
        
        animationFrameId = requestAnimationFrame(detectVoiceActivity);
    }

    function startRecording() {
        setState('RECORDING');
        
        let options = { mimeType: 'audio/webm' };
        if (!MediaRecorder.isTypeSupported('audio/webm')) {
            options = { mimeType: 'audio/mp4' };
        }
        
        mediaRecorder = new MediaRecorder(stream, options);
        audioChunks = [];

        mediaRecorder.ondataavailable = e => {
            if (e.data.size > 0) audioChunks.push(e.data);
        };

        mediaRecorder.start();
    }

    function stopRecording(sendToBackend) {
        if (!mediaRecorder || mediaRecorder.state === 'inactive') return;
        
        mediaRecorder.onstop = async () => {
            if (sendToBackend && audioChunks.length > 0) {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                await sendAudioToBackend(audioBlob);
            } else {
                setState('LISTENING');
            }
        };
        mediaRecorder.stop();
    }

    async function sendAudioToBackend(blob) {
        setState('PROCESSING');

        const formData = new FormData();
        formData.append('audio', blob, 'recording.webm');

        try {
            const res = await fetch('/api/voice', {
                method: 'POST',
                body: formData
            });

            if (!res.ok) throw new Error("Voice API failed");

            const data = await res.json();
            if (data.error) throw new Error(data.error);

            voiceTranscription.style.display = 'block';
            voiceTranscription.innerHTML = `
                <div dir="auto" style="margin-bottom:12px; opacity: 0.8"><strong>You:</strong> ${data.user_text}</div>
                <div dir="auto"><strong>Iris:</strong> ${data.bot_text}</div>
            `;
            
            // Scroll to bottom
            voiceTranscription.scrollTop = voiceTranscription.scrollHeight;

            if (data.audio_url) {
                playAudioResponse(data.audio_url);
            } else {
                if (!isMuted) setState('LISTENING');
                else setState('MUTED');
            }

        } catch (err) {
            console.error(err);
            setState('ERROR');
            setTimeout(() => {
                if (!isMuted) setState('LISTENING');
            }, 3000);
        }
    }

    function playAudioResponse(dataUrl) {
        setState('SPEAKING');

        currentAudio = new Audio(dataUrl);
        currentAudio.play();

        currentAudio.onended = () => {
            currentAudio = null;
            if (!isMuted) setState('LISTENING');
            else setState('MUTED');
        };
    }

    function hangUp() {
        voiceModal.classList.remove('visible');
        if (animationFrameId) cancelAnimationFrame(animationFrameId);
        
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            stopRecording(false);
        }
        
        if (currentAudio) {
            currentAudio.pause();
            currentAudio = null;
        }
        
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        
        if (audioContext) {
            audioContext.close();
            audioContext = null;
        }
    }
});
