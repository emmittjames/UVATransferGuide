import re
from string import capwords

# method to make course_title strings match those of SIS
# ex: "The intro stars and The galaxies" -> "The Intro Stars and the Galaxies"
# ex: "University Of Texas" -> "University of Texas"
def course_title_format(s):

    rn = [ # some roman numerals!
    "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX",
    "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX",
    "XX", "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI", "XXVII", "XXVIII", "XXIX",
    "XXX", "XXXI", "XXXII", "XXXIII", "XXXIV", "XXXV", "XXXVI", "XXXVII", "XXXVIII", "XXXIX",
    "XL", "XLI", "XLII", "XLIII", "XLIV", "XLV", "XLVI", "XLVII", "XLVIII", "XLIX",
    "L", "LI", "LII", "LIII", "LIV", "LV", "LVI", "LVII", "LVIII", "LIX",
    "LX", "LXI", "LXII", "LXIII", "LXIV", "LXV", "LXVI", "LXVII", "LXVIII", "LXIX",
    "LXX", "LXXI", "LXXII", "LXXIII", "LXXIV", "LXXV", "LXXVI", "LXXVII", "LXXVIII", "LXXIX",
    "LXXX", "LXXXI", "LXXXII", "LXXXIII", "LXXXIV", "LXXXV", "LXXXVI", "LXXXVII", "LXXXVIII", "LXXXIX",
    "XC", "XCI", "XCII", "XCIII", "XCIV", "XCV", "XCVI", "XCVII", "XCVIII", "XCIX"]

    pattern = re.compile(r'\b(?:and|or|in|to|the|of)\b', re.IGNORECASE)

    s = s.strip()
    if not s:
        return s

    words = s.split() #split by space
    title_words = []
    if words[0].lower() == "the":
        title_words.append("The") #dont change first word for courses starting with The (they exist for some reason)
        words = words[1:]

    for word in words:
        if word not in rn: #if word is not a roman numeral
            title_word = capwords(word) #capwords capitalizes first letter of word()
            if pattern.match(word):
                title_word = title_word.lower() #if and,or,in, etc lowercase it
            title_words.append(title_word)
        else:
            title_words.append(word)
    return ' '.join(title_words)