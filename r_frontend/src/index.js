import { PorcupineWorker } from '@picovoice/porcupine-web';
import { WebVoiceProcessor } from '@picovoice/web-voice-processor';
import { Orca } from '@picovoice/orca-web';

console.log("Script iniciado: cargando dependencias y configurando variables");

const form = document.getElementById('chat-form');
const messagesDiv = document.getElementById('messages');
const typingIndicator = document.getElementById('typingIndicator');
const streamToggle = document.getElementById('streamToggle');
const micButton = document.getElementById('micButton');

console.log("Elementos del DOM:", { form, messagesDiv, typingIndicator, streamToggle, micButton });

// Variables globales
let eventSource = null;
let recognition;
let isListening = false;
let finalTranscript = '';
let audioContext = null;
let audioQueue = [];
let isPlaying = false;
let textStreamBuffer = [];
let isStreamingResponse = false;
let orcaStream = null;

const listeningIndicator = document.createElement('div');
listeningIndicator.className = 'listening-indicator';
document.body.appendChild(listeningIndicator);

let porcupineWorker = null;
let isWakeWordDetected = false;
let orca = null;

// Función para inicializar Orca
async function initOrca() {
    try {
        const accessKey = "fuEKJbc6fT3kH5sZblrVYgzULtbaTDWY4ak1CiIkVEugKxoC4D4vvw==";
        const modelPath = "/static/g4/orca_params_es_male.pv";

        orca = await Orca.create(
            accessKey,
            { publicPath: modelPath, forceWrite: true }
        );

        console.log("Orca inicializado correctamente");
    } catch (error) {
        console.error("Error inicializando Orca:", error);
    }
}

async function speak(text) {
    try {
        const result = await orca.synthesize(text);
        await playAudio(result.pcm);
    } catch (error) {
        console.error("Error en síntesis:", error);
        // Fallback a Web Speech API
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'es-ES';
        window.speechSynthesis.speak(utterance);
    }
}

async function playAudio(pcmData) {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }

    audioQueue.push(pcmData);

    if (!isPlaying) {
        processAudioQueue();
    }
}

async function processAudioQueue() {
    if (audioQueue.length === 0) {
        isPlaying = false;
        return;
    }

    isPlaying = true;
    const pcm = audioQueue.shift();

    try {
        const buffer = audioContext.createBuffer(1, pcm.length, 22050);
        buffer.getChannelData(0).set(pcm);

        const source = audioContext.createBufferSource();
        source.buffer = buffer;
        source.connect(audioContext.destination);

        source.onended = () => {
            setTimeout(processAudioQueue, 100); // Pequeña pausa entre frases
        };

        source.start(0);
    } catch (error) {
        console.error("Error reproduciendo audio:", error);
        processAudioQueue();
    }
}

async function streamText(textStream) {
    const stream = orca.streamOpen();

    for (const textChunk of textStream) {
        const pcm = stream.synthesize(textChunk);
        if (pcm) {
            playAudio(pcm);
        }
    }

    const finalPcm = stream.flush();
    if (finalPcm) {
        playAudio(finalPcm);
    }

    stream.close();
}

document.addEventListener('DOMContentLoaded', async () => {
    console.log("DOMContentLoaded: inicializando sistemas");
    await initOrca();
    await initWakeWord();

    const loadingElement = document.getElementById('loading');
    if (loadingElement) {
        loadingElement.style.display = 'none';
    }
});

