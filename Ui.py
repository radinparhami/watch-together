import flet as ft
from time import sleep

location = "HOME"

# global
page_title = "Room Control Panel"
def_page_width = 500
def_page_height = 500
page_width = def_page_width
page_height = def_page_height

# main
main_scale = 1.5
main_space_top = main_scale * 50
main_space_left = main_scale * 200


def reset_window(page):
    global page_width, page_height
    page_height = def_page_height
    page_width = def_page_width
    page.window_width = page_width
    page.window_height = page_height
    page.window_center()


def main_center(*buttons, top, left):
    return ft.Row(
        [
            ft.Column([

                *[ft.Container(
                    content=btn,
                    alignment=ft.alignment.center,
                    width=left,
                    height=top,
                ) for btn in buttons]
            ], alignment=ft.MainAxisAlignment.CENTER)
        ], alignment=ft.MainAxisAlignment.CENTER
    )


def on_window_event(e: ft.ControlEvent):
    global page_height, page_width
    e.page: ft.Page

    page_height = e.page.window_height
    page_width = e.page.window_width
    print(e.data, location)
    match e.data:
        case "maximize":
            if location == "CREATE":
                page_height -= 10
                e.page.window_height = page_height
                e.page.controls[0].controls[0].margin.top = -80
            else:
                print(e.data, location)
        case "unmaximize":
            if location == "CREATE":
                page_height = def_page_height
                e.page.window_height = page_height
                e.page.controls[0].controls[0].margin.top = -10
            else:
                reset_window(e.page)
                print(e.data, location)
            # tray_icon.visible = True
        # case "close":
        # tray_icon.stop()
        # p.window_destroy()
        case "blur" | "focus":
            if location == "CREATE":
                selected = e.data == "blur"
                res = [(0, 105, 5), (100, 20, -5)][selected]
                for i in range(*res):
                    e.page.window_opacity = i / 100
                    e.page.update()
                    sleep(.05)
        case _:
            return
        #     print(e.data)
    e.page.update()


def control_panel(page, action, result):
    match action:
        case "WFS":
            page.window_full_screen = result
        case _:
            return
    page.update()


def main(page: ft.Page):
    global location, page_width, page_height
    page.window_center()
    page.title = page_title
    page.window_resizable = False
    page.window_height = page_width
    page.window_width = page_height
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.on_window_event = on_window_event

    def back_btn():
        back_button = ft.ElevatedButton(text="Back", on_click=home, scale=main_scale)
        return ft.Container(
            back_button,
            margin=ft.margin.only(
                top=main_scale ** 4, left=2.7 * main_scale ** 4,
                bottom=main_scale ** 4
            )
        )

    def on_join_click(e):
        global location
        page.clean()
        # page.window_maximized = not page.window_maximized
        page.vertical_alignment = None
        page.horizontal_alignment = None
        location = "JOIN"
        room_id = ft.TextField(label="RoomID", scale=.75 * main_scale)
        join_button = ft.ElevatedButton(text="Join", scale=main_scale)
        page.add(
            ft.Column([back_btn()], alignment=ft.MainAxisAlignment.START),
            ft.Row([
                ft.Column(
                    [ft.Container(room_id, margin=ft.margin.only(bottom=main_scale ** 6)),
                     ft.Row(
                         [join_button], width=page.window_width * .6,
                         alignment=ft.MainAxisAlignment.CENTER)
                     ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    height=page.window_height * .75,
                )
            ], alignment=ft.MainAxisAlignment.CENTER),

        )

    def on_create_click(e):
        global page_width, page_height, location
        page.clean()
        page.vertical_alignment = None
        page.window_always_on_top = True
        page.horizontal_alignment = None
        page.window_maximizable = True
        page_width *= 1.67
        page.window_width = page_width
        page.window_center()
        location = "CREATE"
        sample_media = [
            ft.VideoMedia(
                "https://user-images.githubusercontent.com/28951144/229373720-14d69157-1a56-4a78-a2f4-d7a134d7c3e9.mp4"
            ),
        ]
        video = ft.Video(
            expand=True,
            playlist=sample_media,
            playlist_mode=ft.PlaylistMode.LOOP,
            aspect_ratio=16 / 9,
            fit=ft.ImageFit.COVER,
            volume=100,
            autoplay=False,
            filter_quality=ft.FilterQuality.HIGH,
            muted=False,
            wakelock=True,
            on_loaded=lambda e: print("Video loaded successfully!"),
            on_enter_fullscreen=lambda e: control_panel(page,"WFS", True),
            on_exit_fullscreen=lambda e: control_panel(page,"WFS", False),
        )
        page.add(
            ft.Stack(
                controls=[
                    ft.Container(video, margin=ft.margin.only(top=-10, left=-10, right=-10)),
                    back_btn(),
                ],
            )
        )

    def on_quit_click(e):
        page.window_destroy()

    def home(e):
        global location, page_width, page_height
        page.clean()
        location = "HOME"
        if not page.window_maximized:
            reset_window(page)
        page.window_always_on_top = False
        page.window_maximized = False
        page.window_maximizable = False
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.MainAxisAlignment.CENTER
        join_button = ft.ElevatedButton(text="Join room", on_click=on_join_click, scale=main_scale)
        create_button = ft.ElevatedButton(text="Create room", on_click=on_create_click, scale=main_scale)
        quit_button = ft.ElevatedButton(text="Quit", on_click=on_quit_click, scale=main_scale)

        page.add(main_center(join_button, create_button, quit_button, top=main_space_top, left=main_space_left))

    home(None)


ft.app(target=main)
