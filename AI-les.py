# Importeer de random module zodat de computer willekeurige keuzes kan maken
import random

# Maak een lijst met de mogelijke keuzes in het spel
opties = ["steen", "papier", "schaar"]

# Vraag de speler om een keuze in te voeren
# input() leest tekst van de gebruiker
speler_keuze = input("Kies steen, papier of schaar: ")

# Zorg dat de invoer altijd kleine letters is (handig voor vergelijken)
speler_keuze = speler_keuze.lower()

# Laat de computer willekeurig een keuze maken uit de lijst 'opties'
computer_keuze = random.choice(opties)

# Print de keuze van de computer zodat de speler ziet wat er gekozen is
print("Computer koos:", computer_keuze)

# Controleer eerst of de speler iets geldigs heeft ingevoerd
if speler_keuze not in opties:
    # Als de invoer niet klopt, geef een foutmelding
    print("Ongeldige keuze. Kies steen, papier of schaar.")

# Als beide dezelfde keuze hebben is het gelijkspel
elif speler_keuze == computer_keuze:
    print("Gelijkspel!")

# Alle situaties waarin de speler wint
elif (
    (speler_keuze == "steen" and computer_keuze == "schaar") or
    (speler_keuze == "papier" and computer_keuze == "steen") or
    (speler_keuze == "schaar" and computer_keuze == "papier")
):
    # Bericht dat de speler gewonnen heeft
    print("Je wint!")

# Als geen van de bovenstaande situaties klopt, wint de computer
else:
    print("Computer wint!")
    
