import os
import glob
import subprocess
import typer
from typing import Optional

app = typer.Typer(help="Convert WAV files to MP3 with ID3 tags using FFmpeg.")


def process_file(
    wav_path: str,
    overwrite: bool = False,
    delete_wav: bool = False,
    convert_bad_names: bool = False,
):
    """
    Converts a WAV file to a 320kbps MP3 and embeds metadata using FFmpeg.
    """
    try:
        typer.echo(f"Processing file: {wav_path}")
        base_name = os.path.basename(wav_path)
        name_without_ext = os.path.splitext(base_name)[0]
        mp3_path = os.path.join(os.path.dirname(wav_path), name_without_ext + ".mp3")
        if os.path.exists(mp3_path):
            if overwrite:
                typer.echo(f"Overwriting existing MP3: {mp3_path}")
            else:
                typer.echo(f"Skipping '{wav_path}' as an MP3 file already exists.")
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
            "-ab",
            "320k",
        ]
        if artist:
            command += ["-metadata", f"artist={artist}"]
        if title:
            command += ["-metadata", f"title={title}"]
        command.append(mp3_path)

        subprocess.run(
            command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True
        )
        typer.echo(f"Converted and tagged '{wav_path}' -> '{mp3_path}'")
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
        )


@app.command()
def main(
    input_path: str = typer.Argument(".", help="Path to a .wav file or directory."),
    delete: bool = typer.Option(
        False, "--delete/--keep", help="Delete WAV files after successful conversion."
    ),
    overwrite: bool = typer.Option(
        False, "--overwrite/--skip-existing", help="Overwrite existing MP3 files."
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
):
    """
    Convert WAV files to MP3 with ID3 tags using FFmpeg.
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
        )
    else:
        process_directory(
            input_path,
            overwrite=overwrite,
            delete_wav=delete,
            convert_bad_names=convert_bad_names,
            recursive=recursive,
        )
