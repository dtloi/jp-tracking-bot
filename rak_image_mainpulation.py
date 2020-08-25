import re

def sz10(main_image_url:str):
    """
    {Command Description Here}

    Parameters
    ------------
    main_image_url: str
        {Parameter Description Here}
    """
    regex_for_reso = re.compile("ex=")
    match_or_not = regex_for_reso.search(main_image_url)
    if match_or_not:
        start = match_or_not.span()[0]
        end = match_or_not.span()[1]
        resolution = main_image_url[end:]

        regex_to_split_reso = re.compile("x")
        reso_split = regex_to_split_reso.search(resolution)
        reso_width_index = reso_split.span()[0]
        reso_height_index = reso_split.span()[1]
        reso_width = int(resolution[:reso_width_index])
        reso_height = int(resolution[reso_height_index:])

        new_reso = "ex=" + str(reso_width * 10) + "x" + str(reso_height * 10)
        new_main_image = main_image_url[:start] + new_reso
        return new_main_image
    else:
        return main_image_url