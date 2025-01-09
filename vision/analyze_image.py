from PIL import ImageGrab
from ollama import chat


def get_clipboard_image():
    try:
        img = ImageGrab.grabclipboard()
        return img
    except:
        print("No image found in clipboard")
        return img


def save_clipboard_image(filename="clipboard_image.png"):
    image = get_clipboard_image()
    if image:
        image.save(filename)
        print(f"Image saved as {filename}")
        return True
    return False


def analyze_image(filename: str):
    response = chat(
        model="llama3.2-vision",
        messages=[
            {
                "role": "user",
                "content": "What is in this image? Be concise.",
                "images": [filename],
            }
        ],
    )
    return response


# Usage
if __name__ == "__main__":
    filename = "clipboard_image.png"
    save_clipboard_image(filename)
    response = analyze_image(filename)
    print(response)