// Función para inicializar el wake word
async function initWakeWord() {
    console.log("initWakeWord() llamado");
    try {
        await navigator.mediaDevices.getUserMedia({ audio: true });
        const keywordModel = {
            publicPath: "data:application/octet-stream;base64,mkRDV4PgGidVUXtWVkR4y2MZq3pCP7gaaRELl1APOPFVDZX0MrrgsgeLttrn8sw+9tXV0ECaNjjCiyEEKQxME57WFeymP16woLJzdvDs9rawpeR5ue/Nsm12zfxS9Abs66QCepVlmxd8G9qfG+LiPv2xl2TG+iC1CxVwuKzm3vaNf7bxbg0HAO6QQrR+6jjv2RO9tIjeZ4RklErrohM0O53CTpG2t5RXzMoHNf5K43VAobcafE4h/EQwsl96i4qLgcVncHzywvaFORTKkvco5xUQtIwSpo04LAvQay+STmATbPnhyila9qge6ATccybH0P+qrX6Z/oavt/Wr5s4sZbvhzrHGAYLM7XpSfdL8mN+egwI4aIhTqtq3WF5KT58D950BWB4rcKxJhFnCXVc/Xz0LrzhtG47e/CTbyl97s2i4tdaHx08Kv2zs58MlgZT4Ep26jbVvhR1Xy9OfIBcUCMF93kG4aeoGOTvH8Bq7k0QyymPmU8AtjhTwBavV/bvI6iT9rxNNYPz5Dcpb1zunICgAkIeZnkuttbF+UUWV6Gj0zk/UMLU13Pmv+cv5KR4ikPm9FgWht+69z+Dq5W3v0VvTJKylPSun1umYp8eUdaip5a9p7nKrCeVLMAM1Vd7ZDlADilddj9UlQwWlyeY3xB/X95L3S5bJNwCR2uZLV6hAu/N0PcRBW3OVpIzqlRDlkR82JwZG7WPxL/coBYGzrIRhEIqmTiZ9pyon8nJ6lPL3ypXk0QBS9FH1dPg8dqRW2nsYAFq8EoQnMuzjFWEl5STtFAV4MqlBd9wQnOUS7L6wU168hwkDvG7pEAPgR0/fOL8kPM760/MY6PhtaK64kuvVC9u+YCFlOu+wiouolnGWSoh2Aa2JcsmB3t7eMouXRb9KGaTO1oUoQjaaFlCO6+GUnWjFnGWr0UhxazwYerzA9cDuX7LslwqvKbmNgf6DbBUtQPq8RnuPAR7EGtmD/MP3G178F8lLCcGI4yIFyz/jKuVmP2Tru0XxAj6phMqTcmuzWIAu4A9nPZWDohOmZI5/snYmSKl0Xu5Q2j1SnnR48Ehk2JpPEc/5rXKsbFjr8nnPosunMZ4nxq/4VX29eTIohZSuNqAYr5TW50+8F/w39Cv0xzRPPq/RyCtbI+fWnRRD26IhkdnDk8BZInpsdGie7XUcqW+1DnMC2bhddg38R97P/A1m1Muy9kpzI0CunZJielVj8MWKC3HD6Z+QZ5fm94Ljz27/J/dGte1aHYSh1QRD2lNPY07nFCKxpv/PhgSuG4G0ilpwfDyHMsmnoFhjXj+keRrMq5vK98J3LW8VUpG/NGOB2puELzoDE/17CDU1ODUw9b8QuZWYhCPTvdhdGmbFnTuSzFHMh7Q598V/bpnWYrG2rEASBN75GLeGLWd+bQh0rvQ9o/S+fjJLa76F11FTWAW0tBCsr+ddpuVmQqjDH3g23KRizzC3ZfsKF0LqlOfa/+YitrW3km8FwKAcc8mzp8JjDzyg23O2K1fu2cK1JbLkJEXAd4Nwhixc5Q6mrvl7eZNsd9wMcEiz+iEvnshUDdUyHuF7GfrhZ6XLveP9mHWM7m1m1BdVCGD1B7nV+UVK54uKz1tYPqIaChH54yKAwAHL/l9paoJk0gp4GpgBBAJ3tSwKU/p/NgVX0vzvaNttaIs0NicqrVMrMzUs4ZhXwFYlfiqg3dfT9PNJNWgr0xBV55tBc88zpCCFC3CPhGPxKhWIvAVxwZdSNg7/4zDDPeYUtzBZtf9sHSr9YSZyN3YpLxv8/ZvQTmTvkJGLFLs6x2P1xpXtRAA22u5yNYIcFbRZ+p4rv2YPmv/ocHqDWtuh4KbZvWzq78NQ7zHxWgXdmtGQoNLajgi283cbe+7pMLFe1JNwI5NOpbgoYR4Orgn+ubvcw5FW8PnIXKfviMcUouFbwpG46d72Au2wFPBfQPgo3MDkogPnoNnYqewPrmbILOB4pCgiFOGgreJ8XGzNUbjSZc4bwHv+k4fNNObRMcpHZa/qEBdDs62NrqUgMlkXLaXhOSf2ayudx6+NtYZGYa+KqPAjCk4BOi6IYJD+mmaPUQO3Lu1rGAw2XlqqFpasIZelmQmlap/ZjI6Q2jB2J8Vdk655oJQbmHpx8yjVtx8N3axyAJ4ip2NAAthZeVLvOZmMMMlIoB4bYZZ4j2Fo33GXvL37fSBIkGv9y4jvPcnmAQ8piSPWMudZ+M2qdBFr3kQ98mljg70KdEP9W6X013QKFGECK0EGsXsnlrMTNsRsA0XPynvBWEdgP+B6Jz9jHre9HFRP8/t8mHUsa/uezOkBtyEahV2QvG6V15UISKavK4eEDZlA9RzkTXaC5rhBksaZsiT/8XtypGyq3zziSiWZ0cuFe+BiLh2/BHaZ2w77SwfE8DIFNizldDHYIOUle5058LsCnBd/ddQC72E0Ty/LxqsstAn5NJdpA78Z4pnLlebJgmso9gdICkJnXodBAF7yQ4p8KISp8qDZ6/75Dr5yhh5vRAGmW6DUOEQH5iCjwsWrE3rQA0xHz2Xuwgrcn4tdpnCbpAyj8LrHTPEAPOz4C6OO2V3F51nKTu9zfGMBBMogdFbM5tA7JuWUh2xA/62K3ttiYbtgZazBXK/VaAktlDs5IKUGpmHLRa3X6+gDbEdZJUQeVurA80MdEaE9XzZmZSDIHl9ZnJnaLc7JbUZLcWlrw5PsdKA+1VpjEgPx26OvUbyFXdkfzenu8xf70lf3L76EnIeabCQldEld1jQRpF6gU+C422EnugHqZElOFe2WKje1LcFXoNPiIGdWfofwfGLLy0c2mMcVfL7x3tQjqbJzybgceP/r44C6Tgn7W1WEXIsnaNRk4vvvslOjmSP8s1ZafoDY1apGzWXaTKhvjISoEMCQfY5rapY2KLDXYbpcfqxKCMf1hBgKss9bZkkNtXqhB7nNC9Mgu+BHzevof83jf4FY9hCUH9r813ltjhD4wZB4MJFOEpbShrkC18WMHaZz6QXvdeObwOTPhs3vuuS4ZpZnGZR9e3QfKpJ6yiKVnV8fwV/tw0H/ezgSo6zwYbpit0XABlh0j3nE+2/YY+Hnm+R2W+t/3tcgEkZskZztToS3CyEm9OcQ40Wfo4H7NNbzwNjTxkTXyEzgMEDPftUfSPyCiAr8iF2a66fpb6E3lQy1Ec0MiDkKERfK0u/h0d8kCL62W27K3WcOf2WzajMlwR6MPcu6erlhN+dtGntweXlf9iRP4d44jG6U5KJYL1ej55gS1JxmgycLiRMssrvVL6drnFnaXGr8exKl73/8N4qbqp8Ng8NOKyjLJTSIkbY3h/PwshUpUMRJGSfkzEZpf5jsTXng23LEexUsLSNVoAs8KJJMBxhopqGKgxtDej+drDRNEhSy37Q7XQHgOTF3JnbPYop6Ptee5tpGvVfHY6LJB5lEkFo5TC70OZ1Lu9wT7sgn5huz+N1uoIj4mYAj/xPmNKaIhZUMMwPKFJP3erVwZdB3O4v8vVr1uHUTwBKAsJwv3sp/kyBChfwpARHz/Bz8aetUyha2ik9agvsraBaME3bTqUMfrXysJtlBjNwxmRmqwwBiRBgQu3lPB+UouRAiZsjubgqwG4Gp21vv3+OLLaQocfJ3rWgHYOgqtbusVZxkrdnQs39Bt7EAfpKPiQuWyb+rfazZ0/+9SQE8OmF1JZb+ZiHfTNvPDjuVc3q4SsNdWBCr+DAxu7jCTtiP8Heoa+kkUjG6fwvP/KwqWPd1mCADp/nDzvMip4AKMZkO80WP2nDNKl+WrePnKVC+uifSX5QgrGMICq9gA/gIG75cQEzb3Cmtgm8rMhQGcF9Fc562zX6Qc0LGZyj5WDySejlaYziMWF0DfjA/5VQsQw==", // Tu modelo .ppn en base64 
            label: "G4BR13L",
            forceWrite: true
        };

        console.log("initWakeWord: keywordModel configurado", keywordModel);
        //const accessKey = "PyAXZq9ZjF5ArX3qZQtABnvAx4Pc7aUuLdSiVJbhXMhvLHWDfaz3lA==";
        const accessKey = "fuEKJbc6fT3kH5sZblrVYgzULtbaTDWY4ak1CiIkVEugKxoC4D4vvw==";
        console.log("initWakeWord: usando accessKey", accessKey);

        porcupineWorker = await PorcupineWorker.create(
            accessKey,
            [keywordModel],
            keywordDetectionCallback,
            {
                publicPath: "/static/g4/porcupine_params_es.pv",
                forceWrite: true
            }
        );
        console.log("initWakeWord: PorcupineWorker creado:", porcupineWorker);

        await WebVoiceProcessor.subscribe(porcupineWorker);
        console.log("initWakeWord: WebVoiceProcessor suscrito");
    } catch (error) {
        console.error("Error inicializando wake word:", error);
    }
}

