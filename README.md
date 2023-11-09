MusicLang Jukebox
=================

What is this ? 
--------------

The project is a demonstration the capabilities of our open source package MusicLang that is a high level tonal composition engine.

The use case we chose is the mixing of 3 different songs together to create a new one. 
We create an infinite variation over existing musical assets from various videogames.
For the submission we used the following songs :

- **Orchestration** : Prelude - Final Fantasy 7
- **Melody** : Rayman Bandland - Rayman
- **Chord Progression** : Silent Hill Theme - Silent Hill


How to use it ?
---------------

Install the requirements in a python virtual environment :
    
```bash
pip install -r requirements.txt
```

Then launch the main script :

```bash
python main_submission.py
```

The results will appear in the `data/experiment/output.mid` folder.
We also provide a wav file (result.wav) that is the resulting midi file rendered with some VSTs.
