import re


def format_name(name):
        # If there is a (, dump everything from there on
        name = name.split('(')[0]

        # Initial replacements and formatting
        name = name.strip().upper()
        name = re.sub(r'[,+.*]', '', name)
        name = re.sub(r'\s+(JR|SR|III|II|IV|V)$', '', name)
        name = name.replace("'", "").replace("-", " ")

        # Additional specific replacements
        replacements = {
            "MITCHELL T": "MITCH T",
            "ROBBY ANDERSON": "ROBBIE ANDERSON",
            "WILLIAM ": "WILL ",
            "OLABISI": "BISI",
            "ELI MITCHELL": "ELIJAH MITCHELL",
            "CADILLAC WILLIAMS": "CARNELL WILLIAMS",
            "GABE DAVIS": "GABRIEL DAVIS",
            "JEFFERY ": "JEFF ",
            "JOSHUA ": "JOSH ",
            "CHAUNCEY GARDNER": "CJ GARDNER",
            "BENNETT SKOWRONEK": "BEN SKOWRONEK",
            "NATHANIEL DELL": "TANK DELL",
        }

        for old, new in replacements.items():
            name = name.replace(old, new)

        # Handle specific starting names
        if name.startswith("MICHAEL "):
            name = name.replace("MICHAEL ", "MIKE ", 1)
        if name.startswith("KENNETH "):
            name = name.replace("KENNETH ", "KEN ", 1)

        return name