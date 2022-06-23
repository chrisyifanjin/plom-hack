import os
import fitz
import re
from django.utils.text import slugify
from .models import UploadedPDF


class ExamBuildException(Exception):
    pass


def create_uploaded_pdf(user_id: int, is_guest: bool, pdf) -> UploadedPDF:
    filename_slug = slugify(re.sub('.pdf$', '', pdf.name))
    upload_pdf = UploadedPDF(user_id=user_id, is_guest_upload=is_guest, filename_slug=filename_slug, pdf=pdf)
    upload_pdf.save()
    return upload_pdf


def delete_uploaded_pdf(saved_pdf: UploadedPDF) -> None:
    if os.path.isfile(str(saved_pdf.pdf)):
        if saved_pdf.is_guest_upload:
            user_dir = f'media/guest{saved_pdf.user_id}'
        else:
            user_dir = f'media/user{saved_pdf.user_id}'
        os.remove(str(saved_pdf.pdf))

        saved_pdf.delete()

        # if directory is empty, delete folder
        if len(os.listdir(user_dir)) == 0:
            os.rmdir(user_dir)


def create_mock_exam(pdf_orig: UploadedPDF, top_label: str) -> fitz.Document:
    document = fitz.Document(pdf_orig.pdf)

    # important: We're one-indexing when looping over pages. So the first page (page 1, index 0) is an odd page!
    for i in range(1, document.page_count+1):
        page = document[i-1]
        page.clean_contents()

        page_width = page.bound().width
        page_height = page.bound().height

        create_top_centre_stamp(page, page_width, top_label)

        if i % 2 == 0:
            insert_dummy_qr_codes_even(page, page_width, page_height)
            insert_staple_even(page, page_width)
        else:
            insert_dummy_qr_codes_odd(page, page_width, page_height)
            insert_staple_odd(page)

    delete_uploaded_pdf(pdf_orig)
    return document


def create_top_centre_stamp(page: fitz.Page, width: int, label: str) -> None:
    rect = fitz.Rect(width // 2 - 90, 20, width // 2 + 90, 46)
    excess = page.insert_textbox(
        rect,
        label,
        fontsize=18,
        color=[0, 0, 0],
        fontname="Helvetica",
        fontfile=None,
        align=1
    )
    if excess <= 0:
        raise ExamBuildException("Label does not fit in top text box.")
    page.draw_rect(rect, color=[0, 0, 0])


def insert_dummy_qr_code(page: fitz.Page, top_x: int, top_y: int) -> None:
    rect = fitz.Rect(top_x, top_y, top_x + 70, top_y + 70)
    page.insert_image(rect, stream=open('media/dummy/dummy_qr_code.png', 'rb').read(), overlay=True)
    page.draw_rect(rect, color=[0, 0, 0], width=0.5)


def insert_dummy_qr_codes_even(page: fitz.Page, page_width: int, page_height: int) -> None:
    top_left = (15, 20)
    bottom_left = (15, page_height - 90)
    bottom_right = (page_width - 85, page_height - 90)

    insert_dummy_qr_code(page, *top_left)
    insert_dummy_qr_code(page, *bottom_left)
    insert_dummy_qr_code(page, *bottom_right)


def insert_dummy_qr_codes_odd(page: fitz.Page, page_width: int, page_height: int) -> None:
    top_right = (page_width - 85, 20)
    bottom_left = (15, page_height - 90)
    bottom_right = (page_width - 85, page_height - 90)

    insert_dummy_qr_code(page, *top_right)
    insert_dummy_qr_code(page, *bottom_left)
    insert_dummy_qr_code(page, *bottom_right)


def insert_staple_even(page: fitz.Page, page_width: int) -> None:
    rect = fitz.Rect(page_width - 90, 20, page_width - 15, 90)
    draw_do_not_mark_corner(page, rect.top_left, rect.top_right, rect.bottom_right)
    
    mat = fitz.Matrix(-45)
    pivot = rect.top_right / 2 + rect.bottom_left / 2
    morph = (pivot, mat)
    insert_staple_text(page, rect, morph, "sample")


def insert_staple_odd(page: fitz.Page) -> None:
    rect = fitz.Rect(15, 20, 85, 90)
    draw_do_not_mark_corner(page, rect.top_left, rect.top_right, rect.bottom_left)
    
    mat = fitz.Matrix(45)
    pivot = rect.top_right / 2 + rect.bottom_left / 2
    morph = (pivot, mat)
    insert_staple_text(page, rect, morph, "sample")


def insert_staple_text(page: fitz.Page, rect: fitz.Rect, morph: tuple, text: str) -> None:
    # offset by trial and error
    offset = (-10, 24, 10, -33)

    excess = page.insert_textbox(
        rect + offset,
        text,
        fontsize=8,
        fontname='Helvetica',
        align=1,
        morph=morph
    )
    
    if excess < 0:
        raise ExamBuildException("Label text did not fit on staple corner.")


def draw_do_not_mark_corner(page: fitz.Page, top_left_point: int, top_right_point: int, bottom_point: int) -> None:
    triangle = page.new_shape()
    triangle.draw_line(top_left_point, top_right_point)
    triangle.draw_line(top_right_point, bottom_point)
    triangle.finish(width=0.5, color=[0, 0, 0], fill=[0.75, 0.75, 0.75])
    triangle.commit()
