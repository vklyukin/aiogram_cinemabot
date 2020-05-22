from aiogram.utils.markdown import code, bold

lines = {
    'start': "Hi!\nI'm CinemaBot from YDS!\nType \\help to read more about me.\nDeveloped by Valeriy Klyukin.",
    'help': """I can find any film/tv-show by its name and give the link to you so you could watch it online"""
            f"""\n{bold("Search usage")}: just write the name of the film:\n{code("Venom")}\nand you will receive the link """
            """to the website where you can watch it\n"""
            f"""\n{bold("Random usage")}: type \\random and enjoy the movie from the IMDb top-250 list"""
    ,
    'no_such_film': "Unfortunately, film/tv-show with name **{}** is not found",
    'film_found': "**{}**\n{}",
    'random_movie': "**{}**\n{}\nRating: {:.2f}",
    'not_available': 'Service is not available'
}