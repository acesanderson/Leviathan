from setuptools import setup, find_packages

setup(
    name="Leviathan",
    version="2.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "leviathan=leviathan.leviathan:main",
            "sto=save_to_obsidian.save_to_obsidian:main",
            "tutorialize=tutorialize.tutorialize:main",
        ],
    },
)
