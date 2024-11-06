import os
import sys
import pytest
from unittest.mock import patch
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
# Fonctions à tester
from config import CHOICE_PROMPT, IMAGES_NAMES, CASCADES_NAMES

@pytest.fixture
def setup_test_directory(tmpdir):
    img_dir = tmpdir.mkdir("img")
    cascade_dir = tmpdir.mkdir("cascade")
    
    # Créer des fichiers dans le dossier img/ et cascade/
    img_files = ["image1.jpg", "image2.png"]
    cascade_files = ["cascade1.xml", "cascade2.xml"]

    for img_file in img_files:
        img_dir.join(img_file).write("dummy content")

    for cascade_file in cascade_files:
        cascade_dir.join(cascade_file).write("dummy content")

    return str(img_dir), str(cascade_dir)

def test_images_names_with_authorization(setup_test_directory):
    img_dir, _ = setup_test_directory

    # Mock l'appel à os.listdir pour retourner les fichiers dans le répertoire img/
    with patch("os.listdir", return_value=["image1.jpg", "image2.png"]), patch("os.path.isfile", return_value=True):  # Assurer que les fichiers sont reconnus comme des fichiers
        image_names = IMAGES_NAMES(True)
        assert image_names == ["image1.jpg", "image2.png"]

def test_images_names_without_authorization():
    assert IMAGES_NAMES(False) is None

def test_cascades_names_with_authorization(setup_test_directory):
    _, cascade_dir = setup_test_directory

    # Mock l'appel à os.listdir pour retourner les fichiers dans le répertoire cascade/
    with patch("os.listdir", return_value=["cascade1.xml", "cascade2.xml"]), patch("os.path.isfile", return_value=True):  # Assurer que les fichiers sont reconnus comme des fichiers
        cascade_names = CASCADES_NAMES(True)
        assert cascade_names == ["cascade1.xml", "cascade2.xml"]

def test_cascades_names_without_authorization():
    assert CASCADES_NAMES(False) is None

def test_choice_prompt(setup_test_directory):
    img_dir, cascade_dir = setup_test_directory
    # Simuler os.listdir
    with patch("os.listdir", return_value=["cascade1.xml", "cascade2.xml"]), patch("os.path.isfile", return_value=True):  # Pas de fichiers
        prompt = CHOICE_PROMPT("chat")
        print(prompt)
        assert "Quelle est la meilleure méthode pour reconnaitre un/e chat" in prompt
        assert "fichiers cascades: ['cascade1.xml', 'cascade2.xml']" in prompt


def test_empty_directory_behavior(setup_test_directory):
    img_dir, cascade_dir = setup_test_directory

    # Simuler os.listdir pour retourner un dossier vide
    with patch("os.listdir", return_value=[]), patch("os.path.isfile", return_value=False):  # Pas de fichiers
        image_names = IMAGES_NAMES(True)
        assert image_names == None

    # Simuler os.listdir pour retourner un dossier vide
    with patch("os.listdir", return_value=[]), patch("os.path.isfile", return_value=False):  # Pas de fichiers
        cascade_names = CASCADES_NAMES(True)
        assert cascade_names == None