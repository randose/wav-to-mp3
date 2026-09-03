# WAV to MP3 / AIFF

A command-line tool to convert WAV files to MP3 or AIFF and set metadata using FFmpeg. Built with [Typer](https://typer.tiangolo.com).

---

## Requirements

- FFmpeg (must be available in your system PATH)
- Python 3.10 or higher

---

## 🚀 Installation

1. Clone the repository and navigate to the project directory.
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Build the package:
   ```bash
   poetry build
   ```
4. Install globally with pipx:
   ```bash
   pipx install dist/wav_to_mp3-0.1.0-py3-none-any.whl
   ```

---

## Usage
Ensure WAV files are named in the format `Artist - Title.wav` for proper metadata tagging. If they are not, use the `--convert-bad-names` option to convert them without tagging.

```bash
wav-to-mp3 [OPTIONS] <directory or file>
```

By default, output format is MP3 (320 kbps). Use `--aiff` to output AIFF.

AIFF bit depth behavior:

- Default target is 24-bit AIFF.
- If the source WAV has a lower bit depth, AIFF matches that lower bit depth.

### Options

| Option                        | Description                                                                                   | Default           |
|-------------------------------|----------------------------------------------------------------------------------------------|-------------------|
| `--delete` / `--keep`         | Delete WAV files after successful conversion.                                                | keep              |
| `--overwrite` / `--skip-existing` | Overwrite existing MP3 files or skip them.                                               | skip-existing     |
| `--convert-bad-names` / `--skip-bad-names` | Convert WAVs with bad names without tags or skip them.                    | skip-bad-names |
| `--recursive` (`-r`) / `--no-recursive` | Process directories recursively (only applies to directories).                          | no-recursive      |
| `--aiff`                     | Convert to AIFF instead of MP3. AIFF uses 24-bit unless source WAV is lower bit depth.      | off               |

### 📂 Examples

Convert all WAVs in a directory (non-recursive, keep WAVs, skip existing MP3s):

```bash
wav-to-mp3 /path/to/wavs
```

Convert recursively, delete WAVs after conversion, overwrite existing MP3s:

```bash
wav-to-mp3 --recursive --delete --overwrite /path/to/wavs
```

Convert a single file even if name is not in `Artist - Title.wav` format:

```bash
wav-to-mp3 --convert-bad-names /path/to/file.wav
```

Convert recursively to AIFF, preserving lower source bit depths when applicable:

```bash
wav-to-mp3 --recursive --aiff /path/to/wavs
```

---

## 🛠 License
MIT License.
