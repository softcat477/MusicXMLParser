import xml.etree.ElementTree as ET
import pprint
from Parser.Score import Score
import glob

pp = pprint.PrettyPrinter(indent=4)

for path in glob.glob("Score/*/*.xml"):
    print (path)
    tree = ET.parse(path)
    root = tree.getroot()

    score = Score(len(list(root.iter("measure"))))

    m_count = 0
    for m in root.iter("measure"):
        m_count += 1
        score.addMeasure(m)

    for c in root.iter("credit"):
        score.addCredit(c)

    name = path.replace(".xml", "")
    score.dumpNotes(name)
    score.dumpTones(name)
    score.dumpMeta(name)
