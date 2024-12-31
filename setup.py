from setuptools import setup, find_packages

setup(
    name="Leviathan",
    version="2.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "leviathan=Leviathan.leviathan.leviathan:main",
            "sto=Leviathan.save_to_obsidian.save_to_obsidian:main",
            "tutorialize=Leviathan.tutorialize.tutorialize:main",
        ],
    },
)
