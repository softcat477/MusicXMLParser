# MusicXMLParser

## What can I do?
* Parse a musicXML file and retrieve informations to `csv` files
    1. Key signature, Time signature, Pentatonic in the sub-title, and additional comments near the composer.
    2. Chords in each measure.
    3. Notes, rests, lyrics, slur, and tie.
* Generate `midi` using the retrieved `csv` files.

See [here](https://github.com/softcat477/TwnScore) for example.

## Steps
1. Download scores from the google drive.
    `python3 DownloadGDrive --ID <ID of the google drive>`

2. Parse musicXML files.
    `pythone Parse.py`
    
   Input:
    * `<Score_name>.xml`

   Output:
    * `<Score_name>_meta.csv` : Key Signature, Pentatonic, Time Signature, Note
    * `<Score_name>_chords.csv` : Chords in each measure
    * `<Score_name>_note_keys.csv` : Notes, ...

3. Generate MIDI files from csv files. Validate the correctness of csv files.
    `python3 ToMidi.py`
    
    Input:
    * `<Score_name>_meta.csv`
    * `<Score_name>_note_keys.csv`

    Output:
    * `<Score_name>_out.mid`
