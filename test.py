url_line = "sdfklssdfdsfsd, joe ummmmm huhhh smo <thisismyemail>"
url = url_line.split(", ")[0]
nameAndEmail = url_line.split(", ")[1]
numSpaces = nameAndEmail.count(" ")
email = nameAndEmail.split(" ", 6)[numSpaces]
lastName = nameAndEmail.split(" ", 6)[numSpaces - 1]

firstName = ""
for i in range(0, numSpaces - 1):
    firstName += nameAndEmail.split(" ", 6)[i] # First name will be all words in between comma and last name
    if i == numSpaces - 2:
        pass
    else:
        firstName += " "

print(lastName)
