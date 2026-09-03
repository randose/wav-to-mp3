import os
import glob
import subprocess
import wave
import typer

app = typer.Typer(help="Convert WAV files to MP3 or AIFF with metadata using FFmpeg.")


def _get_wav_bit_depth(wav_path: str) -> int:
    """
    Read WAV bit depth from the sample width.
    """
    with wave.open(wav_path, "rb") as wav_file:
        return wav_file.getsampwidth() * 8


def _build_output_settings(wav_path: str, use_aiff: bool) -> tuple[str, list[str]]:
    """
    Build output path and codec settings based on selected output format.
    """
    base_name = os.path.basename(wav_path)
    name_without_ext = os.path.splitext(base_name)[0]
    output_extension = ".aiff" if use_aiff else ".mp3"
    output_path = os.path.join(
        os.path.dirname(wav_path), name_without_ext + output_extension
    )

    if not use_aiff:
        return output_path, ["-ab", "320k"]

    input_bit_depth = _get_wav_bit_depth(wav_path)
    target_bit_depth = min(input_bit_depth, 24)
    if target_bit_depth <= 8:
        codec_args = ["-c:a", "pcm_s8"]
    elif target_bit_depth <= 16:
        codec_args = ["-c:a", "pcm_s16be"]
    else:
        codec_args = ["-c:a", "pcm_s24be"]

    return output_path, codec_args


def process_file(
    wav_path: str,
    overwrite: bool = False,
    delete_wav: bool = False,
    convert_bad_names: bool = False,
    use_aiff: bool = False,
):
    """
    Converts a WAV file to MP3 or AIFF and embeds metadata using FFmpeg.
    """
    try:
        typer.echo(f"Processing file: {wav_path}")
        base_name = os.path.basename(wav_path)
        name_without_ext = os.path.splitext(base_name)[0]
        output_path, format_args = _build_output_settings(wav_path, use_aiff)
        output_label = "AIFF" if use_aiff else "MP3"

        if os.path.exists(output_path):
            if overwrite:
                typer.echo(f"Overwriting existing {output_label}: {output_path}")
            else:
                typer.echo(
                    f"Skipping '{wav_path}' as a {output_label} file already exists."
                )
                return

        parts = name_without_ext.split(" - ", 1)
        if len(parts) != 2:
            if not convert_bad_names:
                typer.echo(
                    f"Skipping '{base_name}' (does not contain the required ' - ' delimiter)."
                )
                return
            else:
                typer.echo(
                    f"Filename '{base_name}' does not contain the required ' - ' delimiter."
                )
                typer.echo(f"Converting '{base_name}' without metadata tagging.")
                parts = ["", name_without_ext]

        artist = parts[0].strip()
        title = parts[1].strip()

        # Build the FFmpeg command with the desired parameters
        command = [
            "ffmpeg",
            "-y" if overwrite else "-n",  # Overwrite or not
            "-loglevel",
            "error",
            "-i",
            wav_path,
        ]
        command += format_args
        if use_aiff:
            # AIFF stores artist/title in an ID3 chunk; enable writing it explicitly.
            command += ["-write_id3v2", "1"]
        if artist:
            command += ["-metadata", f"artist={artist}"]
            if use_aiff:
                command += ["-metadata", f"author={artist}"]
        if title:
            command += ["-metadata", f"title={title}"]
            if use_aiff:
                command += ["-metadata", f"name={title}"]
        command.append(output_path)

        subprocess.run(
            command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True
        )
        typer.echo(f"Converted and tagged '{wav_path}' -> '{output_path}'")
        if delete_wav:
            os.remove(wav_path)
            typer.echo(f"Deleted original WAV: {wav_path}")
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode("utf-8").strip()
        typer.echo(f"Error processing '{wav_path}': {error_message}")
    except Exception as e:
        typer.echo(f"Error processing '{wav_path}': {str(e)}")


def process_directory(
    directory: str,
    overwrite: bool = False,
    delete_wav: bool = False,
    convert_bad_names: bool = False,
    recursive: bool = False,
    use_aiff: bool = False,
):
    """
    Searches the specified directory for .wav files and processes each file.
    """
    pattern = "**/*.wav" if recursive else "*.wav"
    wav_files = glob.glob(os.path.join(directory, pattern), recursive=recursive)
    if not wav_files:
        typer.echo("No .wav files found in the directory.")
        return

    for wav_file in wav_files:
        process_file(
            wav_file,
            overwrite=overwrite,
            delete_wav=delete_wav,
            convert_bad_names=convert_bad_names,
            use_aiff=use_aiff,
        )


@app.command()
def main(
    input_path: str = typer.Argument(".", help="Path to a .wav file or directory."),
    delete: bool = typer.Option(
        False, "--delete/--keep", help="Delete WAV files after successful conversion."
    ),
    overwrite: bool = typer.Option(
        False, "--overwrite/--skip-existing", help="Overwrite existing output files."
    ),
    convert_bad_names: bool = typer.Option(
        False,
        "--convert-bad-names/--skip-bad-names",
        help="Convert WAVs with bad names without tags instead of skipping them.",
    ),
    recursive: bool = typer.Option(
        False,
        "--recursive/--no-recursive",
        "-r",
        help="Process directories recursively (only applies to directories).",
    ),
    aiff: bool = typer.Option(
        False,
        "--aiff",
        help="Convert to AIFF instead of MP3. AIFF uses 24-bit unless WAV bit depth is lower.",
    ),
):
    """
    Convert WAV files to MP3 or AIFF with metadata using FFmpeg.
    """
    if not os.path.exists(input_path):
        typer.echo("The provided path does not exist.")
        raise typer.Exit(1)

    if os.path.isfile(input_path):
        if not input_path.lower().endswith(".wav"):
            typer.echo("The provided file is not a .wav file.")
            raise typer.Exit(1)
        process_file(
            input_path,
            overwrite=overwrite,
            delete_wav=delete,
            convert_bad_names=convert_bad_names,
            use_aiff=aiff,
        )
    else:
        process_directory(
            input_path,
            overwrite=overwrite,
            delete_wav=delete,
            convert_bad_names=convert_bad_names,
            recursive=recursive,
            use_aiff=aiff,
        )