async function keywordDetectionCallback(detection) {
    console.log("keywordDetectionCallback: detección recibida:", detection);
    if (detection.label === "G4BR13L" && recognition) {
        try {
            // Liberar el micrófono de Porcupine
            await WebVoiceProcessor.unsubscribe(porcupineWorker);
            console.log("Micrófono liberado para reconocimiento de voz");

            isWakeWordDetected = true;
            recognition.start();
            showListeningFeedback();
        } catch (error) {
            console.error("Error al manejar la detección:", error);
        }
    }
}

// Muestra un indicador visual al detectar el wake word
function showListeningFeedback() {
    listeningIndicator.style.display = 'block';
    listeningIndicator.innerHTML = `
        <div class="listening-animation"></div>
        <span>Di tu comando ahora...</span>
    `;

    // Ajustar tiempo de escucha extendido
    setTimeout(() => {
        if (isWakeWordDetected) {
            listeningIndicator.style.display = 'none';
        }
    }, 5000); // 5 segundos para dar tiempo a hablar
}

// Configuración de SpeechRecognition para el wake word
if (window.SpeechRecognition || window.webkitSpeechRecognition) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'es-ES';
    console.log("SpeechRecognition configurado");

    recognition.onstart = () => {
        console.log("recognition.onstart: reconocimiento iniciado");
        if (!isWakeWordDetected) return;
        micButton.innerHTML = '<i class="bi bi-mic-mute"></i>';
    };

    recognition.onresult = (event) => {
        if (!isWakeWordDetected) return;

        finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            }
        }

        if (finalTranscript.length > 0) {
            form.message.value = finalTranscript.trim();
            console.log("Comando detectado:", finalTranscript);
        }
    };

    recognition.onend = () => {
        console.log("recognition.onend: reconocimiento finalizado");
        if (!isWakeWordDetected) return;

        micButton.innerHTML = '<i class="bi bi-mic"></i>';
        if (form.message.value) {
            form.dispatchEvent(new Event('submit'));
        }

        // Reconectar Porcupine después de 1 segundo
        setTimeout(async () => {
            try {
                await WebVoiceProcessor.subscribe(porcupineWorker);
                console.log("Porcupine reconectado exitosamente");
            } catch (error) {
                console.error("Error reconectando Porcupine:", error);
            }
        }, 1000);

        isWakeWordDetected = false;
    };

    recognition.onerror = (event) => {
        console.error("Error en reconocimiento:", event.error);
        isWakeWordDetected = false;
        // Reinicia el reconocimiento si es necesario
        if (event.error === 'no-speech' || event.error === 'aborted') {
            setTimeout(() => recognition.start(), 1000);
        }

        // Reconectar Porcupine si hay error
        WebVoiceProcessor.subscribe(porcupineWorker)
            .then(() => console.log("Reconexión después de error exitosa"))
            .catch(err => console.error("Error reconectando:", err));
    };
} else {
    console.error("SpeechRecognition no soportado en este navegador");
    micButton.innerHTML = '<i class="bi bi-mic-mute"></i> (No soportado)';
}

