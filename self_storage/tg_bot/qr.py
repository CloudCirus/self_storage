import qrcode


def make_qrcode(data, filename):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=20,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")
    image.save(filename)

    return image


if __name__ == "__main__":
    data = "Customer", "Storage adress"
    filename = "qrcode.png"
    make_qrcode(data, filename)
