(() => {
  const video = document.querySelector('#cameraVideo');
  const canvas = document.querySelector('#cameraCanvas');
  const start = document.querySelector('[data-camera-start]');
  const capture = document.querySelector('[data-camera-capture]');
  const status = document.querySelector('[data-camera-status]');
  const placeholder = document.querySelector('[data-camera-placeholder]');
  const result = document.querySelector('[data-expression-result]');
  if (!video || !canvas || !start) return;

  let stream = null;
  let timer = null;
  let busy = false;

  function setStatus(text, kind = '') {
    status.textContent = text;
    status.dataset.state = kind;
  }

  function showResult(expression, confidence, message) {
    result.hidden = false;
    result.dataset.expression = expression || 'Unknown';
    result.querySelector('[data-expression]').textContent = expression || 'Unknown';
    result.querySelector('[data-confidence]').textContent = confidence == null ? 'Confidence —' : `Confidence ${Math.round(confidence * 100)}%`;
    result.querySelector('[data-message]').textContent = message || '';
  }

  async function analyzeFrame() {
    if (busy || !stream || video.readyState < 2 || !video.videoWidth) return;
    busy = true;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d', {willReadFrequently: true}).drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(async blob => {
      if (!blob) { busy = false; return; }
      const data = new FormData();
      data.append('image', blob, 'camera.jpg');
      try {
        const response = await fetch('/api/analyze-face', {method: 'POST', body: data, headers: {'X-Requested-With': 'XMLHttpRequest'}});
        const json = await response.json();
        if (json.ok) {
          showResult(json.expression, json.confidence, json.message);
          setStatus(`Live result: ${json.expression}. Expression only, not a mental-health diagnosis.`, 'success');
        } else if (json.code === 'NO_FACE') {
          showResult('No face detected', null, 'Move into the camera frame and try again.');
          setStatus('No face detected. Keep your face visible and well lit.', 'warning');
        } else {
          setStatus(json.error || 'Expression analysis is unavailable.', 'error');
        }
      } catch (error) {
        setStatus('Could not send a frame to the server. Please try again.', 'error');
      } finally {
        busy = false;
      }
    }, 'image/jpeg', 0.82);
  }

  start.addEventListener('click', async () => {
    try {
      stream = await navigator.mediaDevices.getUserMedia({video: {facingMode: 'user'}, audio: false});
      video.srcObject = stream;
      await video.play();
      capture.disabled = false;
      placeholder.style.display = 'none';
      start.textContent = 'Camera enabled';
      start.disabled = true;
      setStatus('Camera is ready. Detecting visible expression every 1.5 seconds…');
      await new Promise(resolve => {
        if (video.readyState >= 2 && video.videoWidth) resolve();
        else video.addEventListener('loadeddata', resolve, {once: true});
      });
      analyzeFrame();
      timer = window.setInterval(analyzeFrame, 1500);
    } catch (error) {
      setStatus('Camera access was unavailable. Please check browser permissions or continue without this feature.', 'error');
    }
  });

  capture?.addEventListener('click', analyzeFrame);
  window.addEventListener('beforeunload', () => {
    if (timer) clearInterval(timer);
    stream?.getTracks().forEach(track => track.stop());
  });
})();