micButton.addEventListener('click', async () => {
    try {
        await WebVoiceProcessor.subscribe(porcupineWorker);
        console.log("Micrófono activado");
    } catch (error) {
        console.error("Error al activar micrófono:", error);
    }
});



function addMessage(message, isUser = true) {
    console.log("addMessage: agregando mensaje", { message, isUser });
    const messageDiv = document.createElement('div');
    messageDiv.className = `message-bubble ${isUser ? 'user-message' : 'assistant-message'}`;
    messageDiv.innerHTML = `
    <div class="fw-bold small">${isUser ? 'Tú' : 'G4BR13L'}</div>
    <div class="message-content">${message}</div>
  `;
    messagesDiv.appendChild(messageDiv);
    if (!isUser) {
        speak(message);
    }
    messagesDiv.scrollTo(0, messagesDiv.scrollHeight);
}


function showTyping() {
    console.log("showTyping: mostrando typing indicator");
    typingIndicator.style.display = 'block';
    messagesDiv.scrollTo(0, messagesDiv.scrollHeight);
}

function hideTyping() {
    console.log("hideTyping: ocultando typing indicator");
    typingIndicator.style.display = 'none';
}

let ttsBuffer = '';
let isProcessingTTS = false;

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    console.log("form submit: evento submit disparado");
    const formData = new FormData(form);
    const message = formData.get('message');
    const isStreaming = streamToggle.checked;
    console.log("form submit: mensaje recibido:", message, "isStreaming:", isStreaming);

    addMessage(message, true);
    form.reset();

    if (isStreaming) {
        showTyping();
        const assistantDiv = document.createElement('div');
        assistantDiv.className = 'message-bubble assistant-message';
        const responseId = `assistant-response-${Date.now()}`;
        assistantDiv.innerHTML = `
<div class="fw-bold small">G4BR13L</div>
<div class="message-content" id="${responseId}"></div>
`;
        messagesDiv.appendChild(assistantDiv);

        if (eventSource) eventSource.close();

        eventSource = new EventSource(`/g4/chat-stream/?message=${encodeURIComponent(message)}`);
        console.log("form submit: EventSource creado", eventSource);

        // Reiniciar buffers al iniciar nuevo stream
        ttsBuffer = '';
        isProcessingTTS = false;

        eventSource.onmessage = async (e) => {
            if (e.data === '[END]') {
                if (ttsBuffer.length > 0) {
                    isProcessingTTS = true;
                    const cleanedText = cleanTextForTTS(ttsBuffer);
                    if (cleanedText) {
                        await processTTS(cleanedText); // Sintetizar todo al final
                    }
                }
                hideTyping();
                eventSource.close();
                return;
            }
        
            // Actualiza UI
            document.getElementById(responseId).textContent += e.data;
            messagesDiv.scrollTo(0, messagesDiv.scrollHeight);
        
            // Acumular y procesar en chunks naturales
            ttsBuffer += e.data + ' ';
            
            // Dividir en oraciones o chunks de 50 caracteres
            /*const sentenceEnd = /[.!?]\s/;
            if (sentenceEnd.test(ttsBuffer) || ttsBuffer.length > 50) {
                const sentences = ttsBuffer.split(sentenceEnd);
                const toProcess = sentences.shift();
                ttsBuffer = sentences.join(' ');
                
                const cleaned = cleanTextForTTS(toProcess);
                if (cleaned) await processTTS(cleaned);
            }*/
        };

        eventSource.onerror = (e) => {
            if (!isProcessingTTS && ttsBuffer.length > 0) {
                processTTS(cleanTextForTTS(ttsBuffer)).finally(() => {
                    hideTyping();
                    eventSource.close();
                });
            }
            assistantDiv.innerHTML += `<div class="text-danger small mt-2"><i class="bi bi-exclamation-triangle"></i> Error en la conexión</div>`;
        };
    } else {
        showTyping();
        try {
            console.log("form submit: enviando mensaje vía fetch");
            const response = await fetch('/g4/chat/', {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            const data = await response.json();
            console.log("form submit: respuesta recibida", data);
            hideTyping();

            if (data.response) {
                addMessage(data.response, false);
            } else if (data.error) {
                addMessage(`<span class="text-danger"><i class="bi bi-exclamation-triangle"></i> Error: ${data.error}</span>`, false);
            }
        } catch (error) {
            console.error("form submit: error en fetch", error);
            hideTyping();
            addMessage(`<span class="text-danger"><i class="bi bi-exclamation-triangle"></i> Error de conexión</span>`, false);
        }
    }
});


