"""Record everything the app says, with free open-source voices (same voices as Ideogram Drills).

    python3 tools/make_audio.py                  # every language, only clips that have no MP3 yet
    python3 tools/make_audio.py --lang de        # one language
    python3 tools/make_audio.py --force          # redo everything (e.g. after changing a text)
    python3 tools/make_audio.py --models DIR     # use voice models already downloaded elsewhere

The texts come from the <script id="i18n"> block in index.html: change a text there, then run this again
with --force (or delete that clip's MP3). Output: audio/<lang>/<key>.mp3, where key is
  n0 … n100      numbers
  s_<key>        fixed phrases ("speech" in the texts)
  i_<item>       option names (colors, symbols, letters, words)
  l_<level>      "Level 3: 3 colors."
The app plays clips one after another and falls back to the system voice if a clip is missing.

Needs: pip install -r tools/requirements.txt, and ffmpeg on the PATH (macOS: brew install ffmpeg).
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile, unicodedata, urllib.request, wave

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
AUDIO = os.path.join(ROOT, "audio")

# One voice per language. Kokoro: en, es, pt-br (and more). Piper for German.
VOICES = {
    "es": {"engine": "kokoro", "voice": "ef_dora", "kokoro_lang": "es"},
    "en": {"engine": "kokoro", "voice": "af_heart", "kokoro_lang": "en-us"},
    "pt": {"engine": "kokoro", "voice": "pf_dora", "kokoro_lang": "pt-br"},
    "de": {"engine": "piper", "model": "de_DE-thorsten-high"},
}
SPEED = 0.95
MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
MODEL_FILES = ["kokoro-v1.0.onnx", "voices-v1.0.bin"]
PIPER_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"
# Trim silence at both ends, normalise loudness to -18 LUFS, add a 50 ms tail
FILTER = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.03,areverse,"
          "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse,"
          "loudnorm=I=-18:TP=-1.5:LRA=7,apad=pad_dur=0.05")
LEVELS = ["bn", "c2", "c3", "c4", "c6", "z2", "z3", "z5", "zc4", "zc6", "l2", "l4", "lc4", "p2", "p4"]  # same order as the app


def slug(s):
    """Must match slug() in index.html."""
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def load_texts():
    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    m = re.search(r'<script type="application/json" id="i18n">(.*?)</script>', html, re.S)
    if not m:
        sys.exit("No i18n block found in index.html")
    return json.loads(m.group(1))


def clips(T):
    """key -> text for one language. Must match the clip keys used in index.html."""
    out = {f"n{k}": f"{k}." for k in range(101)}
    for k, v in T["speech"].items():
        out["s_" + k] = v
    for k, v in T["items"].items():
        out["i_" + slug(k)] = v.get("s") or v["n"]
    for k, v in T["words"].items():
        out["i_" + slug(k)] = v["s"]
    for i, lid in enumerate(LEVELS):
        name = T["levels"][lid]["name"].replace("×", T["times"])
        out["l_" + lid] = T["levelSay"].replace("{n}", str(i + 1)).replace("{name}", name)
    return out


def download(url, path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        print(f"Downloading {os.path.basename(path)} (one time) ...", flush=True)
        urllib.request.urlretrieve(url, path + ".part")
        os.replace(path + ".part", path)
    return path


class Engines:
    def __init__(self, models):
        self.models, self._kokoro, self._piper = models, None, {}

    def kokoro(self):
        if self._kokoro is None:
            from kokoro_onnx import Kokoro
            self._kokoro = Kokoro(*[download(MODEL_URL + f, os.path.join(self.models, f)) for f in MODEL_FILES])
        return self._kokoro

    def piper(self, name):
        if name not in self._piper:
            from piper import PiperVoice
            loc, voice, quality = name.split("-")
            rel = f"{loc.split('_')[0]}/{loc}/{voice}/{quality}/{name}"
            base = os.path.join(self.models, "piper", name)
            download(PIPER_URL + rel + ".onnx.json", base + ".onnx.json")
            self._piper[name] = PiperVoice.load(download(PIPER_URL + rel + ".onnx", base + ".onnx"))
        return self._piper[name]

    def say(self, v, text, wav):
        if v["engine"] == "piper":
            from piper import SynthesisConfig
            with wave.open(wav, "wb") as wf:
                self.piper(v["model"]).synthesize_wav(text, wf, syn_config=SynthesisConfig(length_scale=1.0 / SPEED))
        else:
            import soundfile as sf
            samples, rate = self.kokoro().create(text, voice=v["voice"], speed=SPEED, lang=v["kokoro_lang"])
            sf.write(wav, samples, rate)


def encode(wav, mp3):
    os.makedirs(os.path.dirname(mp3), exist_ok=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", wav, "-af", FILTER,
                    "-ar", "24000", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "40k", mp3], check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lang", help="language code(s), comma separated (default: all)")
    ap.add_argument("--force", action="store_true", help="regenerate even if the MP3 exists")
    ap.add_argument("--models", default=os.path.join(TOOLS, "models"), help="folder for the voice models")
    a = ap.parse_args()
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found. macOS: brew install ffmpeg")

    texts = load_texts()
    langs = a.lang.split(",") if a.lang else list(texts)
    eng = Engines(a.models)
    made = skipped = removed = 0
    with tempfile.TemporaryDirectory() as tmp:
        for code in langs:
            if code not in VOICES:
                sys.exit(f"No voice set for '{code}' in VOICES (tools/make_audio.py)")
            want = clips(texts[code])
            folder = os.path.join(AUDIO, code)
            for key, text in want.items():
                mp3 = os.path.join(folder, key + ".mp3")
                if os.path.exists(mp3) and not a.force:
                    skipped += 1
                    continue
                wav = os.path.join(tmp, "c.wav")
                eng.say(VOICES[code], text, wav)
                encode(wav, mp3)
                made += 1
                print(f"  {code} {key}: {text}", flush=True)
            # Clips no longer used by the app
            for f in os.listdir(folder) if os.path.isdir(folder) else []:
                if f.endswith(".mp3") and f[:-4] not in want:
                    os.remove(os.path.join(folder, f))
                    removed += 1
    print(f"Done: {made} generated, {skipped} already existed, {removed} unused removed.")


if __name__ == "__main__":
    main()
