import pdfplumber
import pytesseract
import re


def find_largest_number_pdf():
    largest_number_text_and_images = float('-inf')

    with pdfplumber.open('input.pdf') as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            largest_number_text = scan_text(text)

            largest_number_tables = scan_tables(page)

            largest_number_images = scan_images(page)

            largest_number_text_and_images = max(largest_number_text_and_images, largest_number_text,
                                                 largest_number_tables, largest_number_images)

    print(f'The largest number in the document is: {largest_number_text_and_images}')


def scan_text(text):
    return parse_document(text)


def scan_tables(page):
    largest_number = float('-inf')

    tables = page.extract_tables()
    for table in tables:
        for row in table:
            for cell in row:
                if cell:
                    largest_number = max(largest_number, parse_document(cell))

    return largest_number


def scan_images(page):
    largest_number = float('-inf')

    for image in page.images:
        try:
            if 'bbox' in image:
                image_data = page.within_bbox(image['bbox']).to_image()
            else:
                image_data = page.to_image()

            img_pil = image_data.original.convert('RGB')
            img_text = extract_text_from_image(img_pil)

            largest_number_image = parse_document(img_text)
            largest_number = max(largest_number, largest_number_image)
        except Exception as e:
            print(f"Error processing image: {e}")
            continue

    return largest_number


def parse_document(text):
    largest_number = float('-inf')
    numbers = re.findall(r'\d+\.\d+|\d+', text)

    for number in numbers:
        value = float(number)

        if "million" in text.lower():
            value *= 1_000_000
        elif "billion" in text.lower():
            value *= 1_000_000_000
        elif "thousand" in text.lower():
            value *= 1_000

        if value > largest_number:
            largest_number = value

    return largest_number


def extract_text_from_image(image):
    return pytesseract.image_to_string(image)


if __name__ == '__main__':
    find_largest_number_pdf()
