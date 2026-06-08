import os
import sys
import logging
import pyaudio
import numpy as np
import speech_recognition as sr
import time

class SpeechRecognitionEngine:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.recognizer = sr.Recognizer()
        
        # 🧠 FIX 3: OPTIMIZE RECOGNIZER (VERY IMPORTANT)
        self.recognizer.energy_threshold = 300 
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.pause_threshold = 1.2 # Allows natural pauses in speech
        
        self.microphone = None
        self._initialize_microphone()

    def _initialize_microphone(self):
        try:
            p = pyaudio.PyAudio()
            
            default_idx = None
            default_name = "System Default"
            try:
                default_idx = p.get_default_input_device_info()['index']
                mics = sr.Microphone.list_microphone_names()
                default_name = mics[default_idx] if default_idx < len(mics) else "System Default"
            except Exception:
                pass
            
            selected_idx = default_idx
            selected_name = default_name
            
            # Check if default microphone is a virtual or problematic device (like Camo)
            is_virtual = False
            if default_name:
                name_lower = default_name.lower()
                virtual_terms = ["camo", "virtual", "droidcam", "obs", "stealth", "steam", "voicemeeter", "vb-audio"]
                if any(term in name_lower for term in virtual_terms):
                    is_virtual = True
            
            if is_virtual:
                logging.info(f"Default microphone '{default_name}' is a virtual device. Searching for physical fallback...")
                fallback_idx = None
                fallback_name = None
                fallback_score = -1
                
                for i in range(p.get_device_count()):
                    try:
                        info = p.get_device_info_by_index(i)
                        if info.get('maxInputChannels', 0) > 0:
                            mics = sr.Microphone.list_microphone_names()
                            name = mics[i] if i < len(mics) else info.get('name', '')
                            name_lower = name.lower()
                            
                            # Skip virtual, loopback, mapper, etc.
                            if any(term in name_lower for term in ["camo", "virtual", "droidcam", "obs", "stealth", "steam", "voicemeeter", "vb-audio", "mapper", "capture"]):
                                continue
                                
                            score = 0
                            if "realtek" in name_lower:
                                score += 10
                            if "microphone" in name_lower:
                                score += 5
                            if "internal" in name_lower or "built-in" in name_lower:
                                score += 3
                            if "array" in name_lower or "high definition" in name_lower:
                                score += 2
                                
                            if score > fallback_score:
                                fallback_score = score
                                fallback_idx = i
                                fallback_name = name
                    except Exception:
                        pass
                
                if fallback_idx is not None:
                    selected_idx = fallback_idx
                    selected_name = fallback_name
                    logging.info(f"Selected physical fallback microphone: [{selected_idx}] {selected_name}")
                else:
                    logging.warning("No physical fallback microphone found. Sticking with default.")
            
            p.terminate()
            
            logging.info(f"Using microphone: [{selected_idx if selected_idx is not None else 'Default'}] {selected_name}")
            self.microphone = sr.Microphone(device_index=selected_idx, sample_rate=self.sample_rate)
            
            with self.microphone as source:
                logging.info("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
            logging.info("Microphone initialized successfully.")
        except OSError as e:
            logging.warning(f"No input audio device available: {e}")
            self.microphone = None
        except Exception as e:
            logging.critical(f"Failed to initialize microphone: {e}")
            self.microphone = None


    def stop(self):
        """Placeholder to prevent AttributeErrors on application exit shutdown calls."""
        pass
        
    def get_audio_sample(self, duration=3):
        """
        Captures a raw audio sample for speaker authentication.
        """
        logging.info(f"Recording {duration}s sample...")
        
        # Create a fresh microphone instance because the main one is locked by the background listening thread
        device_index = None
        if self.microphone:
            device_index = self.microphone.device_index
            
        temp_mic = sr.Microphone(device_index=device_index, sample_rate=self.sample_rate)
        
        # We manually record for the exact duration needed for registration
        with temp_mic as source:
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5) # Quick calibration
                # Listen specifically for the duration required
                audio_data = self.recognizer.record(source, duration=duration)
                
                logging.info("Recording complete.")
                
                # Convert to numpy array
                raw_data = audio_data.get_raw_data(convert_rate=16000, convert_width=2)
                audio_int16 = np.frombuffer(raw_data, dtype=np.int16)
                audio_float = audio_int16.astype(np.float32) / 32768.0
                
                return audio_float
            except Exception as e:
                logging.error(f"Failed to record sample: {e}")
                return None
