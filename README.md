# ikacut

スプラトゥーン2の試合動画を切り出すツール

##  Installation

```bash
$ brew install ffmpeg

$ git clone git@github.com:hrkh/ikacut.git
$ cd ikacut

$ poetry install --no-dev
```

## Usage

### Download video from YouTube

```bash
$ python3 -m ikacut download <url>
```

### Extract start and end times of matches

```bash
$ python3 -m ikacut match -n <number_of_first_match>
```

### Extract death scenes

```bash
$ python3 -m ikacut death
```
