from Parser.Helper import *
import pandas as pds
import copy

class Score(object):
    def __init__(self, measure_num):
        self.meta = []
        self.measure_num = -1
        self.harmony = "-"
        self.tempo = "-"
        self.arrangement = "-"
        self.arrangement_inst = "-"
        self.tie = "x"
        self.slur = "x"
        self.lyric = "x"

        self.duration_onset = 0
        self.arr_dict = {}

        # Put keys of each measure in another file. Use query keys to access keys of each measure
        self.notes_chord = []       # Query keys
        self.chord = []             # Chords, which can be accessed by query keys.
        self.current_chord = None   # Latest key

        self.is_link_chord = False  # Flag devided that whether "current_key" should move
        self.note_in_measure = {i:0 for i in range(measure_num)} # Count notes in a measure, use this variable to create keys.

        # For pentatonic style
        self.pent1 = chr(ord("宮"))
        self.pent2 = chr(ord("商"))
        self.pent3 = chr(ord("角"))
        self.pent5 = chr(ord("徵"))
        self.pent6 = chr(ord("羽"))
        self._pentKey = [self.pent1, self.pent2, self.pent3, self.pent5, self.pent6]
        self._pentNum = {self.pent1:1, self.pent2:2, self.pent3:3, self.pent5:5, self.pent6:6}

    def dumpMeta(self, name):
        d_frames = pds.DataFrame(self.meta, columns=["Key", "Pent", "Time", "Note"])
        d_frames.to_csv("{}_meta.csv".format(name))

    def dumpNotes(self, name):
        d_frames = pds.DataFrame(self.notes_chord, columns=["Note", "Midi", "Key", "Tempo", "Arrangement", "Tie", "Slur", "Lyric", "Onset", "Duration", "Offset", "Measure"])
        d_frames.to_csv("{}_notes_keys.csv".format(name))

    def dumpTones(self, name):
        d_frames = pds.DataFrame(self.chord, columns=["Key", "Chord", "Next"])
        d_frames.to_csv("{}_chords.csv".format(name))

    def addMeasure(self, measure):
        self.measure_num += 1
        self.duration_onset = 0.0
        for P1 in measure:
            # Parse all elements
            if self.measure_num <= 5:
                if P1.tag == "attributes":
                    self._addAtt(P1)

            if P1.tag == "harmony":     # Chord
                self._addHarmony(P1)
            elif P1.tag == "direction": # Tempo/Arrangement
                self._addDirection(P1)
            elif P1.tag == "note":      # Note
                self._addNote(P1)
            elif P1.tag == "backup":    # Voices
                self._addBackup(P1)
        
        if "implicit" not in measure.attrib and float(self.meta[0]["Time"].split("_")[0]) - self.duration_onset > 0.05:
            print ("- - - - -\nImplicit measure")
            print ("Measure:{}".format(self.measure_num))
            print ("Duration:{}".format(self.duration_onset))
            print ("Time signature:{}\n".format(float(self.meta[0]["Time"].split("_")[0])))

    def addCredit(self, credit):
        if "Note" not in self.meta[0].keys():
            self.meta[0]["Note"] = ""
        cnt = credit.find("credit-words").text
        # Pent key
        for ck in self._pentKey:
            if ck in cnt:
                self.meta[0]["Pent"] = self._pentNum[ck]
        # Comment
        if '*' in cnt:
            self.meta[0]["Note"] = cnt

    def _addAtt(self, a_tag):
        _att = {}
        # Add Key
        if len(a_tag.find("key").find("fifths").text) == 1:
            _att["Key"] = "+{}_{}".format(a_tag.find("key").find("fifths").text,
                                        a_tag.find("key").find("mode").text)
        else:
            _att["Key"] = "{}_{}".format(a_tag.find("key").find("fifths").text,
                                        a_tag.find("key").find("mode").text)
        _att["Key"] = key2text(_att["Key"])
        # Add Division
        _att["Division"] = a_tag.find("divisions").text # #divisions per quarter note
        # Add Time signature
        _att["Time"] = "{}_{}".format(a_tag.find("time").find("beats").text,
                                      a_tag.find("time").find("beat-type").text)

        self.meta.append(_att)

    def _addHarmony(self, h_tag):
        """
        Parse chord of each measure.
        Notation:
            <Root>_<Chord>,
                <Root> := <Note Name>_<+0/+1:sharp/-1:flat>. Example: E-1 for E flat, C+1 for C sharp
                <Chord> : see https://usermanuals.musicxml.com/MusicXML/Content/EL-MusicXML-kind.htm for details
                    major : major triad
                    minor : minor triad
                    major-seventh :
                    diminished : 
                    ......

        Steps:
            1. Parse Root
            2. Root inversion
            3. Parse Chord
            4. Chord changes within a note
        """
        # 1. Root
        root = h_tag.find("root").find("root-step").text
        if h_tag.find("root").find("root-alter") != None:
            # Sharp/flat
            alt = h_tag.find("root").find("root-alter").text
            if len(alt) == 1:
                root += "+{}".format(alt) # B+1
            else:
                root += "{}".format(alt) # B-1
        else:
            root += "+0"

        # 2. Inversion
        if h_tag.find("bass") != None:
            bass = h_tag.find("bass").find("bass-step").text
            if h_tag.find("bass").find("bass-alter") != None:
                alt = h_tag.find("bass").find("bass-alter").text
                if len(alt) == 1:
                    bass += "+"
                else:
                    bass += "-"

                if alt != "1" and alt != "-1":
                    print ("alt:{}.".format(alt))
            root= root +"/"+ bass

        # 3. Chord
        chord = h_tag.find("kind").text

        self.harmony = "{}_{}".format(root, chord)

        # To put harmonies in a file
        key = "{}_{}_{}".format(self.measure_num, self.note_in_measure[self.measure_num], len(self.chord)) # measureNum_noteKey_noteIndex
        self.chord.append({"Key":key, "Chord":self.harmony, "Next":"_END_"}) # Add to the chord list
        self.note_in_measure[self.measure_num] += 1 # Update the number of notes

        # 4.
        if self.current_chord == None:
            self.current_chord = key

        if self.is_link_chord == False:
            self.current_chord = key

            # No multiple keys -> self.is_link_chord will be set to False in _addNote
            self.is_link_chord = True
        else:
            # Link two chords together!
            # We did not get a note within two chords, which means that we have multiple chords within a note.
            idx = int(self.current_chord.split("_")[-1])
            self.chord[idx]["Next"] = key

            self.current_chord = key

    def _addDirection(self, d_tag):
        if d_tag.find("direction-type").find("metronome") != None:
            # Tempo
            self.tempo = d_tag.find("direction-type").find("metronome").find("per-minute").text
            unit = d_tag.find("direction-type").find("metronome").find("beat-unit").text
            if unit == "eight":
                self.tempo += "_8"
            elif unit == "quarter":
                self.tempo += "_4"
            elif unit == "half":
                self.tempo += "_2"
            elif unit == "whole":
                self.tempo += "_1"
            else:
                print ("Unknown unit:{}".format(unit))
        elif d_tag.find("direction-type").find("rehearsal") != None:
            # Musical structure
            self.arrangement = d_tag.find("direction-type").find("rehearsal").text
        elif d_tag.find("direction-type").find("words") != None:
            # Inst/vocal-in/vocal-out
            self.arrangement_inst = d_tag.find("direction-type").find("words").text.replace(" ", "-").replace("vacal-in", "vocal-in")
            self.arr_dict[self.arrangement_inst] = 0

    def _addNote(self, note):
        """
        Add rest/grace/note
        """
        # Add rest
        if note.find("rest") != None:
            # Step tie
            self._stepTie()
            self._stepSlur()

            # Note level with the query key
            duration = float(note.find("duration").text) / (float(self.meta[0]["Division"])*(4/float(self.meta[0]["Time"].split("_")[-1])))
            _note = {"Note":"x", "Midi":"-2", "Duration":duration,
                     "Onset":self.duration_onset, "Offset":self.duration_onset+duration}
            _note.update(self._getNoteAddition())
            self.duration_onset += duration
            _note["Key"] = self.current_chord
            self.is_link_chord = False
            self.notes_chord.append(_note)
        elif note.find("grace") != None:
            # Add grace notes
            # Get note name and midi number
            note_name, midi = self._getNoteNameMidi(note)

            # Add Tie
            self._addTie(note)
            self._addSlur(note)

            # Note level with the query key
            _note = {"Note":note_name, "Midi":midi, "Duration":"0.0", # Duration=0 for grace notes
                     "Onset":self.duration_onset, "Offset":self.duration_onset+0.0}
            _note.update(self._getNoteAddition())
            _note["Key"] = self.current_chord
            self.is_link_chord = False
            self.notes_chord.append(_note)
        else:
            # Add notes
            # Get note name and midi number
            note_name, midi = self._getNoteNameMidi(note)

            # Add Tie
            self._addTie(note)
            self._addSlur(note)

            # Unit : crochet beat. 
            # ex: time signature=3/4, duration=1 -> one quarter-note, duartion = 0.5 -> one eighth-note
            duration = float(note.find("duration").text) / (float(self.meta[0]["Division"])*(4/float(self.meta[0]["Time"].split("_")[-1])))
            # Do not change the self.duration_onset if this note belongs to a chord.
            # Example, there's a Gmajor in the score, so we'll get 3 notes sequentially:G/C/E. However, the
            # onset time of these note are the same, so do not move the global onset time (self.duration_onst)
            if note.find("chord") != None: 
                self.duration_onset -= duration

            # Note level with the query key
            _note = {"Note":note_name, "Midi":midi, "Duration":duration,
                     "Onset":self.duration_onset, "Offset":self.duration_onset+duration}
            _note.update(self._getNoteAddition())
            self.duration_onset += duration
            _note["Key"] = self.current_chord
            self.is_link_chord = False
            self.notes_chord.append(_note)

        # Lyric
        if note.find("lyric") != None:
            lyric = note.find("lyric").find("text").text
            self.lyric = lyric
        else:
            if self.arrangement_inst != "vocal-in":
                self.lyric = "x"
            else:
                self.lyric = "-"

    def _addBackup(self, backup):
        duration = float(backup.find("duration").text) / (float(self.meta[0]["Division"])*(4/float(self.meta[0]["Time"].split("_")[-1])))
        self.duration_onset -= duration

    def _getNoteAddition(self, fix=False):
        out = {#"Tone":self.harmony,
               "Tempo":self.tempo,
               "Arrangement":"{}_{}".format(self.arrangement, self.arrangement_inst),
               "Tie":self.tie,
               "Slur":self.slur,
               "Measure":self.measure_num,
               "Lyric":self.lyric,
               }
        if fix == True:
            if self.harmony != "-":
                self.harmony = "-"
            if self.tempo != "-":
                self.tempo = "-"
            if self.arrangement != "-":
                self.arrangement = "-"
        return out

    def _stepTie(self):
        if self.tie == "s":
            self.tie = "-"
        elif self.tie == "p":
            self.tie = "x"

    def _addTie(self, note):
        if note.find("tie") != None:
            # At the start/end of a slur, change the state of self.tie to "s"  or "p"
            state = note.find("tie").attrib["type"]
            if state == "start":
                self.tie = "s"
            elif state == "stop":
                self.tie = "p"
            else:
                print ("Unknown tie attributes:{}".format(state))
                exit()
        else:
            # if we're within the start/end of a slur, change the state to '-'
            # if not, change the state to 'x'
            self._stepTie()

    def _stepSlur(self):
        if self.slur == "s":
            self.slur = "-"
        elif self.slur == "p":
            self.slur = "x"

    def _addSlur(self, note):
        # Same as _addTie
        if note.find("notations") != None and note.find("notations").find("slur") != None:
            state = note.find("notations").find("slur").attrib["type"]
            if state == "start":
                self.slur = "s"
            elif state == "stop":
                self.slur = "p"
            else:
                print ("Unknown tie attributes:{}".format(state))
                exit()
        else:
            self._stepSlur()

    def _getNoteNameMidi(self, note):
        # Add note
        pitch = note.find("pitch").find("step").text
        octave = note.find("pitch").find("octave").text
        alter = "+0"
        if note.find("pitch").find("alter") != None:
            alter = note.find("pitch").find("alter").text
            if len(alter) == 1:
                alter = "+{}".format(alter)

        name = "{}{}{}".format(pitch, octave, alter)
        return name, note2midi(name)