// Función separada para síntesis
async function processTTS(text) {
    try {
        const result = await orca.synthesize(text);
        if (result?.pcm) {
            playAudio(result.pcm);
        }
    } catch (error) {
        console.error("Error síntesis:", error.name, "-", error.message);
        // Intento alternativo eliminando caracteres problemáticos
        const fallbackText = text.replace(/[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s.,!?]/g, '');
        if (fallbackText !== text) {
            await processTTS(fallbackText);
        }
    }
}

function cleanTextForTTS(text) {
    // 1. Eliminar emojis y caracteres especiales
    let cleaned = text.replace(/[\u{1F600}-\u{1F6FF}]/gu, '');
    
    // 2. Eliminar caracteres no ASCII
    cleaned = cleaned.replace(/[^\x00-\x7F]/g, '');
    
    // 3. Eliminar múltiples espacios
    cleaned = cleaned.replace(/\s+/g, ' ').trim();
    
    // 4. Filtrar texto vacío
    return cleaned.length > 2 ? cleaned : null;
}

const inputField = form.querySelector('input');
if (inputField) {
    inputField.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            console.log("inputField: Enter presionado, enviando formulario");
            form.dispatchEvent(new Event('submit'));
        }
    });
}

function updateMicStatus(active) {
    const micStatus = document.getElementById('micStatus');
    micStatus.innerHTML = active ?
        '<i class="bi bi-mic"></i> Escuchando...' :
        '<i class="bi bi-mic-mute"></i> Micrófono inactivo';
    micStatus.className = `badge ${active ? 'bg-success' : 'bg-secondary'}`;
}

async function checkMicrophonePermission() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        updateMicStatus(true);
        return true;
    } catch (error) {
        console.error("Error al acceder al micrófono:", error);
        updateMicStatus(false);
        return false;
    }
}