_name2Midi = {"C":60, "D":62, "E":64, "F":65, "G":67, "A":69, "B":71}
circle5 = {"+0":{"major":"C", "minor":"a"},
           "+1":{"major":"G", "minor":"e"},
           "+2":{"major":"D", "minor":"b"},
           "+3":{"major":"A", "minor":"f+"},
           "+4":{"major":"E", "minor":"c+"},
           "+5":{"major":"B", "minor":"g+"},
           "+6":{"major":"F+", "minor":"d+"},
           "+7":{"major":"C+", "minor":"a+"},
           "-1":{"major":"F", "minor":"d"},
           "-2":{"major":"B-", "minor":"g"},
           "-3":{"major":"E-", "minor":"c"},
           "-4":{"major":"A-", "minor":"f"},
           "-5":{"major":"D-", "minor":"b-"},
           "-6":{"major":"G-", "minor":"e-"},
}

def note2midi(note):
    if '+' in note:
        D = '+'
    else:
        D = '-'
    name = note[0]
    octave = note.split(D)[0][1:]
    alter = D+note.split(D)[-1]

    out = _name2Midi[name] + int(alter)
    out += (int(octave)-4)*12

    return str(out)

def key2text(key):
    sign, m = key.split("_")
    return circle5[sign][m]

if __name__ == "__main__":

    note = "C0+0"
    out = note2midi(note)
    print (note, out)

    note = "G9+0"
    out = note2midi(note)
    print (note, out)

    note = "G9-1"
    out = note2midi(note)
    print (note, out)

    note = "A3+1"
    out = note2midi("C0+0")
    out = note2midi(note)
    print (note, out)

    note = "A3-2"
    out = note2midi(note)
    print (note, out)