import pretty_midi
import glob
import csv

flat = True
for path_notes, path_meta in zip(glob.glob("Score/*/*_notes_keys.csv"), glob.glob("Score/*/*_meta.csv")):
    # Read the csv file
    notes = []
    with open(path_notes, newline="") as fp:
        rows = csv.reader(fp)
        _notes = [i for i in rows]
        for rnote in _notes[1:]:
            note = {_notes[0][i]:rnote[i] for i in range(1, len(rnote))}
            notes.append(note)

    with open(path_meta, newline="") as fp:
        rows = csv.reader(fp)
        meta = [i for i in rows]
        meta = {meta[0][i]:meta[1][i] for i in range(1, len(meta[0]))}
    
    # Create a PrettyMIDI object
    tempo, unit = float(notes[0]["Tempo"].split("_")[0]), int(notes[0]["Tempo"].split("_")[-1])
    tempo *= (4/unit)
    piano_c_chord = pretty_midi.PrettyMIDI(initial_tempo=tempo)

    # Create an Instrument instance for a piano instrument
    piano_program = pretty_midi.instrument_name_to_program('Acoustic Grand Piano')
    piano = pretty_midi.Instrument(program=piano_program)
    t_sig = pretty_midi.TimeSignature(int(meta["Time"].split("_")[0]), int(meta["Time"].split("_")[1]), 0.0)
    A, B = int(meta["Time"].split("_")[0]), int(meta["Time"].split("_")[1])

    # Iterate over note names, which will be converted to note number later
    tstep = 0.0
    for note_in in notes:
        # Note name -> Note numner
        note_number = int(note_in["Midi"])
        """ dur(sec) = beat * sec_per_beat """
        dur = float(note_in["Duration"]) * (60.0/float(note_in["Tempo"].split("_")[0]))
        """ onset(sec) = (beat_in_measure + #measure * beat_per_measure) * sec_per_beat """
        onset = (float(note_in["Onset"]) + float(note_in["Measure"]) * A) * (60.0/float(note_in["Tempo"].split("_")[0]))


        # Get a note 
        if note_number > 0:
            note = pretty_midi.Note(velocity=100, pitch=note_number, start=onset, end=onset+dur)
            # Add the note to the instrument
            piano.notes.append(note)

    # Add the piano instrument to the PrettyMIDI object
    piano_c_chord.instruments.append(piano)
    piano_c_chord.time_signature_changes.append(t_sig)

    # Write out the MIDI data
    #filename = path_notes.replace("notes_keys.csv", "out.mid")
    filename = path_meta.replace("_meta.csv", "_out.mid")
    print ("Write to {}".format(filename))
    piano_c_chord.write(filename)
