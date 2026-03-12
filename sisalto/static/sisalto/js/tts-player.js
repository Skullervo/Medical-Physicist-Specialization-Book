/**
 * TTS Player for Theory Pages
 * Uses OpenAI TTS via server-side API to generate Finnish speech.
 * Auto-initializes on pages with .theory-panel elements.
 */
(function() {
    'use strict';

    // Available voices: {id, label, gender}
    var VOICES = [
        { id: 'nova',    label: 'Nova',    gender: 'f' },
        { id: 'shimmer', label: 'Shimmer', gender: 'f' },
        { id: 'echo',    label: 'Echo',    gender: 'm' },
        { id: 'onyx',    label: 'Onyx',    gender: 'm' },
        { id: 'fable',   label: 'Fable',   gender: 'm' },
    ];

    // State
    var isPlaying = false;
    var isPaused = false;
    var audioQueue = [];         // Array of {audio: Audio, url: blobURL}
    var currentAudioIndex = 0;
    var currentRate = 1.0;
    var currentVoice = localStorage.getItem('tts_voice') || 'nova';
    var playerBar = null;
    var activeBtn = null;
    var isLoading = false;
    var abortController = null;
    var totalChunks = 0;

    // ==========================================
    // TEXT EXTRACTION
    // ==========================================

    function extractText(panel) {
        var content = panel.querySelector('.theory-content');
        if (!content) return '';

        var clone = content.cloneNode(true);

        // Remove non-readable elements
        var removeSelectors = [
            '.theory-references',
            '.theory-quiz-section',
            '.theory-image-slot',
            '.tts-listen-btn',
            'script', 'style', 'sup'
        ];
        clone.querySelectorAll(removeSelectors.join(',')).forEach(function(el) {
            el.remove();
        });

        // Build readable text with natural pauses
        var parts = [];
        var walker = document.createTreeWalker(clone, NodeFilter.SHOW_ELEMENT, null, false);
        var node;

        while (node = walker.nextNode()) {
            var tag = node.tagName.toLowerCase();

            if (tag === 'h2' || tag === 'h3') {
                var heading = (node.textContent || '').trim();
                if (heading) parts.push('\n' + heading + '.\n');
            } else if (tag === 'p') {
                var pText = (node.textContent || '').trim();
                if (pText) parts.push(pText);
            } else if (tag === 'li') {
                var liText = (node.textContent || '').trim();
                if (liText && !node.querySelector('li')) {
                    parts.push(liText);
                }
            } else if (tag === 'th' || tag === 'td') {
                var cellText = (node.textContent || '').trim();
                if (cellText && !node.querySelector('th, td')) {
                    parts.push(cellText);
                }
            }
        }

        var structured = parts.join(' ').replace(/\s+/g, ' ').trim();
        if (structured.length < 50) {
            structured = (clone.textContent || '').replace(/\s+/g, ' ').trim();
        }

        return structured;
    }

    function splitIntoChunks(text) {
        // Split into chunks of ~3500 chars at sentence boundaries
        // (OpenAI TTS limit is 4096 chars per request)
        var sentences = text.match(/[^.!?\n]+[.!?\n]+|[^.!?\n]+$/g) || [text];
        var result = [];
        var current = '';

        for (var i = 0; i < sentences.length; i++) {
            var s = sentences[i].trim();
            if (!s) continue;

            if (current.length + s.length > 3500 && current) {
                result.push(current.trim());
                current = s;
            } else {
                current += (current ? ' ' : '') + s;
            }
        }
        if (current.trim()) result.push(current.trim());

        return result;
    }

    // ==========================================
    // SERVER API
    // ==========================================

    function getCsrfToken() {
        // Try global getCookie first (defined in base template)
        if (typeof getCookie === 'function') {
            return getCookie('csrftoken');
        }
        // Fallback: read from cookie directly
        var match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? match[1] : '';
    }

    function fetchAudio(text, signal) {
        return fetch('/modaliteetit/api/tts/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({ text: text, voice: currentVoice }),
            signal: signal,
        })
        .then(function(response) {
            if (!response.ok) {
                return response.json().then(function(data) {
                    throw new Error(data.error || 'TTS-virhe');
                });
            }
            return response.blob();
        })
        .then(function(blob) {
            var url = URL.createObjectURL(blob);
            var audio = new Audio(url);
            audio.playbackRate = currentRate;
            return { audio: audio, url: url };
        });
    }

    // ==========================================
    // PLAYER BAR UI
    // ==========================================

    function createPlayerBar() {
        if (playerBar) return playerBar;

        var voiceOptions = VOICES.map(function(v) {
            var gIcon = v.gender === 'f' ? '♀' : v.gender === 'm' ? '♂' : '◈';
            var sel = v.id === currentVoice ? ' selected' : '';
            return '<option value="' + v.id + '"' + sel + '>' + gIcon + ' ' + v.label + '</option>';
        }).join('');

        var bar = document.createElement('div');
        bar.className = 'tts-player-bar';
        bar.innerHTML =
            '<div class="tts-player-inner">' +
                '<button class="tts-btn tts-play-pause" title="Tauko / Jatka">' +
                    '<i class="fas fa-pause"></i>' +
                '</button>' +
                '<button class="tts-btn tts-stop" title="Lopeta">' +
                    '<i class="fas fa-stop"></i>' +
                '</button>' +
                '<div class="tts-progress">' +
                    '<div class="tts-progress-bar"><div class="tts-progress-fill"></div></div>' +
                '</div>' +
                '<span class="tts-status-text">Kuuntelee...</span>' +
                '<select class="tts-voice-select" title="Valitse ääni">' + voiceOptions + '</select>' +
                '<button class="tts-btn tts-speed-btn" title="Nopeus">1×</button>' +
            '</div>';

        document.body.appendChild(bar);

        bar.querySelector('.tts-play-pause').addEventListener('click', togglePause);
        bar.querySelector('.tts-stop').addEventListener('click', stopPlayback);
        bar.querySelector('.tts-speed-btn').addEventListener('click', cycleSpeed);
        bar.querySelector('.tts-voice-select').addEventListener('change', function() {
            currentVoice = this.value;
            localStorage.setItem('tts_voice', currentVoice);
            // Stop current playback so next Kuuntele press uses new voice
            if (isPlaying || isLoading) {
                stopPlayback();
            }
        });

        playerBar = bar;
        return bar;
    }

    function showPlayer() {
        createPlayerBar();
        playerBar.offsetHeight; // Force reflow
        playerBar.classList.add('visible');
    }

    function hidePlayer() {
        if (playerBar) playerBar.classList.remove('visible');
    }

    function updateProgress() {
        if (!playerBar || totalChunks === 0) return;
        var pct = Math.round(((currentAudioIndex + 1) / totalChunks) * 100);
        var fill = playerBar.querySelector('.tts-progress-fill');
        if (fill) fill.style.width = pct + '%';
    }

    // ==========================================
    // PLAYBACK CONTROLS
    // ==========================================

    function togglePause() {
        if (!isPlaying) return;
        var audio = audioQueue[currentAudioIndex];
        if (!audio) return;

        if (isPaused) {
            audio.audio.play();
            isPaused = false;
            if (playerBar) {
                playerBar.querySelector('.tts-play-pause i').className = 'fas fa-pause';
                playerBar.querySelector('.tts-status-text').textContent = 'Kuuntelee...';
            }
        } else {
            audio.audio.pause();
            isPaused = true;
            if (playerBar) {
                playerBar.querySelector('.tts-play-pause i').className = 'fas fa-play';
                playerBar.querySelector('.tts-status-text').textContent = 'Tauolla';
            }
        }
    }

    function stopPlayback() {
        // Abort any pending fetches
        if (abortController) {
            abortController.abort();
            abortController = null;
        }

        // Stop and clean up all audio
        audioQueue.forEach(function(item) {
            try {
                item.audio.pause();
                item.audio.src = '';
                URL.revokeObjectURL(item.url);
            } catch (e) {}
        });

        audioQueue = [];
        currentAudioIndex = 0;
        totalChunks = 0;
        isPlaying = false;
        isPaused = false;
        isLoading = false;
        hidePlayer();

        // Reset active button
        if (activeBtn) {
            activeBtn.classList.remove('active', 'loading');
            activeBtn.querySelector('.tts-btn-text').textContent = 'Kuuntele';
            activeBtn.querySelector('i').className = 'fas fa-headphones';
            activeBtn = null;
        }
    }

    var SPEEDS = [0.75, 1.0, 1.25, 1.5];

    function cycleSpeed() {
        var idx = SPEEDS.indexOf(currentRate);
        currentRate = SPEEDS[(idx + 1) % SPEEDS.length];
        if (playerBar) {
            playerBar.querySelector('.tts-speed-btn').textContent = currentRate + '×';
        }

        // Apply speed to current audio
        if (isPlaying && audioQueue[currentAudioIndex]) {
            audioQueue[currentAudioIndex].audio.playbackRate = currentRate;
        }
        // Apply to all future queued audio
        audioQueue.forEach(function(item) {
            item.audio.playbackRate = currentRate;
        });
    }

    // ==========================================
    // SEQUENTIAL PLAYBACK
    // ==========================================

    function playCurrentAudio() {
        if (currentAudioIndex >= audioQueue.length) {
            // If still loading more chunks, wait
            if (isLoading) {
                setTimeout(playCurrentAudio, 300);
                return;
            }
            // All done
            stopPlayback();
            return;
        }

        var item = audioQueue[currentAudioIndex];
        item.audio.playbackRate = currentRate;
        updateProgress();

        item.audio.onended = function() {
            currentAudioIndex++;
            playCurrentAudio();
        };

        item.audio.onerror = function() {
            currentAudioIndex++;
            playCurrentAudio();
        };

        item.audio.play().catch(function() {
            // Autoplay blocked — user interaction needed
            currentAudioIndex++;
            playCurrentAudio();
        });
    }

    // ==========================================
    // START READING
    // ==========================================

    function startReading(panel, btn) {
        // If clicking the already-active button, stop
        if ((isPlaying || isLoading) && btn === activeBtn) {
            stopPlayback();
            return;
        }

        // Stop any current playback
        if (isPlaying || isLoading) {
            stopPlayback();
        }

        var text = extractText(panel);
        if (!text || text.length < 10) return;

        var chunks = splitIntoChunks(text);
        totalChunks = chunks.length;
        audioQueue = [];
        currentAudioIndex = 0;
        isLoading = true;
        activeBtn = btn;

        // Show loading state
        btn.classList.add('active', 'loading');
        btn.querySelector('.tts-btn-text').textContent = 'Ladataan...';
        btn.querySelector('i').className = 'fas fa-spinner fa-spin';

        // AbortController for cancellation
        abortController = new AbortController();
        var signal = abortController.signal;

        var playbackStarted = false;

        // Fetch chunks sequentially; start playback as soon as first chunk arrives
        function fetchNext(index) {
            if (index >= chunks.length) {
                isLoading = false;
                return;
            }
            if (signal.aborted) return;

            fetchAudio(chunks[index], signal)
                .then(function(item) {
                    if (signal.aborted) {
                        URL.revokeObjectURL(item.url);
                        return;
                    }

                    audioQueue.push(item);

                    // Start playback when first chunk is ready
                    if (!playbackStarted) {
                        playbackStarted = true;
                        isPlaying = true;

                        btn.classList.remove('loading');
                        btn.querySelector('.tts-btn-text').textContent = 'Kuuntelee...';
                        btn.querySelector('i').className = 'fas fa-volume-up';

                        showPlayer();
                        if (playerBar) {
                            playerBar.querySelector('.tts-play-pause i').className = 'fas fa-pause';
                            playerBar.querySelector('.tts-status-text').textContent = 'Kuuntelee...';
                            playerBar.querySelector('.tts-speed-btn').textContent = currentRate + '×';
                        }

                        playCurrentAudio();
                    }

                    // Fetch next chunk
                    fetchNext(index + 1);
                })
                .catch(function(err) {
                    if (err.name === 'AbortError') return;
                    console.error('TTS-virhe:', err.message);

                    if (!playbackStarted) {
                        // First chunk failed — show error
                        stopPlayback();
                        btn.classList.remove('active', 'loading');
                        btn.querySelector('.tts-btn-text').textContent = 'Virhe!';
                        btn.querySelector('i').className = 'fas fa-exclamation-triangle';
                        setTimeout(function() {
                            btn.querySelector('.tts-btn-text').textContent = 'Kuuntele';
                            btn.querySelector('i').className = 'fas fa-headphones';
                        }, 3000);
                    } else {
                        // Later chunk failed — try next
                        fetchNext(index + 1);
                    }
                });
        }

        fetchNext(0);
    }

    // ==========================================
    // INITIALIZATION
    // ==========================================

    function init() {
        var panels = document.querySelectorAll('.theory-panel');
        if (panels.length === 0) return;

        panels.forEach(function(panel) {
            var content = panel.querySelector('.theory-content');
            if (!content) return;

            var btn = document.createElement('button');
            btn.className = 'tts-listen-btn';
            btn.innerHTML = '<i class="fas fa-headphones"></i> <span class="tts-btn-text">Kuuntele</span>';
            btn.title = 'Kuuntele tämän osion sisältö';

            btn.addEventListener('click', function() {
                startReading(panel, btn);
            });

            content.insertBefore(btn, content.firstChild);
        });
    }

    // Init when DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Cleanup on page unload
    window.addEventListener('beforeunload', function() {
        if (abortController) abortController.abort();
        audioQueue.forEach(function(item) {
            try {
                item.audio.pause();
                URL.revokeObjectURL(item.url);
            } catch (e) {}
        });
    });

})();
