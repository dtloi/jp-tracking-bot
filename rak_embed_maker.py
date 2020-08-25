import rak_image_mainpulation
import discord

def make(item:dict):
    """
    Function that returns a discord embed that contains item details

    Parameters
    ------------
    item: dict
        {Parameter Description Here}
    """
    main_image = item["item_json"]["Item"]["mediumImageUrls"][0]["imageUrl"]
    new_main_image = rak_image_mainpulation.sz10(main_image_url=main_image)
    embedVar = discord.Embed(title=item["item_name"], description=item["price"], color=0x00ff00)
    embedVar.set_image(url=new_main_image)
    embedVar.add_field(name="Link", value=item["item_url"], inline=False)
    return embedVar